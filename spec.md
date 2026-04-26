# CyberGuard: The NIST Dungeon — Project Specification

**Version:** 2.0  
**Date:** 2026-04-26  
**Instructor:** Professor Snyder  
**Audience:** Undergraduate/graduate cybersecurity students  
**Frameworks:** NIST CSF 2.0, AI RMF 1.0, SP 800-53 Rev. 5, SP 800-37 Rev. 2

---

## Purpose

An interactive, browser-based educational game that teaches NIST cybersecurity and AI governance frameworks through play. Players navigate a DOOM-inspired 2.5D dungeon, collect policy cards grounded in real NIST controls, complete scenario-matching challenges, and face a final AI governance boss. The game demonstrates AI agentic capability applied to policy-based game design.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Renderer | HTML5 Canvas (raycasting, `ImageData` pixel writes) |
| Logic | Vanilla JavaScript (ES6+) |
| UI/Overlays | HTML5 + CSS3 (DOM over canvas) |
| Data | JSON (maps, policy cards, scenarios) |
| Fonts | Orbitron, Share Tech Mono (Google Fonts) |
| Build | None — static files, open `index.html` directly |
| Dependencies | None (Google Fonts is only external resource) |

---

## File Structure

```
cyberguard/
├── index.html              # Entry point, canvas, overlay containers
├── style.css               # Color system, panels, HUD, fonts, animations
├── engine.js               # Raycasting renderer, game loop, input map
├── mechanics.js            # Collision, pickups, scenario triggers, door logic, grade system
├── state.js                # GAME_STATE, GAME_CONFIG, level constants
├── ui_components.js        # HUD, Codex, scenario panel, card toast, briefing, game over, certificate
├── data/
│   ├── policy_cards.json   # 46 NIST policy cards (full schema)
│   ├── scenarios.json      # 25 scenario MCQ challenges
│   └── maps/
│       ├── lobby.json
│       ├── level1_govern.json
│       ├── level2_identify.json
│       ├── level3_protect.json
│       ├── level4_detect.json
│       ├── level5_respond.json
│       ├── level6_recover.json
│       └── boss_ai_rmf.json
├── assets/
│   ├── title_logo.png          # Title screen hero image (skull-shield emblem, circuit background)
│   └── nist_logo.svg
├── spec.md                 # This file
├── command.log             # Append-only build command log
└── README.md               # Instructor guide
```

Script load order: `state.js` → `engine.js` → `mechanics.js` → `ui_components.js`

---

## Architecture

### Game Loop

Single `requestAnimationFrame` loop. Each frame:

1. **Input** — Read boolean `keys` map (populated by `keydown`/`keyup` listeners that only flip flags, never execute logic). Zero input lag guaranteed.
2. **Update** — Apply movement using delta-time. Frame-rate-independent.
3. **Render** — Write RGBA bytes to pre-allocated `ImageData` buffer, flush with one `ctx.putImageData()`. No per-column `fillRect`. No per-frame allocations.
4. **UI** — DOM overlays handle independently via CSS; never touch the render loop.

Performance contract: no memory leaks, no growing arrays, no per-frame allocations. FPS must not degrade over session duration.

### Input Map

```javascript
const keys = { w: false, a: false, s: false, d: false, e: false, c: false, esc: false, tab: false };
document.addEventListener('keydown', e => keys[e.key.toLowerCase()] = true);
document.addEventListener('keyup',   e => keys[e.key.toLowerCase()] = false);
```

### Map Grid

2D array. Cell values:
- `0` = empty floor
- `1` = wall
- `2` = door (locked until zone complete)
- `3` = policy card pickup
- `4` = scenario trigger

---

## Level Design

### Progression
```
Lobby → Level 1 (GOVERN) → Level 2 (IDENTIFY) → Level 3 (PROTECT)
      → Level 4 (DETECT) → Level 5 (RESPOND) → Level 6 (RECOVER)
      → Boss Room (AI RMF)
```

This sequence mirrors the CSF 2.0 lifecycle: GOVERN is the overarching foundation, followed by the core operational cycle of IDENTIFY → PROTECT → DETECT → RESPOND → RECOVER.

### Zone Color Coding
| Zone | Wall Color | Hex | Card Count |
|---|---|---|---|
| GOVERN | Gold | `#FFD700` | 6 |
| IDENTIFY | Blue | `#1E90FF` | 8 |
| PROTECT | Green | `#00AA44` | 8 |
| DETECT | Orange | `#FF8C00` | 6 |
| RESPOND | Red | `#FF3333` | 6 |
| RECOVER | Teal | `#00CED1` | 4 |
| AI RMF Boss | Violet | `#9B30FF` | 8 |

