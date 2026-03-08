import sys

def trace_binary_search(func, arr, target):
    """
    Traces the execution of a binary search function step by step.
    Records every variable change at every step.
    """
    steps = []  # This will store every step of the algorithm
    step_number = 0  # Counter to track which step we're on

    # We create a custom tracer function that Python calls at every line
    def tracer(frame, event, arg):
        nonlocal step_number

        # We only care about lines inside our binary search function
        if frame.f_code.co_name != func.__name__:
            return tracer

        if event == 'line':
            # Capture all local variables at this exact moment
            local_vars = frame.f_locals.copy()
            step_number += 1

            # Save this step with all variable values
            steps.append({
                "step": step_number,
                "variables": local_vars
            })

        return tracer

    # Activate our tracer, run the function, then deactivate
    sys.settrace(tracer)
    result = func(arr, target)
    sys.settrace(None)

    return {
        "result": result,
        "total_steps": step_number,
        "steps": steps
    }


# This is the binary search we will test
def binary_search(arr, target):
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


# Test it right here
if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11, 13]
    target = 7

    print(f"Searching for {target} in {arr}")
    print("-" * 40)

    trace = trace_binary_search(binary_search, arr, target)

    print(f"Found at index: {trace['result']}")
    print(f"Total steps taken: {trace['total_steps']}")
    print("\nStep by step trace:")
    for step in trace['steps']:
        print(f"Step {step['step']}: {step['variables']}")