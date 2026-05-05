# Server Rack Foe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add rogue server rack NPCs to the FloorDoom campus map with Arista EOS subnetting challenges and two stairwell access panels that unlock when 3 valid IPs are configured per side.

**Architecture:** Campus-only additions. Six RACK NPCs wander the map, each linked to a unique subnetting challenge. When caught, a multi-phase Arista terminal appears. IP entries accumulate in `GAME_STATE.panel_ips`; `isZoneComplete()` checks if either panel has 3 valid entries. All new code isolated to campus (`level_num: 8`); NIST levels 1–7 untouched.

**Tech Stack:** Vanilla JS, no build step. Browser-only. Open `cyberguard/index.html` directly to test.

---

## File Map

| File | Action |
|---|---|
| `cyberguard/data/subnet_challenges.js` | **CREATE** — 6 rack challenge definitions |
| `cyberguard/data/npc_data.js` | **MODIFY** — add RACK type + 6 spawn entries |
| `cyberguard/data/maps_floordoom.js` | **MODIFY** — place cell 11 panels at row 21 cols 5 and 56 |
| `cyberguard/state.js` | **MODIFY** — add `active_subnet_challenge`, `subnet_close_time`, `panel_ips` to GAME_STATE |
| `cyberguard/index.html` | **MODIFY** — add `<script>` tag + two new overlay divs |
| `cyberguard/engine.js` | **MODIFY** — RACK sprite, cell 11 in `canMoveTo` + `renderSprites`, update cell type comment |
| `cyberguard/mechanics.js` | **MODIFY** — wander behavior, FT immunity, `loadLevel`, `isZoneComplete`, `checkCellInteractions`, `handleEscKey`, `triggerRackEncounter`, `returnToLobby` |
| `cyberguard/ui_components.js` | **MODIFY** — `showSubnetChallenge`, `hideSubnetChallenge`, `submitSubnetCommand`, `showPanelOverlay`, `hidePanelOverlay`, `renderHUD` rogue IP |
| `cyberguard/style.css` | **MODIFY** — styles for subnet panel and panel overlay |

---

## Task 1: GAME_STATE additions (`state.js`)

**Files:**
- Modify: `cyberguard/state.js`

- [ ] **Step 1: Add new fields to GAME_STATE**

In `cyberguard/state.js`, find the block ending with:
```js
  terminal_close_time: 0,
};
```
Replace with:
```js
  terminal_close_time: 0,
  active_subnet_challenge: null,
  subnet_close_time: 0,
  panel_ips: {
    left:  [null, null, null],
    right: [null, null, null],
  },
};
```

- [ ] **Step 2: Update screen state comment**

Find:
```js
  screen: 'briefing', // 'briefing'|'playing'|'codex'|'scenario'|'campus_challenge'|'terminal_challenge'|'gameover'|'certificate'|'paused'|'transition'
```
Replace with:
```js
  screen: 'briefing', // 'briefing'|'playing'|'codex'|'scenario'|'campus_challenge'|'terminal_challenge'|'subnet_challenge'|'panel'|'gameover'|'certificate'|'paused'|'transition'
```

- [ ] **Step 3: Commit**
```bash
git add cyberguard/state.js
git commit -m "feat: add subnet challenge and panel_ips state to GAME_STATE"
```

---

## Task 2: Subnet challenge data (`subnet_challenges.js`)

**Files:**
- Create: `cyberguard/data/subnet_challenges.js`

- [ ] **Step 1: Create the file with all 6 challenges**

```js
// cyberguard/data/subnet_challenges.js
// Campus-only (level_num: 8) — Arista EOS subnetting challenges.
// One challenge per RACK NPC. panel: 'left'|'right', slot: 0|1|2.

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
    explanation: '/26 = 255.255.255.192 — 62 usable hosts. Valid range 10.30.0.1–10.30.0.62.',
  },
  {
    challenge_id: 'rack_left_2',
    panel: 'left',
    slot: 1,
    rack_label: 'SRV-3B',
    rogue_ip: '169.254.33.17',
    situation: 'Rogue rack found on server room floor — management interface unconfigured.',
    subnet: '172.16.4.0/28',
    valid_range: ['172.16.4.1', '172.16.4.14'],
    broadcast: '172.16.4.15',
    explanation: '/28 = 255.255.255.240 — 14 usable hosts. Valid range 172.16.4.1–172.16.4.14.',
  },
  {
    challenge_id: 'rack_left_3',
    panel: 'left',
    slot: 2,
    rack_label: 'SRV-3C',
    rogue_ip: '169.254.7.200',
    situation: 'Rack detected with link-local address — must be assigned to the lab subnet.',
    subnet: '192.168.10.0/27',
    valid_range: ['192.168.10.1', '192.168.10.30'],
    broadcast: '192.168.10.31',
    explanation: '/27 = 255.255.255.224 — 30 usable hosts. Valid range 192.168.10.1–192.168.10.30.',
  },
  {
    challenge_id: 'rack_right_1',
    panel: 'right',
    slot: 0,
    rack_label: 'SRV-3D',
    rogue_ip: '169.254.88.1',
    situation: 'Orphaned rack in east wing — no VLAN assignment, management IP missing.',
    subnet: '10.20.8.0/25',
    valid_range: ['10.20.8.1', '10.20.8.126'],
    broadcast: '10.20.8.127',
    explanation: '/25 = 255.255.255.128 — 126 usable hosts. Valid range 10.20.8.1–10.20.8.126.',
  },
  {
    challenge_id: 'rack_right_2',
    panel: 'right',
    slot: 1,
    rack_label: 'SRV-3E',
    rogue_ip: '169.254.55.99',
    situation: 'Compact rack unit pulled from storage — needs IP on the IoT management segment.',
    subnet: '172.31.0.0/29',
    valid_range: ['172.31.0.1', '172.31.0.6'],
    broadcast: '172.31.0.7',
    explanation: '/29 = 255.255.255.248 — 6 usable hosts. Valid range 172.31.0.1–172.31.0.6.',
  },
  {
    challenge_id: 'rack_right_3',
    panel: 'right',
    slot: 2,
    rack_label: 'SRV-3F',
    rogue_ip: '169.254.101.5',
    situation: 'Datacenter rack with factory default config — assign to production management subnet.',
    subnet: '192.168.50.0/24',
    valid_range: ['192.168.50.1', '192.168.50.254'],
    broadcast: '192.168.50.255',
    explanation: '/24 = 255.255.255.0 — 254 usable hosts. Valid range 192.168.50.1–192.168.50.254.',
  },
];
```

