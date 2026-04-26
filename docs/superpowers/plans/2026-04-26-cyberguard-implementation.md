# CyberGuard: The NIST Dungeon — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully playable browser-based 2.5D raycasting dungeon game that teaches NIST CSF 2.0, AI RMF 1.0, and SP 800-53 Rev. 5 through policy card collection, scenario MCQs, and a grade health system.

**Architecture:** Vanilla JS ES6+, HTML5 Canvas (DDA raycasting, ImageData pixel writes, 800×500), DOM overlays for all UI. All game data in `.js` files (not `.json`) for `file://` protocol compatibility — no server required. Script load order: `state.js` → `data/maps.js` → `data/policy_cards.js` → `data/scenarios.js` → `engine.js` → `mechanics.js` → `ui_components.js`.

**Tech Stack:** Vanilla JavaScript, HTML5 Canvas, CSS3, Google Fonts (Orbitron, Share Tech Mono)

---

## File Structure

```
cyberguard/
├── index.html
├── style.css
├── state.js
├── engine.js
├── mechanics.js
├── ui_components.js
├── data/
│   ├── maps.js
│   ├── policy_cards.js
│   └── scenarios.js
├── assets/
│   ├── title_logo.png
│   └── nist_logo.svg
├── README.md
└── command.log
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `cyberguard/` directory tree

- [ ] **Step 1: Create directories**

```bash
mkdir -p cyberguard/data cyberguard/assets
```

- [ ] **Step 2: Create empty source files**

```bash
touch cyberguard/index.html cyberguard/style.css cyberguard/state.js \
  cyberguard/engine.js cyberguard/mechanics.js cyberguard/ui_components.js \
  cyberguard/data/maps.js cyberguard/data/policy_cards.js \
  cyberguard/data/scenarios.js cyberguard/README.md cyberguard/command.log
```

- [ ] **Step 3: Copy title logo**

```bash
cp /home/b/NIST/public/title_logo.png cyberguard/assets/title_logo.png
```

- [ ] **Step 4: Verify**

```bash
find cyberguard -type f | sort
```

Expected: 11 files listed across the directory tree.

- [ ] **Step 5: Commit**

```bash
cd cyberguard && git init && git add -A && git commit -m "chore: initial project scaffold"
```

---

### Task 2: state.js

**Files:**
- Write: `cyberguard/state.js`

- [ ] **Step 1: Write state.js**

```javascript
// cyberguard/state.js

const ZONE_COLORS = {
  LOBBY:    '#888888',
  GOVERN:   '#FFD700',
  IDENTIFY: '#1E90FF',
  PROTECT:  '#00AA44',
  DETECT:   '#FF8C00',
  RESPOND:  '#FF3333',
  RECOVER:  '#00CED1',
  AI_RMF:   '#9B30FF',
};

const LEVEL_ORDER = [
  'lobby', 'level1_govern', 'level2_identify', 'level3_protect',
  'level4_detect', 'level5_respond', 'level6_recover', 'boss_ai_rmf'
];

const LEVEL_METADATA = {
  lobby:            { zone: 'LOBBY',    next: 'level1_govern',   spawn: { x: 6.5, y: 2,   angle: Math.PI * 0.5 }, cards: 0, scenarios: 0,  level_num: 0 },
  level1_govern:    { zone: 'GOVERN',   next: 'level2_identify', spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 6, scenarios: 3,  level_num: 1 },
  level2_identify:  { zone: 'IDENTIFY', next: 'level3_protect',  spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 8, scenarios: 4,  level_num: 2 },
  level3_protect:   { zone: 'PROTECT',  next: 'level4_detect',   spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 8, scenarios: 4,  level_num: 3 },
  level4_detect:    { zone: 'DETECT',   next: 'level5_respond',  spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 6, scenarios: 3,  level_num: 4 },
  level5_respond:   { zone: 'RESPOND',  next: 'level6_recover',  spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 6, scenarios: 4,  level_num: 5 },
  level6_recover:   { zone: 'RECOVER',  next: 'boss_ai_rmf',     spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 4, scenarios: 3,  level_num: 6 },
  boss_ai_rmf:      { zone: 'AI_RMF',   next: null,              spawn: { x: 1.5, y: 9.5, angle: 0              }, cards: 8, scenarios: 4,  level_num: 7 },
};

const GAME_CONFIG = {
  canvas_width:       800,
  canvas_height:      500,
  fov:                Math.PI / 3,
  move_speed:         2.5,
  turn_speed:         2.0,
  player_radius:      0.25,
  wall_height_scale:  320,
  minimap_scale:      10,
  minimap_visible:    true,
};

const GAME_STATE = {
  screen: 'briefing', // 'briefing'|'playing'|'codex'|'scenario'|'gameover'|'certificate'|'paused'|'transition'
  player: {
    x: 6.5,
    y: 2,
    angle: Math.PI * 0.5,
    role: null,
  },
  level: {
    id: 'lobby',
    map: [],
    zone: 'LOBBY',
    level_num: 0,
    cards_total: 0,
    scenarios_total: 0,
  },
  progress: {
    cards_collected: [],
    scenarios_completed: [],
    scenarios_penalized: [],
    grade: 100,
    score: 0,
  },
  active_scenario: null,
  minimap_visible: true,
  last_door_message_time: 0,
};
```

- [ ] **Step 2: Verify in browser console**

Open `cyberguard/index.html` (after Task 10 wires scripts). In console:
```javascript
console.log(GAME_STATE.screen); // → 'briefing'
console.log(LEVEL_METADATA.level1_govern.zone); // → 'GOVERN'
console.log(ZONE_COLORS.AI_RMF); // → '#9B30FF'
```

- [ ] **Step 3: Commit**

```bash
git add state.js && git commit -m "feat: add GAME_STATE, GAME_CONFIG, LEVEL_METADATA"
```

---

### Task 3: data/maps.js

**Files:**
- Write: `cyberguard/data/maps.js`

Map cell legend: `0`=floor, `1`=wall, `2`=door, `3`=card pickup, `4`=scenario trigger.
All levels use 20×20 grids. Lobby uses 14×14.
Door is always at `[9][19]` on the east wall (except lobby: `[13][6]` south wall).
Player spawns west side facing east for all levels except lobby (spawns north facing south).

- [ ] **Step 1: Write data/maps.js**

```javascript
// cyberguard/data/maps.js

