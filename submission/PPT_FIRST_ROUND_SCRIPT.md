# AI Code Mentor: Visual-First PPT Script

Goal: minimal text, maximum product proof.
Recommended length: 8 slides.

## Slide 1 - Hero (Full-screen product)
Text on slide:
- AI Code Mentor
- "Blocks wrong AI explanations before students learn from them"

Image:
- Full-screen UI screenshot (editor + verdict area visible)

## Slide 2 - Problem in One Frame
Text on slide:
- AI sounds confident, even when code logic is wrong.
- Students trust it.

Image:
- Split image:
  - left: buggy code snippet
  - right: confident but wrong AI claim

## Slide 3 - The Moment of Truth (Main wow slide)
Text on slide:
- AI claim: "This is correct"
- System verdict: BLOCKED

Image:
- Large screenshot of hallucination analysis card with red verdict

## Slide 4 - How We Decide (Only one line + diagram)
Text on slide:
- Trace -> Audit -> Verify -> Approve/Block

Image:
- Pipeline diagram (icons + arrows, no paragraphs)

## Slide 5 - Product Walkthrough (3 snapshots)
Text on slide:
- 1. Paste code
- 2. Run analyze
- 3. Get safe verdict

Image:
- Three screenshots side-by-side for each step

## Slide 6 - Technical Credibility
Text on slide:
- Sandboxed execution
- Invariant checks
- Claim verification gate

Image:
- Architecture graphic: React UI -> FastAPI -> Trace/Audit/Claims modules

## Slide 7 - Why It Matters
Text on slide:
- Safer AI learning for students
- Trust layer for EdTech platforms

Image:
- Clean impact graphic (student/mentor/platform icons)

## Slide 8 - Submission Links (Evaluator action slide)
Text on slide:
- GitHub: [PASTE_GITHUB_URL]
- Prototype: [PASTE_LIVE_URL]
- Demo Video: [PASTE_VIDEO_URL]
- Project Summary: [PASTE_SUMMARY_URL]

Image:
- QR codes for each link (optional)

---

## Visual Rules (important)
- Max 2 short bullets per slide.
- Font large enough to read in 5 seconds.
- One key message per slide.
- Use red/green verdict colors from product UI for consistency.
- Avoid long paragraphs completely.

## Screenshot Capture Plan (take these exact shots)
1. Home screen with code editor loaded.
2. Analyze button pressed / loading state.
3. BLOCKED verdict with hallucination detail open.
4. APPROVED verdict with verified explanation.
5. Audit section showing violations.
6. Execution trace section showing step-by-step variables.
7. Optional architecture screenshot from docs/diagram.

## 60-Second Presentation Script
- "AI explanations often sound correct even when algorithm logic is wrong."
- "Our system traces execution, audits invariants, and verifies explanation claims before showing them to learners."
- "If the explanation is unsafe, we block it and show exactly why."
- "This adds a trust layer for AI-powered coding education."