- [ ] **Step 2: Commit**
```bash
git add cyberguard/data/subnet_challenges.js
git commit -m "feat: add subnet challenge data for 6 campus server racks"
```

---

## Task 3: RACK NPC type and spawns (`npc_data.js`)

**Files:**
- Modify: `cyberguard/data/npc_data.js`

- [ ] **Step 1: Add RACK to NPC_TYPES**

Find:
```js
  BOSS:  { label:'ARIA — Autonomous Risk Intelligence Agent', icon:'🤖', color:'#FF00FF', threat:'FINAL THREAT' },
};
```
Replace with:
```js
  BOSS:  { label:'ARIA — Autonomous Risk Intelligence Agent', icon:'🤖', color:'#FF00FF', threat:'FINAL THREAT' },
  RACK:  { label:'Rogue Server Rack', icon:'🗄', color:'#00FF41', threat:'NETWORK THREAT' },
};
```

- [ ] **Step 2: Add 6 RACK spawn entries at end of NPC_SPAWNS, before the closing `];`**

Find:
```js
  { id:'ghost_board', type:'BOARD', level_num:7, ghost:true, x:13.5, y:15.5, patrol:[[13.5,15.5]] },
];
```
Replace with:
```js
  { id:'ghost_board', type:'BOARD', level_num:7, ghost:true, x:13.5, y:15.5, patrol:[[13.5,15.5]] },

  //    CAMPUS — Rogue server racks (level_num:8). No patrol — wander behavior in updateNPCs.
  { id:'rack_left_1',  type:'RACK', level_num:8, x:4.5,  y:2.5,  patrol:[[4.5,2.5]],   challenge_id:'rack_left_1',  panel:'left',  slot:0 },
  { id:'rack_left_2',  type:'RACK', level_num:8, x:20.5, y:2.5,  patrol:[[20.5,2.5]],  challenge_id:'rack_left_2',  panel:'left',  slot:1 },
  { id:'rack_left_3',  type:'RACK', level_num:8, x:44.5, y:6.5,  patrol:[[44.5,6.5]],  challenge_id:'rack_left_3',  panel:'left',  slot:2 },
  { id:'rack_right_1', type:'RACK', level_num:8, x:14.5, y:9.5,  patrol:[[14.5,9.5]],  challenge_id:'rack_right_1', panel:'right', slot:0 },
  { id:'rack_right_2', type:'RACK', level_num:8, x:35.5, y:5.5,  patrol:[[35.5,5.5]],  challenge_id:'rack_right_2', panel:'right', slot:1 },
  { id:'rack_right_3', type:'RACK', level_num:8, x:56.5, y:5.5,  patrol:[[56.5,5.5]],  challenge_id:'rack_right_3', panel:'right', slot:2 },
];
```

- [ ] **Step 3: Commit**
```bash
git add cyberguard/data/npc_data.js
git commit -m "feat: add RACK NPC type and 6 campus spawn entries"
```

---

## Task 4: Panel cells in campus map (`maps_floordoom.js`)

**Files:**
- Modify: `cyberguard/data/maps_floordoom.js`

- [ ] **Step 1: Update the cell type comment at top of file**

Find:
```js
// Cell types: 0=floor  1=wall  2=exit door  3=policy card  5=FT pickup  8=AP scenario (campus only)  9=PC workstation (terminal challenge)
```
Replace with:
```js
// Cell types: 0=floor  1=wall  2=exit door  3=policy card  5=FT pickup  8=AP scenario (campus only)  9=PC workstation (terminal challenge)  10=hint token  11=stairwell access panel
```

- [ ] **Step 2: Place left panel cell at row 21, col 5**

Row 21 is the 22nd array row (0-indexed). Find this exact line:
```js
    [1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,5,1,0,0,1],
```
Replace with (col 5 changed from `0` to `11`):
```js
    [1,0,0,1,0,11,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,5,1,0,0,1],
```

- [ ] **Step 3: Place right panel cell at row 21, col 56**

The same line (just edited) now needs col 56 changed from `0` to `11`:
```js
    [1,0,0,1,0,11,0,1,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,11,5,1,0,0,1],
```

- [ ] **Step 4: Commit**
```bash
git add cyberguard/data/maps_floordoom.js
git commit -m "feat: place stairwell access panel cells (11) in campus map"
```

---

## Task 5: HTML infrastructure (`index.html`)

**Files:**
- Modify: `cyberguard/index.html`

- [ ] **Step 1: Add subnet_challenges.js script tag**

Find:
```html
  <script src="data/terminal_challenges.js"></script>
```
Replace with:
```html
  <script src="data/terminal_challenges.js"></script>
  <script src="data/subnet_challenges.js"></script>
```

- [ ] **Step 2: Add new overlay div elements**