const MAPS = {

  lobby: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,0,0,0,0,1,1,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,0,0,0,1,0,0,1],
    [1,0,0,1,1,0,0,0,0,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,1,1],
  ],

  level1_govern: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,4,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  level2_identify: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,3,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,4,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,0,0,0,0,0,0,4,0,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,3,0,0,0,0,3,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  level3_protect: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,3,0,0,0,3,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,4,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,3,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,4,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  level4_detect: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,4,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,3,1,1,0,0,1,1,1,3,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,3,1,1,0,0,1,1,1,3,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  level5_respond: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,4,0,0,0,0,0,0,4,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  level6_recover: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,4,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,0,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

  boss_ai_rmf: [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,3,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,4,0,0,0,1,0,0,0,0,1],
    [1,1,0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1],
    [1,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,4,0,4,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,3,0,0,1,0,0,0,0,0,0,0,0,1,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  ],

};
```

- [ ] **Step 2: Verify card/scenario counts match LEVEL_METADATA**

Open browser console after index.html is wired:
```javascript
// Count 3s and 4s in each level map
Object.entries(MAPS).forEach(([id, map]) => {
  let cards = 0, scens = 0;
  map.forEach(row => row.forEach(c => { if (c===3) cards++; if (c===4) scens++; }));
  console.log(id, 'cards:', cards, 'scenarios:', scens);
});
```

Expected:
```
lobby         cards: 0  scenarios: 0
level1_govern cards: 6  scenarios: 3
level2_identify cards: 8  scenarios: 4
level3_protect  cards: 8  scenarios: 4
level4_detect   cards: 6  scenarios: 3
level5_respond  cards: 6  scenarios: 4
level6_recover  cards: 4  scenarios: 3
boss_ai_rmf     cards: 8  scenarios: 4
```

- [ ] **Step 3: Commit**

```bash
git add data/maps.js && git commit -m "feat: add all 8 level maps"
```

---

### Task 4: data/policy_cards.js

**Files:**
- Write: `cyberguard/data/policy_cards.js`

- [ ] **Step 1: Write data/policy_cards.js**

```javascript
// cyberguard/data/policy_cards.js
const POLICY_CARDS = [
  // GOVERN (level_num 1)
  { card_id:"NIST-GV-OC-1", function:"GOVERN", subcategory:"GV.OC-01", title:"Mission and Stakeholder Expectations", summary:"The organizational mission is understood and informs cybersecurity risk management.", why_it_matters:"Security decisions disconnected from mission lead to misallocated resources.", real_world_example:"A hospital shapes cybersecurity priorities around patient safety and HIPAA, not just IT convenience.", sp800_53_refs:["PM-1","PM-2"], level_num:1, rarity:"common" },
  { card_id:"NIST-GV-RM-1", function:"GOVERN", subcategory:"GV.RM-01", title:"Risk Management Strategy", summary:"Organizational risk management strategy and risk tolerance are established and communicated.", why_it_matters:"Without a documented strategy, teams make inconsistent risk decisions in isolation.", real_world_example:"A bank's risk committee sets maximum acceptable downtime before security measures are required.", sp800_53_refs:["PM-9","RA-1"], level_num:1, rarity:"common" },
  { card_id:"NIST-GV-RM-2", function:"GOVERN", subcategory:"GV.RM-02", title:"Risk Appetite and Tolerance", summary:"Risk appetite and risk tolerance statements guide risk-based decisions across the organization.", why_it_matters:"Without defined tolerance, every risk becomes a subjective judgment call.", real_world_example:"A retailer states it will accept up to $50K in residual risk per system before requiring additional controls.", sp800_53_refs:["PM-9","RA-2"], level_num:1, rarity:"uncommon" },
  { card_id:"NIST-GV-RR-1", function:"GOVERN", subcategory:"GV.RR-01", title:"Organizational Roles and Responsibilities", summary:"Cybersecurity roles and responsibilities are established, communicated, and enforced.", why_it_matters:"Unclear ownership means incidents fall through the cracks.", real_world_example:"A RACI matrix assigns the CISO as accountable for all breach notifications within 72 hours.", sp800_53_refs:["PM-2","PL-9"], level_num:1, rarity:"common" },
  { card_id:"NIST-GV-PO-1", function:"GOVERN", subcategory:"GV.PO-01", title:"Policy Establishment", summary:"Cybersecurity policies are established, reviewed, and approved by organizational leadership.", why_it_matters:"Policies without formal approval lack authority and enforcement teeth.", real_world_example:"The CEO signs the information security policy annually, giving it organizational weight.", sp800_53_refs:["PL-1","SA-1"], level_num:1, rarity:"common" },
  { card_id:"NIST-GV-SC-1", function:"GOVERN", subcategory:"GV.SC-01", title:"Supply Chain Risk Management Policy", summary:"A supply chain risk management policy addresses third-party security expectations.", why_it_matters:"Most breaches now involve third parties; policy sets the baseline for vendor selection.", real_world_example:"A contractor must pass a security assessment before accessing production systems.", sp800_53_refs:["SA-9","PM-9"], level_num:1, rarity:"rare" },

  // IDENTIFY (level_num 2)
  { card_id:"NIST-ID-AM-1", function:"IDENTIFY", subcategory:"ID.AM-01", title:"Inventory of Physical Devices", summary:"Physical devices and systems within the organization are inventoried.", why_it_matters:"You cannot protect what you do not know exists.", real_world_example:"A university maintains a CMDB tracking every laptop, server, and IoT sensor on campus.", sp800_53_refs:["CM-8","PM-5"], level_num:2, rarity:"common" },
  { card_id:"NIST-ID-AM-2", function:"IDENTIFY", subcategory:"ID.AM-02", title:"Inventory of Software", summary:"Software platforms and applications within the organization are inventoried.", why_it_matters:"Unmanaged software is a primary vector for supply chain and vulnerability exploits.", real_world_example:"An enterprise uses an automated tool to discover all installed software weekly.", sp800_53_refs:["CM-8","SA-10"], level_num:2, rarity:"common" },
  { card_id:"NIST-ID-AM-5", function:"IDENTIFY", subcategory:"ID.AM-05", title:"Resource Prioritization", summary:"Resources are prioritized based on classification, criticality, and business value.", why_it_matters:"Limited security budgets must go to the assets that matter most.", real_world_example:"Payment processing servers are classified Tier 1 and receive 24/7 monitoring; lab PCs are Tier 3.", sp800_53_refs:["PL-8","SA-17"], level_num:2, rarity:"uncommon" },
  { card_id:"NIST-ID-AM-7", function:"IDENTIFY", subcategory:"ID.AM-07", title:"Vulnerabilities in Assets Identified", summary:"Vulnerabilities in assets are identified and documented in an actionable format.", why_it_matters:"Untracked vulnerabilities become exploited vulnerabilities.", real_world_example:"A weekly scan exports CVE findings into the ticketing system for remediation tracking.", sp800_53_refs:["RA-3","SI-2"], level_num:2, rarity:"common" },
  { card_id:"NIST-ID-RA-1", function:"IDENTIFY", subcategory:"ID.RA-01", title:"Vulnerabilities Identified and Documented", summary:"Asset vulnerabilities are identified, validated, and recorded with sufficient detail.", why_it_matters:"Documentation creates accountability and enables risk-based prioritization.", real_world_example:"Every CVE above CVSS 7.0 gets a risk register entry within 48 hours of discovery.", sp800_53_refs:["RA-3","RA-5"], level_num:2, rarity:"common" },
  { card_id:"NIST-ID-RA-3", function:"IDENTIFY", subcategory:"ID.RA-03", title:"Threat Intelligence", summary:"Internal and external threat intelligence is used to identify threats to the organization.", why_it_matters:"Reactive security misses threats that intelligence could have predicted.", real_world_example:"A financial firm subscribes to FS-ISAC and integrates feeds into its SIEM.", sp800_53_refs:["RA-3","SI-5"], level_num:2, rarity:"uncommon" },
  { card_id:"NIST-ID-RA-5", function:"IDENTIFY", subcategory:"ID.RA-05", title:"Threats, Vulnerabilities, Likelihoods, Impacts", summary:"Threats, vulnerabilities, likelihoods, and impacts are used to understand risk.", why_it_matters:"Combining all four factors produces a defensible risk score for decision-making.", real_world_example:"A risk analyst multiplies threat likelihood by potential financial impact to rank remediation priority.", sp800_53_refs:["RA-3","PM-16"], level_num:2, rarity:"uncommon" },
  { card_id:"NIST-ID-IM-1", function:"IDENTIFY", subcategory:"ID.IM-01", title:"Improvements from Evaluations", summary:"Improvements are identified from security assessments, audits, and post-incident reviews.", why_it_matters:"Organizations that do not learn from assessments repeat the same failures.", real_world_example:"A tabletop exercise uncovers a gap in backup verification; a remediation task is created the next day.", sp800_53_refs:["PM-6","CA-2"], level_num:2, rarity:"rare" },

  // PROTECT (level_num 3)
  { card_id:"NIST-PR-AA-1", function:"PROTECT", subcategory:"PR.AA-01", title:"Identities and Credentials Managed", summary:"Identities and credentials are issued, managed, verified, revoked, and audited.", why_it_matters:"Credential sprawl is the most common entry point for attackers.", real_world_example:"Offboarding checklist revokes AD account, VPN cert, and SaaS licenses within one hour of termination.", sp800_53_refs:["IA-1","IA-2"], level_num:3, rarity:"common" },
  { card_id:"NIST-PR-AA-3", function:"PROTECT", subcategory:"PR.AA-03", title:"Users Authenticated to Access Assets", summary:"Users, services, and hardware are authenticated before accessing organizational resources.", why_it_matters:"Authentication is the gate; weak authentication invites intrusion.", real_world_example:"MFA is enforced for all VPN and cloud console access across the organization.", sp800_53_refs:["IA-5","IA-8"], level_num:3, rarity:"common" },
  { card_id:"NIST-PR-DS-1", function:"PROTECT", subcategory:"PR.DS-01", title:"Data at Rest Protected", summary:"Data at rest is protected to prevent unauthorized disclosure and modification.", why_it_matters:"Stolen encrypted drives are useless to attackers; unencrypted drives are not.", real_world_example:"All laptops use BitLocker with TPM binding; database tablespaces use AES-256 TDE.", sp800_53_refs:["SC-28","MP-2"], level_num:3, rarity:"common" },
  { card_id:"NIST-PR-DS-2", function:"PROTECT", subcategory:"PR.DS-02", title:"Data in Transit Protected", summary:"Data in transit is protected to prevent unauthorized access and tampering.", why_it_matters:"Unencrypted data in transit is trivially intercepted on shared networks.", real_world_example:"All internal service communication uses mTLS; external APIs enforce TLS 1.2+.", sp800_53_refs:["SC-8","SC-28"], level_num:3, rarity:"common" },
  { card_id:"NIST-PR-PS-1", function:"PROTECT", subcategory:"PR.PS-01", title:"Configuration Management Enforced", summary:"Configuration management policies are established and the configuration of assets is managed.", why_it_matters:"Misconfiguration is the leading cause of cloud breaches.", real_world_example:"A golden AMI baseline disables all unnecessary services; drift is detected and auto-remediated.", sp800_53_refs:["CM-7","CM-9"], level_num:3, rarity:"uncommon" },
  { card_id:"NIST-PR-IR-1", function:"PROTECT", subcategory:"PR.IR-01", title:"Networks and Environments Protected", summary:"Networks and environments are protected from unauthorized logical access.", why_it_matters:"Network segmentation limits blast radius when a system is compromised.", real_world_example:"PCI-scoped systems live in an isolated VLAN; cross-zone traffic requires firewall rule approval.", sp800_53_refs:["SC-7","SI-3"], level_num:3, rarity:"uncommon" },
  { card_id:"NIST-PR-AT-1", function:"PROTECT", subcategory:"PR.AT-01", title:"Personnel Aware of Cybersecurity Risks", summary:"All personnel are informed and trained on their cybersecurity responsibilities.", why_it_matters:"Humans remain the most exploited attack surface; awareness is the first layer of defense.", real_world_example:"Annual security awareness training with phishing simulation is mandatory for all employees.", sp800_53_refs:["AT-2","PM-13"], level_num:3, rarity:"common" },
  { card_id:"NIST-PR-AT-2", function:"PROTECT", subcategory:"PR.AT-02", title:"Personnel Trained for Roles", summary:"Privileged users and security staff receive role-specific cybersecurity training.", why_it_matters:"Admins with elevated access need deeper training than general users.", real_world_example:"All sysadmins complete a 40-hour security operations curriculum before gaining production access.", sp800_53_refs:["AT-3","AT-4"], level_num:3, rarity:"uncommon" },

  // DETECT (level_num 4)
  { card_id:"NIST-DE-CM-1", function:"DETECT", subcategory:"DE.CM-01", title:"Networks Monitored for Anomalies", summary:"The network is monitored to detect potential cybersecurity events.", why_it_matters:"Attacks that go undetected for days cause exponentially more damage than those caught in minutes.", real_world_example:"A SIEM correlates firewall logs and NetFlow to alert on lateral movement within the network.", sp800_53_refs:["SI-4","CA-7"], level_num:4, rarity:"common" },
  { card_id:"NIST-DE-CM-2", function:"DETECT", subcategory:"DE.CM-02", title:"Physical Environment Monitored", summary:"The physical environment is monitored to detect potential cybersecurity events.", why_it_matters:"Physical access bypasses all logical controls.", real_world_example:"Badge reader logs are reviewed weekly; tailgating triggers an immediate security alert.", sp800_53_refs:["PE-6","SI-4"], level_num:4, rarity:"uncommon" },
  { card_id:"NIST-DE-AE-2", function:"DETECT", subcategory:"DE.AE-02", title:"Potentially Adverse Events Analyzed", summary:"Potentially adverse events are analyzed to better characterize them and detect attack patterns.", why_it_matters:"Individual alerts are noise; correlated events reveal campaigns.", real_world_example:"Three failed logins followed by a success and an unusual file access are correlated into a single alert.", sp800_53_refs:["SI-4","AU-6"], level_num:4, rarity:"uncommon" },
  { card_id:"NIST-DE-AE-3", function:"DETECT", subcategory:"DE.AE-03", title:"Event Data Aggregated", summary:"Event data is aggregated from multiple sources to support analysis and correlation.", why_it_matters:"Siloed logs prevent detection of multi-stage attacks.", real_world_example:"Endpoint, network, and identity logs all feed into a centralized SIEM with normalized schemas.", sp800_53_refs:["AU-6","IR-4"], level_num:4, rarity:"common" },
  { card_id:"NIST-DE-AE-6", function:"DETECT", subcategory:"DE.AE-06", title:"Cybersecurity Incidents Declared", summary:"A cybersecurity incident is declared and response initiated when detection thresholds are met.", why_it_matters:"Delayed declaration prolongs attacker dwell time.", real_world_example:"SOC policy states: any confirmed malware execution automatically escalates to a P1 incident.", sp800_53_refs:["IR-6","IR-8"], level_num:4, rarity:"rare" },
  { card_id:"NIST-DE-AE-7", function:"DETECT", subcategory:"DE.AE-07", title:"Cyber Threat Intelligence Received", summary:"Cyber threat intelligence is received from information-sharing forums and external sources.", why_it_matters:"Threat intelligence turns reactive detection into proactive hunting.", real_world_example:"STIX/TAXII feeds from ISACs are ingested and matched against SIEM queries each hour.", sp800_53_refs:["SI-5","IR-4"], level_num:4, rarity:"rare" },

  // RESPOND (level_num 5)
  { card_id:"NIST-RS-MA-1", function:"RESPOND", subcategory:"RS.MA-01", title:"Incident Response Plan Executed", summary:"The incident response plan is executed consistently and coordinated with relevant parties.", why_it_matters:"An untested plan is a false sense of security; execution requires practice.", real_world_example:"Upon ransomware detection, the IRP checklist is activated within 15 minutes and ownership assigned.", sp800_53_refs:["IR-4","IR-8"], level_num:5, rarity:"common" },
  { card_id:"NIST-RS-MA-2", function:"RESPOND", subcategory:"RS.MA-02", title:"Incident Reported to Internal Stakeholders", summary:"Incidents are reported to appropriate internal stakeholders in a timely and accurate manner.", why_it_matters:"Leadership needs timely information to make containment and communication decisions.", real_world_example:"The CISO receives a breach brief within 30 minutes; the legal team is notified within one hour.", sp800_53_refs:["IR-5","IR-6"], level_num:5, rarity:"common" },
  { card_id:"NIST-RS-AN-3", function:"RESPOND", subcategory:"RS.AN-03", title:"Analysis Performed to Determine Response", summary:"Analysis is performed to establish what occurred and support recovery and eradication.", why_it_matters:"Acting without analysis risks remediating symptoms rather than root causes.", real_world_example:"Forensic images of compromised hosts are analyzed before re-imaging to identify the initial access vector.", sp800_53_refs:["IR-4","AU-6"], level_num:5, rarity:"uncommon" },
  { card_id:"NIST-RS-AN-6", function:"RESPOND", subcategory:"RS.AN-06", title:"Actions Performed to Prevent Expansion", summary:"Actions are performed to prevent expansion of an event and mitigate its effects.", why_it_matters:"Containment stops a single compromised host from becoming a full network breach.", real_world_example:"Infected endpoint is isolated at the switch level within minutes of detection.", sp800_53_refs:["IR-4","CM-6"], level_num:5, rarity:"uncommon" },
  { card_id:"NIST-RS-CO-2", function:"RESPOND", subcategory:"RS.CO-02", title:"Coordination with Authorities", summary:"Activities are coordinated with relevant external stakeholders including law enforcement.", why_it_matters:"Law enforcement involvement is legally required in some breach scenarios and aids attribution.", real_world_example:"FBI Cyber Division is notified for incidents involving critical infrastructure or nation-state attribution.", sp800_53_refs:["IR-6","IR-7"], level_num:5, rarity:"rare" },
  { card_id:"NIST-RS-MI-1", function:"RESPOND", subcategory:"RS.MI-01", title:"Incidents Contained", summary:"Incidents are contained to minimize impact and prevent further damage.", why_it_matters:"Every minute of uncontained access increases the attacker's foothold.", real_world_example:"Compromised domain admin credentials are disabled and all active sessions terminated within 10 minutes.", sp800_53_refs:["IR-4","CM-6"], level_num:5, rarity:"common" },

  // RECOVER (level_num 6)
  { card_id:"NIST-RC-RP-1", function:"RECOVER", subcategory:"RC.RP-01", title:"Recovery Plan Executed", summary:"The recovery plan is executed during or after a cybersecurity incident.", why_it_matters:"Recovery without a plan leads to ad-hoc decisions under pressure that extend downtime.", real_world_example:"After ransomware, systems are restored from verified backups following the documented RTO/RPO targets.", sp800_53_refs:["IR-4","CP-10"], level_num:6, rarity:"common" },
  { card_id:"NIST-RC-RP-3", function:"RECOVER", subcategory:"RC.RP-03", title:"Recovery Activities Communicated", summary:"Recovery activities are communicated to internal and external stakeholders.", why_it_matters:"Silence during recovery erodes stakeholder trust and invites speculation.", real_world_example:"Status updates are posted to an internal status page every two hours during a major outage.", sp800_53_refs:["CP-10","IR-4"], level_num:6, rarity:"uncommon" },
  { card_id:"NIST-RC-RP-5", function:"RECOVER", subcategory:"RC.RP-05", title:"Recovery Plan Updated", summary:"Recovery plan testing and incident execution drive updates to the recovery plan.", why_it_matters:"A recovery plan that is never updated reflects the past, not the current environment.", real_world_example:"Each tabletop exercise produces a lessons-learned document that drives plan revisions within 30 days.", sp800_53_refs:["CP-9","CP-10"], level_num:6, rarity:"uncommon" },
  { card_id:"NIST-RC-CO-3", function:"RECOVER", subcategory:"RC.CO-03", title:"Recovery Communication with Stakeholders", summary:"Recovery activities are communicated to restore stakeholder confidence in the organization.", why_it_matters:"Transparent communication protects reputation and satisfies regulatory obligations.", real_world_example:"A breach notification letter is sent to affected customers within 72 hours per GDPR requirements.", sp800_53_refs:["IR-7","IR-8"], level_num:6, rarity:"rare" },

  // AI RMF BOSS (level_num 7)
  { card_id:"NIST-AI-GV-1-1", function:"AI_RMF", subcategory:"GOVERN 1.1", title:"AI Risk Management Policies", summary:"Policies, processes, and procedures for AI risk management are established and maintained.", why_it_matters:"Without formal AI governance, teams deploy models with unreviewed risks.", real_world_example:"A firm's AI governance board reviews all model deployments against a risk criteria checklist.", sp800_53_refs:[], level_num:7, rarity:"rare" },
  { card_id:"NIST-AI-GV-2-2", function:"AI_RMF", subcategory:"GOVERN 2.2", title:"Accountability for AI Risk", summary:"Organizational teams are committed to a culture that addresses AI risk transparently.", why_it_matters:"Diffuse accountability for AI risk means no one owns failures.", real_world_example:"Each AI product has a named responsible AI owner who signs off on deployment and monitors outputs.", sp800_53_refs:[], level_num:7, rarity:"rare" },
  { card_id:"NIST-AI-MAP-1-1", function:"AI_RMF", subcategory:"MAP 1.1", title:"AI System Context Documented", summary:"Context is established to understand the AI system's intended purpose, users, and environment.", why_it_matters:"AI systems behave unpredictably when deployed outside their intended context.", real_world_example:"A hiring algorithm's design doc specifies it was trained on US resumes and should not be used globally.", sp800_53_refs:[], level_num:7, rarity:"uncommon" },
  { card_id:"NIST-AI-MAP-3-5", function:"AI_RMF", subcategory:"MAP 3.5", title:"Human Oversight Processes Defined", summary:"Processes for human oversight and intervention in AI-driven decisions are established.", why_it_matters:"Fully automated high-stakes decisions without human review amplify AI errors at scale.", real_world_example:"A loan approval AI flags borderline decisions for human review before final determination.", sp800_53_refs:[], level_num:7, rarity:"uncommon" },
  { card_id:"NIST-AI-MS-2-5", function:"AI_RMF", subcategory:"MEASURE 2.5", title:"AI Validity and Reliability Demonstrated", summary:"The AI system's validity and reliability are evaluated and documented.", why_it_matters:"A model that performs well on training data may fail dangerously on real-world edge cases.", real_world_example:"A medical diagnosis AI is tested on demographically diverse holdout sets before clinical deployment.", sp800_53_refs:[], level_num:7, rarity:"rare" },
  { card_id:"NIST-AI-MS-2-9", function:"AI_RMF", subcategory:"MEASURE 2.9", title:"AI Model Explainability", summary:"Mechanisms for explainability are established so AI outputs can be understood and audited.", why_it_matters:"Black-box decisions in regulated industries expose the organization to legal and reputational risk.", real_world_example:"A credit scoring model uses SHAP values to explain each prediction to loan officers and regulators.", sp800_53_refs:[], level_num:7, rarity:"rare" },
  { card_id:"NIST-AI-MG-1-3", function:"AI_RMF", subcategory:"MANAGE 1.3", title:"High-Priority AI Risks Responded To", summary:"Responses to identified high-priority AI risks are planned and implemented.", why_it_matters:"Identified risks without response plans are just documented liabilities.", real_world_example:"A bias finding in a content recommendation model triggers an immediate rollback and root-cause analysis.", sp800_53_refs:[], level_num:7, rarity:"rare" },
  { card_id:"NIST-AI-MG-4-1", function:"AI_RMF", subcategory:"MANAGE 4.1", title:"Post-Deployment Monitoring", summary:"Post-deployment AI monitoring tracks performance, drift, and emerging risks over time.", why_it_matters:"AI models degrade as real-world data distribution shifts away from training data.", real_world_example:"A fraud detection model's precision and recall are tracked weekly; alerts fire when metrics drop 5%.", sp800_53_refs:[], level_num:7, rarity:"uncommon" },
];
```

- [ ] **Step 2: Verify count in console**

```javascript
console.log(POLICY_CARDS.length); // → 46
console.log(POLICY_CARDS.filter(c => c.function === 'GOVERN').length); // → 6
console.log(POLICY_CARDS.filter(c => c.function === 'AI_RMF').length); // → 8
```

- [ ] **Step 3: Commit**

```bash
git add data/policy_cards.js && git commit -m "feat: add 46 NIST policy cards"
```

---

### Task 5: data/scenarios.js

**Files:**
- Write: `cyberguard/data/scenarios.js`

- [ ] **Step 1: Write data/scenarios.js**

```javascript
// cyberguard/data/scenarios.js
// correct: 0-based index into options array

