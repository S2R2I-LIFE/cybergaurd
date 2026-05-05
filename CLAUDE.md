# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CyberGuard: The NIST Dungeon** — a browser-based 2.5D educational game (DOOM-style raycasting, vanilla JS) teaching NIST CSF 2.0, AI RMF 1.0, SP 800-53, and SP 800-37 to university students (Professor Snyder's courses at UAlbany).

**Status:** Implemented. Playable game lives in `cyberguard/`. Open `cyberguard/index.html` directly in a browser — no build step, no server required.

The original spec lives in `cybergaurd.json` (note typo in filename) and `spec.md`. The `backup/` directory contains historical snapshots; work from `cyberguard/` only.

## Architecture

All game code is vanilla JS loaded via `<script>` tags in `index.html` in this order (dependency order matters):

| File | Role |
|---|---|
| `state.js` | Global constants and `GAME_STATE` object. Source of truth for roles, zone colors, level metadata, FT throw constants, `TERM_HINT_TOKENS`. |
| `data/maps.js` | `MAPS` object — one 2D array per NIST levels. Cell types: `0`=floor `1`=wall `2`=exit door `3`=policy card `4`=scenario `5`=FT pickup. |
| `data/maps_floordoom.js` | Campus map (`floordoom_level`). Same cell types plus `8`=AP unit `9`=PC workstation `10`=terminal hint token `11`=stairwell access panel. |
| `data/policy_cards.js` | `POLICY_CARDS` array — 80+ cards, each with `card_id`, `function`, `level_num`, `rarity`, NIST refs. Campus cards use `level_num:8`, `function:'CAMPUS'`. |
| `data/scenarios.js` | `SCENARIOS` array — MCQ puzzles keyed by `level_num`. All options normalized to within ±10 chars to prevent longest-answer bias. |
| `data/campus_challenges.js` | `CAMPUS_CHALLENGES` array — MCQ/code_spot/log_analysis challenges for cell 8 AP pickups (campus only). Must load before `mechanics.js`. |
| `data/terminal_challenges.js` | `TERMINAL_CHALLENGES` array — Linux forensic terminal challenges for cell 9 PC workstations (campus only). Must load before `mechanics.js`. |
| `data/subnet_challenges.js` | `SUBNET_CHALLENGES` array — Arista EOS subnetting challenges for campus RACK NPCs. 6 entries, 3 per stairwell panel side. Must load before `mechanics.js`. |
| `data/npc_data.js` | NPC definitions (sprites, dialogue, behavior). `NPC_TYPES`, `NPC_SPAWNS`, `ARIA_CHALLENGES` (boss). RACK type added for campus. |
| `engine.js` | Raycasting renderer (800×500 canvas, 66° FOV, `ImageData` pixel writes). Procedural wall/floor/ceiling textures per zone. NPC sprite rendering. Game loop (`startEngine`). |
| `mechanics.js` | `loadLevel`, player movement, collision, card/scenario pickup logic, FT newspaper throw mechanic, NPC AI, `placeDecorations`. |
| `ui_components.js` | All DOM overlays: HUD, briefing screen, scenario panel, codex, pause, certificate, NPC dialogue, campus panel, terminal panel. Terminal simulator (`_simCmd`). |

## Key Constants (state.js)

- **Level order:** `lobby → level1_govern → level2_identify → level3_protect → level4_detect → level5_respond → level6_recover → boss_ai_rmf`
- **Campus level:** `floordoom_level` (accessible from lobby north exit)
- **Zone colors:** LOBBY=`#888`, GOVERN=`#FFD700`, IDENTIFY=`#1E90FF`, PROTECT=`#00AA44`, DETECT=`#FF8C00`, RESPOND=`#FF3333`, RECOVER=`#00CED1`, AI_RMF=`#9B30FF`, CAMPUS=`#CC3333`
- **Player roles:** `analyst` (specialty: DETECT/RESPOND), `auditor` (GOVERN/AI_RMF), `risk_manager` (IDENTIFY/PROTECT/RECOVER)
- **FT mechanic:** FT = Financial Times newspaper — throwable weapon that stuns NPCs. `FT_STUN_DURATION=8s`, `FT_THROW_RANGE=7`, `FT_HALF_CONE=0.4rad`, `FT_PER_LEVEL=3` papers per level
- **Turn speed:** `turn_speed=2.0` rad/sec (keyboard A/D)

## Boss Level (boss_ai_rmf)

ARIA is the final boss — a 7-phase sequential MCQ challenge defined in `ARIA_CHALLENGES` in `data/npc_data.js`. ARIA spawns when the player enters the level (`GAME_STATE.boss.spawned`). Exit door (cell 2) only unlocks after all 7 phases are answered correctly (`GAME_STATE.boss.defeated`). Phase tracked in `GAME_STATE.boss.phase` (0–6).