Find:
```html
    <div id="terminal-panel"  class="overlay"></div>
```
Replace with:
```html
    <div id="terminal-panel"  class="overlay"></div>
    <div id="subnet-panel"    class="overlay"></div>
    <div id="panel-overlay"   class="overlay"></div>
```

- [ ] **Step 3: Commit**
```bash
git add cyberguard/index.html
git commit -m "feat: add subnet-panel and panel-overlay DOM elements"
```

---

## Task 6: Engine — RACK sprite + cell 11 passable + render (`engine.js`)

**Files:**
- Modify: `cyberguard/engine.js`

- [ ] **Step 1: Update cell type comment at top of engine.js**

Find:
```js
// Cell types: 0=floor 1=wall 2=exit 3=card 4=scenario 5=FT pickup 6=torch 7=hint poster 8=AP (campus scenario) 9=PC workstation (terminal challenge)
```
Replace with:
```js
// Cell types: 0=floor 1=wall 2=exit 3=card 4=scenario 5=FT pickup 6=torch 7=hint poster 8=AP (campus scenario) 9=PC workstation (terminal challenge) 10=hint token 11=stairwell panel
```

- [ ] **Step 2: Add cell 11 to `canMoveTo`**

Find:
```js
function canMoveTo(map, x, y) {
  const c=getCell(map,x,y); return c===0||c===3||c===4||c===5||c===6||c===7||c===8||c===9||c===10;
}
```
Replace with:
```js
function canMoveTo(map, x, y) {
  const c=getCell(map,x,y); return c===0||c===3||c===4||c===5||c===6||c===7||c===8||c===9||c===10||c===11;
}
```

- [ ] **Step 3: Add cell 11 to renderSprites map scan**

Find:
```js
    if (cell!==3&&cell!==4&&cell!==5&&cell!==7&&cell!==8&&cell!==9&&cell!==10) continue;
```
Replace with:
```js
    if (cell!==3&&cell!==4&&cell!==5&&cell!==7&&cell!==8&&cell!==9&&cell!==10&&cell!==11) continue;
```

- [ ] **Step 4: Add cell 11 to SPRITE_SCALE**

Find:
```js
  const SPRITE_SCALE = { 3:0.5, 4:0.55, 5:0.4, 6:0.45, 7:0.65, 8:0.6, 9:0.65, 10:0.50 };
```
Replace with:
```js
  const SPRITE_SCALE = { 3:0.5, 4:0.55, 5:0.4, 6:0.45, 7:0.65, 8:0.6, 9:0.65, 10:0.50, 11:0.55 };
```

- [ ] **Step 5: Add SPRITE_TEXTURES[11] (stairwell panel sprite)**

Find the block ending with:
```js
    SPRITE_TEXTURES[10] = tex;
  }

  // Cell 8 — AP fallback
```
Insert after `SPRITE_TEXTURES[10] = tex;  }`:
```js

  // Cell 11 — Stairwell access panel: dark keypad with green LED bar
  {
    const tex = new Uint8ClampedArray(S * S * 4);
    function sp11(x,y,r,g,b,a=255){if(x<0||x>=S||y<0||y>=S)return;const i=(y*S+x)*4;tex[i]=r;tex[i+1]=g;tex[i+2]=b;tex[i+3]=a;}
    // Panel body
    for (let y=6;y<=57;y++) for (let x=14;x<=49;x++) sp11(x,y,22,26,22);
    // Border
    for (let x=14;x<=49;x++) { sp11(x,6,0,180,60); sp11(x,57,0,180,60); }
    for (let y=6;y<=57;y++) { sp11(14,y,0,180,60); sp11(49,y,0,180,60); }
    // LED status bar (green = active)
    for (let x=18;x<=45;x++) { sp11(x,10,0,220,80); sp11(x,11,0,160,50); }
    // Keypad button grid (3×4)
    const btnColors = [[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80],[80,85,80]];
    for (let row=0;row<4;row++) for (let col=0;col<3;col++) {
      const bx=18+col*10, by=16+row*9;
      for (let dy=0;dy<7;dy++) for (let dx=0;dx<8;dx++) sp11(bx+dx,by+dy,75,80,75);
      // Key highlight
      sp11(bx,by,100,108,100); sp11(bx+1,by,100,108,100);
    }
    // Bottom display strip
    for (let y=52;y<=55;y++) for (let x=18;x<=45;x++) sp11(x,y,8,14,8);
    for (let x=20;x<=38;x++) sp11(x,53,0,190,55);
    SPRITE_TEXTURES[11] = tex;
  }
```

- [ ] **Step 6: Add RACK-specific branch at start of `generateNPCSprite`**

Find:
```js
function generateNPCSprite(npcType) {
  const S = SPRITE_SIZE;
  const tex = new Uint8ClampedArray(S * S * 4); // all transparent
  const cfg = NPC_TYPES[npcType];
  if (!cfg) return tex;
```
Replace with:
```js
function generateNPCSprite(npcType) {
  const S = SPRITE_SIZE;
  const tex = new Uint8ClampedArray(S * S * 4); // all transparent
  const cfg = NPC_TYPES[npcType];
  if (!cfg) return tex;

  if (npcType === 'RACK') {
    function rd(x,y,r,g,b,a=255){if(x<0||x>=S||y<0||y>=S)return;const i=(y*S+x)*4;tex[i]=r;tex[i+1]=g;tex[i+2]=b;tex[i+3]=a;}
    function rr(x0,y0,x1,y1,r,g,b){for(let y=y0;y<=y1;y++)for(let x=x0;x<=x1;x++)rd(x,y,r,g,b);}
    // Chassis
    rr(14,4,50,62,18,20,18);
    // Bezel
    rr(16,6,48,60,30,34,30);
    // Rails
    rr(14,4,15,62,55,60,55); rr(49,4,50,62,55,60,55);
    // Top handle
    rr(22,2,42,4,72,78,72);
    // 6 server units
    for (let u=0;u<6;u++) {
      const uy=8+u*9;
      rr(17,uy,47,uy+7,38,42,38);       // unit face
      rr(19,uy+1,35,uy+6,12,14,12);     // drive bay
      rd(43,uy+3,0,255,65); rd(44,uy+3,0,255,65);   // green status LED
      rd(43,uy+4,0,180,40); rd(44,uy+4,0,180,40);
      if (u===2) { rd(40,uy+3,255,180,0); rd(41,uy+3,255,180,0); } // amber fault
    }
    // Network port LEDs at bottom
    rd(22,58,0,255,65); rd(23,58,0,255,65);
    rd(26,58,0,255,65); rd(27,58,0,255,65);
    rd(30,58,255,180,0); rd(31,58,255,180,0);
    // Casters
    rr(16,61,20,63,72,78,72); rr(44,61,48,63,72,78,72);
    return tex;
  }
```

