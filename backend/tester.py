from tracer import trace_binary_search

# ============================================================
# ALL 5 BINARY SEARCH CASES
# ============================================================

# CASE 1 — Correct Code (Control Case)
# This is the GOOD one — should PASS everything
def binary_search_correct(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# CASE 2 — Infinite Loop Bug
# hi = mid instead of mid - 1 causes infinite loop
def binary_search_infinite_loop(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo < hi:              # bug 1: should be lo <= hi
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid            # bug 2: should be mid - 1
    return -1


# CASE 3 — Empty Array Crash
# Doesn't check if array is empty before searching
def binary_search_empty_array(arr, target):
    lo, hi = 0, len(arr) - 1   # crashes if arr is []
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# CASE 4 — Wrong Return Value
# Returns mid + 1 instead of mid
def binary_search_wrong_return(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid + 1      # bug: should be mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# CASE 5 — Integer Overflow Risk
# Uses (lo + hi) // 2 which can overflow in other languages
def binary_search_overflow(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2   # bug: should be lo + (hi-lo)//2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ============================================================
# TEST ALL 5 CASES
# ============================================================
def run_all_tests():
    arr = [1, 3, 5, 7, 9, 11, 13]
    target = 7

    cases = [
        ("CASE 1 - Correct Code",        binary_search_correct,       arr, target),
        ("CASE 2 - Infinite Loop Bug",   binary_search_infinite_loop, arr, target),
        ("CASE 3 - Empty Array Crash",   binary_search_empty_array,   [],  target),
        ("CASE 4 - Wrong Return Value",  binary_search_wrong_return,  arr, target),
        ("CASE 5 - Overflow Risk",       binary_search_overflow,      arr, target),
    ]

    for name, func, test_arr, test_target in cases:
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print(f"{'='*50}")
        try:
            trace = trace_binary_search(func, test_arr, test_target)
            print(f"✅ Result:      {trace['result']}")
            print(f"📊 Total Steps: {trace['total_steps']}")
            for step in trace['steps']:
                print(f"   Step {step['step']}: {step['variables']}")
        except Exception as e:
            print(f"❌ CRASHED: {e}")


if __name__ == "__main__":
    run_all_tests()