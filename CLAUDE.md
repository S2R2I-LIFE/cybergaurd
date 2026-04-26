# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CyberGuard: The NIST Dungeon** — a browser-based 2.5D educational game (DOOM-style raycasting, vanilla JS) that teaches NIST cybersecurity frameworks (CSF 2.0, AI RMF 1.0, SP 800-53, SP 800-37) to university students. Designed for Professor Snyder for undergraduate/graduate cybersecurity courses.

**Status:** Specification phase. The entire design lives in `cybergaurd.json` — a single orchestration document with embedded Markdown sections for each agent. No implementation code exists yet.

## Source of Truth

`cybergaurd.json` is the master spec. It contains 7 embedded Markdown sections:

| Section | Contents |
|---|---|
| `MASTER_ORCHESTRATOR.md` | Agent execution order, handoff rules, output artifacts |
| `GAME_DESIGN.md` | Map layout, level progression, game mechanics |
| `POLICY_CONTENT.md` | Policy card schema (30+ cards), scenario templates (15+) |
| `GAME_ENGINE.md` | Raycasting engine spec, state management, event system |
| `UI_DESIGN.md` | Color system (IDENTIFY=blue, PROTECT=green, DETECT=orange, AI RMF=purple), HUD, components |
| `QA_VALIDATION.md` | Validation checklist, governance veto protocol |
| `DEPLOYMENT.md` | Output file structure, deployment targets, instructor README |

## Agent Orchestration Architecture

The spec defines a **7-agent sequential pipeline** where each agent receives prior agents' artifacts:

```
AGT-01 WorldBuilder → AGT-02 PolicyScribe → AGT-03 GameMechanicEngineer
→ AGT-04 UIRenderer → AGT-05 NarrativeDirector → AGT-06 QAValidator → AGT-07 DeploymentAgent
```

Each agent has a defined role, input dependencies, and output artifacts (e.g., `world_map.json`, `engine.js`, `style.css`, `qa_report.json`, `/dist/cyberguard_v1.0/`).

## Implementation Target

When built, the game is a **fully self-contained static site** (no backend, no external APIs):
- HTML5 canvas raycasting renderer (~800×500px, 66° FOV)
- Player roles: Security Analyst, AI Auditor, Risk Manager
- Level flow: Lobby → IDENTIFY → PROTECT → DETECT → Boss (AI RMF)
- Policy card inventory, scenario MCQ puzzles, knowledge-gate quizzes
- Completion certificate with NIST mastery metrics
- Target browsers: Chrome, Firefox, Safari, Edge; mobile-responsive (min 375px)
- No build step — deploy as static files (GitHub Pages, Netlify, or direct HTML)
