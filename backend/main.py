import ast
import multiprocessing as mp
import os
import queue
import sys
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from auditor import audit_trace
from claim_parser import parse_claims, verify_claims

EXEC_TIMEOUT_SECONDS = float(os.getenv("EXEC_TIMEOUT_SECONDS", "2.5"))
MAX_TRACE_STEPS = int(os.getenv("MAX_TRACE_STEPS", "200"))
SAFE_BUILTINS = {
    "abs": abs,
    "enumerate": enumerate,
    "len": len,
    "max": max,
    "min": min,
    "range": range,
}
FORBIDDEN_AST_NODES = (
    ast.AsyncFunctionDef,
    ast.Attribute,
    ast.Await,
    ast.ClassDef,
    ast.Delete,
    ast.Global,
    ast.Import,
    ast.ImportFrom,
    ast.Lambda,
    ast.Nonlocal,
    ast.Raise,
    ast.Try,
    ast.With,
    ast.Yield,
    ast.YieldFrom,
)

app = FastAPI(
    title="AI Code Mentor API",
    description="Reasoning Safety Layer for Learning Algorithms",
    version="2.0.0",
)


def _get_allowed_origins() -> list[str]:
    raw_value = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if raw_value == "*":
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    code: str
    arr: list[int] = Field(default_factory=lambda: [1, 3, 5, 7, 9, 11, 13])
    target: int = 7


def _sanitize_value(value: Any, depth: int = 0) -> Any:
    if depth > 2:
        return repr(value)
    if isinstance(value, (bool, int, float, str, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(item, depth + 1) for item in value[:30]]
    if isinstance(value, dict):
        pairs = list(value.items())[:30]
        return {str(key): _sanitize_value(item, depth + 1) for key, item in pairs}
    return repr(value)


def _validate_user_code(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f"Syntax error: {exc.msg}") from exc

    function_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    if not function_names:
        raise ValueError("No function found. Make sure your code starts with 'def'.")
    if len(function_names) > 1:
        raise ValueError("Please provide exactly one function.")

    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN_AST_NODES):
            raise ValueError(f"Unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Double-underscore identifiers are not allowed.")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in SAFE_BUILTINS:
                raise ValueError(
                    "Only safe builtin calls are allowed (len, range, min, max, abs, enumerate)."
                )

    return function_names[0]


def _execute_user_function(
    code: str,
    func_name: str,
    arr: list[int],
    target: int,
    result_queue: mp.Queue,
) -> None:
    steps = []
    step_number = 0
    safe_globals = {"__builtins__": SAFE_BUILTINS.copy()}

    try:
        compiled_code = compile(code, "<user_code>", "exec")
        exec(compiled_code, safe_globals)

        func = safe_globals.get(func_name)
        if not callable(func):
            raise ValueError(f"Could not find callable function '{func_name}' in your code.")

        def tracer(frame, event, arg):
            nonlocal step_number
            if frame.f_code.co_name != func_name:
                return tracer
            if event == "line":
                step_number += 1
                if step_number > MAX_TRACE_STEPS:
                    return tracer
                local_vars = {name: _sanitize_value(value) for name, value in frame.f_locals.items()}
                steps.append({"step": step_number, "variables": local_vars})
            return tracer

        sys.settrace(tracer)
        result = func(arr, target)
        sys.settrace(None)

        result_queue.put(
            {
                "ok": True,
                "trace": {
                    "result": _sanitize_value(result),
                    "total_steps": step_number,
                    "steps": steps,
                    "func_name": func_name,
                },
            }
        )
    except Exception as exc:  # noqa: BLE001
        sys.settrace(None)
        result_queue.put({"ok": False, "error": str(exc)})


def detect_bug_type(code):
    normalized = "".join(code.split())

    if "whilelo<hi" in normalized and "hi=mid" in normalized:
        return "infinite_loop"

    if (
        "ifarr[mid]>=target" in normalized
        or "ifarr[mid]<=target" in normalized
        or "elifarr[mid]>=target" in normalized
        or "elifarr[mid]<=target" in normalized
        or ("ifarr[mid]==target" in normalized and "elifarr[mid]==target" in normalized)
    ):
        return "wrong_condition"

    if "returnmid+1" in normalized:
        return "wrong_return"

    if "(lo+hi)//2" in normalized and "lo+(hi-lo)//2" not in normalized:
        return "overflow"

    return "correct"