## Exit Door Unlock

Cell 2 (exit door) only becomes passable when the level's completion condition is met:
- **NIST levels (1–6):** all policy cards collected AND all scenarios completed for that level
- **Boss level:** `GAME_STATE.boss.defeated === true`
- **Campus level:** either stairwell panel fully unlocked (all 3 `panel_ips[side]` slots valid for `left` OR `right`)

## Campus Level (floordoom_level)

MITRE ATT&CK / attack-techniques map. Three interactive object types:

| Cell | Object | Mechanic |
|---|---|---|
| 8 | AP unit | Opens campus challenge panel (MCQ / code_spot / log_analysis) |
| 9 | PC workstation | Opens macOS-style terminal; player must type correct Linux forensic command |
| 10 | Terminal hint token (`>_`) | Consumed on contact; toast shows a command + tip from `TERM_HINT_TOKENS` |
| 11 | Stairwell access panel | Opens panel overlay showing per-slot IP status; 400ms re-trigger cooldown |

**Terminal challenge rules:**
- Accepted commands matched case-insensitive, whitespace-normalized
- Correct → `+200 pts`, cell cleared
- Known command (simulator) → realistic output shown, no penalty
- Unknown command → `command not found`, `−8% grade` once + hint shown
- Close (red X) without completing → cell 9 restored to map so player can retry
- Arrow-up/down cycles command history within the session

**Terminal simulator** (`_simCmd` in `ui_components.js`) handles: `ls`, `cd`, `pwd`, `cat`, `grep`, `find`, `ps`, `netstat`, `ss`, `crontab`, `df`, `free`, `ip`, `ifconfig`, `sudo`, `man`, `lsof`, `top`, `ping`, `curl`, `wget`, `python3`, `whoami`, `id`, `hostname`, `uname`, `date`, `echo`, `history`, `which`, `clear`, `exit`, pipe (`|`) with grep filter, and silent-success file ops.

Torches do **not** spawn on the campus map (`floordoom_level` is excluded in `placeDecorations`).

## Common Gotchas

- **Codex missing cards:** If policy cards with a new `function` value don't appear in the codex, add that zone to `ZONE_ORDER` (and `ZONE_LABELS`) in `ui_components.js`. The codex loop silently skips zones not in `ZONE_ORDER`.
- **Script load order:** `index.html` loads files in dependency order. If a new data file is referenced by `mechanics.js` or `ui_components.js`, add its `<script>` tag before those files in `index.html`.
- **Pickup not disappearing:** Pickup handlers must set `map[row][col] = 0` to clear the cell. Without this the sprite stays and the interaction fires repeatedly.
- **Terminal cell restoring:** Cell 9 is cleared to `0` when the player steps on it and restored to `9` if they close without completing (`hideTerminalChallenge` checks `terminal_completed`). Same pattern should be applied to any future closeable challenge cells.
- **Scenario answer length:** All four options in a scenario must be within ±10 chars of each other. Run the length check script (`node -e ...` in VARIABLES.md) after adding new scenarios.

## Adding Content

- **New policy card:** append to `POLICY_CARDS` in `data/policy_cards.js` with matching `level_num` (1–7, or 8 for campus).
- **New scenario:** append to `SCENARIOS` in `data/scenarios.js` with matching `level_num`. Keep all four options within ±10 chars of each other in length.
- **New campus challenge:** append to `CAMPUS_CHALLENGES` in `data/campus_challenges.js`.
- **New terminal challenge:** append to `TERMINAL_CHALLENGES` in `data/terminal_challenges.js`.
- **New terminal hint token:** add entry to `TERM_HINT_TOKENS` in `state.js`, place cell `10` on `data/maps_floordoom.js`.
- **New level map:** add entry to `MAPS` in `data/maps.js` and corresponding entry in `LEVEL_METADATA` and `LEVEL_ORDER` in `state.js`.
- **New wall texture:** add zone branch to `generateZoneTexture()` in `engine.js`.

## FloorDoom Tool

`FloorDoom/` is a standalone Python utility that converts blueprint PNG images into JS tilemap arrays.

```bash
cd FloorDoom
python3 main.py <image_path>
# outputs: output/floor3.js, output/floor3.npy, output/floor3_preview.png
```

Requires: numpy, PIL. Output `floor3.js` can be copy-pasted into `data/maps_floordoom.js`. PNG inputs and `output/` are gitignored.

## Deployment

Static files only. Copy `cyberguard/` to any host. GitHub Pages, Netlify, or direct `index.html` all work.