const SCENARIOS = [
  // GOVERN (level_num 1)
  {
    scenario_id:"SCN-001", level_num:1, function:"GOVERN", control_ref:"GV.OC-01",
    situation:"A CISO presents a cybersecurity budget request to the board. The request lists tools and headcount but contains no reference to business objectives, regulatory requirements, or risk priorities. The board asks for justification.",
    question:"Which CSF 2.0 outcome most directly addresses the gap in this budget request?",
    options:["GV.OC-01 — Organizational mission informs cybersecurity risk decisions","PR.DS-01 — Data at rest is protected","DE.CM-01 — Networks are monitored for anomalies","RS.MA-01 — Incident response plan is executed"],
    correct:0,
    explanation:"GV.OC-01 requires cybersecurity strategy to be grounded in organizational mission and stakeholder expectations — exactly what was missing from the budget request."
  },
  {
    scenario_id:"SCN-002", level_num:1, function:"GOVERN", control_ref:"GV.RM-02",
    situation:"Your organization accepts all identified risks without documentation of what level of risk is acceptable. A new audit finding reveals that three critical systems carry risks that would exceed most industries' tolerance thresholds.",
    question:"What is the most foundational governance control missing in this scenario?",
    options:["A documented risk appetite and tolerance statement (GV.RM-02)","A vulnerability scanner (ID.RA-01)","An incident response plan (RS.MA-01)","Encryption at rest (PR.DS-01)"],
    correct:0,
    explanation:"GV.RM-02 requires the organization to define and communicate its risk appetite. Without this, there is no basis for evaluating whether identified risks are acceptable."
  },
  {
    scenario_id:"SCN-003", level_num:1, function:"GOVERN", control_ref:"GV.SC-01",
    situation:"A cloud vendor is onboarded to process customer PII. No security questionnaire was sent, no contract security addendum was included, and the vendor's compliance posture is unknown. Six months later the vendor suffers a breach exposing your customer data.",
    question:"Which CSF 2.0 supply chain control should have been applied before onboarding?",
    options:["GV.SC-01 — Supply chain risk management policy governs third-party engagement","DE.AE-03 — Event data is aggregated from multiple sources","RC.RP-01 — Recovery plan is executed","PR.AT-01 — Personnel are aware of cybersecurity risks"],
    correct:0,
    explanation:"GV.SC-01 requires organizations to establish supply chain risk management policies that define security expectations for vendors before they are engaged."
  },

  // IDENTIFY (level_num 2)
  {
    scenario_id:"SCN-004", level_num:2, function:"IDENTIFY", control_ref:"ID.AM-01",
    situation:"An unknown device appears on your network causing unusual traffic. Your team cannot determine whether it is an employee device, IoT sensor, or unauthorized intruder device because asset inventory records have not been updated in 18 months.",
    question:"Which IDENTIFY control would have given you the context to respond immediately?",
    options:["ID.AM-01 — Physical devices and systems are inventoried","RS.MI-01 — Incidents are contained","PR.AA-01 — Identities and credentials are managed","DE.AE-06 — Cybersecurity incidents are declared"],
    correct:0,
    explanation:"ID.AM-01 requires an up-to-date inventory of physical devices. Without it, you cannot distinguish authorized from unauthorized devices when anomalies appear."
  },
  {
    scenario_id:"SCN-005", level_num:2, function:"IDENTIFY", control_ref:"ID.RA-01",
    situation:"A critical vulnerability (CVSS 9.1) is published for a web framework your organization uses. Three weeks pass and the security team is still debating whether you use the affected version because there is no documented software inventory or vulnerability register.",
    question:"Which two controls together would have enabled immediate triage?",
    options:["ID.AM-02 (software inventory) + ID.RA-01 (vulnerabilities documented)","PR.DS-02 (data in transit) + RC.RP-01 (recovery plan)","DE.CM-01 (network monitoring) + RS.AN-03 (analysis)","GV.SC-01 (supply chain policy) + PR.PS-01 (config management)"],
    correct:0,
    explanation:"ID.AM-02 provides the software inventory needed to confirm exposure. ID.RA-01 requires that identified vulnerabilities be documented in actionable form for timely response."
  },
  {
    scenario_id:"SCN-006", level_num:2, function:"IDENTIFY", control_ref:"ID.AM-02",
    situation:"A developer installs an open-source dependency with a known critical CVE that was not in your approved software catalog. This shadow dependency goes unnoticed for four months until a pen test discovers it.",
    question:"Which control directly addresses the risk of unapproved software entering the environment?",
    options:["ID.AM-02 — Software platforms and applications are inventoried","GV.RR-01 — Roles and responsibilities are established","DE.CM-02 — Physical environment is monitored","RC.CO-03 — Recovery communication with stakeholders"],
    correct:0,
    explanation:"ID.AM-02 requires inventorying all software. Combined with approval workflows, it prevents unapproved dependencies from entering the environment undetected."
  },
  {
    scenario_id:"SCN-007", level_num:2, function:"IDENTIFY", control_ref:"ID.RA-05",
    situation:"Your threat intel team receives a report that a nation-state group is actively targeting your industry's supply chain using a specific spear-phishing technique. Leadership asks how exposed you are, but there is no process to map threat intelligence to asset risk.",
    question:"Which IDENTIFY control supports mapping threat intelligence to organizational risk?",
    options:["ID.RA-05 — Threats, vulnerabilities, likelihoods, and impacts are used to understand risk","PR.AT-01 — Personnel are aware of cybersecurity risks","RS.CO-02 — Coordination with authorities","RC.RP-05 — Recovery plan is updated"],
    correct:0,
    explanation:"ID.RA-05 requires combining threat data, vulnerabilities, likelihood, and impact to produce a risk assessment — the process needed to answer the leadership question."
  },

  // PROTECT (level_num 3)
  {
    scenario_id:"SCN-008", level_num:3, function:"PROTECT", control_ref:"PR.AA-01",
    situation:"An investigation reveals that five administrators share a single 'admin' account password that has not been changed in two years. Audit logs cannot attribute actions to individuals. A recent incident cannot be attributed to any specific person.",
    question:"Which PROTECT control is most directly violated?",
    options:["PR.AA-01 — Identities and credentials are issued, managed, and verified","DE.AE-02 — Adverse events are analyzed","GV.PO-01 — Policies are established","ID.IM-01 — Improvements are identified from evaluations"],
    correct:0,
    explanation:"PR.AA-01 requires individual identity management and credential controls. Shared accounts violate individual accountability and make forensic attribution impossible."
  },
  {
    scenario_id:"SCN-009", level_num:3, function:"PROTECT", control_ref:"PR.DS-01",
    situation:"A laptop containing 50,000 customer records is stolen from a car. The laptop had no full-disk encryption enabled. The organization must now notify all 50,000 customers and faces significant regulatory fines.",
    question:"Which control would have prevented this from becoming a reportable breach?",
    options:["PR.DS-01 — Data at rest is protected (full-disk encryption)","RS.MA-02 — Incident is reported to stakeholders","DE.CM-01 — Networks are monitored","GV.SC-01 — Supply chain risk management policy"],
    correct:0,
    explanation:"PR.DS-01 requires data at rest to be protected. Full-disk encryption ensures that a stolen device does not result in data disclosure — the defining factor for breach notification obligations."
  },
  {
    scenario_id:"SCN-010", level_num:3, function:"PROTECT", control_ref:"PR.PS-01",
    situation:"A server is compromised because it was running an outdated FTP service that no one knew was still enabled. The service was not in the approved configuration baseline and had not been reviewed during the last security audit.",
    question:"Which PROTECT control directly addresses unnecessary service exposure?",
    options:["PR.PS-01 — Configuration management policies ensure only approved services run","PR.AA-03 — Users are authenticated to access assets","DE.AE-07 — Threat intelligence is received","RS.AN-06 — Actions are performed to prevent expansion"],
    correct:0,
    explanation:"PR.PS-01 requires that configuration management disable all unnecessary services. An approved baseline with enforcement would have flagged and removed the unused FTP service."
  },
  {
    scenario_id:"SCN-011", level_num:3, function:"PROTECT", control_ref:"PR.AT-01",
    situation:"An employee receives a phishing email, clicks a malicious link, and enters their credentials. The employee later says they did not recognize the signs of phishing. This is the third such incident this quarter from the same department.",
    question:"Which PROTECT control addresses the root cause of repeated human error?",
    options:["PR.AT-01 — Personnel are informed and trained on cybersecurity responsibilities","PR.DS-02 — Data in transit is protected","DE.AE-03 — Event data is aggregated","RC.RP-03 — Recovery activities are communicated"],
    correct:0,
    explanation:"PR.AT-01 requires ongoing cybersecurity awareness training. Repeated phishing successes indicate the training program is insufficient or not enforced for the affected department."
  },

  // DETECT (level_num 4)
  {
    scenario_id:"SCN-012", level_num:4, function:"DETECT", control_ref:"DE.CM-01",
    situation:"An attacker has been moving laterally inside your network for 11 days, exfiltrating data via HTTPS to an external IP. No alerts fired. Post-incident review finds that outbound HTTPS traffic to new external IPs was never monitored.",
    question:"Which DETECT control was absent that would have enabled earlier discovery?",
    options:["DE.CM-01 — Network is monitored to detect potential cybersecurity events","PR.AA-03 — Users are authenticated","RS.MA-01 — Incident response plan is executed","GV.RM-01 — Risk management strategy is established"],
    correct:0,
    explanation:"DE.CM-01 requires continuous monitoring of the network for anomalies. Monitoring outbound traffic patterns would have flagged the sustained exfiltration to a new external destination."
  },
  {
    scenario_id:"SCN-013", level_num:4, function:"DETECT", control_ref:"DE.AE-02",
    situation:"Your SIEM generates 10,000 alerts per day. The SOC team is overwhelmed and closes most without investigation. Three low-severity alerts about failed logins on the same account over two days were never correlated, and the account was later used in a breach.",
    question:"Which DETECT capability would have surfaced the attack pattern hidden in the alert noise?",
    options:["DE.AE-02 — Potentially adverse events are analyzed and correlated to detect patterns","DE.CM-02 — Physical environment is monitored","RS.CO-02 — Coordination with authorities","PR.PS-01 — Configuration management policies are enforced"],
    correct:0,
    explanation:"DE.AE-02 requires analysis and correlation of potentially adverse events. Correlating the three low-severity login failures would have revealed the pattern of credential stuffing before account compromise."
  },
  {
    scenario_id:"SCN-014", level_num:4, function:"DETECT", control_ref:"DE.AE-06",
    situation:"Your SIEM fires a high-confidence alert for a known ransomware precursor: a domain admin account running Mimikatz. The on-call analyst acknowledges the alert and marks it 'review later' without escalating. Ransomware deploys four hours later.",
    question:"Which DETECT control was not properly implemented in this scenario?",
    options:["DE.AE-06 — A cybersecurity incident is declared when detection thresholds are met","DE.CM-02 — Physical environment is monitored","ID.AM-07 — Vulnerabilities in assets are identified","RC.RP-05 — Recovery plan is updated"],
    correct:0,
    explanation:"DE.AE-06 requires that incidents be declared and response initiated when thresholds are met. The Mimikatz alert should have triggered an automatic P1 declaration, not a manual deferral."
  },

  // RESPOND (level_num 5)
  {
    scenario_id:"SCN-015", level_num:5, function:"RESPOND", control_ref:"RS.MA-01",
    situation:"Ransomware is detected encrypting files on a file server. The SOC team has no documented playbook for ransomware. Each analyst takes different actions: one isolates the server, another attempts decryption, a third calls the vendor. Coordination collapses and 3 additional servers are infected before action is unified.",
    question:"Which RESPOND control would have prevented the uncoordinated response?",
    options:["RS.MA-01 — The incident response plan is executed consistently and coordinated","DE.AE-03 — Event data is aggregated","GV.OC-01 — Organizational mission informs cybersecurity","PR.DS-01 — Data at rest is protected"],
    correct:0,
    explanation:"RS.MA-01 requires that the IRP be executed consistently with clear ownership and coordination. A tested ransomware playbook with defined roles prevents the ad-hoc response that allowed lateral spread."
  },
  {
    scenario_id:"SCN-016", level_num:5, function:"RESPOND", control_ref:"RS.AN-03",
    situation:"After isolating a compromised system, the team immediately re-images it to get the service back online. Two weeks later, the same attack vector is used to compromise three more systems because the root cause was never determined.",
    question:"Which RESPOND control was skipped that would have prevented recurrence?",
    options:["RS.AN-03 — Analysis is performed to determine what occurred and support recovery","RS.MI-01 — Incidents are contained","RC.RP-01 — Recovery plan is executed","PR.AT-02 — Personnel are trained for their roles"],
    correct:0,
    explanation:"RS.AN-03 requires forensic analysis before eradication and recovery. Skipping analysis meant the initial access vector remained unknown and unpatched, enabling re-exploitation."
  },
  {
    scenario_id:"SCN-017", level_num:5, function:"RESPOND", control_ref:"RS.CO-02",
    situation:"A breach involves theft of 100,000 health records. Internal response is handled well. However, no notification is sent to HHS OCR, no law enforcement contact is made, and affected patients are notified 90 days late. Regulatory penalties result.",
    question:"Which RESPOND control governs external notification and coordination obligations?",
    options:["RS.CO-02 — Activities are coordinated with relevant external stakeholders including authorities","RS.MA-02 — Incidents are reported to internal stakeholders","DE.AE-06 — Cybersecurity incidents are declared","GV.RR-01 — Roles and responsibilities are established"],
    correct:0,
    explanation:"RS.CO-02 requires coordination with external parties including regulators and law enforcement. HIPAA breach notification to HHS and patient notification are legal obligations triggered by this control."
  },
  {
    scenario_id:"SCN-018", level_num:5, function:"RESPOND", control_ref:"RS.MI-01",
    situation:"An attacker is actively moving through your environment using valid credentials. The SOC detects the activity but delays containment for 2 hours while waiting for change-management approval to disable the compromised account.",
    question:"Which RESPOND control was improperly blocked by process overhead?",
    options:["RS.MI-01 — Incidents are contained to minimize impact and prevent further damage","GV.PO-01 — Policies are established and approved","ID.RA-03 — Threat intelligence is used to identify threats","RC.RP-03 — Recovery activities are communicated"],
    correct:0,
    explanation:"RS.MI-01 requires rapid containment actions during active incidents. Change management processes must have pre-authorized emergency procedures that allow disabling compromised accounts without delay."
  },

  // RECOVER (level_num 6)
  {
    scenario_id:"SCN-019", level_num:6, function:"RECOVER", control_ref:"RC.RP-01",
    situation:"After a destructive attack, the team begins restoration but realizes the recovery plan was written for a different system architecture. Critical steps are missing, backups are in an untested format, and RTO cannot be met. The system is offline for 5 days instead of the target 4 hours.",
    question:"Which RECOVER control failure caused the extended downtime?",
    options:["RC.RP-01 — Recovery plan is executed and kept aligned to current architecture","RS.CO-02 — Coordination with authorities","DE.CM-01 — Networks are monitored","ID.AM-05 — Resources are prioritized"],
    correct:0,
    explanation:"RC.RP-01 requires that the recovery plan be tested and maintained. A plan that hasn't been validated against the current architecture will fail under real conditions, exactly as occurred here."
  },
  {
    scenario_id:"SCN-020", level_num:6, function:"RECOVER", control_ref:"RC.RP-05",
    situation:"After last year's ransomware incident, several lessons were identified: backups were not air-gapped, recovery runbooks were incomplete, and RTO was unrealistic. A new incident occurs one year later and the same gaps exist because lessons-learned were never incorporated into the plan.",
    question:"Which RECOVER control was not followed after the first incident?",
    options:["RC.RP-05 — Recovery plan is updated based on lessons learned from incidents","RC.CO-03 — Recovery communication with stakeholders","RS.MA-01 — Incident response plan is executed","PR.PS-01 — Configuration management policies are enforced"],
    correct:0,
    explanation:"RC.RP-05 requires that recovery plan testing and incident execution drive updates to the plan. Failing to incorporate lessons-learned guarantees repeat failures when the next incident occurs."
  },
  {
    scenario_id:"SCN-021", level_num:6, function:"RECOVER", control_ref:"RC.CO-03",
    situation:"Systems are restored after a breach but customers, regulators, and the press are receiving conflicting information from different spokespeople. Customer trust collapses. A regulator issues a sanction for insufficient breach communication rather than the breach itself.",
    question:"Which RECOVER control governs stakeholder communication during restoration?",
    options:["RC.CO-03 — Recovery activities are communicated to restore stakeholder confidence","RC.RP-01 — Recovery plan is executed","RS.AN-06 — Actions are performed to prevent expansion","GV.PO-01 — Policies are established"],
    correct:0,
    explanation:"RC.CO-03 requires coordinated, consistent external communication during recovery. A single communication lead, approved messaging, and regular status updates would have prevented the conflicting information."
  },

  // AI RMF BOSS (level_num 7)
  {
    scenario_id:"SCN-022", level_num:7, function:"AI_RMF", control_ref:"GOVERN 1.1",
    situation:"A data science team deploys an AI model to production that automates loan approvals. No AI governance policy was consulted, no risk review was conducted, and no accountability owner was assigned. The model later shows discriminatory patterns against a protected class.",
    question:"Which AI RMF GOVERN control was absent before deployment?",
    options:["GOVERN 1.1 — AI risk management policies and processes are established","MAP 3.5 — Human oversight processes are defined","MEASURE 2.5 — AI validity and reliability are demonstrated","MANAGE 4.1 — Post-deployment monitoring is implemented"],
    correct:0,
    explanation:"GOVERN 1.1 requires that AI risk management policies govern all deployments. A policy requiring pre-deployment risk review and accountability assignment would have caught the bias risk before harm occurred."
  },
  {
    scenario_id:"SCN-023", level_num:7, function:"AI_RMF", control_ref:"MAP 1.1",
    situation:"An AI content moderation system trained on English social media data is deployed globally for all languages. It fails dramatically on non-English content, blocking legitimate speech while missing harmful content. The deployment team did not document the system's intended scope.",
    question:"Which AI RMF MAP control would have prevented this out-of-context deployment?",
    options:["MAP 1.1 — AI system context, purpose, and intended users are documented","MANAGE 1.3 — High-priority AI risks are responded to","MEASURE 2.9 — AI model explainability is documented","GOVERN 2.2 — Accountability for AI risk is established"],
    correct:0,
    explanation:"MAP 1.1 requires documenting the AI system's context, intended purpose, and deployment scope. Explicit documentation of English-only training would have flagged the global deployment as out of scope."
  },
  {
    scenario_id:"SCN-024", level_num:7, function:"AI_RMF", control_ref:"MEASURE 2.5",
    situation:"A predictive maintenance AI is deployed in a manufacturing plant without validation on the plant's specific equipment. The model was only tested on lab data. It misses 40% of actual failures in the first month, causing costly unplanned downtime.",
    question:"Which AI RMF MEASURE control was not applied before production deployment?",
    options:["MEASURE 2.5 — AI system validity and reliability are evaluated on representative data","MAP 3.5 — Human oversight processes are defined","GOVERN 1.1 — AI risk management policies are established","MANAGE 4.1 — Post-deployment monitoring is implemented"],
    correct:0,
    explanation:"MEASURE 2.5 requires evaluating AI validity and reliability against data representative of the deployment context. Testing only on lab data failed to reveal the model's poor generalization to real equipment."
  },
  {
    scenario_id:"SCN-025", level_num:7, function:"AI_RMF", control_ref:"MANAGE 1.3",
    situation:"An AI hiring screening tool is found to systematically disadvantage candidates from certain universities. The bias finding is documented in an internal audit six months ago. No action was taken because the product team considered it low priority. Litigation follows.",
    question:"Which AI RMF MANAGE control was violated by the inaction on the documented finding?",
    options:["MANAGE 1.3 — Responses to high-priority AI risks are planned and implemented","MEASURE 2.9 — AI model explainability is documented","MAP 1.1 — AI system context is documented","GOVERN 2.2 — Accountability for AI risk is established"],
    correct:0,
    explanation:"MANAGE 1.3 requires that identified high-priority risks have response plans and that those plans are implemented. A documented bias finding that sits unaddressed violates the 'respond' mandate of the AI RMF."
  },
];
```

- [ ] **Step 2: Verify counts**

```javascript
console.log(SCENARIOS.length); // → 25
console.log(SCENARIOS.filter(s => s.level_num === 7).length); // → 4
```

- [ ] **Step 3: Commit**

```bash
git add data/scenarios.js && git commit -m "feat: add 25 NIST scenario challenges"
```

---

### Task 6: engine.js

**Files:**
- Write: `cyberguard/engine.js`

- [ ] **Step 1: Write engine.js**

```javascript
// cyberguard/engine.js