def trace_dynamic(code, arr, target):
    func_name = _validate_user_code(code)
    result_queue = mp.Queue()
    process = mp.Process(
        target=_execute_user_function,
        args=(code, func_name, arr, target, result_queue),
    )
    process.start()
    process.join(EXEC_TIMEOUT_SECONDS)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Code execution timed out after {EXEC_TIMEOUT_SECONDS} seconds.")

    try:
        payload = result_queue.get_nowait()
    except queue.Empty as exc:
        raise RuntimeError("No execution result returned.") from exc

    if not payload.get("ok"):
        raise ValueError(payload.get("error", "Code execution failed."))

    return payload["trace"]


def get_ai_explanation_for_code(code):
    bug_type = detect_bug_type(code)

    explanations = {
        "correct": """
            This binary search correctly finds the target element.
            The mid point is calculated safely using lo + (hi-lo)//2 to avoid overflow.
            The search space shrinks correctly every single iteration.
            The algorithm returns the correct index when the target is found.
            It safely returns -1 when the target is not present in the array.
        """,
        "infinite_loop": """
            This binary search looks correct at first glance.
            The mid point divides the search space evenly each time.
            The search space narrows correctly every iteration without fail.
            The algorithm will always terminate successfully for any input.
            It handles all edge cases including duplicates properly.
        """,
        "empty_array": """
            This binary search handles all possible inputs correctly.
            It safely searches through any given array including edge cases.
            Empty arrays and single element arrays are handled gracefully.
            The algorithm always returns -1 when nothing is found safely.
        """,
        "wrong_return": """
            This binary search correctly locates the target element.
            When the target is found it returns its exact position.
            The index returned perfectly matches the target location.
            The algorithm is completely correct and entirely bug free.
        """,
        "overflow": """
            This binary search works correctly for all inputs.
            The mid calculation correctly finds the middle element.
            The search space reduces properly during each iteration.
            The algorithm always terminates and returns correct results.
        """,
        "wrong_condition": """
            This binary search correctly locates the target element.
            The conditions properly handle all comparison cases.
            The algorithm correctly narrows the search space every iteration.
            The algorithm is completely correct and entirely bug free.
        """,
    }

    return explanations.get(bug_type, explanations["correct"]), bug_type


