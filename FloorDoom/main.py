import sys
import os
from blueprint_converter import BlueprintConverter

# Usage: python3 main.py <image_path> [map_name] [tile_size] [stair_regions]
# stair_regions format: "x1,y1,w1,h1;x2,y2,w2,h2" (pixel coordinates)
# Example: "32,1248,352,128;2528,1248,384,128"

if len(sys.argv) < 2:
    print("Usage: python3 main.py <image_path> [map_name] [tile_size] [stair_regions]")
    print('  stair_regions: "x,y,w,h;x,y,w,h" in pixels (optional, overrides auto-detect)')
    sys.exit(1)

image_path = sys.argv[1]
map_name   = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(image_path))[0]
tile_size  = int(sys.argv[3]) if len(sys.argv) > 3 else 8

stair_regions = []
if len(sys.argv) > 4:
    for region in sys.argv[4].split(';'):
        x, y, w, h = map(int, region.split(','))
        stair_regions.append((x, y, w, h))

if not os.path.exists(image_path):
    print(f"Error: Cannot find file {image_path}")
    sys.exit(1)

os.makedirs('output', exist_ok=True)

converter = BlueprintConverter(image_path=image_path, tile_size=tile_size, stair_regions=stair_regions)
converter.load_image()
converter.clean_image()
converter.detect_walls()
converter.detect_floors()
converter.detect_doors()
converter.detect_stairs()

tilemap = converter.combine_to_array()
converter.export(f'output/{map_name}')
converter.export_js(map_name, f'output/{map_name}.js')

stair_tiles = int((tilemap == 3).sum())
print(f"Exported: output/{map_name}.js  ({tilemap.shape[1]}w × {tilemap.shape[0]}h tiles, {stair_tiles} stair/exit cells)")