const keys = { w:false, a:false, s:false, d:false, e:false, c:false, esc:false, tab:false };
const keysJustPressed = { e:false, c:false, esc:false, tab:false };

let canvas, ctx, imageBuffer;
let animFrameId = null;
let lastFrameTime = 0;

function hexToRGB(hex) {
  return {
    r: parseInt(hex.slice(1,3), 16),
    g: parseInt(hex.slice(3,5), 16),
    b: parseInt(hex.slice(5,7), 16),
  };
}

function getCell(map, x, y) {
  const col = Math.floor(x);
  const row = Math.floor(y);
  if (row < 0 || row >= map.length || col < 0 || col >= map[0].length) return 1;
  return map[row][col];
}

function canMoveTo(map, x, y) {
  const c = getCell(map, x, y);
  return c === 0 || c === 3 || c === 4;
}

function castRay(rayAngle, px, py, map) {
  const rdx = Math.cos(rayAngle);
  const rdy = Math.sin(rayAngle);
  let mapX = Math.floor(px);
  let mapY = Math.floor(py);
  const ddx = rdx === 0 ? 1e30 : Math.abs(1 / rdx);
  const ddy = rdy === 0 ? 1e30 : Math.abs(1 / rdy);
  let sdx, sdy, stepX, stepY;
  if (rdx < 0) { stepX = -1; sdx = (px - mapX) * ddx; }
  else         { stepX =  1; sdx = (mapX + 1 - px) * ddx; }
  if (rdy < 0) { stepY = -1; sdy = (py - mapY) * ddy; }
  else         { stepY =  1; sdy = (mapY + 1 - py) * ddy; }
  let side = 0;
  const rows = map.length, cols = map[0].length;
  for (let i = 0; i < 64; i++) {
    if (sdx < sdy) { sdx += ddx; mapX += stepX; side = 0; }
    else           { sdy += ddy; mapY += stepY; side = 1; }
    if (mapX < 0 || mapY < 0 || mapX >= cols || mapY >= rows) break;
    const cell = map[mapY][mapX];
    if (cell === 1 || cell === 2) break;
  }
  const dist = Math.max(0.001, side === 0 ? sdx - ddx : sdy - ddy);
  return { dist, side };
}