### Zone Completion Condition
All policy cards in zone collected AND all scenarios in zone answered correctly before door (cell 2) opens.

### Lobby
- NPC: Professor S. (AI Avatar) — introduces NIST CSF 2.0 and objectives
- Player selects role: Security Analyst, AI Auditor, or Risk Manager
- Controls tutorial

---

## Game Mechanics

### Policy Card Pickup
- **Trigger:** Player position overlaps cell value `3`
- **Action:** Cell cleared → card added to `GAME_STATE.progress.cards_collected` → card toast (bottom-right, 3s auto-dismiss, non-blocking)

### Scenario Trigger
- **Trigger:** Player position overlaps cell value `4`
- **Action:** Movement paused → MCQ panel shown
- **Correct:** Scenario complete, movement resumes, cell cleared
- **Wrong:** Grade −8% (charged once per scenario on first wrong attempt only), explanation shown, retry available immediately
- Cell clears only on correct answer

### Door Interaction
- **Trigger:** Player faces cell value `2`, presses E
- **Zone incomplete:** Message displayed, door remains closed
- **Zone complete:** Level transition → next map loaded

### Codex
- **Trigger:** Press C (any time)
- **Action:** Loop paused, full-screen overlay with all cards grouped by NIST function; locked placeholders for uncollected
- **Dismiss:** C or ESC → loop resumes

---

## Grade Health System

### Scale
| Grade | Range | HUD Color |
|---|---|---|
| A | 90–100% | Green |
| B | 80–89% | Cyan |
| C | 70–79% | Yellow |
| D | 60–69% | Orange |
| F | < 60% | Red (Game Over) |

### Rules
- Starts at 100% (A)
- Wrong answer on scenario: −8% (once per scenario, not per retry)
- Grade only decreases during play
- Correct first-try answers maintain grade, do not restore it

### Score
- Policy card collected: +100 points
- Scenario correct on first try: +200 points
- Scenario correct after retry: +50 points
- Level completed: +500 points bonus
- Boss room cleared: +1,000 points bonus
- Maximum possible score: ~14,100 points (all 46 cards + all 25 first-try correct + all 7 level bonuses + boss)

### Game Over (grade < 60%)
- Player position preserved — no level restart, no full-game restart
- Overlay shows failed scenario with correct answer and explanation
- Grade resets to 70% (C)
- All cards and completed scenarios preserved

### Future Enhancement
Grade restoration mechanic — method TBD (bonus challenges, perfect-answer streaks, remediation tokens, etc.). Scheduled for a follow-up design session.

---

## UI Components

### HUD (always visible)
```
LEVEL: GOVERN  |  CARDS: 2/6  |  GRADE: A 96%  |  SCORE: 800
```
Grade color shifts live with grade value.

### Overlays
| Component | Trigger | Blocks input |
|---|---|---|
| Briefing screen | Game load | Yes (until role selected) |
| Card pickup toast | Card collected | No (auto-dismiss 3s) |
| Scenario panel | Cell 4 entered | Yes (until answered) |
| Codex | C key | Yes (loop paused) |
| Game Over | Grade < 60% | Yes (until dismissed) |
| Completion certificate | Boss room cleared | Yes |

### Visual Identity

**Reference:** `assets/title_logo.png` — skull-on-shield emblem with crossed weapons, molten metal lettering, circuit-board background, ember/fire particles. Tagline: **DETECT | RESPOND | NEUTRALIZE**.

Key visual attributes to carry through:
- Dark metallic background with etched circuit traces (`--bg-dark: #0A0A0F`)
- Orange-red fire/threat accents for danger states and boss room
- Embossed rune-like decorative glyphs in panel borders
- Heavy all-caps display font (Orbitron) for zone titles and HUD
- Monospace font (Share Tech Mono) for policy card text and scenario body

The title screen renders `title_logo.png` centered over `--bg-dark`, with the briefing panel overlaid below.

### Color System
```css
--cyberguard-primary:   #00FFD1;   /* Cyber teal */
--cyberguard-secondary: #7B2FBE;   /* Policy purple */
--cyberguard-danger:    #FF4444;   /* Threat red */
--cyberguard-warn:      #FFB800;   /* Alert amber */
--cyberguard-safe:      #00CC66;   /* Secure green */
--bg-dark:              #0A0A0F;
--bg-panel:             #12121A;
--font-display:         'Orbitron', sans-serif;
--font-primary:         'Share Tech Mono', monospace;
```