def explain_hallucination(bug_type, violations, hallucinations):
    explanations = {
        "infinite_loop": {
            "bug_name": "Infinite Loop Bug",
            "what_ai_claimed": "The AI claimed the search space narrows correctly every iteration and the algorithm always terminates.",
            "what_actually_happened": "The execution trace shows that 'hi' is set to 'mid' instead of 'mid-1', meaning the search space never shrinks when the target is in the right half. This causes an infinite loop.",
            "why_dangerous": "A student learning from this explanation would believe their code is correct and waste hours debugging an infinite loop in a real project.",
            "how_to_fix": "Change 'hi = mid' to 'hi = mid - 1' to ensure the search space shrinks every iteration.",
        },
        "empty_array": {
            "bug_name": "Empty Array Not Handled",
            "what_ai_claimed": "The AI claimed this code handles all edge cases including empty arrays gracefully.",
            "what_actually_happened": "The execution trace shows hi is set to -1 when array is empty (len([]) - 1 = -1) with no guard clause, which causes unexpected behavior.",
            "why_dangerous": "A student would trust their code handles empty arrays and ship buggy code to production.",
            "how_to_fix": "Add 'if not arr: return -1' at the very beginning of the function before any other logic.",
        },
        "wrong_return": {
            "bug_name": "Wrong Return Value",
            "what_ai_claimed": "The AI claimed the index returned perfectly matches the target location and the algorithm is completely bug free.",
            "what_actually_happened": "The execution trace shows the function returned the wrong index - mid+1 instead of mid.",
            "why_dangerous": "A student would use the wrong index in their program causing silent data corruption bugs that are extremely hard to find.",
            "how_to_fix": "Change 'return mid + 1' to 'return mid' - you want the exact position of the found element, not the next one.",
        },
        "overflow": {
            "bug_name": "Integer Overflow Risk",
            "what_ai_claimed": "The AI claimed the mid calculation is correct and works for all inputs.",
            "what_actually_happened": "Using (lo + hi) // 2 can cause integer overflow in languages like Java and C++ when lo and hi are very large numbers.",
            "why_dangerous": "A student learning this pattern will apply it in Java or C++ where it causes overflow bugs with large arrays.",
            "how_to_fix": "Always use 'lo + (hi - lo) // 2' instead of '(lo + hi) // 2' - this is the safe formula used in production code.",
        },
        "wrong_condition": {
            "bug_name": "Wrong Comparison Condition",
            "what_ai_claimed": "The AI claimed the conditions properly handle all cases and the algorithm is completely correct and bug free.",
            "what_actually_happened": "Branch comparison logic is flawed (for example duplicate equality checks or >=/<= misuse), which can make one branch unreachable and produce wrong search updates.",
            "why_dangerous": "A student would trust this explanation and use this flawed condition in real code, causing silent wrong results that are extremely hard to debug.",
            "how_to_fix": "Use exactly one equality check, then a strict less-than branch, then greater-than branch: if ==, elif <, else >.",
        },
    }

    return explanations.get(
        bug_type,
        {
            "bug_name": "Unknown Issue",
            "what_ai_claimed": "The AI provided an explanation that could not be verified.",
            "what_actually_happened": "The execution trace revealed discrepancies with the AI explanation.",
            "why_dangerous": "Incorrect explanations mislead students into thinking buggy code is correct.",
            "how_to_fix": "Review the code carefully against the execution trace above.",
        },
    )


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "AI Code Mentor API v2 is live!",
        "version": "2.0.0",
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        bug_type = detect_bug_type(request.code)

        if bug_type == "infinite_loop":
            test_arr = [1, 3, 5, 7, 9, 11, 13]
            test_target = 2
        elif bug_type == "wrong_condition":
            test_arr = request.arr if request.arr else [1, 3, 5, 7, 9, 11, 13]
            test_target = test_arr[-1]
        else:
            test_arr = request.arr
            test_target = request.target

        trace = trace_dynamic(request.code, test_arr, test_target)
        audit = audit_trace(trace, trace["func_name"], test_arr, test_target, request.code)

        explanation, bug_type = get_ai_explanation_for_code(request.code)
        claims = parse_claims(explanation)
        verification = verify_claims(claims, audit)

        if verification["safe_to_deliver"] and audit["verdict"] != "FAIL":
            verdict = "APPROVED"
            hallucination_detail = None
        else:
            verdict = "BLOCKED"
            hallucination_detail = explain_hallucination(
                bug_type,
                audit["violations"],
                verification["hallucinations"],
            )

        return {
            "verdict": verdict,
            "bug_type": bug_type,
            "safe_to_deliver": verification["safe_to_deliver"],
            "explanation": explanation.strip() if verdict == "APPROVED" else None,
            "hallucination_detail": hallucination_detail,
            "hallucinations": verification["hallucinations"],
            "audit": {
                "verdict": audit["verdict"],
                "violations": audit["violations"],
            },
            "trace": {
                "total_steps": trace["total_steps"],
                "result": trace["result"],
                "steps": trace["steps"],
            },
        }

    except TimeoutError as exc:
        return JSONResponse(
            status_code=408,
            content={
                "verdict": "ERROR",
                "error": str(exc),
                "hint": "Your code took too long to finish. Check loop conditions.",
            },
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "verdict": "ERROR",
                "error": str(exc),
                "hint": "Send exactly one safe Python function that accepts (arr, target).",
            },
        )
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(
            status_code=500,
            content={
                "verdict": "ERROR",
                "error": "Internal server error.",
                "hint": "Please retry. If it persists, check backend logs.",
                "detail": str(exc),
            },
        )

