# CyberGuard Variable Reference

Quick lookup for tuneable constants and state fields. File paths relative to `cyberguard/`.

---

## state.js

### GAME_CONFIG
| Variable | Value | Purpose |
|---|---|---|
| `canvas_width` | 800 | Render canvas width in pixels |
| `canvas_height` | 500 | Render canvas height in pixels |
| `fov` | π/3 (~60°) | Horizontal field of view in radians |
| `move_speed` | 3.5 | Player movement speed (units/sec) |
| `turn_speed` | 2.0 | Keyboard turn speed (radians/sec) |
| `player_radius` | 0.25 | Collision radius (fractions of a tile) |
| `wall_height_scale` | 450 | Controls perceived ceiling height; higher = taller walls |
| `minimap_scale` | 10 | Pixels per tile on the minimap overlay |
| `minimap_visible` | true | Minimap shown on game start |

### FT (Financial Times) Throw Constants
| Variable | Value | Purpose |
|---|---|---|
| `FT_STUN_DURATION` | 8.0 | Seconds an NPC stays stunned after a hit |
| `FT_THROW_RANGE` | 7.0 | Max throw distance in tile units |
| `FT_HALF_CONE` | 0.4 | Half-width of throw cone in radians (~23°) |
| `FT_PER_LEVEL` | 3 | Papers given to player at each level start |

### NPC AI Constants
| Variable | Value | Purpose |
|---|---|---|
| `NPC_VISION_RANGE` | 6.0 | Tiles at which NPC can spot the player |
| `NPC_CATCH_RANGE` | 0.85 | Distance at which NPC triggers an encounter |
| `NPC_FOV_HALF` | π × 0.55 | Half-angle of NPC vision cone |
| `NPC_PATROL_SPEED` | 0.9 | NPC movement speed while patrolling |
| `NPC_CHASE_SPEED` | 1.5 | NPC movement speed while chasing |
| `NPC_ALERT_TIME` | 0.4 | Seconds in alerted state before chase begins |
| `NPC_COOLDOWN_TIME` | 15.0 | Seconds NPC waits after losing player before resuming patrol |

### ROLE_CONFIG
Object keyed by `analyst` / `auditor` / `risk_manager`. Each entry has:
- `label` — display name
- `icon` — emoji
- `specialty` — array of zone IDs where role earns 2× score and forgives first wrong answer
- `perk` — description shown on briefing screen
- `tagline` — subtitle shown on HUD

### ZONE_COLORS
Maps zone ID → hex colour used for wall textures and UI accents.
`LOBBY` `GOVERN` `IDENTIFY` `PROTECT` `DETECT` `RESPOND` `RECOVER` `AI_RMF` `CAMPUS`

### LEVEL_ORDER
Array defining the progression sequence from lobby through boss level.

### LEVEL_METADATA
Object keyed by level ID. Each entry:
| Field | Purpose |
|---|---|
| `zone` | Zone ID (links to ZONE_COLORS, textures, ZONE_HINTS) |
| `next` | Default next level ID on exit |
| `exits` | Array of `{row, col, next}` — used when a level has multiple exit doors |
| `spawn` | `{x, y, angle}` — player start position and facing direction |
| `cards` | Total policy cards placed in this level |
| `scenarios` | Total scenarios placed in this level |
| `level_num` | Numeric index (0=lobby, 7=boss); links POLICY_CARDS and SCENARIOS |

### ZONE_HINTS
Maps zone ID → hint string shown when player touches a hint poster (cell 7).

### TERM_HINT_TOKENS
Array of `{ cmd, tip }` objects. Cycled through as player collects cell 10 hint tokens on the campus map. Add entries here when adding new terminal hint tokens to the map.

