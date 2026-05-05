# Server Rack Foe — FloorDoom Campus Map
**Date:** 2026-05-05
**Scope:** Campus level only (`level_num: 8`, `floordoom_level`). NIST levels 1–7 untouched.

---

## Overview

A rogue datacenter server rack slides through the halls of the FloorDoom campus map. When it catches the player, a mandatory multi-phase Arista EOS terminal challenge appears. The player must SSH into the rack using its rogue IP, then assign a valid host IP within a given subnet using Arista configuration syntax. Two stairwell access panels (one per staircase) track correctly-configured IPs. Unlocking one panel (3 correct IPs) allows descent to the next floor.

---

## Architecture & File Separation

### New files
| File | Purpose |
|---|---|
| `cyberguard/data/subnet_challenges.js` | 6 rack challenge definitions (3 per panel) |

### Modified files
| File | Change |
|---|---|
| `cyberguard/data/npc_data.js` | Add `RACK` to `NPC_TYPES`; add 6 rack entries to `NPC_SPAWNS` with `level_num: 8` |
| `cyberguard/ui_components.js` | Add `showSubnetChallenge()`, `hideSubnetChallenge()`, `showPanelOverlay()`, `hidePanelOverlay()`, phase state machine |
| `cyberguard/mechanics.js` | Cell `11` interaction, rack catch → subnet challenge, rack wander behavior |
| `cyberguard/state.js` | Add `active_subnet_challenge`, `active_subnet_challenge_pos`, `subnet_close_time`, `panel_ips` |
| `cyberguard/data/maps_floordoom.js` | Add cell `11` (panel) adjacent to existing exit `2` cells near each staircase |
| `cyberguard/index.html` | Add `<script src="data/subnet_challenges.js">` before `mechanics.js` |
| `cyberguard/style.css` | Styles for Arista subnet terminal and panel overlay |

### `GAME_STATE` additions
```js
active_subnet_challenge: null,
active_subnet_challenge_pos: null,
subnet_close_time: 0,
panel_ips: {
  left:  [null, null, null],  // index matches rack order; null = not yet attempted
  right: [null, null, null],
},
```

Each slot stores `{ ip: '10.30.0.15/26', valid: true/false }` after a completed challenge. `null` = rack not yet encountered or challenge was closed before `write memory`.

---

## Server Rack NPC

### Type definition (`NPC_TYPES`)
```js
RACK: { label: 'Rogue Server Rack', icon: '🗄', color: '#00FF41', threat: 'NETWORK THREAT' }
```

### Wander behavior
Racks do not follow fixed patrol waypoints. On spawn, each rack picks a random floor tile as a target and moves toward it. On arrival it picks a new random target. This is distinct from existing `patrol` logic — a new `wander` branch in `updateNPCs`.

Speed: faster than standard patrol NPCs, same as chase speed. No `alerted` state — transitions directly from `wander` to `chasing` when player enters vision range.

### FT immunity
Racks are immune to the FT newspaper (same as ARIA). Player can run but must eventually be caught to progress. The close button on the challenge keeps encounters non-coercive — player may walk away and retry later.

### Rogue IP
Each rack has a `rogue_ip` in the `169.254.x.x` APIPA range (link-local, clearly wrong). Displayed on HUD as a small indicator when rack is within vision range:

```
🗄 ROGUE: 169.254.12.44
```

Disappears when rack moves out of range.

### Catch behavior
When rack reaches `NPC_CATCH_RANGE` of player → `showSubnetChallenge(rack)`. `GAME_STATE.screen` = `'subnet_challenge'`. No grade penalty for being caught. On challenge close (red X, no `write memory`) → rack teleports to random floor tile, screen back to `'playing'`, `subnet_close_time` set (400ms cooldown prevents immediate re-catch).

### NPC spawn entries (in `NPC_SPAWNS`, `level_num: 8`)
6 entries — `panel: 'left'` or `panel: 'right'`, `slot: 0|1|2`, each with unique `challenge_id`.

---

## Subnet Challenge UI

### Visual
Reuses macOS-style terminal frame (same CSS classes as terminal panel) but is a separate DOM element (`#subnet-panel`) and separate JS functions. Title bar: `admin@<rack_label> — Arista EOS`.

### Phase state machine
Stored in `GAME_STATE.active_subnet_challenge.phase` (string):

| Phase | Player types | Validation |
|---|---|---|
| `ssh` | `ssh admin@<rogue_ip>` | IP must match rack's `rogue_ip` exactly |
| `configure` | `configure terminal` or `conf t` | either accepted |
| `interface` | `interface Management0` | case-insensitive match |
| `ip_assign` | `ip address <x.x.x.x/prefix>` | valid host in subnet (not network, not broadcast) |
| `write` | `write memory` or `wr mem` | either accepted |