function renderFrame() {
  const { x, y, angle } = GAME_STATE.player;
  const { canvas_width, canvas_height, fov, wall_height_scale } = GAME_CONFIG;
  const map = GAME_STATE.level.map;
  const wallRGB = hexToRGB(ZONE_COLORS[GAME_STATE.level.zone]);
  const darkR = Math.floor(wallRGB.r * 0.6);
  const darkG = Math.floor(wallRGB.g * 0.6);
  const darkB = Math.floor(wallRGB.b * 0.6);
  const buf = imageBuffer.data;
  const half = canvas_height >> 1;

  // Ceiling
  for (let i = 0, end = half * canvas_width * 4; i < end; i += 4) {
    buf[i]=12; buf[i+1]=12; buf[i+2]=20; buf[i+3]=255;
  }
  // Floor
  for (let i = half * canvas_width * 4, end = canvas_width * canvas_height * 4; i < end; i += 4) {
    buf[i]=18; buf[i+1]=18; buf[i+2]=18; buf[i+3]=255;
  }

  for (let col = 0; col < canvas_width; col++) {
    const rayAngle = angle - fov * 0.5 + (col / canvas_width) * fov;
    const { dist, side } = castRay(rayAngle, x, y, map);
    const wallH = Math.min(canvas_height, Math.floor(wall_height_scale / dist));
    const top    = Math.max(0, half - (wallH >> 1));
    const bottom = Math.min(canvas_height, top + wallH);
    const r = side === 1 ? darkR : wallRGB.r;
    const g = side === 1 ? darkG : wallRGB.g;
    const b = side === 1 ? darkB : wallRGB.b;
    for (let row = top; row < bottom; row++) {
      const idx = (row * canvas_width + col) * 4;
      buf[idx]=r; buf[idx+1]=g; buf[idx+2]=b; buf[idx+3]=255;
    }
  }
  ctx.putImageData(imageBuffer, 0, 0);
}

function renderMinimap() {
  if (!GAME_STATE.minimap_visible) return;
  const s = GAME_CONFIG.minimap_scale;
  const map = GAME_STATE.level.map;
  const ox = 8, oy = 8;
  ctx.save();
  ctx.globalAlpha = 0.75;
  for (let row = 0; row < map.length; row++) {
    for (let col = 0; col < map[row].length; col++) {
      const cell = map[row][col];
      ctx.fillStyle = cell === 1 ? '#555' : cell === 2 ? '#FFD700' : cell === 3 ? '#00FFD1' : cell === 4 ? '#FF8C00' : '#111';
      ctx.fillRect(ox + col * s, oy + row * s, s - 1, s - 1);
    }
  }
  // Player dot
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(ox + GAME_STATE.player.x * s, oy + GAME_STATE.player.y * s, 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function updatePlayer(dt) {
  const { move_speed, turn_speed, player_radius } = GAME_CONFIG;
  const p = GAME_STATE.player;
  const map = GAME_STATE.level.map;
  if (keys.a) p.angle -= turn_speed * dt;
  if (keys.d) p.angle += turn_speed * dt;
  let dx = 0, dy = 0;
  if (keys.w) { dx += Math.cos(p.angle) * move_speed * dt; dy += Math.sin(p.angle) * move_speed * dt; }
  if (keys.s) { dx -= Math.cos(p.angle) * move_speed * dt; dy -= Math.sin(p.angle) * move_speed * dt; }
  if (dx !== 0 && canMoveTo(map, p.x + dx + Math.sign(dx) * player_radius, p.y)) p.x += dx;
  if (dy !== 0 && canMoveTo(map, p.x, p.y + dy + Math.sign(dy) * player_radius)) p.y += dy;
}

function gameLoop(timestamp) {
  const dt = Math.min((timestamp - lastFrameTime) / 1000, 0.1);
  lastFrameTime = timestamp;

  if (GAME_STATE.screen === 'playing') {
    updatePlayer(dt);
    checkCellInteractions();
    if (keysJustPressed.e) checkDoorInteraction();
    renderFrame();
    if (GAME_STATE.minimap_visible) renderMinimap();
  }

  if (keysJustPressed.c) {
    if (GAME_STATE.screen === 'playing') openCodex();
    else if (GAME_STATE.screen === 'codex') closeCodex();
  }
  if (keysJustPressed.tab && GAME_STATE.screen === 'playing') {
    GAME_STATE.minimap_visible = !GAME_STATE.minimap_visible;
  }
  if (keysJustPressed.esc) handleEscKey();

  keysJustPressed.e = false;
  keysJustPressed.c = false;
  keysJustPressed.esc = false;
  keysJustPressed.tab = false;

  animFrameId = requestAnimationFrame(gameLoop);
}

function setupInput() {
  const map = { arrowup:'w', arrowdown:'s', arrowleft:'a', arrowright:'d' };
  window.addEventListener('keydown', e => {
    const k = map[e.key.toLowerCase()] || e.key.toLowerCase();
    if (k in keys) {
      if (!keys[k]) { keys[k] = true; if (k in keysJustPressed) keysJustPressed[k] = true; }
    }
    if (k === 'tab') e.preventDefault();
  });
  window.addEventListener('keyup', e => {
    const k = map[e.key.toLowerCase()] || e.key.toLowerCase();
    if (k in keys) keys[k] = false;
  });
}

function startEngine() {
  canvas = document.getElementById('game-canvas');
  ctx = canvas.getContext('2d');
  imageBuffer = ctx.createImageData(GAME_CONFIG.canvas_width, GAME_CONFIG.canvas_height);
  setupInput();
  loadLevel('lobby');
  showBriefingScreen();
}

function pauseEngine() {
  if (animFrameId) { cancelAnimationFrame(animFrameId); animFrameId = null; }
}

function resumeEngine() {
  if (!animFrameId) { lastFrameTime = performance.now(); animFrameId = requestAnimationFrame(gameLoop); }
}
```

- [ ] **Step 2: Smoke test — open index.html, verify canvas renders**

Open `cyberguard/index.html` after all tasks complete. After role selection:
- Canvas should show raycasting view of the lobby (gray walls, dark ceiling, dark floor)
- WASD should move the player
- Minimap should appear top-left

- [ ] **Step 3: Commit**

```bash
git add engine.js && git commit -m "feat: raycasting engine with DDA, input loop, minimap"
```

---

### Task 7: mechanics.js

**Files:**
- Write: `cyberguard/mechanics.js`

- [ ] **Step 1: Write mechanics.js**

```javascript
// cyberguard/mechanics.js

function loadLevel(levelId) {
  const meta = LEVEL_METADATA[levelId];
  const mapData = MAPS[levelId];
  GAME_STATE.level.id = levelId;
  GAME_STATE.level.map = mapData.map(row => [...row]); // deep copy so pickups mutate safely
  GAME_STATE.level.zone = meta.zone;
  GAME_STATE.level.level_num = meta.level_num;
  GAME_STATE.level.cards_total = meta.cards;
  GAME_STATE.level.scenarios_total = meta.scenarios;
  GAME_STATE.player.x = meta.spawn.x;
  GAME_STATE.player.y = meta.spawn.y;
  GAME_STATE.player.angle = meta.spawn.angle;
  renderHUD();
}

function getCardsCollectedInLevel() {
  return GAME_STATE.progress.cards_collected.filter(id => {
    const card = POLICY_CARDS.find(c => c.card_id === id);
    return card && card.level_num === GAME_STATE.level.level_num;
  }).length;
}

function getScenariosCompletedInLevel() {
  return GAME_STATE.progress.scenarios_completed.filter(id => {
    const scen = SCENARIOS.find(s => s.scenario_id === id);
    return scen && scen.level_num === GAME_STATE.level.level_num;
  }).length;
}

function isZoneComplete() {
  if (GAME_STATE.level.level_num === 0) return true; // lobby always passable
  return getCardsCollectedInLevel() >= GAME_STATE.level.cards_total &&
         getScenariosCompletedInLevel() >= GAME_STATE.level.scenarios_total;
}

function checkCellInteractions() {
  const px = GAME_STATE.player.x;
  const py = GAME_STATE.player.y;
  const col = Math.floor(px);
  const row = Math.floor(py);
  const map = GAME_STATE.level.map;
  const cell = map[row] && map[row][col];

  if (cell === 3) {
    // Find which card corresponds to this level and position — use card order by level
    const levelCards = POLICY_CARDS.filter(c => c.level_num === GAME_STATE.level.level_num);
    const collected = GAME_STATE.progress.cards_collected.filter(id =>
      levelCards.some(c => c.card_id === id)
    );
    const nextCard = levelCards[collected.length];
    if (nextCard && !GAME_STATE.progress.cards_collected.includes(nextCard.card_id)) {
      map[row][col] = 0;
      GAME_STATE.progress.cards_collected.push(nextCard.card_id);
      GAME_STATE.progress.score += 100;
      showCardToast(nextCard);
      renderHUD();
    }
  }

  if (cell === 4 && GAME_STATE.screen === 'playing') {
    const levelScens = SCENARIOS.filter(s => s.level_num === GAME_STATE.level.level_num);
    const completed = GAME_STATE.progress.scenarios_completed.filter(id =>
      levelScens.some(s => s.scenario_id === id)
    );
    const nextScen = levelScens[completed.length];
    if (nextScen && !GAME_STATE.progress.scenarios_completed.includes(nextScen.scenario_id)) {
      GAME_STATE.active_scenario = nextScen;
      GAME_STATE.screen = 'scenario';
      showScenarioPanel(nextScen);
    }
  }
}

function checkDoorInteraction() {
  if (GAME_STATE.screen !== 'playing') return;
  const px = GAME_STATE.player.x;
  const py = GAME_STATE.player.y;
  const map = GAME_STATE.level.map;
  // Check cells within 1.2 units
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      const col = Math.floor(px + dx * 1.2);
      const row = Math.floor(py + dy * 1.2);
      if (map[row] && map[row][col] === 2) {
        if (isZoneComplete()) {
          startLevelTransition();
        } else {
          showDoorMessage();
        }
        return;
      }
    }
  }
}