- [ ] **Step 7: Commit**
```bash
git add cyberguard/engine.js
git commit -m "feat: add RACK sprite, cell-11 passable + rendered in engine"
```

---

## Task 7: Mechanics — loadLevel, isZoneComplete, returnToLobby (`mechanics.js`)

**Files:**
- Modify: `cyberguard/mechanics.js`

- [ ] **Step 1: Update `isZoneComplete` with campus panel check**

Find:
```js
function isZoneComplete() {
  if (GAME_STATE.level.level_num === 0) return true; // lobby always passable
  return getCardsCollectedInLevel() >= GAME_STATE.level.cards_total &&
         getScenariosCompletedInLevel() >= GAME_STATE.level.scenarios_total;
}
```
Replace with:
```js
function isZoneComplete() {
  if (GAME_STATE.level.level_num === 0) return true; // lobby always passable
  if (GAME_STATE.level.level_num === 8) {
    const l = GAME_STATE.panel_ips.left;
    const r = GAME_STATE.panel_ips.right;
    const leftDone  = l.every(s => s !== null && s.valid);
    const rightDone = r.every(s => s !== null && s.valid);
    return leftDone || rightDone;
  }
  return getCardsCollectedInLevel() >= GAME_STATE.level.cards_total &&
         getScenariosCompletedInLevel() >= GAME_STATE.level.scenarios_total;
}
```

- [ ] **Step 2: Reset `panel_ips` in `returnToLobby`**

Find:
```js
  GAME_STATE.progress.campus_completed   = [];
  GAME_STATE.progress.terminal_completed = [];
  GAME_STATE.progress.term_hints_collected = [];
```
Replace with:
```js
  GAME_STATE.progress.campus_completed   = [];
  GAME_STATE.progress.terminal_completed = [];
  GAME_STATE.progress.term_hints_collected = [];
  GAME_STATE.panel_ips = { left: [null, null, null], right: [null, null, null] };
```

- [ ] **Step 3: Commit**
```bash
git add cyberguard/mechanics.js
git commit -m "feat: campus panel completion check in isZoneComplete, reset in returnToLobby"
```

---

## Task 8: Mechanics — rack wander, FT immunity, encounter trigger, cell 11, handleEscKey (`mechanics.js`)

**Files:**
- Modify: `cyberguard/mechanics.js`

- [ ] **Step 1: Add `wander_target` and rack fields to `initNPCs`**

Find:
```js
      return {
        id:             s.id,
        type:           s.type,
        level_num:      s.level_num,
        ghost:          s.ghost || false,
        x:              safe.x,
        y:              safe.y,
        patrol:         s.patrol.map(([px,py]) => { const sp = snapToFloor(map,px,py); return [sp.x, sp.y]; }),
        patrol_idx:     0,
        challenges:     s.challenges || [],
        state:          s.ghost ? 'chasing' : 'patrol',
        alert_timer:    0,
        cooldown_timer: 0,
        stun_timer:     0,
      };
```
Replace with:
```js
      return {
        id:             s.id,
        type:           s.type,
        level_num:      s.level_num,
        ghost:          s.ghost || false,
        x:              safe.x,
        y:              safe.y,
        patrol:         (s.patrol || []).map(([px,py]) => { const sp = snapToFloor(map,px,py); return [sp.x, sp.y]; }),
        patrol_idx:     0,
        challenges:     s.challenges || [],
        challenge_id:   s.challenge_id || null,
        panel:          s.panel || null,
        slot:           s.slot !== undefined ? s.slot : null,
        state:          s.ghost ? 'chasing' : (s.type === 'RACK' ? 'wander' : 'patrol'),
        alert_timer:    0,
        cooldown_timer: 0,
        stun_timer:     0,
        wander_target:  s.type === 'RACK' ? { x: safe.x, y: safe.y } : null,
      };
```

- [ ] **Step 2: Add RACK 360° vision to `npcCanSeePlayer`**

Find:
```js
function npcCanSeePlayer(npc) {
  const px = GAME_STATE.player.x, py = GAME_STATE.player.y;
  const dx = px - npc.x, dy = py - npc.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist > NPC_VISION_RANGE) return false;
  // NPC faces toward its next patrol waypoint
```
Replace with:
```js
function npcCanSeePlayer(npc) {
  const px = GAME_STATE.player.x, py = GAME_STATE.player.y;
  const dx = px - npc.x, dy = py - npc.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist > NPC_VISION_RANGE) return false;
  if (npc.type === 'RACK') return !wallBetween(npc.x, npc.y, px, py); // 360° vision
  // NPC faces toward its next patrol waypoint
```