### GAME_STATE
Runtime mutable state. Key sub-objects:
| Path | Purpose |
|---|---|
| `GAME_STATE.screen` | Current UI mode: `briefing` `playing` `codex` `scenario` `campus_challenge` `terminal_challenge` `subnet_challenge` `panel` `gameover` `certificate` `paused` `transition` |
| `GAME_STATE.player.x/y` | Player world position |
| `GAME_STATE.player.angle` | Facing direction in radians |
| `GAME_STATE.player.role` | Selected role key (`analyst` etc.) |
| `GAME_STATE.player.ft_papers` | Remaining newspaper throws |
| `GAME_STATE.level.id` | Current level ID string |
| `GAME_STATE.level.map` | Deep-copied 2D tile array (mutates as pickups are collected) |
| `GAME_STATE.level.card_pool` | Shuffled policy cards for this level |
| `GAME_STATE.level.scenario_pool` | Shuffled scenarios for this level |
| `GAME_STATE.level.campus_challenge_pool` | Shuffled campus AP challenges (floordoom only) |
| `GAME_STATE.level.terminal_challenge_pool` | Shuffled PC workstation challenges (floordoom only) |
| `GAME_STATE.progress.grade` | Current grade (starts 100, penalised on wrong answers) |
| `GAME_STATE.progress.score` | Cumulative score |
| `GAME_STATE.progress.cards_collected` | Array of collected card IDs |
| `GAME_STATE.progress.scenarios_completed` | Array of completed scenario IDs |
| `GAME_STATE.progress.campus_completed` | Completed campus challenge IDs + `pen_X` penalty markers |
| `GAME_STATE.progress.terminal_completed` | Completed terminal challenge IDs + `pen_X` penalty markers |
| `GAME_STATE.progress.term_hints_collected` | Array of `"row_col"` keys for consumed hint tokens |
| `GAME_STATE.boss.spawned` | Whether ARIA has been spawned |
| `GAME_STATE.boss.defeated` | Whether ARIA has been beaten (unlocks exit) |
| `GAME_STATE.boss.phase` | Current ARIA question phase (0–6) |
| `GAME_STATE.active_campus_challenge` | Challenge object currently displayed in campus panel |
| `GAME_STATE.active_terminal_challenge` | Challenge object currently displayed in terminal panel |
| `GAME_STATE.active_terminal_challenge_pos` | `{row, col}` of the cell 9 that opened the terminal — used to restore if player quits |
| `GAME_STATE.active_subnet_challenge` | Active Arista EOS challenge object (campus only): challenge data + `rack_id`, `phase`, `entered_ip`, `ip_valid` |
| `GAME_STATE.subnet_close_time` | `performance.now()` timestamp — 400ms cooldown prevents immediate re-catch after dismissing rack terminal |
| `GAME_STATE.panel_close_time` | `performance.now()` timestamp — 400ms cooldown prevents panel reopening when standing on cell 11 |
| `GAME_STATE.panel_ips` | Campus-only: `{ left: [null\|{ip,valid}, ×3], right: [...×3] }` — tracks configured IPs per stairwell panel |
| `GAME_STATE.decorations` | Array of `{x, y, cellType}` for wall-offset torch sprites |
| `GAME_STATE.npcs` | Array of active NPC objects |

---

## engine.js

### Texture / Sprite Constants
| Variable | Value | Purpose |
|---|---|---|
| `TEX_SIZE` | 64 | Wall texture resolution (64×64 px) |
| `SPRITE_SIZE` | 64 | Sprite texture resolution (64×64 px) |
| `MOUSE_SENSITIVITY` | 0.001 | Radians per pixel for mouse-look |

### SPRITE_SCALE (inside renderSprites)
Per-cell-type size multiplier. NPCs default to 1.0.
| Cell | Value | Object |
|---|---|---|
| 3 | 0.50 | Policy card |
| 4 | 0.55 | Scenario trigger (NIST levels) |
| 5 | 0.40 | FT newspaper pickup |
| 6 | 0.45 | Torch |
| 7 | 0.65 | Hint poster |
| 8 | 0.60 | AP unit (campus level) |
| 9 | 0.65 | PC workstation (campus level) |
| 10 | 0.50 | Terminal hint token (`>_`) |
| 11 | 0.55 | Stairwell access panel (campus level) |

### AP Spin Speed
```js
AP_FRAMES[Math.floor(Date.now() / 200) % AP_FRAMES.length]
```
Change `200` (ms per frame). 16 frames total → full rotation = `200 × 16 = 3200ms`.
Lower = faster spin.

### Asset Paths (loadXxxImage functions)
| Asset | Path | Purpose |
|---|---|---|
| Door texture | `assets/ualbany.png` | UAlbany logo shown on exit doors |
| FT newspaper | `assets/times.png` | Weapon sprite drawn in first-person view |
| AP sprite sheet | `assets/sprite_sheet.png` | 16-frame rotation strip for campus AP objects |

---

## mechanics.js

