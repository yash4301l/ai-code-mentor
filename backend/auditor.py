def audit_trace(trace, func_name, arr, target, code=""):
    steps = trace['steps']
    result = trace['result']
    violations = []

    # RULE 1 - Correct result check
    expected_index = -1
    for i, val in enumerate(arr):
        if val == target:
            expected_index = i
            break

    if result != expected_index:
        violations.append({
            "rule": "Return value must be correct index",
            "expected": f"index {expected_index}",
            "actual": f"returned {result}",
            "severity": "HIGH"
        })

    # RULE 2 - mid must always be between lo and hi (only while lo <= hi)
    for step in steps:
        vars = step['variables']
        if 'lo' in vars and 'hi' in vars and 'mid' in vars:
            lo = vars['lo']
            hi = vars['hi']
            mid = vars['mid']
            if lo <= hi and (mid < lo or mid > hi):
                violations.append({
                    "rule": "mid must be between lo and hi",
                    "expected": "lo <= mid <= hi",
                    "actual": f"mid={mid}, lo={lo}, hi={hi} at step {step['step']}",
                    "severity": "HIGH"
                })

    # RULE 3 - Search space should make progress across loop states
    # We only evaluate snapshots where lo/hi/mid exist, then dedupe adjacent repeats
    loop_states = []
    for step in steps:
        vars = step['variables']
        if 'lo' in vars and 'hi' in vars and 'mid' in vars:
            loop_states.append((vars['lo'], vars['hi'], vars['mid'], step['step']))

    stagnant_runs = 0
    for idx in range(1, len(loop_states)):
        prev_lo, prev_hi, prev_mid, _ = loop_states[idx - 1]
        lo, hi, mid, step_num = loop_states[idx]
        if lo == prev_lo and hi == prev_hi and mid == prev_mid:
            stagnant_runs += 1
            if stagnant_runs >= 3:
                violations.append({
                    "rule": "Search space progression risk",
                    "expected": "lo/hi/mid should change as loop progresses",
                    "actual": f"lo={lo}, hi={hi}, mid={mid} repeated through step {step_num}",
                    "severity": "HIGH"
                })
                break
        else:
            stagnant_runs = 0

    # RULE 4 - Wrong condition check
    if code:
        lines = code.split('\n')
        has_if_eq = any("if arr[mid] == target" in line.strip() for line in lines)
        has_elif_eq = any("elif arr[mid] == target" in line.strip() for line in lines)

        if has_if_eq and has_elif_eq:
            violations.append({
                "rule": "Duplicate equality condition",
                "expected": "Use 'elif arr[mid] < target' after equality check",
                "actual": "Found both 'if arr[mid] == target' and 'elif arr[mid] == target'",
                "severity": "HIGH"
            })
        else:
            for line in lines:
                stripped = line.strip()
                if ('>= target' in stripped or '<= target' in stripped) and stripped.startswith('if'):
                    violations.append({
                        "rule": "Wrong comparison operator in if condition",
                        "expected": "if arr[mid] == target (use == not >= or <=)",
                        "actual": f"Found: '{stripped}' - >= or <= can make branches unreachable",
                        "severity": "HIGH"
                    })
                    break

        normalized = "".join(code.split())
        reversed_branch = (
            "ifarr[mid]>target:lo=mid+1" in normalized
            or "elifarr[mid]>target:lo=mid+1" in normalized
            or "ifarr[mid]<target:hi=mid-1" in normalized
            or "elifarr[mid]<target:hi=mid-1" in normalized
        )
        if reversed_branch:
            violations.append({
                "rule": "Reversed branch update",
                "expected": "arr[mid] > target should move hi left; arr[mid] < target should move lo right",
                "actual": "Detected comparison branch updating the wrong pointer direction",
                "severity": "HIGH"
            })
    # RULE 5 - Potential infinite-loop source pattern from code
    # This is a heuristic only; trace-based rules carry more weight.
    if code:
        lines = code.split('\n')
        has_lo_less_hi = any('lo < hi' in line for line in lines)
        has_hi_equals_mid = any(
            line.strip() == 'hi = mid' or (line.strip().endswith('= mid') and 'hi' in line)
            for line in lines
        )
        if has_lo_less_hi and has_hi_equals_mid:
            violations.append({
                "rule": "Potential infinite-loop pattern",
                "expected": "Prefer while lo <= hi with hi = mid - 1",
                "actual": "Detected 'while lo < hi' combined with 'hi = mid'",
                "severity": "MEDIUM"
            })

    # RULE 6 - Empty array safety expectation
    # Only warn when empty array behavior returns a non -1 result.
    if len(arr) == 0 and result != -1:
        violations.append({
            "rule": "Empty array handling",
            "expected": "return -1 for empty array",
            "actual": f"returned {result}",
            "severity": "MEDIUM"
        })

    # FINAL VERDICT
    high_severity = [v for v in violations if v['severity'] == 'HIGH']

    if len(high_severity) > 0:
        verdict = "FAIL"
    elif len(violations) > 0:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "func_name": func_name,
        "total_violations": len(violations),
        "violations": violations,
        "result": result,
        "expected": expected_index
    }


if __name__ == "__main__":
    from tracer import trace_binary_search
    from tester import (
        binary_search_correct,
        binary_search_infinite_loop,
        binary_search_empty_array,
        binary_search_wrong_return,
        binary_search_overflow
    )

    cases = [
        ("CASE 1 - Correct Code",       binary_search_correct,       [1,3,5,7,9,11,13], 7),
        ("CASE 2 - Infinite Loop Bug",  binary_search_infinite_loop, [1,3,5,7,9,11,13], 2),
        ("CASE 3 - Empty Array",        binary_search_empty_array,   [],                 7),
        ("CASE 4 - Wrong Return Value", binary_search_wrong_return,  [1,3,5,7,9,11,13], 7),
        ("CASE 5 - Overflow Risk",      binary_search_overflow,      [1,3,5,7,9,11,13], 7),
    ]

    for name, func, arr, target in cases:
        print(f"\n{'='*50}")
        print(f"Auditing: {name}")
        print(f"{'='*50}")
        try:
            trace = trace_binary_search(func, arr, target)
            audit = audit_trace(trace, func.__name__, arr, target)
            print(f"Verdict:  {audit['verdict']}")
            if audit['violations']:
                for v in audit['violations']:
                    print(f"  [{v['severity']}] {v['rule']}")
            else:
                print("No violations found!")
        except Exception as e:
            print(f"CRASHED: {e}")

