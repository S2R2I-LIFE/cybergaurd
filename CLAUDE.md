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
| `state.js` | Global constants and `GAME_STATE` object. Source of truth for roles, zone colors, level metadata, FT throw constants. |
| `data/maps.js` | `MAPS` object — one 2D array per level. Cell types: `0`=floor `1`=wall `2`=exit door `3`=policy card `4`=scenario `5`=FT pickup. |
| `data/policy_cards.js` | `POLICY_CARDS` array — 60+ cards, each with `card_id`, `function`, `level_num`, `rarity`, NIST refs. |
| `data/scenarios.js` | `SCENARIOS` array — MCQ puzzles keyed by `level_num`. |
| `data/npc_data.js` | NPC definitions (sprites, dialogue, behavior). |
| `engine.js` | Raycasting renderer (800×500 canvas, 66° FOV, `ImageData` pixel writes). Procedural wall/floor/ceiling textures per zone. NPC sprite rendering. Game loop (`startEngine`). |
| `mechanics.js` | `loadLevel`, player movement, collision, card/scenario pickup logic, FT newspaper throw mechanic, NPC AI. |
| `ui_components.js` | All DOM overlays: HUD, briefing screen, scenario panel, codex, pause, certificate, NPC dialogue. |

## Key Constants (state.js)

- **Level order:** `lobby → level1_govern → level2_identify → level3_protect → level4_detect → level5_respond → level6_recover → boss_ai_rmf`
- **Zone colors:** LOBBY=`#888`, GOVERN=`#FFD700`, IDENTIFY=`#1E90FF`, PROTECT=`#00AA44`, DETECT=`#FF8C00`, RESPOND=`#FF3333`, RECOVER=`#00CED1`, AI_RMF=`#9B30FF`
- **Player roles:** `analyst` (specialty: DETECT/RESPOND), `auditor` (GOVERN/AI_RMF), `risk_manager` (IDENTIFY/PROTECT/RECOVER)
- **FT mechanic:** `FT_STUN_DURATION=8s`, `FT_THROW_RANGE=7`, `FT_HALF_CONE=0.4rad`, `FT_PER_LEVEL=3`

## Adding Content

- **New policy card:** append to `POLICY_CARDS` in `data/policy_cards.js` with matching `level_num` (1–7).
- **New scenario:** append to `SCENARIOS` in `data/scenarios.js` with matching `level_num`.
- **New level map:** add entry to `MAPS` in `data/maps.js` and corresponding entry in `LEVEL_METADATA` and `LEVEL_ORDER` in `state.js`.
- **New wall texture:** add zone branch to `generateZoneTexture()` in `engine.js`.

## FloorDoom Tool

`FloorDoom/` is a standalone Python utility that converts blueprint PNG images into JS tilemap arrays.

```bash
cd FloorDoom
python3 main.py <image_path>
# outputs: output/floor3.js, output/floor3.npy, output/floor3_preview.png
```

Requires: numpy, PIL. Output `floor3.js` can be copy-pasted into `data/maps.js`.

## Deployment

Static files only. Copy `cyberguard/` to any host. GitHub Pages, Netlify, or direct `index.html` all work.