---

## Policy Content

### Card Schema
```json
{
  "card_id": "NIST-GV-OC-1",
  "framework": "NIST CSF 2.0",
  "function": "GOVERN",
  "category": "Organizational Context",
  "subcategory": "GV.OC-01",
  "title": "Mission and Stakeholder Expectations",
  "summary": "The organizational mission is understood and informs cybersecurity risk management decisions.",
  "why_it_matters": "Security decisions disconnected from mission lead to misallocated resources.",
  "real_world_example": "A healthcare system's cybersecurity priorities are shaped by patient safety obligations and HIPAA requirements.",
  "sp800_53_refs": ["PM-1", "PM-2"],
  "level": 1,
  "rarity": "common"
}
```

### Scenario Schema
```json
{
  "scenario_id": "SCN-001",
  "level": 1,
  "function": "GOVERN",
  "situation": "A CISO presents a cybersecurity budget request with no connection to business objectives or regulatory requirements. The board asks for justification.",
  "question": "Which CSF 2.0 control most directly addresses the gap?",
  "options": [
    "GV.OC-01 — Mission and stakeholder expectations inform cybersecurity",
    "PR.DS-01 — Data at rest is protected",
    "DE.CM-01 — Networks and assets are monitored",
    "RS.MA-01 — Incident response is executed"
  ],
  "correct_answer": "GV.OC-01 — Mission and stakeholder expectations inform cybersecurity",
  "explanation": "GV.OC-01 requires that the organizational mission and stakeholder expectations inform risk management priorities — connecting security spend to business value."
}
```

---

### Cards: GOVERN Zone (6 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-GV-OC-1 | GV.OC-01 | Mission and Stakeholder Expectations | PM-1, PM-2 |
| NIST-GV-RM-1 | GV.RM-01 | Risk Management Strategy | PM-9, RA-1 |
| NIST-GV-RM-2 | GV.RM-02 | Risk Appetite and Tolerance | PM-9, RA-2 |
| NIST-GV-RR-1 | GV.RR-01 | Organizational Roles and Responsibilities | PM-2, PL-9 |
| NIST-GV-PO-1 | GV.PO-01 | Policy Establishment | PL-1, SA-1 |
| NIST-GV-SC-1 | GV.SC-01 | Supply Chain Risk Management Policy | SA-9, PM-9 |

### Cards: IDENTIFY Zone (8 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-ID-AM-1 | ID.AM-01 | Inventory of Physical Devices | CM-8, PM-5 |
| NIST-ID-AM-2 | ID.AM-02 | Inventory of Software | CM-8, SA-10 |
| NIST-ID-AM-5 | ID.AM-05 | Resource Prioritization | PL-8, SA-17 |
| NIST-ID-AM-7 | ID.AM-07 | Vulnerabilities in Assets Identified | RA-3, SI-2 |
| NIST-ID-RA-1 | ID.RA-01 | Vulnerabilities Identified and Documented | RA-3, RA-5 |
| NIST-ID-RA-3 | ID.RA-03 | Internal and External Threat Intelligence | RA-3, SI-5 |
| NIST-ID-RA-5 | ID.RA-05 | Threats, Vulnerabilities, Likelihoods, Impacts | RA-3, PM-16 |
| NIST-ID-IM-1 | ID.IM-01 | Improvements Identified from Evaluations | PM-6, CA-2 |

### Cards: PROTECT Zone (8 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-PR-AA-1 | PR.AA-01 | Identities and Credentials Managed | IA-1, IA-2 |
| NIST-PR-AA-3 | PR.AA-03 | Users Authenticated to Access Assets | IA-5, IA-8 |
| NIST-PR-DS-1 | PR.DS-01 | Data at Rest Protected | SC-28, MP-2 |
| NIST-PR-DS-2 | PR.DS-02 | Data in Transit Protected | SC-8, SC-28 |
| NIST-PR-PS-1 | PR.PS-01 | Config Management Policies Enforced | CM-7, CM-9 |
| NIST-PR-IR-1 | PR.IR-01 | Networks and Environments Protected | SC-7, SI-3 |
| NIST-PR-AT-1 | PR.AT-01 | Personnel Aware of Cybersecurity Risks | AT-2, PM-13 |
| NIST-PR-AT-2 | PR.AT-02 | Personnel Trained for Roles | AT-3, AT-4 |