- [ ] **Step 3: Add RACK wander branch to `updateNPCs` (insert after ghost block, before cooldown block)**

Find:
```js
    if (npc.state === 'cooldown') {
      npc.cooldown_timer -= dt;
      if (npc.cooldown_timer <= 0) npc.state = 'patrol';
      continue;
    }
```
Replace with:
```js
    // Rack — wander/chase, no stun/cooldown states
    if (npc.type === 'RACK') {
      if (npc.state === 'chasing') {
        const dx = px - npc.x, dy = py - npc.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist <= NPC_CATCH_RANGE) { triggerRackEncounter(npc); return; }
        const speed = NPC_CHASE_SPEED * dt;
        const nx = dx / dist, ny = dy / dist;
        if (canMoveTo(map, npc.x + nx * speed, npc.y)) npc.x += nx * speed;
        if (canMoveTo(map, npc.x, npc.y + ny * speed)) npc.y += ny * speed;
      } else {
        if (npcCanSeePlayer(npc)) { npc.state = 'chasing'; continue; }
        const wdx = npc.wander_target.x - npc.x, wdy = npc.wander_target.y - npc.y;
        const wdist = Math.sqrt(wdx * wdx + wdy * wdy);
        if (wdist < 0.2) {
          const pos = randomFloorTile(map);
          npc.wander_target = { x: pos.x, y: pos.y };
        } else {
          const speed = NPC_PATROL_SPEED * dt;
          const nx = wdx / wdist, ny = wdy / wdist;
          if (canMoveTo(map, npc.x + nx * speed, npc.y)) npc.x += nx * speed;
          if (canMoveTo(map, npc.x, npc.y + ny * speed)) npc.y += ny * speed;
        }
      }
      continue;
    }

    if (npc.state === 'cooldown') {
      npc.cooldown_timer -= dt;
      if (npc.cooldown_timer <= 0) npc.state = 'patrol';
      continue;
    }
```

- [ ] **Step 4: Add RACK FT immunity in `throwFT`**

Find:
```js
    if (npc.type === 'BOSS') continue; // ARIA immune to FT
```
Replace with:
```js
    if (npc.type === 'BOSS' || npc.type === 'RACK') continue; // ARIA and racks immune to FT
```

- [ ] **Step 5: Add `triggerRackEncounter` function (insert after `triggerNPCEncounter`)**

Find the function `triggerARIAEncounter`:
```js
function triggerARIAEncounter(npc) {
```
Insert before it:
```js
function triggerRackEncounter(npc) {
  if (GAME_STATE.screen !== 'playing') return;
  if (performance.now() - GAME_STATE.subnet_close_time < 400) return;
  const ch = SUBNET_CHALLENGES.find(c => c.challenge_id === npc.challenge_id);
  if (!ch) return;
  const challenge = Object.assign({}, ch, { rack_id: npc.id, phase: 'ssh', entered_ip: null, ip_valid: false });
  GAME_STATE.active_subnet_challenge = challenge;
  GAME_STATE.screen = 'subnet_challenge';
  showSubnetChallenge(challenge);
}

```

- [ ] **Step 6: Add cell 11 interaction to `checkCellInteractions`**

Find:
```js
  if (cell === 10 && GAME_STATE.screen === 'playing') {
```
Insert before it:
```js
  if (cell === 11 && GAME_STATE.screen === 'playing') {
    const side = col < 31 ? 'left' : 'right';
    showPanelOverlay(side);
  }

```

- [ ] **Step 7: Add subnet_challenge and panel to `handleEscKey`**

Find:
```js
  } else if (GAME_STATE.screen === 'codex') {
    closeCodex();
  }
}
```
Replace with:
```js
  } else if (GAME_STATE.screen === 'codex') {
    closeCodex();
  } else if (GAME_STATE.screen === 'subnet_challenge') {
    hideSubnetChallenge(false);
  } else if (GAME_STATE.screen === 'panel') {
    hidePanelOverlay();
  }
}
```

- [ ] **Step 8: Commit**
```bash
git add cyberguard/mechanics.js
git commit -m "feat: rack wander AI, FT immunity, encounter trigger, cell-11 panel interaction"
```

---

## Task 9: UI — subnet challenge terminal (`ui_components.js`)

**Files:**
- Modify: `cyberguard/ui_components.js`

- [ ] **Step 1: Add IP validation helper and phase helpers before `showSubnetChallenge`**

Add these functions before the `// ── TERMINAL CHALLENGES ───` section comment:

```js
// ── SUBNET CHALLENGES (campus RACK encounters) ────────────────────────────────

function ipInSubnet(ipStr, validRange) {
  function toInt(s) {
    const p = s.split('.').map(Number);
    return ((p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]) >>> 0;
  }
  return toInt(ipStr) >= toInt(validRange[0]) && toInt(ipStr) <= toInt(validRange[1]);
}

function _subnetPs1(challenge) {
  switch (challenge.phase) {
    case 'ssh':       return 'attacker@terminal:~$ ';
    case 'configure': return `admin@${challenge.rack_label}:~# `;
    case 'interface': return `${challenge.rack_label}(config)# `;
    case 'ip_assign': return `${challenge.rack_label}(config-if-Ma0)# `;
    case 'write':     return `${challenge.rack_label}(config-if-Ma0)# `;
    default:          return '$ ';
  }
}

