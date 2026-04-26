# CyberGuard: The NIST Dungeon — Design Document

**Date:** 2026-04-26  
**Status:** Approved — ready for implementation  
**Source spec:** `cybergaurd.json`

---

## 1. Project Overview

Browser-based 2.5D educational game built with vanilla JavaScript, HTML5 Canvas, and CSS3. Teaches NIST CSF 2.0, AI RMF 1.0, SP 800-53, and SP 800-37 to university students. Designed for Professor Snyder's cybersecurity and AI governance courses. Fully self-contained — no server, no build step, no external APIs (except Google Fonts).

**Success criteria (from spec):**
- Playable in-browser, no install
- 3 levels tied to NIST CSF Functions (Identify, Protect, Detect) + Boss Room (AI RMF)
- Policy card collection mechanic functional
- Scenario MCQ mechanic functional
- Grade health system functional
- Professor Snyder briefing screen on launch
- Mobile responsive (min 375px)
- Game completable in 20–30 minutes

---

## 2. Implementation Strategy

**Option A — Engine-first.** Raycasting engine + input loop + HUD built and validated before UI panels, content, or levels are added. Ensures the performance foundation is solid before building on top of it.

**Build phases:**
1. Engine foundation (`state.js`, `engine.js`, `mechanics.js`)
2. Data files (`maps/*.json`, `policy_cards.json`, `scenarios.json`)
3. UI layer (`index.html`, `style.css`, `ui_components.js`)
4. Integration & narrative (NPC dialogue, level transitions, completion certificate)
5. Deployment packaging (`README.md`, final verification)

---

## 3. Core Architecture & Game Loop

Single `requestAnimationFrame` loop. Each frame executes in order:

1. **Input read** — boolean `keys` map (`{ w, a, s, d, e, c, esc, tab }`) populated by `keydown`/`keyup` listeners that only flip flags. Loop reads the map at the top of every frame. No logic inside event handlers. Guarantees zero input lag regardless of render time.

2. **Update** — Player position and angle updated from `keys` state using delta-time (`dt = currentTime - lastFrameTime`). Movement is frame-rate-independent.

3. **Raycasting render** — One `ImageData` buffer allocated once at startup (never reallocated). Each frame writes RGBA bytes directly into the buffer, flushed with a single `ctx.putImageData()` call. No `fillRect` per column. Ray count = 800 (canvas width). No adaptive quality reduction — performance is maintained through correct implementation, not governors.

4. **UI overlay** — HUD, panels, and overlays are HTML/CSS layered over the canvas (`position: absolute`). They never draw to the canvas and never interact with the render loop.

**Performance contract:** No memory leaks, no growing arrays, no per-frame allocations. FPS should not degrade over time.

---

## 4. File Structure

```
cyberguard/
├── index.html              # Entry point, canvas, overlay containers
├── style.css               # Full color system, panels, HUD, fonts
├── engine.js               # Raycasting renderer, game loop, input map
├── mechanics.js            # Collision, card pickup, scenario trigger, door logic, grade system
├── state.js                # GAME_STATE, GAME_CONFIG, constants
├── ui_components.js        # HUD, Codex, scenario panel, card toast, briefing, game over, certificate
├── data/
│   ├── policy_cards.json   # 30 NIST policy cards
│   ├── scenarios.json      # 15 scenario challenges
│   └── maps/
│       ├── lobby.json
│       ├── level1_identify.json
│       ├── level2_protect.json
│       ├── level3_detect.json
│       └── boss_ai_rmf.json
├── assets/
│   └── nist_logo.svg
├── spec.md                 # Comprehensive project specification
├── command.log             # Append-only build command log
└── README.md               # Instructor guide for Professor Snyder
```

Script load order in `index.html`: `state.js` → `engine.js` → `mechanics.js` → `ui_components.js`

Assets (wall textures, sprites, enemies) rendered programmatically on canvas as colored geometric shapes — no binary image files required.

---

## 5. Map & Level Design

**Grid cell values:**
- `0` = empty floor
- `1` = wall
- `2` = door (requires zone completion to pass)
- `3` = policy card pickup
- `4` = scenario trigger

**Level progression:**
```
Lobby → Level 1 (GOVERN) → Level 2 (IDENTIFY) → Level 3 (PROTECT)
      → Level 4 (DETECT) → Level 5 (RESPOND) → Level 6 (RECOVER)
      → Boss Room (AI RMF)
```

Sequence mirrors CSF 2.0 lifecycle: GOVERN is the overarching foundation, followed by the core operational cycle.

**Zone color coding (wall tones):**
- GOVERN: Gold (`#FFD700`)
- IDENTIFY: Blue (`#1E90FF`)
- PROTECT: Green (`#00AA44`)
- DETECT: Orange (`#FF8C00`)
- RESPOND: Red (`#FF3333`)
- RECOVER: Teal (`#00CED1`)
- AI RMF Boss: Violet (`#9B30FF`)

**Zone completion condition:** All policy cards collected AND all scenarios passed in the current zone before door opens.

---

## 6. Game Mechanics

### Policy Card Pickup (cell = 3)
- Trigger: player position overlaps cell
- Action: cell cleared from map → card added to `GAME_STATE.progress.cards_collected` → card toast overlay shown (auto-dismiss 3 seconds, bottom-right, non-blocking)

### Scenario Trigger (cell = 4)
- Trigger: player position overlaps cell
- Action: movement paused → scenario MCQ panel rendered → player selects and submits
- Correct: scenario marked complete, movement resumes, cell cleared
- Wrong: `-8%` grade penalty (charged once per scenario, not per retry), explanation shown, player may retry immediately
- Cell is only cleared on correct answer