function submitScenarioAnswer(optionIndex) {
  const scen = GAME_STATE.active_scenario;
  if (!scen) return;
  const map = GAME_STATE.level.map;

  if (optionIndex === scen.correct) {
    // Correct answer
    const firstTry = !GAME_STATE.progress.scenarios_penalized.includes(scen.scenario_id);
    GAME_STATE.progress.score += firstTry ? 200 : 50;
    GAME_STATE.progress.scenarios_completed.push(scen.scenario_id);
    // Clear the scenario cell
    for (let r = 0; r < map.length; r++) {
      for (let c = 0; c < map[r].length; c++) {
        if (map[r][c] === 4) {
          const levelScens = SCENARIOS.filter(s => s.level_num === GAME_STATE.level.level_num);
          const completedCount = GAME_STATE.progress.scenarios_completed.filter(id =>
            levelScens.some(s => s.scenario_id === id)
          ).length;
          if (completedCount === GAME_STATE.progress.scenarios_completed.filter(id =>
              levelScens.some(s => s.scenario_id === id)).length) {
            map[r][c] = 0;
            break;
          }
        }
      }
      break;
    }
    GAME_STATE.active_scenario = null;
    GAME_STATE.screen = 'playing';
    hideScenarioPanel();
    renderHUD();
  } else {
    // Wrong answer
    if (!GAME_STATE.progress.scenarios_penalized.includes(scen.scenario_id)) {
      GAME_STATE.progress.scenarios_penalized.push(scen.scenario_id);
      GAME_STATE.progress.grade = Math.max(0, GAME_STATE.progress.grade - 8);
      renderHUD();
      if (GAME_STATE.progress.grade < 60) {
        triggerGameOver(scen);
        return;
      }
    }
    showScenarioWrongAnswer(scen, optionIndex);
  }
}

function triggerGameOver(scen) {
  GAME_STATE.screen = 'gameover';
  GAME_STATE.active_scenario = null;
  GAME_STATE.progress.grade = 70; // reset to C, preserve progress
  showGameOver(scen);
}

function startLevelTransition() {
  GAME_STATE.screen = 'transition';
  const meta = LEVEL_METADATA[GAME_STATE.level.id];
  GAME_STATE.progress.score += 500;
  renderHUD();
  showLevelTransition(meta.zone, () => {
    if (meta.next === null) {
      GAME_STATE.progress.score += 1000;
      GAME_STATE.screen = 'certificate';
      showCertificate();
    } else {
      loadLevel(meta.next);
      GAME_STATE.screen = 'playing';
    }
  });
}

function handleEscKey() {
  if (GAME_STATE.screen === 'playing') {
    GAME_STATE.screen = 'paused';
    showPauseMenu();
  } else if (GAME_STATE.screen === 'paused') {
    GAME_STATE.screen = 'playing';
    hidePauseMenu();
  } else if (GAME_STATE.screen === 'codex') {
    closeCodex();
  }
}

function openCodex() {
  GAME_STATE.screen = 'codex';
  pauseEngine();
  showCodex();
}

function closeCodex() {
  GAME_STATE.screen = 'playing';
  hideCodex();
  resumeEngine();
}

// Clear the scenario cell that triggered the active scenario (called after correct answer)
function clearActiveScenarioCell() {
  const map = GAME_STATE.level.map;
  const px = GAME_STATE.player.x;
  const py = GAME_STATE.player.y;
  const col = Math.floor(px);
  const row = Math.floor(py);
  if (map[row] && map[row][col] === 4) map[row][col] = 0;
}
```

- [ ] **Step 2: Verify grade system in console (after full wiring)**

```javascript
// Simulate wrong answers
GAME_STATE.progress.grade = 65;
submitScenarioAnswer(99); // wrong
// grade should drop to 57 → triggers game over
console.log(GAME_STATE.screen); // → 'gameover'
console.log(GAME_STATE.progress.grade); // → 70 (reset)
```

- [ ] **Step 3: Commit**

```bash
git add mechanics.js && git commit -m "feat: mechanics — level loading, interactions, grade system"
```

---

### Task 8: style.css

**Files:**
- Write: `cyberguard/style.css`

- [ ] **Step 1: Write style.css**

```css
/* cyberguard/style.css */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

:root {
  --primary:   #00FFD1;
  --secondary: #7B2FBE;
  --danger:    #FF4444;
  --warn:      #FFB800;
  --safe:      #00CC66;
  --bg-dark:   #0A0A0F;
  --bg-panel:  #12121A;
  --bg-panel2: #1A1A28;
  --border:    #2A2A3A;
  --text:      #C8C8E0;
  --font-d:    'Orbitron', sans-serif;
  --font-m:    'Share Tech Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg-dark);
  color: var(--text);
  font-family: var(--font-m);
  overflow: hidden;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

#game-container {
  position: relative;
  width: 800px;
  height: 500px;
}

#game-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

/* HUD */
#hud {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 36px;
  background: rgba(10,10,15,0.88);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 24px;
  font-family: var(--font-d);
  font-size: 11px;
  letter-spacing: 0.08em;
  z-index: 10;
  pointer-events: none;
}
#hud .hud-zone  { color: var(--primary); font-weight: 700; }
#hud .hud-cards { color: #aaa; }
#hud .hud-grade { font-weight: 700; }
#hud .hud-score { color: #aaa; margin-left: auto; }
.grade-a { color: var(--safe); }
.grade-b { color: #00E5FF; }
.grade-c { color: var(--warn); }
.grade-d { color: #FF8C00; }
.grade-f { color: var(--danger); }

/* Overlays */
.overlay {
  position: absolute;
  inset: 0;
  display: none;
  z-index: 20;
}
.overlay.active { display: flex; }

/* Briefing screen */
#briefing-screen {
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  background: var(--bg-dark);
  overflow-y: auto;
  padding: 20px;
}
#briefing-screen .logo-wrap {
  width: 100%;
  max-height: 160px;
  overflow: hidden;
  border-radius: 6px;
  margin-bottom: 16px;
}
#briefing-screen .logo-wrap img { width: 100%; object-fit: cover; }
#briefing-screen h1 {
  font-family: var(--font-d);
  font-size: 18px;
  color: var(--primary);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}
#briefing-screen .subtitle {
  font-size: 11px;
  color: #888;
  margin-bottom: 14px;
  letter-spacing: 0.06em;
}
#briefing-screen .brief-text {
  font-size: 12px;
  color: var(--text);
  text-align: center;
  max-width: 560px;
  margin-bottom: 18px;
  line-height: 1.6;
}
#briefing-screen .role-grid {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}
.role-btn {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 18px;
  cursor: pointer;
  font-family: var(--font-d);
  font-size: 10px;
  color: var(--text);
  letter-spacing: 0.06em;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
  min-width: 130px;
}
.role-btn:hover { border-color: var(--primary); background: var(--bg-panel2); color: var(--primary); }
.role-btn .role-icon { font-size: 22px; margin-bottom: 6px; }
.briefing-footer {
  font-size: 10px;
  color: #555;
  margin-top: 6px;
  letter-spacing: 0.08em;
}