function _subnetAppend(html) {
  const out = document.getElementById('subnet-output');
  if (!out) return;
  const div = document.createElement('div');
  div.innerHTML = html;
  out.appendChild(div);
  const body = document.getElementById('subnet-body');
  if (body) body.scrollTop = body.scrollHeight;
}
```

- [ ] **Step 2: Add `showSubnetChallenge`**

```js
function showSubnetChallenge(challenge) {
  const el = document.getElementById('subnet-panel');
  const now = new Date().toString().slice(0, 24);
  el.innerHTML = `
    <div class="terminal-box">
      <div class="term-titlebar">
        <span class="term-dot term-dot-close" onclick="hideSubnetChallenge(false)" title="Close — abandon challenge"></span>
        <span class="term-dot term-dot-min"></span>
        <span class="term-dot term-dot-max"></span>
        <span class="term-wintitle">admin@${escapeHtml(challenge.rack_label)} — Arista EOS</span>
      </div>
      <div class="term-body" id="subnet-body">
        <div class="term-banner">Last login: ${escapeHtml(now)} on ttys001

<span class="term-incident">⚠  ROGUE DEVICE DETECTED — ${escapeHtml(challenge.situation)}</span>

<span class="term-task-line">TASK ▶  Assign a valid host IP within the correct subnet.</span>
<span class="term-task-line">Network: ${escapeHtml(challenge.subnet)}  —  determine the valid host range.</span>
</div>
        <div id="subnet-output"></div>
        <div class="term-prompt-line" id="subnet-prompt-line">
          <span class="term-ps1" id="subnet-ps1-prompt">attacker@terminal:~$ </span><input type="text" id="subnet-input" class="term-input" autocomplete="off" spellcheck="false" autocorrect="off" autocapitalize="off">
        </div>
      </div>
    </div>`;
  el.classList.add('active');
  const input = document.getElementById('subnet-input');
  if (input) {
    input.focus();
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); submitSubnetCommand(); }
    });
  }
}
```

- [ ] **Step 3: Add `submitSubnetCommand` with full phase state machine**

```js
function submitSubnetCommand() {
  const challenge = GAME_STATE.active_subnet_challenge;
  if (!challenge) return;
  const input = document.getElementById('subnet-input');
  if (!input) return;
  const cmd = input.value.trim();
  if (!cmd) return;
  input.value = '';

  _subnetAppend(`<div class="term-echo"><span class="term-ps1">${escapeHtml(_subnetPs1(challenge))}</span>${escapeHtml(cmd)}</div>`);

  const norm = cmd.toLowerCase().replace(/\s+/g, ' ');

  if (challenge.phase === 'ssh') {
    if (norm === `ssh admin@${challenge.rogue_ip}`) {
      _subnetAppend(`<pre class="term-cmd-out">The authenticity of host '${escapeHtml(challenge.rogue_ip)}' can't be established.\nRSA key fingerprint is SHA256:xK3mP9rL2vQ8nW1bA5fD7gH6jC4sU0tY.\nAre you sure you want to continue connecting (yes/no)? yes\nWarning: Permanently added '${escapeHtml(challenge.rogue_ip)}' (RSA) to known hosts.\nadmin@${escapeHtml(challenge.rack_label)}:~#</pre>`);
      challenge.phase = 'configure';
    } else {
      _subnetAppend(`<div class="term-cmd-err">ssh: Could not resolve hostname — or incorrect IP. Try: ssh admin@${escapeHtml(challenge.rogue_ip)}</div>`);
    }
  } else if (challenge.phase === 'configure') {
    if (norm === 'configure terminal' || norm === 'conf t') {
      _subnetAppend(`<pre class="term-cmd-out">Enter configuration commands, one per line. End with CNTL/Z.\n${escapeHtml(challenge.rack_label)}(config)#</pre>`);
      challenge.phase = 'interface';
    } else {
      _subnetAppend(`<div class="term-cmd-err">% Invalid input detected. Expected: configure terminal</div>`);
    }
  } else if (challenge.phase === 'interface') {
    if (norm === 'interface management0') {
      _subnetAppend(`<pre class="term-cmd-out">${escapeHtml(challenge.rack_label)}(config-if-Ma0)#</pre>`);
      challenge.phase = 'ip_assign';
    } else {
      _subnetAppend(`<div class="term-cmd-err">% Invalid input detected. Expected: interface Management0</div>`);
    }
  } else if (challenge.phase === 'ip_assign') {
    const m = cmd.match(/^ip\s+address\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\/(\d{1,2})$/i);
    if (!m) {
      _subnetAppend(`<div class="term-cmd-err">% Invalid input detected. Expected: ip address &lt;x.x.x.x/prefix&gt;</div>`);
    } else {
      challenge.entered_ip = m[1] + '/' + m[2];
      challenge.ip_valid   = ipInSubnet(m[1], challenge.valid_range);
      _subnetAppend(`<pre class="term-cmd-out">% Configuration accepted.\n${escapeHtml(challenge.rack_label)}(config-if-Ma0)#</pre>`);
      challenge.phase = 'write';
    }
  } else if (challenge.phase === 'write') {
    if (norm === 'write memory' || norm === 'wr mem') {
      _subnetAppend(`<pre class="term-cmd-out">Copy complete, [OK]\n\n${escapeHtml(challenge.rack_label)}#</pre>`);
      _subnetAppend(`<div class="term-result-ok">✓  Configuration saved to NVRAM.</div>`);
      _subnetAppend(`<div class="term-continue-wrap"><span class="term-ps1">$&nbsp;</span><button class="term-continue-btn" onclick="hideSubnetChallenge(true)">[ CONTINUE ]</button></div>`);
      const promptLine = document.getElementById('subnet-prompt-line');
      if (promptLine) promptLine.style.display = 'none';
    } else {
      _subnetAppend(`<div class="term-cmd-err">% Invalid input detected. Expected: write memory</div>`);
    }
  }

  const ps1el = document.getElementById('subnet-ps1-prompt');
  if (ps1el) ps1el.textContent = _subnetPs1(challenge);
  const body = document.getElementById('subnet-body');
  if (body) body.scrollTop = body.scrollHeight;
  const inp = document.getElementById('subnet-input');
  if (inp) inp.focus();
}
```

- [ ] **Step 4: Add `hideSubnetChallenge` with panel slot recording and rack teleport**

```js
function hideSubnetChallenge(completed) {
  const challenge = GAME_STATE.active_subnet_challenge;
  if (completed && challenge && challenge.entered_ip !== null) {
    GAME_STATE.panel_ips[challenge.panel][challenge.slot] = {
      ip: challenge.entered_ip,
      valid: challenge.ip_valid,
    };
    if (GAME_STATE.panel_ips[challenge.panel].every(s => s !== null && s.valid)) {
      showHintToast(`STAIRWELL ${challenge.panel.toUpperCase()} UNLOCKED — descend when ready`);
    }
  }
  if (challenge) {
    const rack = GAME_STATE.npcs.find(n => n.id === challenge.rack_id);
    if (rack) {
      const pos = randomFloorTile(GAME_STATE.level.map);
      rack.x = pos.x; rack.y = pos.y;
      rack.state = 'wander';
      rack.wander_target = { x: pos.x, y: pos.y };
    }
  }
  const el = document.getElementById('subnet-panel');
  if (el) { el.classList.remove('active'); el.innerHTML = ''; }
  GAME_STATE.active_subnet_challenge = null;
  GAME_STATE.subnet_close_time = performance.now();
  GAME_STATE.screen = 'playing';
}
```

- [ ] **Step 5: Commit**
```bash
git add cyberguard/ui_components.js
git commit -m "feat: subnet challenge terminal UI — phase machine, IP validation, panel slot recording"
```

---

## Task 10: UI — panel overlay and HUD rogue IP (`ui_components.js`)

**Files:**
- Modify: `cyberguard/ui_components.js`

- [ ] **Step 1: Add `showPanelOverlay` and `hidePanelOverlay`**

Add after `hideSubnetChallenge`:

```js
function showPanelOverlay(side) {
  GAME_STATE.screen = 'panel';
  const slots = GAME_STATE.panel_ips[side];
  const challenges = SUBNET_CHALLENGES.filter(c => c.panel === side).sort((a, b) => a.slot - b.slot);
  const slotRows = challenges.map((ch, i) => {
    const entry = slots[i];
    if (!entry) return `<div class="panel-slot"><span class="panel-slot-num">Slot ${i + 1}:</span> <span class="panel-slot-empty">[ not configured ]</span></div>`;
    return `<div class="panel-slot"><span class="panel-slot-num">Slot ${i + 1}:</span> <span class="panel-slot-ip">${escapeHtml(entry.ip)}</span></div>`;
  }).join('');
  const allValid = slots.every(s => s !== null && s.valid);
  const statusCls = allValid ? 'panel-status-unlocked' : 'panel-status-locked';
  const statusTxt = allValid ? 'UNLOCKED — stairwell is passable' : 'LOCKED — configure all 3 racks';
  const el = document.getElementById('panel-overlay');
  el.innerHTML = `
    <div class="panel-box">
      <div class="panel-header">STAIRWELL ACCESS PANEL (${side.toUpperCase()})</div>
      <div class="panel-desc">Configure 3 server racks to unlock descent.</div>
      <div class="panel-slots">${slotRows}</div>
      <div class="panel-status ${statusCls}">STATUS: ${statusTxt}</div>
      <button class="panel-close-btn" onclick="hidePanelOverlay()">[ CLOSE ]</button>
    </div>`;
  el.classList.add('active');
}

