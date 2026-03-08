# AI Code Mentor: Round-2 Prototype PPT (Visual-First)

Goal: show a working prototype with technical depth, fast.
Recommended length: 10 slides.
Rule: each slide must be understandable in 5-8 seconds.

## Slide 1 - Prototype Hero
Text on slide:
- AI Code Mentor (Round-2 Prototype)
- "Safety layer for AI coding explanations"

Image:
- Full-screen product screenshot (editor + verdict panel)
- Small QR to live prototype

## Slide 2 - Problem Snapshot
Text on slide:
- Fluent AI feedback can still be logically wrong.
- Learners trust it and carry forward bad reasoning.

Image:
- Split visual: buggy code vs confident AI claim

## Slide 3 - Live Product Flow
Text on slide:
- Paste code -> Analyze -> Safe verdict

Image:
- 3-step screenshot strip:
  1) code input
  2) pipeline running
  3) final verdict panel

## Slide 4 - Proof Case A (Blocked)
Text on slide:
- AI claim: "Looks correct"
- System verdict: BLOCKED

Image:
- Hallucination analysis screenshot (red verdict)
- Highlight: what AI claimed vs what trace showed

## Slide 5 - Proof Case B (Approved)
Text on slide:
- Verified logic -> APPROVED explanation

Image:
- Approved explanation screenshot (green verdict)
- Show audit PASS and clean trace summary

## Slide 6 - Internal Pipeline (Technical Core)
Text on slide:
- Trace -> Audit -> Claim Parse -> Verify -> Gate

Image:
- Clean architecture diagram:
  - React UI
  - FastAPI `/analyze`
  - tracer/auditor/claim-verifier modules

## Slide 7 - Engineering Safety Controls
Text on slide:
- AST restrictions + safe builtins
- timeout + max trace steps
- deterministic invariant checks

Image:
- Code snippets or component cards from backend modules

## Slide 8 - Deployment and Stack
Text on slide:
- Frontend: React + Monaco
- Backend: FastAPI
- AWS Bedrock ready integration path

Image:
- Deployment diagram (browser -> frontend -> API -> model layer)

## Slide 9 - Prototype Scope and Expansion
Text on slide:
- Current: binary search reasoning safety
- Next: more DSA patterns, more languages

Image:
- Roadmap timeline graphic (Now / Next / Later)

## Slide 10 - Evaluator Action Slide
Text on slide:
- GitHub: [PASTE_GITHUB_URL]
- Live Prototype: [PASTE_LIVE_URL]
- Demo Video: [PASTE_VIDEO_URL]
- Project Summary: [PASTE_SUMMARY_URL]

Image:
- QR codes for each link
- Footer: "Start with Live Prototype"

---

## Round-2 Visual Rules
- Max 12 words per bullet.
- Max 2 bullets per slide.
- One primary screenshot per slide.
- Keep colors consistent with product verdict colors.
- Avoid long paragraphs entirely.

## Mandatory Screenshot Shot List
1. Landing UI with code editor.
2. Analyze button + loading state.
3. BLOCKED verdict card.
4. Hallucination detail section.
5. APPROVED verdict card.
6. Audit violations section.
7. Execution trace section.
8. Optional architecture diagram.

## 75-Second Round-2 Pitch
- "This is a working prototype that verifies AI code explanations before they reach learners."
- "We trace actual execution, audit invariants, parse explanation claims, and gate unsafe reasoning."
- "Buggy code with overconfident AI output is blocked with transparent evidence and fix guidance."
- "So the platform teaches correct reasoning, not just fluent answers."