### Cards: DETECT Zone (6 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-DE-CM-1 | DE.CM-01 | Networks Monitored for Anomalies | SI-4, CA-7 |
| NIST-DE-CM-2 | DE.CM-02 | Physical Environment Monitored | PE-6, SI-4 |
| NIST-DE-AE-2 | DE.AE-02 | Potentially Adverse Events Analyzed | SI-4, AU-6 |
| NIST-DE-AE-3 | DE.AE-03 | Event Data Aggregated | AU-6, IR-4 |
| NIST-DE-AE-6 | DE.AE-06 | Cybersecurity Incidents Declared | IR-6, IR-8 |
| NIST-DE-AE-7 | DE.AE-07 | Cyber Threat Intelligence Received | SI-5, IR-4 |

### Cards: RESPOND Zone (6 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-RS-MA-1 | RS.MA-01 | Incident Response Plan Executed | IR-4, IR-8 |
| NIST-RS-MA-2 | RS.MA-02 | Incident Reported to Internal Stakeholders | IR-5, IR-6 |
| NIST-RS-AN-3 | RS.AN-03 | Analysis of Incident to Determine Response | IR-4, AU-6 |
| NIST-RS-AN-6 | RS.AN-06 | Actions Performed to Prevent Expansion | IR-4, CM-6 |
| NIST-RS-CO-2 | RS.CO-02 | Coordination with Authorities | IR-6, IR-7 |
| NIST-RS-MI-1 | RS.MI-01 | Incidents Contained | IR-4, CM-6 |

### Cards: RECOVER Zone (4 cards)

| Card ID | Subcategory | Title | SP 800-53 Refs |
|---|---|---|---|
| NIST-RC-RP-1 | RC.RP-01 | Recovery Plan Executed | IR-4, CP-10 |
| NIST-RC-RP-3 | RC.RP-03 | Recovery Activities Communicated | CP-10, IR-4 |
| NIST-RC-RP-5 | RC.RP-05 | Recovery Plan Updated | CP-9, CP-10 |
| NIST-RC-CO-3 | RC.CO-03 | Recovery Communication with Stakeholders | IR-7, IR-8 |

### Cards: AI RMF Boss Room (8 cards)

| Card ID | Subcategory | Title | Notes |
|---|---|---|---|
| NIST-AI-GV-1-1 | GOVERN 1.1 | AI Risk Management Policies Established | AI RMF 1.0 |
| NIST-AI-GV-2-2 | GOVERN 2.2 | Accountability for AI Risk | AI RMF 1.0 |
| NIST-AI-MAP-1-1 | MAP 1.1 | AI System Context and Purpose Documented | AI RMF 1.0 |
| NIST-AI-MAP-3-5 | MAP 3.5 | Human Oversight Processes Defined | AI RMF 1.0 |
| NIST-AI-MS-2-5 | MEASURE 2.5 | AI System Validity and Reliability Demonstrated | AI RMF 1.0 |
| NIST-AI-MS-2-9 | MEASURE 2.9 | AI Model Explainability Documented | AI RMF 1.0 |
| NIST-AI-MG-1-3 | MANAGE 1.3 | High-Priority AI Risks Responded To | AI RMF 1.0 |
| NIST-AI-MG-4-1 | MANAGE 4.1 | Post-Deployment Monitoring Implemented | AI RMF 1.0 |

**Total cards: 46** (6 + 8 + 8 + 6 + 6 + 4 + 8)

---

### Scenarios (25 total)

**GOVERN — 3 scenarios (SCN-001 to SCN-003)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-001 | GV.OC-01 | CISO presents budget with no link to business objectives |
| SCN-002 | GV.RM-02 | Organization has no documented risk tolerance; accepts every risk equally |
| SCN-003 | GV.SC-01 | Cloud vendor has no security review before contract signing |

**IDENTIFY — 4 scenarios (SCN-004 to SCN-007)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-004 | ID.AM-01 | Employee connects unregistered personal USB to company laptop |
| SCN-005 | ID.AM-02 | Team discovers unlicensed software running on production servers |
| SCN-006 | ID.RA-01 | Patch Tuesday passes without any vulnerability scan being run |
| SCN-007 | ID.RA-03 | No external threat intelligence feeds are monitored |