Wrong input at any phase: `% Invalid input detected.` — player can retry that phase. No phase regression.

### IP validation
On `ip_assign` phase: parse IP and prefix from input, confirm IP falls within `valid_range` of the challenge. Any valid host address accepted. If outside range: terminal shows `% Configuration accepted.` (silent wrong answer). Panel slot records `{ ip, valid: false }`.

### Banner
```
⚠  ROGUE DEVICE DETECTED — <situation>
TASK ▶  Assign a valid host IP within the correct subnet.
Network: <subnet>  —  determine the valid host range.
```

### Completion
On `write memory`: terminal shows `Copy complete, [OK]`. A `[ CONTINUE ]` button appears. Clicking it calls `hideSubnetChallenge()`, which records the IP to the correct panel slot and sets screen back to `'playing'`.

### Close button
Red X is present and functional. Closing before `write memory` abandons the challenge — no panel entry written. Rack teleports away; `subnet_close_time` set.

---

## Panel Cell (type 11)

### Placement
Cell `11` placed adjacent to (or replacing one of) the `2` exit cells near each staircase on the south wall of `maps_floordoom.js`. Two panels — `left` staircase, `right` staircase.

### Interaction
Player steps on cell `11` → `showPanelOverlay(side)` where `side` is `'left'` or `'right'`.

### Display
```
┌─ STAIRWELL ACCESS PANEL (LEFT) ──────────────┐
│  Configure 3 server racks to unlock.          │
│                                               │
│  Slot 1:  10.30.0.15/26                       │
│  Slot 2:  [ not configured ]                  │
│  Slot 3:  [ not configured ]                  │
│                                               │
│  STATUS: LOCKED                               │
│                                  [ CLOSE ]    │
└───────────────────────────────────────────────┘
```

- Slots show entered IPs as plain text — no ✓/✗ per slot until all 3 are filled.
- All 3 filled + all valid → `STATUS: UNLOCKED`, adjacent exit cell `2` becomes passable.
- All 3 filled + any invalid → `STATUS: LOCKED`, all 3 IPs shown so player can see what was entered and re-encounter the relevant rack.
- Re-encountering a rack after a failed slot overwrites that slot.

### Unlock logic
Panel unlock check runs immediately when a subnet challenge completes (inside `hideSubnetChallenge()`). If `panel_ips[side]` has 3 entries all with `valid: true`, mark that staircase's exit door passable in the map. Opening the panel overlay is read-only — it never triggers or blocks unlock.

---

## FloorDoom Completion Condition

Current condition: all AP challenges + terminal challenges completed.
New condition: **at least one panel (`left` OR `right`) fully unlocked**. AP and terminal challenges remain accessible and award score/grade but are not required to descend.

The `isZoneComplete()` function in `mechanics.js` will gain a campus-specific branch checking `panel_ips`.

---

## `subnet_challenges.js` Data Structure

```js
const SUBNET_CHALLENGES = [
  {
    challenge_id: 'rack_left_1',
    panel: 'left',
    slot: 0,
    rack_label: 'SRV-3A',
    rogue_ip: '169.254.12.44',
    situation: 'Unregistered rack broadcasting on VLAN 30 — no management IP assigned.',
    subnet: '10.30.0.0/26',
    valid_range: ['10.30.0.1', '10.30.0.62'],
    broadcast: '10.30.0.63',
    arista_interface: 'Management0',
    explanation: '/26 = 255.255.255.192 — 62 usable hosts. Valid range 10.30.0.1–10.30.0.62.',
  },
  // ... 5 more entries
];
```

### 6 subnets — varied prefix lengths

| Rack | Panel | Subnet | Prefix | Usable hosts |
|---|---|---|---|---|
| SRV-3A | left | 10.30.0.0 | /26 | 62 |
| SRV-3B | left | 172.16.4.0 | /28 | 14 |
| SRV-3C | left | 192.168.10.0 | /27 | 30 |
| SRV-3D | right | 10.20.8.0 | /25 | 126 |
| SRV-3E | right | 172.31.0.0 | /29 | 6 |
| SRV-3F | right | 192.168.50.0 | /24 | 254 |

Covers /24–/29. Floors 2 and 1 can introduce /30, VLSMs, and named subnets.

---

## Out of Scope (this spec)

- Floors 2 and 1 maps and their rack challenges
- Additional NPC types for lower floors
- Scoring/grade integration for subnet challenges (to be decided per floor)
- Multiplayer or shared panel state
