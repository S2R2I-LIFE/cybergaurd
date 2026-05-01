import numpy as np
import cv2
from PIL import Image

class BlueprintConverter:
    def __init__(self, image_path, tile_size=8, stair_regions=None):
        self.image_path = image_path
        self.tile_size = tile_size  # pixels per tile
        self.stair_regions = stair_regions or []  # [(x, y, w, h), ...] in pixel coords

        # Color codes for output
        self.FLOOR    = 0
        self.WALL     = 1
        self.DOOR     = 2
        self.STAIRS   = 3
        self.EXTERIOR = 4

    def load_image(self):
        img = cv2.imread(self.image_path)
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.original = img.copy()
        return self.gray

    def clean_image(self):
        """Remove text and small symbols"""
        _, binary = cv2.threshold(
            self.gray, 200, 255,
            cv2.THRESH_BINARY_INV
        )

        # FIX: start from binary and erase small contours (text, symbols).
        # Previous approach (blank mask + fill large contours) filled room
        # interiors solid, making clean 95%+ nonzero and breaking everything.
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        mask = binary.copy()
        for cnt in contours:
            if cv2.contourArea(cnt) <= 500:
                cv2.drawContours(mask, [cnt], -1, 0, -1)

        self.clean = mask
        return mask

    def detect_walls(self):
        """Extract wall lines"""
        # Larger kernel + 2 iterations closes wider gaps between wall segments
        kernel = np.ones((5,5), np.uint8)
        walls = cv2.morphologyEx(
            self.clean,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2
        )
        self.walls = walls
        return walls

    def detect_floors(self):
        """Mark interior floor via border flood fill.
        Exterior pixels connect to image border through non-wall space;
        interior floor pixels do not."""
        not_wall = cv2.bitwise_not(self.walls)
        h, w = not_wall.shape
        flood = not_wall.copy()
        mask = np.zeros((h + 2, w + 2), np.uint8)

        for x in range(w):
            if flood[0, x] == 255:
                cv2.floodFill(flood, mask, (x, 0), 0)
            if flood[h-1, x] == 255:
                cv2.floodFill(flood, mask, (x, h-1), 0)
        for y in range(h):
            if flood[y, 0] == 255:
                cv2.floodFill(flood, mask, (0, y), 0)
            if flood[y, w-1] == 255:
                cv2.floodFill(flood, mask, (w-1, y), 0)

        # Close interior holes caused by wall gaps that let exterior flood in.
        # 21px radius only bridges small gaps — true exterior (large open area) unaffected.
        fill_kernel = np.ones((21, 21), np.uint8)
        filled = cv2.morphologyEx(flood, cv2.MORPH_CLOSE, fill_kernel)
        self.floors = cv2.bitwise_and(filled, not_wall)
        return self.floors

    def detect_doors(self):
        """Find door arcs"""
        contours, _ = cv2.findContours(
            self.clean,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )

        door_mask = np.zeros_like(self.clean)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)

            if perimeter == 0:
                continue

            if area < 500 or area > 20000:
                continue

            # FIX: reject elongated shapes (wall segments, not door arcs)
            x, y, bw, bh = cv2.boundingRect(cnt)
            box_aspect = bw / bh if bh > 0 else 0
            if box_aspect < 0.4 or box_aspect > 2.5:
                continue

            circularity = 4 * np.pi * area / (perimeter ** 2)

            # Arcs have mid circularity (not full circle)
            if 0.3 < circularity < 0.75:
                cv2.drawContours(
                    door_mask, [cnt], -1, 255, -1
                )

        self.doors = door_mask
        return door_mask

    def detect_stairs(self):
        """
        Stairs are in corners of building.
        If stair_regions provided at init, use those pixel rects directly.
        Otherwise auto-detect via dense parallel horizontal line heuristic.
        """
        stair_mask = np.zeros_like(self.clean)

        if self.stair_regions:
            for (x, y, w, h) in self.stair_regions:
                cv2.rectangle(stair_mask, (x, y), (x + w, y + h), 255, -1)
            self.stairs = stair_mask
            return stair_mask

        h_kernel = np.ones((1, 30), np.uint8)
        h_lines = cv2.morphologyEx(
            self.clean, cv2.MORPH_OPEN, h_kernel
        )

        # FIX: individual horizontal lines have h=1-2px — h>50 can never pass.
        # Dilate vertically to merge nearby parallel lines into stair regions.
        v_kernel = np.ones((20, 1), np.uint8)
        merged = cv2.dilate(h_lines, v_kernel)

        contours, _ = cv2.findContours(
            merged,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect = w / h if h > 0 else 0

            # Count distinct horizontal lines in region (corridor walls = few
            # lines; stair symbols = many densely packed lines)
            region = h_lines[y:y+h, x:x+w]
            row_has_line = np.any(region > 0, axis=1)
            line_count = int(np.sum(np.diff(row_has_line.astype(int)) > 0))

            if (area > 2000 and w > 50 and h > 50
                    and aspect < 4.0
                    and line_count >= 5):
                cv2.rectangle(
                    stair_mask,
                    (x, y), (x+w, y+h),
                    255, -1
                )

        self.stairs = stair_mask
        return stair_mask

    def combine_to_array(self):
        """Build final tilemap array"""
        h, w = self.walls.shape

        # Exterior = unclassified; floor only inside building boundary
        result = np.full((h, w), self.EXTERIOR, dtype=np.uint8)
        result[self.floors > 0]  = self.FLOOR
        result[self.walls > 0]   = self.WALL
        result[self.doors > 0]   = self.DOOR
        result[self.stairs > 0]  = self.STAIRS

        tile_h = h // self.tile_size
        tile_w = w // self.tile_size

        tilemap = np.zeros(
            (tile_h, tile_w), dtype=np.uint8
        )

        for y in range(tile_h):
            for x in range(tile_w):
                region = result[
                    y*self.tile_size:(y+1)*self.tile_size,
                    x*self.tile_size:(x+1)*self.tile_size
                ]
                # FIX: priority order so thin walls aren't outvoted by
                # surrounding floor pixels in the majority vote.
                if np.any(region == self.DOOR):
                    tilemap[y, x] = self.DOOR
                elif np.any(region == self.STAIRS):
                    tilemap[y, x] = self.STAIRS
                elif np.any(region == self.WALL):
                    tilemap[y, x] = self.WALL
                else:
                    values, counts = np.unique(region, return_counts=True)
                    tilemap[y, x] = values[np.argmax(counts)]

        # Recover interior regions mislabeled as exterior due to wall gaps.
        # True exterior touches the tilemap border; enclosed mislabeled regions do not.
        ext_mask = (tilemap == self.EXTERIOR).astype(np.uint8) * 255
        _, labels, stats, _ = cv2.connectedComponentsWithStats(ext_mask)
        for label in range(1, stats.shape[0]):
            rows, cols = np.where(labels == label)
            touches_border = (
                rows.min() == 0 or rows.max() == tile_h - 1 or
                cols.min() == 0 or cols.max() == tile_w - 1
            )
            if not touches_border:
                tilemap[labels == label] = self.FLOOR

        self.tilemap = tilemap
        return tilemap

    def export(self, output_path):
        """Save array and visual preview"""
        np.save(output_path + '.npy', self.tilemap)

        preview = np.zeros(
            (*self.tilemap.shape, 3),
            dtype=np.uint8
        )

        # Colors in BGR order (cv2.imwrite uses BGR)
        preview[self.tilemap == self.EXTERIOR] = [30,  30,  30 ]  # Near-black
        preview[self.tilemap == self.FLOOR]    = [200, 200, 200]  # Gray
        preview[self.tilemap == self.WALL]     = [0,   0,   0  ]  # Black
        preview[self.tilemap == self.DOOR]     = [0,   255, 0  ]  # Green
        preview[self.tilemap == self.STAIRS]   = [0,   0,   255]  # Red

        cv2.imwrite(output_path + '_preview.png', preview)

        return self.tilemap

    def export_js(self, map_name, output_path):
        """Export tilemap as maps.js entry.
        Converter codes → game codes:
          FLOOR(0)→0, WALL(1)→1, DOOR(2)→0, STAIRS(3)→0, EXTERIOR(4)→1
        """
        remap = {
            self.FLOOR:    0,
            self.WALL:     1,
            self.DOOR:     0,  # blueprint door arcs = passable openings = floor
            self.STAIRS:   2,  # stairwells = entrance/exit
            self.EXTERIOR: 1,
        }

        lines = [f'  {map_name}: [']
        for row in self.tilemap:
            cells = ','.join(str(remap[v]) for v in row)
            lines.append(f'    [{cells}],')
        lines.append('  ],')

        with open(output_path, 'w') as f:
            f.write('// Cell types: 0=floor  1=wall  2=exit door  3=policy card  4=scenario  5=FT pickup\n')
            f.write('\n')
            f.write('const MAPS = {\n\n')
            f.write('\n'.join(lines))
            f.write('\n\n};\n')

        return output_path

# Usage
# converter = BlueprintConverter('floor_plan.png', tile_size=8)
# converter.load_image()
# converter.clean_image()
# converter.detect_walls()
# converter.detect_floors()
# converter.detect_doors()
# converter.detect_stairs()
# tilemap = converter.combine_to_array()
# converter.export('floor3')