function hidePanelOverlay() {
  const el = document.getElementById('panel-overlay');
  if (el) { el.classList.remove('active'); el.innerHTML = ''; }
  GAME_STATE.screen = 'playing';
}
```

- [ ] **Step 2: Add rogue IP indicator to `renderHUD`**

Find:
```js
    <span class="hud-ft" title="Financial Times — press F to throw">📰 ${ft}</span>
  `;
}
```
Replace with:
```js
    <span class="hud-ft" title="Financial Times — press F to throw">📰 ${ft}</span>
    ${rackHtml}
  `;
}
```

And add the `rackHtml` variable computation. Find the block just before the `hud.innerHTML` assignment:
```js
  hud.innerHTML = `
```
Insert before it:
```js
  let rackHtml = '';
  if (GAME_STATE.level.level_num === 8) {
    const nearRack = GAME_STATE.npcs.find(n => {
      if (n.type !== 'RACK') return false;
      const dx = n.x - GAME_STATE.player.x, dy = n.y - GAME_STATE.player.y;
      return Math.sqrt(dx * dx + dy * dy) <= NPC_VISION_RANGE;
    });
    if (nearRack) {
      const ch = SUBNET_CHALLENGES.find(c => c.challenge_id === nearRack.challenge_id);
      if (ch) rackHtml = `<span class="hud-rogue" title="SSH target IP">🗄 ROGUE: ${ch.rogue_ip}</span>`;
    }
  }
```

- [ ] **Step 3: Commit**
```bash
git add cyberguard/ui_components.js
git commit -m "feat: panel overlay UI and HUD rogue IP indicator for campus racks"
```

---

## Task 11: Styles (`style.css`)

**Files:**
- Modify: `cyberguard/style.css`

- [ ] **Step 1: Add all new CSS at end of file**

Append to `cyberguard/style.css`:

