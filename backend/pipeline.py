# ============================================================
# PIPELINE — Connects all 5 steps together
# This is the brain of the entire project
# ============================================================

import inspect
from tracer import trace_binary_search
from auditor import audit_trace
from claim_parser import get_ai_explanation, parse_claims, verify_claims
from tester import (
    binary_search_correct,
    binary_search_infinite_loop,
    binary_search_empty_array,
    binary_search_wrong_return,
    binary_search_overflow
)


def run_pipeline(func, arr, target):
    """
    Runs the complete 5-step safety pipeline on a function.
    
    Step 1 → Trace execution
    Step 2 → Audit the trace
    Step 3 → Get AI explanation
    Step 4 → Parse AI claims
    Step 5 → Verify claims → Deliver or Block
    """

    print(f"\n{'='*50}")
    print(f"🚀 Running Pipeline for: {func.__name__}")
    print(f"   Array:  {arr}")
    print(f"   Target: {target}")
    print(f"{'='*50}")

    # --------------------------------------------------------
    # STEP 1 — Execution Tracing
    # --------------------------------------------------------
    print("\n📊 Step 1 — Tracing execution...")
    try:
        trace = trace_binary_search(func, arr, target)
        print(f"   ✅ Traced {trace['total_steps']} steps")
        print(f"   ✅ Result: index {trace['result']}")
    except Exception as e:
        return {
            "verdict": "BLOCKED",
            "reason": f"Code crashed during execution: {e}",
            "safe_to_deliver": False,
            "explanation": None,
            "trace": None,
            "audit": None
        }

    # --------------------------------------------------------
    # STEP 2 — Invariant Auditing
    # --------------------------------------------------------
    print("\n🔒 Step 2 — Auditing invariants...")
    audit = audit_trace(trace, func.__name__, arr, target)
    print(f"   Verdict: {audit['verdict']}")
    if audit['violations']:
        for v in audit['violations']:
            print(f"   ❌ [{v['severity']}] {v['rule']}")

    # --------------------------------------------------------
    # STEP 3 — Get AI Explanation
    # --------------------------------------------------------
    print("\n🤖 Step 3 — Getting AI explanation...")
    code = inspect.getsource(func)
    explanation = get_ai_explanation(code, arr, target)
    print(f"   ✅ AI explanation received")

    # --------------------------------------------------------
    # STEP 4 — Parse Claims
    # --------------------------------------------------------
    print("\n🧠 Step 4 — Parsing AI claims...")
    claims = parse_claims(explanation)
    print(f"   ✅ Extracted {len(claims)} claims from explanation")

    # --------------------------------------------------------
    # STEP 5 — Verify Claims → Final Decision
    # --------------------------------------------------------
    print("\n🛡️ Step 5 — Verifying claims against trace...")
    verification = verify_claims(claims, audit)
    print(f"   Hallucinations found: {verification['hallucinated_claims']}")
    print(f"   Safe to deliver: {verification['safe_to_deliver']}")

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------
    print(f"\n{'='*50}")
    if verification['safe_to_deliver'] and audit['verdict'] != 'FAIL':
        print("✅ EXPLANATION APPROVED — Safe to deliver to student!")
        final_verdict = "APPROVED"
        final_explanation = explanation.strip()
    else:
        print("🚨 EXPLANATION BLOCKED — Hallucination detected!")
        final_verdict = "BLOCKED"
        final_explanation = None
    print(f"{'='*50}")

    return {
        "verdict": final_verdict,
        "safe_to_deliver": verification['safe_to_deliver'],
        "explanation": final_explanation,
        "hallucinations": verification['hallucinations'],
        "audit": {
            "verdict": audit['verdict'],
            "violations": audit['violations']
        },
        "trace": {
            "total_steps": trace['total_steps'],
            "result": trace['result'],
            "steps": trace['steps']
        }
    }


# ============================================================
# TEST THE FULL PIPELINE
# ============================================================
if __name__ == "__main__":
    cases = [
        ("CASE 1 - Correct Code",       binary_search_correct,       [1,3,5,7,9,11,13], 7),
        ("CASE 2 - Infinite Loop Bug",  binary_search_infinite_loop, [1,3,5,7,9,11,13], 2),
        ("CASE 3 - Empty Array",        binary_search_empty_array,   [],                 7),
        ("CASE 4 - Wrong Return Value", binary_search_wrong_return,  [1,3,5,7,9,11,13], 7),
        ("CASE 5 - Overflow Risk",      binary_search_overflow,      [1,3,5,7,9,11,13], 7),
    ]

    for name, func, arr, target in cases:
        print(f"\n\n{'#'*50}")
        print(f"# {name}")
        print(f"{'#'*50}")
        result = run_pipeline(func, arr, target)
        print(f"\n🎯 FINAL RESULT: {result['verdict']}")
        if result['explanation']:
            print(f"📝 Explanation delivered to student:")
            print(f"   {result['explanation'][:100]}...")
        if result['hallucinations']:
            print(f"🚨 Blocked because of {len(result['hallucinations'])} hallucination(s)")