**PROTECT — 4 scenarios (SCN-008 to SCN-011)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-008 | PR.AA-01 | Shared admin credentials used across all servers |
| SCN-009 | PR.DS-01 | Laptop with unencrypted PII is stolen from a car |
| SCN-010 | PR.PS-01 | Default ports and services left enabled on all endpoints |
| SCN-011 | PR.AT-01 | 60% of staff cannot identify a phishing email |

**DETECT — 3 scenarios (SCN-012 to SCN-014)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-012 | DE.CM-01 | Lateral movement goes undetected for 90 days due to no network monitoring |
| SCN-013 | DE.AE-03 | Security team gets flooded with siloed alerts from disconnected tools |
| SCN-014 | DE.AE-06 | Analysts disagree whether a security event qualifies as an incident |

**RESPOND — 4 scenarios (SCN-015 to SCN-018)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-015 | RS.MA-01 | Ransomware hits; no incident response plan exists |
| SCN-016 | RS.AN-03 | Team patches affected system without determining initial access vector |
| SCN-017 | RS.CO-02 | Breach affects 50k customers; regulatory authority not notified |
| SCN-018 | RS.MI-01 | Infected workstation left on network while investigation proceeds |

**RECOVER — 3 scenarios (SCN-019 to SCN-021)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-019 | RC.RP-01 | Systems restored from backup not tested since 2019 |
| SCN-020 | RC.RP-05 | Recovery plan used during incident never updated afterward |
| SCN-021 | RC.CO-03 | Customers learn of data breach from media, not from the company |

**AI RMF Boss Room — 4 scenarios (SCN-022 to SCN-025)**

| ID | Control | Situation Summary |
|---|---|---|
| SCN-022 | GOVERN 1.1 | AI procurement starts with no policy for risk management |
| SCN-023 | MEASURE 2.5 | ML model deployed to production without validation on target population |
| SCN-024 | MEASURE 2.9 | Loan-denial AI cannot explain decisions when legally required |
| SCN-025 | MANAGE 1.3 | High-risk AI outputs are flagged in testing but system is deployed anyway |

---

## Controls

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

## Deployment

| Method | Description |
|---|---|
| Direct file | Open `index.html` in browser |
| GitHub Pages | Push repo, enable Pages |
| Netlify | Drag folder to netlify.com |
| USB drive | Copy folder, open `index.html` |

---

## QA Checklist (AGT-06 Governance Layer)

### Policy Accuracy
- [ ] All CSF 2.0 subcategory IDs verified against NIST.CSWP.29 (Feb 2024)
- [ ] All AI RMF subcategory IDs verified against NIST.AI.100-1 (Jan 2023)
- [x] All SP 800-53 cross-references verified against Rev. 5
- [ ] No control descriptions misrepresent NIST intent
- [ ] Scenario answers align with framework guidance
- [ ] All wrong MCQ answers are plausible but distinguishable

### Educational Integrity
- [ ] Difficulty curve appropriate for undergrad/grad level
- [ ] No oversimplification that creates misconceptions
- [ ] Game completable in 20–35 minutes
- [ ] CSF 2.0 lifecycle order preserved in level sequence (GOVERN → IDENTIFY → PROTECT → DETECT → RESPOND → RECOVER)

### Technical
- [ ] Runs in Chrome, Firefox, Safari, Edge
- [ ] Mobile responsive (min 375px)
- [ ] WCAG 2.1 AA accessibility
- [ ] No external API calls
- [ ] FPS does not degrade over session

### Demonstration Readiness
- [ ] Professor Snyder briefing screen renders
- [ ] All 7 zones + boss accessible
- [ ] Grade health system functional
- [ ] Completion certificate functional

---

## Agent Pipeline (reference)

| Agent | Responsibility | Output |
|---|---|---|
| AGT-01 WorldBuilder | Map design (8 maps) | `maps/*.json` |
| AGT-02 PolicyScribe | NIST content (46 cards, 25 scenarios) | `policy_cards.json`, `scenarios.json` |
| AGT-03 GameMechanicEngineer | Engine, mechanics, state | `engine.js`, `mechanics.js`, `state.js` |
| AGT-04 UIRenderer | Visuals, HUD, CSS | `style.css`, `ui_components.js`, `index.html` |
| AGT-05 NarrativeDirector | Story, NPC dialogue | Embedded in `ui_components.js` |
| AGT-06 QAValidator | Accuracy review | `qa_report.json`, `validation_log.md` |
| AGT-07 DeploymentAgent | Build, packaging | `/dist/cyberguard_v1.0/` |