```css
/* ── SUBNET CHALLENGE PANEL ─────────────────────────────────────────────── */
#subnet-panel.active {
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.88);
}

/* ── STAIRWELL ACCESS PANEL OVERLAY ─────────────────────────────────────── */
#panel-overlay.active {
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.82);
}
.panel-box {
  background: #0d1a0d;
  border: 2px solid #00FF41;
  border-radius: 8px;
  padding: 32px 40px 28px;
  min-width: 380px;
  max-width: 480px;
  box-shadow: 0 0 40px #00FF4144;
  display: flex;
  flex-direction: column;
  gap: 14px;
  font-family: var(--font-m);
}
.panel-header {
  font-family: var(--font-h);
  font-size: 13px;
  letter-spacing: 0.12em;
  color: #00FF41;
  text-transform: uppercase;
}
.panel-desc {
  font-size: 11px;
  color: #7ca87c;
}
.panel-slots {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 4px 0;
}
.panel-slot {
  font-size: 12px;
  color: #c9d1d9;
}
.panel-slot-num {
  color: #7ca87c;
  margin-right: 8px;
}
.panel-slot-empty {
  color: #444;
  font-style: italic;
}
.panel-slot-ip {
  color: #00FF41;
  font-family: var(--font-m);
}
.panel-status {
  font-family: var(--font-h);
  font-size: 12px;
  letter-spacing: 0.08em;
  padding: 8px 0 0;
  border-top: 1px solid #1a2e1a;
}
.panel-status-locked   { color: #FF4444; }
.panel-status-unlocked { color: #00FF41; }
.panel-close-btn {
  align-self: flex-end;
  background: transparent;
  border: 1px solid #00FF41;
  color: #00FF41;
  font-family: var(--font-m);
  font-size: 11px;
  padding: 5px 14px;
  cursor: pointer;
  letter-spacing: 0.06em;
}
.panel-close-btn:hover { background: #00FF4122; }

/* ── HUD ROGUE IP INDICATOR ─────────────────────────────────────────────── */
.hud-rogue {
  color: #00FF41;
  font-family: var(--font-m);
  font-size: 11px;
  animation: rogue-pulse 1.2s ease-in-out infinite;
}
@keyframes rogue-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
```

- [ ] **Step 2: Commit**
```bash
git add cyberguard/style.css
git commit -m "feat: styles for subnet challenge, panel overlay, and HUD rogue IP indicator"
```

---

## Task 12: Smoke test

- [ ] **Step 1: Open game in browser**

Open `cyberguard/index.html` directly in a browser. Select any role. At the lobby, walk north through the top exit (row 0, col 12) to enter the campus (FloorDoom) level.

- [ ] **Step 2: Verify RACK NPCs visible and wandering**

6 green server rack sprites should appear in the 3D view as you explore the campus map. They should move around independently (no fixed patrol path). When one spots you, it should start chasing. Confirm it cannot be stunned with the FT newspaper (press F when facing one).

- [ ] **Step 3: Verify HUD rogue IP**

When a RACK is within vision range, the HUD should show a pulsing `🗄 ROGUE: 169.254.x.x` indicator in green.

- [ ] **Step 4: Verify subnet challenge opens on catch**

Let a rack catch you. The Arista EOS terminal should open with the rack's label in the title bar, the subnet displayed in the banner, and the prompt starting at `attacker@terminal:~$ `.

- [ ] **Step 5: Walk through all 5 phases with a correct IP**

Type the correct sequence (example for SRV-3A — adjust for whichever rack you encounter):
```
ssh admin@169.254.12.44
configure terminal
interface Management0
ip address 10.30.0.10/26
write memory
```
At each step verify the prompt changes correctly and the terminal shows appropriate Arista output. After `write memory`, `[ CONTINUE ]` button appears.

- [ ] **Step 6: Verify wrong IP silently accepted**

Repeat with an out-of-range IP (e.g. `ip address 10.30.1.5/26`). Terminal should still say `% Configuration accepted.` — no visible failure.

- [ ] **Step 7: Verify panel overlay**

Walk to row 21, col 5 (near left staircase). The panel overlay should appear showing which slots are filled. Wrong IPs appear without ✓/✗. Correct IPs accumulate. ESC closes the overlay.

- [ ] **Step 8: Verify staircase unlocks after 3 valid IPs**

Configure all 3 left-panel racks with valid IPs. After the third `[ CONTINUE ]`, a "STAIRWELL LEFT UNLOCKED" toast should appear. Walking near the exit door at cols 4-6 rows 23-24 should allow passage (level transition triggers). The right panel should remain locked until its own 3 racks are configured.

- [ ] **Step 9: Verify close button abandons without recording**

Let a rack catch you. Close with the red X before `write memory`. Panel slot should remain `null` for that rack's slot (verify by opening the panel overlay). The rack should teleport away and be re-encounterable after a moment.

- [ ] **Step 10: Commit smoke test confirmation**
```bash
git add -p  # stage nothing new
git commit --allow-empty -m "chore: smoke test passed — server rack foe feature complete"
```

---

## Self-Review Notes

- `ipInSubnet` uses unsigned right-shift (`>>> 0`) to handle high-bit IPs correctly (e.g. `192.168.x.x` where the top byte sets bit 31).
- RACK `wander_target` is initialized to the spawn position; first `randomFloorTile` pick happens when the rack arrives there (distance < 0.2).
- `hideSubnetChallenge(false)` vs `hideSubnetChallenge(true)`: `false` = abandoned (no panel write), `true` = completed after `write memory`.
- `panel_ips` slot overwrite is intentional: if a player re-encounters a rack after a wrong entry, the new result replaces the old one.
- Both `#subnet-panel` and `#terminal-panel` reuse `.terminal-box`, `.term-titlebar`, `.term-dot-*`, `.term-body`, `.term-ps1`, `.term-input` CSS — no new classes needed for the terminal frame itself.
- `showHintToast` is used for the unlock notification — it already exists in `ui_components.js` and fits.