### placeDecorations
Controls how many decorations spawn per level:
```js
const torches = levelId === 'floordoom_level' ? 0 : Math.min(14, Math.ceil(candidates.length * 0.10));
const posters  = Math.min(5, Math.ceil(candidates.length * 0.04));
```
Torches are suppressed on the campus map. Torch world offset from wall: `0.18` (near wall) vs `0.82` (far wall).

Ceiling lights are baked into `generateCeilTex()` as a tiling panel — one light per tile, evenly spaced. Color is zone-specific (gold=GOVERN, blue=IDENTIFY, etc.). Adjust `addLightPanel(r,g,b,w,h)` args per zone to change colour or panel size.

---

## Cell Type Reference (all map files)
| Value | Object | Interactive? |
|---|---|---|
| 0 | Floor | — |
| 1 | Wall | Solid (blocks movement + raycasting) |
| 2 | Exit door | Triggers level transition when zone complete |
| 3 | Policy card | Collected on contact, adds to codex |
| 4 | Scenario trigger | Opens MCQ panel on contact |
| 5 | FT newspaper pickup | Adds 1 paper on contact |
| 6 | Torch | Visual only (world position from `GAME_STATE.decorations`) |
| 7 | Hint poster | Shows zone hint toast on contact (5s cooldown) |
| 8 | AP unit (campus) | Opens campus challenge panel on contact; animated sprite sheet |
| 9 | PC workstation (campus) | Opens terminal challenge panel on contact; restored to map if player quits without completing |
| 10 | Terminal hint token (campus) | Consumed on contact; shows command hint toast; neon-green `>_` sprite |
| 11 | Stairwell access panel (campus) | Opens `showPanelOverlay` on contact (400ms cooldown after dismiss); not consumed |

---

## data/campus_challenges.js
`CAMPUS_CHALLENGES` array. Each entry: `challenge_id` `type` (`mcq`/`code_spot`/`log_analysis`) `topic` `tactic` `situation` `lines[]` or `options[]`/`snippet` `correct_line` or `correct` `explanation`.
Linked to cell 8 (AP) pickups. Shuffled into `GAME_STATE.level.campus_challenge_pool` at level load.

## data/terminal_challenges.js
`TERMINAL_CHALLENGES` array. Each entry: `challenge_id` `task` `situation` `accepted_cmds[]` `hint` `fake_output` `explanation`.
Linked to cell 9 (PC workstation) pickups. Points: **+200** correct, **−8% grade** first wrong attempt.
Accepted commands matched case-insensitive, whitespace-normalized. Unknown commands (not handled by simulator) trigger the penalty; known-but-wrong commands show realistic simulator output with no penalty.

## data/maps.js + data/maps_floordoom.js
Contains `MAPS` object — one 2D array per level ID. Edit these to change room layout.
Level IDs: `lobby` `level1_govern` `level2_identify` `level3_protect` `level4_detect` `level5_respond` `level6_recover` `boss_ai_rmf` `floordoom_level`

## data/policy_cards.js
`POLICY_CARDS` array. Each card: `card_id` `function` `level_num` `rarity` + NIST reference fields.
`level_num` must match the level where the card should appear (1–7, or 8 for campus CAMPUS-zone cards).

## data/scenarios.js
`SCENARIOS` array. Each scenario: `scenario_id` `level_num` `question` `options[]` `correct` `explanation`.
All four options in each scenario are within ±10 chars of each other in length to prevent longest-answer bias.

## data/subnet_challenges.js
`SUBNET_CHALLENGES` array (campus-only, `level_num: 8`). Each entry: `challenge_id` `panel` (`left`/`right`) `slot` (0–2) `rack_label` `rogue_ip` (169.254.x.x APIPA) `situation` `subnet` `valid_range:[lo,hi]` `broadcast` `explanation`.
Linked to RACK NPC spawns by `challenge_id`. One challenge per rack; 3 per panel side.

## data/npc_data.js
- `NPC_TYPES` — display config per NPC type (label, icon, color, threat label). Includes `RACK` (campus rogue server rack).
- `NPC_SPAWNS` — array of spawn definitions: `{level_num, type, x, y, patrol_points[], ghost, challenges[]}`. RACK entries also have `challenge_id`, `panel`, `slot`.
- `ARIA_CHALLENGES` — 7-phase sequential MCQ for the final boss
