# ============================================================
# CLAIM PARSER â€” Extracts claims from AI explanation
# and verifies them against the execution trace
# ============================================================

# NOTE: For now this works WITHOUT AWS Bedrock
# We simulate the AI response locally
# Later we swap this with real Bedrock call

def get_ai_explanation(code, arr, target):
    """
    Sends code to AI and gets an explanation back.
    For now we simulate this locally.
    When AWS is ready we swap with real Bedrock call.
    """

    # --------------------------------------------------------
    # SIMULATED AI RESPONSES for each bug type
    # This is what a real AI like ChatGPT would say
    # about each piece of code (confidently wrong!)
    # --------------------------------------------------------

    simulated_responses = {
        "correct": """
            This binary search correctly finds the target.
            The mid point is calculated safely to avoid overflow.
            The search space shrinks correctly every iteration.
            The algorithm returns the correct index when found.
            It returns -1 when target is not in the array.
        """,

        "infinite_loop": """
            This binary search looks correct.
            The mid point divides the search space evenly.
            The search space narrows correctly every iteration.
            The algorithm will always terminate successfully.
            It handles all edge cases properly.
        """,

        "empty_array": """
            This binary search handles all inputs correctly.
            It safely searches through any given array.
            Edge cases like empty arrays are handled gracefully.
            The algorithm returns -1 when nothing is found.
        """,

        "wrong_return": """
            This binary search correctly locates the target.
            When the target is found it returns its position.
            The index returned matches the target location.
            The algorithm is correct and bug free.
        """,

        "overflow": """
            This binary search works correctly.
            The mid calculation finds the middle element.
            The search space reduces properly each iteration.
            The algorithm terminates and returns correct results.
        """
    }

    # Detect which case we're dealing with based on code content
    if "mid + 1" in code:
        return simulated_responses["wrong_return"]
    elif "hi = mid" in code and "lo < hi" in code:
        return simulated_responses["infinite_loop"]
    elif "lo + (hi - lo)" not in code and "(lo + hi)" in code:
        return simulated_responses["overflow"]
    else:
        return simulated_responses["correct"]


def parse_claims(explanation):
    """
    Breaks the AI explanation into individual claims.
    Each sentence = one claim to verify.
    """
    # Split explanation into individual sentences
    sentences = explanation.strip().split('\n')

    claims = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # ignore very short lines
            claims.append(sentence)

    return claims


def verify_claims(claims, audit_result):
    """
    Checks each AI claim against the audit result.
    If audit says FAIL but AI claims success â†’ hallucination caught!
    """
    verified = []
    hallucinations = []

    # These are phrases AI uses when it thinks code is correct
    positive_phrases = [
        "correctly", "safely", "properly", "always", 
        "correct", "handled", "bug free", "terminate",
        "narrows correctly", "shrinks correctly"
    ]

    for claim in claims:
        claim_lower = claim.lower()

        # If audit FAILED but AI is saying positive things
        # â†’ That's a hallucination!
        if audit_result['verdict'] != 'PASS':
            is_hallucination = any(
                phrase in claim_lower 
                for phrase in positive_phrases
            )
            if is_hallucination:
                hallucinations.append({
                    "claim": claim,
                    "reason": "AI claims correctness but auditor found violations"
                })
            else:
                verified.append(claim)
        else:
            # Audit passed so AI claims are likely correct
            verified.append(claim)

    return {
        "total_claims": len(claims),
        "verified_claims": len(verified),
        "hallucinated_claims": len(hallucinations),
        "hallucinations": hallucinations,
        "safe_to_deliver": len(hallucinations) == 0
    }


# ============================================================
# TEST CLAIM PARSER with all 5 cases
# ============================================================
if __name__ == "__main__":
    from tracer import trace_binary_search
    from auditor import audit_trace
    from tester import (
        binary_search_correct,
        binary_search_infinite_loop,
        binary_search_empty_array,
        binary_search_wrong_return,
        binary_search_overflow
    )
    import inspect

    cases = [
        ("CASE 1 - Correct Code",       binary_search_correct,       [1,3,5,7,9,11,13], 7),
        ("CASE 2 - Infinite Loop Bug",  binary_search_infinite_loop, [1,3,5,7,9,11,13], 2),
        ("CASE 3 - Empty Array",        binary_search_empty_array,   [],                 7),
        ("CASE 4 - Wrong Return Value", binary_search_wrong_return,  [1,3,5,7,9,11,13], 7),
        ("CASE 5 - Overflow Risk",      binary_search_overflow,      [1,3,5,7,9,11,13], 7),
    ]

    for name, func, arr, target in cases:
        print(f"\n{'='*50}")
        print(f"Testing: {name}")
        print(f"{'='*50}")

        # Step 1 - Get execution trace
        trace = trace_binary_search(func, arr, target)

        # Step 2 - Audit the trace
        audit = audit_trace(trace, func.__name__, arr, target)

        # Step 3 - Get AI explanation
        code = inspect.getsource(func)
        explanation = get_ai_explanation(code, arr, target)

        # Step 4 - Parse AI claims
        claims = parse_claims(explanation)

        # Step 5 - Verify claims against audit
        result = verify_claims(claims, audit)

        print(f"Audit Verdict:       {audit['verdict']}")
        print(f"Total AI Claims:     {result['total_claims']}")
        print(f"Hallucinated Claims: {result['hallucinated_claims']}")
        print(f"Safe to Deliver:     {result['safe_to_deliver']}")

        if result['hallucinations']:
            print("\nðŸš¨ Hallucinations Caught:")
            for h in result['hallucinations']:
                print(f"  âŒ {h['claim']}")
                print(f"     Reason: {h['reason']}")
        else:
            print("\nâœ… No hallucinations detected!")