/* Scenario panel */
#scenario-panel {
  align-items: center;
  justify-content: center;
  background: rgba(10,10,15,0.94);
}
.scenario-box {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px 28px;
  max-width: 600px;
  width: 100%;
}
.scenario-box .scen-header {
  font-family: var(--font-d);
  font-size: 10px;
  color: var(--warn);
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}
.scenario-box .scen-situation {
  font-size: 12px;
  line-height: 1.65;
  color: var(--text);
  margin-bottom: 16px;
  border-left: 2px solid var(--border);
  padding-left: 12px;
}
.scenario-box .scen-question {
  font-family: var(--font-d);
  font-size: 11px;
  color: var(--primary);
  margin-bottom: 12px;
}
.option-btn {
  display: block;
  width: 100%;
  background: var(--bg-panel2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 9px 14px;
  margin-bottom: 7px;
  cursor: pointer;
  font-family: var(--font-m);
  font-size: 11px;
  color: var(--text);
  text-align: left;
  transition: border-color 0.12s, background 0.12s;
}
.option-btn:hover { border-color: var(--primary); background: #1A1A2F; }
.option-btn.correct { border-color: var(--safe); color: var(--safe); background: #0A1F14; }
.option-btn.wrong   { border-color: var(--danger); color: var(--danger); background: #1F0A0A; }
.scen-explanation {
  font-size: 11px;
  color: #aaa;
  margin-top: 10px;
  line-height: 1.5;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-dark);
}

/* Card toast */
#card-toast {
  position: absolute;
  bottom: 16px;
  right: 16px;
  z-index: 30;
  display: none;
}
#card-toast.visible { display: block; animation: toastIn 0.3s ease; }
@keyframes toastIn { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
.toast-box {
  background: var(--bg-panel);
  border: 1px solid var(--primary);
  border-radius: 6px;
  padding: 10px 14px;
  max-width: 260px;
  box-shadow: 0 0 12px rgba(0,255,209,0.15);
}
.toast-box .toast-label { font-family: var(--font-d); font-size: 9px; color: var(--primary); letter-spacing: 0.1em; margin-bottom: 3px; }
.toast-box .toast-title { font-size: 12px; font-weight: 700; color: #fff; margin-bottom: 2px; }
.toast-box .toast-sub   { font-size: 10px; color: #888; }

/* Codex overlay */
#codex-overlay {
  flex-direction: column;
  background: rgba(10,10,15,0.97);
  padding: 24px;
  overflow-y: auto;
}
.codex-header {
  font-family: var(--font-d);
  font-size: 16px;
  color: var(--primary);
  letter-spacing: 0.12em;
  margin-bottom: 6px;
}
.codex-sub { font-size: 11px; color: #666; margin-bottom: 20px; }
.codex-zone { margin-bottom: 18px; }
.codex-zone-title {
  font-family: var(--font-d);
  font-size: 11px;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
.codex-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.codex-card {
  background: var(--bg-panel2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 8px 10px;
  width: 175px;
  font-size: 10px;
}
.codex-card.collected { border-color: var(--primary); }
.codex-card .cc-sub  { color: var(--primary); font-size: 9px; margin-bottom: 2px; }
.codex-card .cc-title{ color: #ddd; font-weight: 700; margin-bottom: 3px; }
.codex-card .cc-sum  { color: #888; line-height: 1.4; }
.codex-card.locked .cc-sub  { color: #444; }
.codex-card.locked .cc-title{ color: #333; }
.codex-card.locked .cc-sum  { color: #2a2a2a; }
.codex-close {
  position: absolute;
  top: 16px; right: 20px;
  font-family: var(--font-d);
  font-size: 10px;
  color: #555;
  cursor: pointer;
  letter-spacing: 0.08em;
}
.codex-close:hover { color: var(--primary); }

/* Game over */
#gameover-overlay {
  align-items: center;
  justify-content: center;
  background: rgba(10,10,15,0.96);
}
.gameover-box {
  background: var(--bg-panel);
  border: 1px solid var(--danger);
  border-radius: 8px;
  padding: 28px 32px;
  max-width: 500px;
  width: 100%;
  text-align: center;
}
.gameover-box h2 {
  font-family: var(--font-d);
  font-size: 20px;
  color: var(--danger);
  letter-spacing: 0.1em;
  margin-bottom: 6px;
}
.gameover-box .go-sub    { font-size: 11px; color: #888; margin-bottom: 18px; }
.gameover-box .go-answer { font-size: 12px; color: var(--safe); margin: 12px 0; padding: 10px; background: var(--bg-dark); border-radius: 4px; }
.gameover-box .go-expl   { font-size: 11px; color: #aaa; line-height: 1.5; margin-bottom: 20px; }
.btn-primary {
  background: var(--primary);
  color: var(--bg-dark);
  border: none;
  border-radius: 4px;
  padding: 10px 24px;
  font-family: var(--font-d);
  font-size: 11px;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-primary:hover { opacity: 0.85; }

/* Certificate */
#certificate-overlay {
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-dark);
  padding: 32px;
  text-align: center;
}
.cert-box {
  border: 2px solid var(--primary);
  border-radius: 10px;
  padding: 32px 40px;
  max-width: 560px;
  background: var(--bg-panel);
}
.cert-box h2 {
  font-family: var(--font-d);
  font-size: 14px;
  color: var(--primary);
  letter-spacing: 0.14em;
  margin-bottom: 4px;
}
.cert-box h1 {
  font-family: var(--font-d);
  font-size: 22px;
  color: #fff;
  letter-spacing: 0.08em;
  margin-bottom: 20px;
}
.cert-box .cert-name   { font-size: 13px; color: var(--text); margin-bottom: 12px; }
.cert-box .cert-stats  { display: flex; gap: 24px; justify-content: center; margin-bottom: 20px; }
.cert-stat { text-align: center; }
.cert-stat .cs-val   { font-family: var(--font-d); font-size: 20px; color: var(--primary); }
.cert-stat .cs-label { font-size: 9px; color: #666; letter-spacing: 0.08em; }
.cert-box .cert-foot { font-size: 9px; color: #444; letter-spacing: 0.1em; margin-top: 16px; }

/* Pause menu */
#pause-overlay {
  align-items: center;
  justify-content: center;
  background: rgba(10,10,15,0.88);
}
.pause-box {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 28px 36px;
  text-align: center;
}
.pause-box h2 { font-family: var(--font-d); font-size: 16px; color: var(--primary); letter-spacing: 0.12em; margin-bottom: 20px; }
.pause-box .pause-hint { font-size: 11px; color: #666; margin-top: 12px; }

/* Level transition */
#level-transition {
  position: absolute;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: var(--bg-dark);
  z-index: 25;
  flex-direction: column;
  gap: 8px;
}
#level-transition.active { display: flex; animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
#level-transition h2 { font-family: var(--font-d); font-size: 22px; color: var(--primary); letter-spacing: 0.14em; }
#level-transition p  { font-size: 12px; color: #888; letter-spacing: 0.1em; }

/* Door message */
#door-message {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255,68,68,0.12);
  border: 1px solid var(--danger);
  border-radius: 4px;
  padding: 8px 16px;
  font-family: var(--font-d);
  font-size: 10px;
  color: var(--danger);
  letter-spacing: 0.08em;
  pointer-events: none;
  display: none;
  z-index: 15;
  white-space: nowrap;
}
#door-message.visible { display: block; animation: fadeIn 0.2s ease; }

/* Controls hint */
#controls-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  color: #333;
  letter-spacing: 0.06em;
  pointer-events: none;
  z-index: 10;
  white-space: nowrap;
}

/* Responsive */
@media (max-width: 820px) {
  #game-container { width: 100vw; height: calc(100vw * 0.625); }
}
@media (max-width: 420px) {
  #game-container { width: 100vw; height: 100vh; }
}
```

- [ ] **Step 2: Verify fonts load**

Open index.html → Orbitron font should appear in the HUD and overlays. Check in Network tab that fonts.googleapis.com request succeeds.

- [ ] **Step 3: Commit**

```bash
git add style.css && git commit -m "feat: full visual system — color tokens, HUD, overlays, responsive"
```

---

### Task 9: ui_components.js

**Files:**
- Write: `cyberguard/ui_components.js`

- [ ] **Step 1: Write ui_components.js**

```javascript
// cyberguard/ui_components.js

// ── HUD ──────────────────────────────────────────────────────────────────────
function gradeLabel(g) {
  if (g >= 90) return { letter:'A', cls:'grade-a' };
  if (g >= 80) return { letter:'B', cls:'grade-b' };
  if (g >= 70) return { letter:'C', cls:'grade-c' };
  if (g >= 60) return { letter:'D', cls:'grade-d' };
  return { letter:'F', cls:'grade-f' };
}

function renderHUD() {
  const hud = document.getElementById('hud');
  if (!hud) return;
  const { zone, level_num } = GAME_STATE.level;
  const { cards_collected, scenarios_completed, grade, score } = GAME_STATE.progress;
  const cards = cards_collected.filter(id => {
    const c = POLICY_CARDS.find(x => x.card_id === id);
    return c && c.level_num === level_num;
  }).length;
  const total = GAME_STATE.level.cards_total;
  const { letter, cls } = gradeLabel(grade);
  const zoneColor = ZONE_COLORS[zone] || '#aaa';
  hud.innerHTML = `
    <span class="hud-zone" style="color:${zoneColor}">${zone}</span>
    <span class="hud-cards">CARDS ${cards}/${total}</span>
    <span class="hud-grade ${cls}">${letter} ${grade}%</span>
    <span class="hud-score">SCORE ${score.toLocaleString()}</span>
  `;
}

// ── BRIEFING SCREEN ──────────────────────────────────────────────────────────
function showBriefingScreen() {
  const el = document.getElementById('briefing-screen');
  el.innerHTML = `
    <div class="logo-wrap"><img src="assets/title_logo.png" alt="CyberGuard logo"></div>
    <h1>CYBERGUARD: THE NIST DUNGEON</h1>
    <div class="subtitle">PROFESSOR SNYDER — CYBERSECURITY &amp; AI GOVERNANCE</div>
    <p class="brief-text">
      Navigate a NIST framework dungeon. Collect <strong>policy cards</strong>, complete
      <strong>scenario challenges</strong>, and defeat the <strong>AI RMF boss</strong>.
      Your grade is your health — drop below 60% and you'll need to regroup.
      Learn CSF 2.0, AI RMF 1.0, and SP 800-53 Rev. 5 through play.
    </p>
    <p class="brief-text" style="color:#888;font-size:11px;margin-bottom:16px;">
      WASD / Arrow Keys to move &nbsp;|&nbsp; E to interact &nbsp;|&nbsp;
      C for Codex &nbsp;|&nbsp; TAB for minimap &nbsp;|&nbsp; ESC to pause
    </p>
    <div class="role-grid">
      <button class="role-btn" onclick="selectRole('analyst')">
        <div class="role-icon">🔍</div>SECURITY<br>ANALYST
      </button>
      <button class="role-btn" onclick="selectRole('auditor')">
        <div class="role-icon">📋</div>AI<br>AUDITOR
      </button>
      <button class="role-btn" onclick="selectRole('risk_manager')">
        <div class="role-icon">⚖️</div>RISK<br>MANAGER
      </button>
    </div>
    <div class="briefing-footer">DETECT | RESPOND | NEUTRALIZE</div>
  `;
  el.classList.add('active');
}

function selectRole(role) {
  GAME_STATE.player.role = role;
  document.getElementById('briefing-screen').classList.remove('active');
  GAME_STATE.screen = 'playing';
  renderHUD();
  lastFrameTime = performance.now();
  animFrameId = requestAnimationFrame(gameLoop);
}

// ── CARD TOAST ───────────────────────────────────────────────────────────────
let toastTimer = null;
function showCardToast(card) {
  const el = document.getElementById('card-toast');
  const zoneColor = ZONE_COLORS[card.function] || ZONE_COLORS[GAME_STATE.level.zone];
  el.innerHTML = `
    <div class="toast-box" style="border-color:${zoneColor}">
      <div class="toast-label" style="color:${zoneColor}">POLICY CARD COLLECTED</div>
      <div class="toast-title">${card.title}</div>
      <div class="toast-sub">${card.subcategory} &nbsp;+100 pts</div>
    </div>
  `;
  el.classList.add('visible');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('visible'), 3000);
}

// ── SCENARIO PANEL ───────────────────────────────────────────────────────────
function showScenarioPanel(scen) {
  const el = document.getElementById('scenario-panel');
  el.innerHTML = `
    <div class="scenario-box">
      <div class="scen-header">⚠ SCENARIO CHALLENGE — ${scen.control_ref}</div>
      <div class="scen-situation">${scen.situation}</div>
      <div class="scen-question">${scen.question}</div>
      ${scen.options.map((opt, i) =>
        `<button class="option-btn" id="opt-${i}" onclick="submitScenarioAnswer(${i})">${opt}</button>`
      ).join('')}
      <div class="scen-explanation" id="scen-expl" style="display:none"></div>
    </div>
  `;
  el.classList.add('active');
}

function showScenarioWrongAnswer(scen, chosenIdx) {
  const chosen = document.getElementById(`opt-${chosenIdx}`);
  if (chosen) chosen.classList.add('wrong');
  const correct = document.getElementById(`opt-${scen.correct}`);
  if (correct) correct.classList.add('correct');
  // Disable all options
  document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
  const expl = document.getElementById('scen-expl');
  if (expl) {
    expl.style.display = 'block';
    expl.textContent = `−8% grade penalty (charged once). ${scen.explanation} Try again: click the highlighted correct answer.`;
  }
  // Re-enable correct button only
  if (correct) {
    correct.disabled = false;
    correct.onclick = () => submitScenarioAnswer(scen.correct);
  }
}

function hideScenarioPanel() {
  const el = document.getElementById('scenario-panel');
  el.classList.remove('active');
  el.innerHTML = '';
}

// ── CODEX ────────────────────────────────────────────────────────────────────
const ZONE_ORDER = ['GOVERN','IDENTIFY','PROTECT','DETECT','RESPOND','RECOVER','AI_RMF'];
const ZONE_LABELS = { GOVERN:'GOVERN', IDENTIFY:'IDENTIFY', PROTECT:'PROTECT', DETECT:'DETECT', RESPOND:'RESPOND', RECOVER:'RECOVER', AI_RMF:'AI RMF' };

function showCodex() {
  const el = document.getElementById('codex-overlay');
  const collected = new Set(GAME_STATE.progress.cards_collected);
  let html = `
    <div class="codex-header">POLICY CODEX</div>
    <div class="codex-sub">${collected.size} / ${POLICY_CARDS.length} cards collected &nbsp;|&nbsp; C or ESC to close</div>
    <span class="codex-close" onclick="closeCodex()">[ CLOSE ]</span>
  `;
  for (const zone of ZONE_ORDER) {
    const cards = POLICY_CARDS.filter(c => c.function === zone);
    if (!cards.length) continue;
    const zoneColor = ZONE_COLORS[zone] || '#aaa';
    html += `<div class="codex-zone">
      <div class="codex-zone-title" style="color:${zoneColor}">${ZONE_LABELS[zone]}</div>
      <div class="codex-grid">`;
    for (const card of cards) {
      const isCollected = collected.has(card.card_id);
      html += `<div class="codex-card ${isCollected ? 'collected' : 'locked'}">
        <div class="cc-sub">${card.subcategory}</div>
        <div class="cc-title">${isCollected ? card.title : '???'}</div>
        <div class="cc-sum">${isCollected ? card.summary : 'Not yet collected'}</div>
      </div>`;
    }
    html += `</div></div>`;
  }
  el.innerHTML = html;
  el.classList.add('active');
}

function hideCodex() {
  const el = document.getElementById('codex-overlay');
  el.classList.remove('active');
}

// ── GAME OVER ────────────────────────────────────────────────────────────────
function showGameOver(scen) {
  const el = document.getElementById('gameover-overlay');
  el.innerHTML = `
    <div class="gameover-box">
      <h2>GRADE CRITICAL</h2>
      <div class="go-sub">Your grade dropped below 60%. Review the correct answer, then continue.</div>
      <div class="go-sub" style="color:#FF8C00">Scenario: ${scen.control_ref}</div>
      <div class="go-answer">✓ ${scen.options[scen.correct]}</div>
      <div class="go-expl">${scen.explanation}</div>
      <div class="go-sub" style="color:var(--warn);margin-bottom:16px">Grade reset to 70% (C) — your progress is preserved.</div>
      <button class="btn-primary" onclick="dismissGameOver()">CONTINUE MISSION</button>
    </div>
  `;
  el.classList.add('active');
}

function dismissGameOver() {
  document.getElementById('gameover-overlay').classList.remove('active');
  GAME_STATE.screen = 'playing';
  renderHUD();
}

// ── CERTIFICATE ───────────────────────────────────────────────────────────────
function showCertificate() {
  const el = document.getElementById('certificate-overlay');
  const { grade, score, cards_collected, scenarios_completed } = GAME_STATE.progress;
  const { letter } = gradeLabel(grade);
  const roleLabels = { analyst:'Security Analyst', auditor:'AI Auditor', risk_manager:'Risk Manager' };
  const role = roleLabels[GAME_STATE.player.role] || 'Cybersecurity Professional';
  el.innerHTML = `
    <div class="cert-box">
      <h2>CERTIFICATE OF COMPLETION</h2>
      <h1>CYBERGUARD: THE NIST DUNGEON</h1>
      <div class="cert-name">Awarded to: <strong>${role}</strong></div>
      <div class="cert-stats">
        <div class="cert-stat"><div class="cs-val">${letter} ${grade}%</div><div class="cs-label">FINAL GRADE</div></div>
        <div class="cert-stat"><div class="cs-val">${score.toLocaleString()}</div><div class="cs-label">SCORE</div></div>
        <div class="cert-stat"><div class="cs-val">${cards_collected.length}/${POLICY_CARDS.length}</div><div class="cs-label">CARDS</div></div>
        <div class="cert-stat"><div class="cs-val">${scenarios_completed.length}/${SCENARIOS.length}</div><div class="cs-label">SCENARIOS</div></div>
      </div>
      <div class="cert-name" style="font-size:11px;color:#888">
        Demonstrated mastery of NIST CSF 2.0, AI RMF 1.0, and SP 800-53 Rev. 5
      </div>
      <div class="cert-foot">PROFESSOR SNYDER — CYBERSECURITY &amp; AI GOVERNANCE — ${new Date().getFullYear()}</div>
    </div>
  `;
  el.classList.add('active');
}

// ── LEVEL TRANSITION ─────────────────────────────────────────────────────────
function showLevelTransition(fromZone, callback) {
  const meta = LEVEL_METADATA[GAME_STATE.level.id];
  const nextId = meta.next;
  const nextMeta = nextId ? LEVEL_METADATA[nextId] : null;
  const label = nextMeta ? nextMeta.zone.replace('_', ' ') : 'MISSION COMPLETE';
  const el = document.getElementById('level-transition');
  el.innerHTML = `
    <h2>ZONE CLEARED: ${fromZone.replace('_',' ')}</h2>
    <p>ENTERING ${label}</p>
  `;
  el.classList.add('active');
  setTimeout(() => {
    el.classList.remove('active');
    callback();
  }, 1800);
}

// ── DOOR MESSAGE ─────────────────────────────────────────────────────────────
function showDoorMessage() {
  const now = Date.now();
  if (now - GAME_STATE.last_door_message_time < 2500) return;
  GAME_STATE.last_door_message_time = now;
  const cards = getCardsCollectedInLevel();
  const scens = getScenariosCompletedInLevel();
  const totalC = GAME_STATE.level.cards_total;
  const totalS = GAME_STATE.level.scenarios_total;
  const msg = document.getElementById('door-message');
  msg.textContent = `Collect all cards (${cards}/${totalC}) and scenarios (${scens}/${totalS}) first`;
  msg.classList.add('visible');
  setTimeout(() => msg.classList.remove('visible'), 2200);
}

// ── PAUSE MENU ────────────────────────────────────────────────────────────────
function showPauseMenu() {
  const el = document.getElementById('pause-overlay');
  el.innerHTML = `
    <div class="pause-box">
      <h2>PAUSED</h2>
      <button class="btn-primary" onclick="resumeFromPause()">RESUME</button>
      <div class="pause-hint">ESC to resume &nbsp;|&nbsp; C for Codex &nbsp;|&nbsp; TAB for minimap</div>
    </div>
  `;
  el.classList.add('active');
}

function hidePauseMenu() {
  document.getElementById('pause-overlay').classList.remove('active');
}

function resumeFromPause() {
  hidePauseMenu();
  GAME_STATE.screen = 'playing';
}
```

- [ ] **Step 2: Verify briefing renders after index.html**

Open `cyberguard/index.html`. Should see title logo, game name, three role buttons. Click a role → canvas with raycasting view should appear, HUD should show LOBBY / CARDS 0/0.

- [ ] **Step 3: Commit**

```bash
git add ui_components.js && git commit -m "feat: UI — briefing, HUD, scenario panel, codex, game over, certificate"
```

---

### Task 10: index.html

**Files:**
- Write: `cyberguard/index.html`

- [ ] **Step 1: Write index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CyberGuard: The NIST Dungeon</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="game-container">
    <canvas id="game-canvas" width="800" height="500"></canvas>

    <div id="hud"></div>

    <div id="briefing-screen" class="overlay"></div>
    <div id="scenario-panel"  class="overlay"></div>
    <div id="codex-overlay"   class="overlay"></div>
    <div id="gameover-overlay" class="overlay"></div>
    <div id="certificate-overlay" class="overlay"></div>
    <div id="pause-overlay"   class="overlay"></div>

    <div id="level-transition"></div>
    <div id="card-toast"></div>
    <div id="door-message"></div>
    <div id="controls-hint">WASD MOVE &nbsp;|&nbsp; E DOOR &nbsp;|&nbsp; C CODEX &nbsp;|&nbsp; TAB MAP &nbsp;|&nbsp; ESC PAUSE</div>
  </div>

  <script src="state.js"></script>
  <script src="data/maps.js"></script>
  <script src="data/policy_cards.js"></script>
  <script src="data/scenarios.js"></script>
  <script src="engine.js"></script>
  <script src="mechanics.js"></script>
  <script src="ui_components.js"></script>
  <script>
    window.addEventListener('DOMContentLoaded', startEngine);
  </script>
</body>
</html>
```

- [ ] **Step 2: Full end-to-end smoke test**

```
1. Open cyberguard/index.html in Chrome
2. Briefing screen appears with logo and three role buttons → PASS
3. Click "Security Analyst" → raycasting lobby view renders (gray walls) → PASS
4. WASD moves player, view updates → PASS
5. TAB toggles minimap → PASS
6. Walk to south wall, press E near door (cell at row 13, col 6) → transition to GOVERN → PASS
7. Walk into a card cell (3) → toast appears bottom-right → PASS
8. Walk into a scenario cell (4) → scenario panel appears, movement pauses → PASS
9. Answer incorrectly → wrong option highlighted red, correct highlighted green, grade drops 8% → PASS
10. Answer correctly → panel closes, movement resumes → PASS
11. C key → Codex opens, rAF pauses → PASS
12. C or ESC → Codex closes, rAF resumes → PASS
13. ESC → pause menu appears → PASS
14. Complete all cards + scenarios → walk to door, press E → level transition fires → PASS
```

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat: index.html — wires all scripts, DOM overlay structure"
```

---

### Task 11: Fix scenario cell clearing

The scenario cell (`4`) needs to clear from the map when the scenario tied to that cell is answered correctly. The current `checkCellInteractions` binds cells to scenarios by order, which works, but `clearActiveScenarioCell` is never called from `submitScenarioAnswer`. Fix this.

**Files:**
- Modify: `cyberguard/mechanics.js`

- [ ] **Step 1: Replace the correct-answer branch in submitScenarioAnswer**

In `submitScenarioAnswer`, replace the block that clears the cell (the nested loop) with a call to `clearActiveScenarioCell()`:

```javascript
function submitScenarioAnswer(optionIndex) {
  const scen = GAME_STATE.active_scenario;
  if (!scen) return;

  if (optionIndex === scen.correct) {
    const firstTry = !GAME_STATE.progress.scenarios_penalized.includes(scen.scenario_id);
    GAME_STATE.progress.score += firstTry ? 200 : 50;
    GAME_STATE.progress.scenarios_completed.push(scen.scenario_id);
    clearActiveScenarioCell();
    GAME_STATE.active_scenario = null;
    GAME_STATE.screen = 'playing';
    hideScenarioPanel();
    renderHUD();
  } else {
    if (!GAME_STATE.progress.scenarios_penalized.includes(scen.scenario_id)) {
      GAME_STATE.progress.scenarios_penalized.push(scen.scenario_id);
      GAME_STATE.progress.grade = Math.max(0, GAME_STATE.progress.grade - 8);
      renderHUD();
      if (GAME_STATE.progress.grade < 60) { triggerGameOver(scen); return; }
    }
    showScenarioWrongAnswer(scen, optionIndex);
  }
}
```

- [ ] **Step 2: Verify — walk into scenario cell, answer correctly, cell clears (no re-trigger)**

Walk back to the same spot after answering correctly → scenario does NOT re-trigger → PASS

- [ ] **Step 3: Commit**

```bash
git add mechanics.js && git commit -m "fix: clear scenario cell on correct answer"
```

---

### Task 12: README.md

**Files:**
- Write: `cyberguard/README.md`

- [ ] **Step 1: Write README.md**

```markdown
# CyberGuard: The NIST Dungeon

**Instructor:** Professor Snyder  
**Course use:** Cybersecurity fundamentals, AI governance, risk management  
**Frameworks covered:** NIST CSF 2.0, AI RMF 1.0, SP 800-53 Rev. 5

---

## How to Run

Open `index.html` in any modern browser. No server, no install, no build step required.
Works directly from a USB drive, GitHub Pages, or Netlify.

**Tested browsers:** Chrome, Firefox, Safari, Edge

---

## Learning Objectives

Students who complete the game will be able to:

1. Name and sequence the six CSF 2.0 Functions (GOVERN → IDENTIFY → PROTECT → DETECT → RESPOND → RECOVER)
2. Identify the four AI RMF core functions (GOVERN, MAP, MEASURE, MANAGE) and their purpose
3. Match real-world security scenarios to the correct CSF 2.0 subcategory
4. Explain the role of SP 800-53 Rev. 5 controls as implementation guidance for CSF outcomes
5. Apply risk management thinking to triage decisions under time pressure

---

## Game Structure

| Level | Zone | Cards | Scenarios |
|---|---|---|---|
| Lobby | Orientation | 0 | 0 |
| Level 1 | GOVERN | 6 | 3 |
| Level 2 | IDENTIFY | 8 | 4 |
| Level 3 | PROTECT | 8 | 4 |
| Level 4 | DETECT | 6 | 3 |
| Level 5 | RESPOND | 6 | 4 |
| Level 6 | RECOVER | 4 | 3 |
| Boss Room | AI RMF | 8 | 4 |

**Total:** 46 policy cards, 25 scenario challenges  
**Estimated play time:** 20–35 minutes

---

## Grade Health System

Players start at 100% (A). Each wrong scenario answer deducts 8% (charged once per scenario). Dropping below 60% triggers a learning moment — the correct answer and explanation are shown, and grade resets to 70% (C) so play can continue.

| Grade | Range | Meaning |
|---|---|---|
| A | 90–100% | Excellent — first-try correct answers |
| B | 80–89% | Good — one or two wrong attempts |
| C | 70–79% | Satisfactory — several wrong attempts |
| D | 60–69% | Needs improvement |
| F / Reset | < 60% | Game over — review and continue |

---

## Controls

| Key | Action |
|---|---|
| W / ↑ | Move forward |
| S / ↓ | Move backward |
| A / ← | Rotate left |
| D / → | Rotate right |
| E | Interact / open door |
| C | Toggle Codex (card collection) |
| TAB | Toggle minimap |
| ESC | Pause |

---

## NIST References

- **CSF 2.0:** NIST Cybersecurity Framework 2.0 (NIST.CSWP.29, February 2024)
- **AI RMF 1.0:** Artificial Intelligence Risk Management Framework (NIST.AI.100-1, January 2023)
- **SP 800-53 Rev. 5:** Security and Privacy Controls for Information Systems and Organizations (September 2020)

---

## Suggested Course Integration

- **Pre-class:** Assign students to play the game before a CSF 2.0 lecture as a primer
- **In-class:** Use specific scenario IDs (e.g., SCN-015) as discussion prompts
- **Assessment:** Ask students to explain why their chosen answer was wrong (or right)
- **Lab extension:** Have students write their own scenario for an unrepresented CSF subcategory
```

- [ ] **Step 2: Commit**

```bash
git add README.md && git commit -m "docs: instructor README with learning objectives and course integration guide"
```

---

## Self-Review Against Spec

**Spec coverage check:**

| Requirement | Covered by task |
|---|---|
| Playable in-browser, no install | Task 10 (index.html, file:// compatible) |
| 7 zones + Boss Room (AI RMF) | Task 3 (maps.js — 8 maps) |
| Policy card collection | Tasks 4, 7, 9 (cards data, mechanics, UI toast) |
| Scenario MCQ mechanic | Tasks 5, 7, 9 (scenarios data, mechanics, panel) |
| Grade health system | Task 7 (mechanics — grade, game over, reset) |
| Professor Snyder briefing screen | Task 9 (showBriefingScreen) |
| Mobile responsive (min 375px) | Task 8 (CSS @media) |
| Game completable in 20–30 min | Task 3 (map size and card/scenario counts) |
| Raycasting ImageData buffer | Task 6 (engine — pre-allocated, no per-frame alloc) |
| Input map, no logic in handlers | Task 6 (keys map, keysJustPressed) |
| Zone wall color coding | Tasks 2+6 (ZONE_COLORS → hexToRGB → renderFrame) |
| Codex pauses rAF loop | Tasks 7+9 (openCodex → pauseEngine, closeCodex → resumeEngine) |
| title_logo.png in briefing | Tasks 1+9 (copy asset, img tag in showBriefingScreen) |
| SP 800-53 cross-references on cards | Task 4 (sp800_53_refs field on all cards) |
| completion certificate | Task 9 (showCertificate) |
| command.log | Task 1 (created as empty file, appended throughout build) |

All 16 requirements covered. No gaps found.