### Door / Level Transition (cell = 2, press E)
- If zone incomplete: brief message "Collect all policy cards and complete all scenarios first"
- If zone complete: level transition animation → next map loaded

### Codex (press C)
- Pauses `requestAnimationFrame` loop
- Full-screen DOM overlay: cards grouped by NIST function (IDENTIFY / PROTECT / DETECT / AI RMF), collected cards shown in full, uncollected shown as locked placeholders
- Dismissed with C or ESC → loop resumes

---

## 7. Grade Health System

| Grade | Range | HUD Color |
|---|---|---|
| A | 90–100% | Green |
| B | 80–89% | Cyan |
| C | 70–79% | Yellow |
| D | 60–69% | Orange |
| F / Game Over | < 60% | Red |

**Rules:**
- Player starts at 100% (A)
- Wrong answer on a scenario: −8% (charged once per scenario on first wrong attempt)
- Grade only decreases during normal play — no restoration mechanic in v1.0
- Correct first-try answers maintain grade, do not restore it

**Scoring:**
- Card collected: +100 pts | Scenario first-try correct: +200 pts | Scenario retry correct: +50 pts
- Level complete bonus: +500 pts | Boss cleared: +1000 pts | Maximum: 5000 pts

**Game Over (grade < 60%):**
- Player position unchanged — no level restart, no full-game restart
- Brief overlay shows the failed scenario and the correct answer with explanation (learning moment)
- Grade resets to 70% (C) — enough to continue without trivializing the failure
- All collected cards and completed scenarios are preserved
- Overlay dismissed automatically after explanation is shown

**Future enhancement:** Grade restoration mechanic — method TBD (e.g., bonus challenges, perfect-answer streaks, collectible "remediation tokens"). To be designed in a follow-up session.

---

## 8. UI Layer

All UI is DOM overlaid on canvas (`position: absolute`). Never drawn to canvas. CSS handles animations.

### HUD (always visible, top bar)
```
LEVEL: IDENTIFY  |  CARDS: 3/8  |  GRADE: B 84%  |  SCORE: 1200
```
Grade letter and percentage color-shift live as grade degrades.

### Overlays (toggled via CSS class)
| Overlay | Trigger | Blocks input? |
|---|---|---|
| Briefing screen | Game load | Yes — until role selected |
| Card pickup toast | Card collected | No — auto-dismiss 3s |
| Scenario panel | Cell 4 entered | Yes — until answered |
| Codex | C key | Yes — loop paused |
| Game Over | Grade < 60% | Yes — until dismissed |
| Completion certificate | Boss room cleared | Yes |

### Color System
```css
--cyberguard-primary: #00FFD1;
--cyberguard-secondary: #7B2FBE;
--cyberguard-danger: #FF4444;
--cyberguard-warn: #FFB800;
--cyberguard-safe: #00CC66;
--bg-dark: #0A0A0F;
--bg-panel: #12121A;
--font-primary: 'Share Tech Mono', monospace;
--font-display: 'Orbitron', sans-serif;
```

Fonts loaded from Google Fonts (only external dependency). For offline use: bundle as base64 in CSS.

---

## 9. Policy Content Summary

**46 policy cards across 7 zones** (sourced from NIST.CSWP.29 Feb 2024 and NIST.AI.100-1 Jan 2023):
- Level 1 GOVERN: 6 cards (GV.OC-01, GV.RM-01/02, GV.RR-01, GV.PO-01, GV.SC-01)
- Level 2 IDENTIFY: 8 cards (ID.AM-01/02/05/07, ID.RA-01/03/05, ID.IM-01)
- Level 3 PROTECT: 8 cards (PR.AA-01/03, PR.DS-01/02, PR.PS-01, PR.IR-01, PR.AT-01/02)
- Level 4 DETECT: 6 cards (DE.CM-01/02, DE.AE-02/03/06/07)
- Level 5 RESPOND: 6 cards (RS.MA-01/02, RS.AN-03/06, RS.CO-02, RS.MI-01)
- Level 6 RECOVER: 4 cards (RC.RP-01/03/05, RC.CO-03)
- Boss Room AI RMF: 8 cards (GOVERN-1.1/2.2, MAP-1.1/3.5, MEASURE-2.5/2.9, MANAGE-1.3/4.1)

Each card includes SP 800-53 Rev. 5 cross-references.

**25 scenarios:** 3-4 per zone, MCQ format, each tied to a specific NIST control, with situation, 4 options, correct answer, and explanation.

Full card schema and scenario schema defined in `spec.md`.

---

## 10. Player Roles

Selected on briefing screen, stored in `GAME_STATE.player.role`:
- `analyst` — Security Analyst
- `auditor` — AI Auditor
- `risk_manager` — Risk Manager

Roles are cosmetic/narrative only. They do not affect mechanics, grade system, or win conditions.

---

## 11. Controls

| Key | Action |
|---|---|
| W / ↑ | Move forward |
| S / ↓ | Move backward |
| A / ← | Rotate left |
| D / → | Rotate right |
| E | Interact / open door |
| C | Toggle Codex |
| ESC | Pause menu |
| TAB | Toggle minimap |

---

## 12. Deployment

- Open `index.html` directly in any browser — no server required
- GitHub Pages, Netlify, or USB drive all work as-is
- Zero external dependencies beyond Google Fonts
- Target browsers: Chrome, Firefox, Safari, Edge
- Mobile responsive: min 375px width

---

## 13. Documentation

- **`spec.md`** — comprehensive specification (this document, project root version)
- **`command.log`** — append-only log of every command/agent invocation during the build. Format: `[YYYY-MM-DD HH:MM] [PHASE] description`
- **`README.md`** — instructor guide for Professor Snyder (learning objectives, suggested use, NIST references)
