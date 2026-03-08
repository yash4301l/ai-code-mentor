import { useState } from "react";
import axios from "axios";
import Editor from "@monaco-editor/react";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const PLACEHOLDER_CODE = `# Type your binary search code here
# Example:
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
    return -1`;

export default function App() {
  const [code, setCode] = useState(PLACEHOLDER_CODE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        code: code,
        arr: [1, 3, 5, 7, 9, 11, 13],
        target: 7,
      });
      setResult(response.data);
    } catch (error) {
      const apiError = error?.response?.data;
      if (apiError && typeof apiError === "object") {
        setResult({
          verdict: "ERROR",
          error: apiError.error || apiError.detail || "Request failed.",
          hint: apiError.hint || (typeof apiError.detail === "string" ? apiError.detail : undefined),
        });
      } else {
        setResult({ verdict: "ERROR", error: "Could not connect to backend. Make sure it is running!" });
      }
    }
    setLoading(false);
  };

  return (
    <div style={styles.container}>

      {/* HEADER */}
      <div style={styles.header}>
        <div style={styles.headerInner}>
          <div>
            <h1 style={styles.title}>AI Code Mentor</h1>
            <p style={styles.subtitle}>
              Reasoning Safety Layer â€” paste any binary search code and we'll
              verify if the AI explanation is safe to deliver
            </p>
          </div>
          <div style={styles.badge}>
            <span style={styles.badgeDot} />
            Pipeline Active
          </div>
        </div>
      </div>

      <div style={styles.main}>

        {/* LEFT â€” Editor */}
        <div style={styles.left}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Your Code</span>
            <span style={styles.cardHint}>Paste any binary search implementation</span>
          </div>

          <div style={styles.editorWrapper}>
            <Editor
              height="420px"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(val) => setCode(val ?? "")}
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 16 },
              }}
            />
          </div>

          <div style={styles.examplesRow}>
            <span style={styles.examplesLabel}>Load example:</span>
            {[
              { label: "Correct", code: `def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1` },
              { label: "Infinite Loop", code: `def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid\n    return -1` },
              { label: "Wrong Return", code: `def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            return mid + 1\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1` },
              { label: "Empty Array", code: `def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1` },
            ].map((ex) => (
              <button
                key={ex.label}
                onClick={() => { setCode(ex.code); setResult(null); }}
                style={styles.exampleBtn}
              >
                {ex.label}
              </button>
            ))}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              ...styles.analyzeBtn,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Analyzing..." : "Analyze Code"}
          </button>
        </div>

        {/* RIGHT â€” Results */}
        <div style={styles.right}>
          <div style={styles.cardHeader}>
            <span style={styles.cardTitle}>Pipeline Results</span>
          </div>

          {/* Empty state */}
          {!result && !loading && (
            <div style={styles.emptyState}>
              <div style={styles.emptyIcon}>[ ]</div>
              <p style={styles.emptyTitle}>Ready to Analyze</p>
              <p style={styles.emptyDesc}>
                Paste your code on the left and click Analyze. Our 5-step
                pipeline will verify if the AI explanation is safe.
              </p>
              <div style={styles.stepsPreview}>
                {["Execution Tracing", "Invariant Auditing", "AI Explanation", "Claim Parsing", "Safe Delivery"].map((s, i) => (
                  <div key={i} style={styles.stepPreviewItem}>
                    <span style={styles.stepNum}>{i + 1}</span> {s}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div style={styles.emptyState}>
              <p style={styles.emptyTitle}>Running Pipeline...</p>
              {["Tracing execution", "Auditing invariants", "Getting AI explanation", "Parsing claims", "Verifying safety"].map((s, i) => (
                <div key={i} style={styles.loadingStep}>
                  <span style={styles.loadingDot} /> {s}
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {result && result.verdict === "ERROR" && (
            <div style={{ ...styles.verdictBox, background: "#1a0a0a", border: "2px solid #ef4444" }}>
              <div style={styles.verdictLabel} >ERROR</div>
              <div style={styles.verdictDesc}>{result.error}</div>
              {result.hint && <div style={styles.hintBox}>{result.hint}</div>}
            </div>
          )}

          {/* Results */}
          {result && result.verdict !== "ERROR" && (
            <div>

              {/* Verdict */}
              <div style={{
                ...styles.verdictBox,
                background: result.verdict === "APPROVED" ? "#031a0f" : "#1a0505",
                border: `2px solid ${result.verdict === "APPROVED" ? "#10b981" : "#ef4444"}`,
              }}>
                <div style={{
                  ...styles.verdictLabel,
                  color: result.verdict === "APPROVED" ? "#10b981" : "#ef4444"
                }}>
                  {result.verdict === "APPROVED" ? "EXPLANATION APPROVED" : "EXPLANATION BLOCKED"}
                </div>
                <div style={styles.verdictDesc}>
                  {result.verdict === "APPROVED"
                    ? "This explanation is verified and safe to deliver to students."
                    : "AI hallucination detected â€” this explanation has been blocked."}
                </div>
              </div>

              {/* Hallucination detail */}
              {result.hallucination_detail && (
                <div style={styles.section}>
                  <div style={styles.sectionTitle}>Hallucination Analysis</div>

                  <div style={styles.hallRow}>
                    <div style={styles.hallLabel}>Bug Detected</div>
                    <div style={styles.hallBugName}>
                      {result.hallucination_detail.bug_name}
                    </div>
                  </div>

                  <div style={styles.hallCard}>
                    <div style={styles.hallCardTitle}>What the AI Claimed</div>
                    <div style={styles.hallCardText}>
                      {result.hallucination_detail.what_ai_claimed}
                    </div>
                  </div>

                  <div style={{ ...styles.hallCard, borderColor: "#ef4444" }}>
                    <div style={styles.hallCardTitle}>What Actually Happened</div>
                    <div style={styles.hallCardText}>
                      {result.hallucination_detail.what_actually_happened}
                    </div>
                  </div>

                  <div style={{ ...styles.hallCard, borderColor: "#f59e0b" }}>
                    <div style={styles.hallCardTitle}>Why This is Dangerous</div>
                    <div style={styles.hallCardText}>
                      {result.hallucination_detail.why_dangerous}
                    </div>
                  </div>

                  <div style={{ ...styles.hallCard, borderColor: "#10b981" }}>
                    <div style={styles.hallCardTitle}>How to Fix It</div>
                    <div style={styles.hallCardText}>
                      {result.hallucination_detail.how_to_fix}
                    </div>
                  </div>
                </div>
              )}

              {/* Approved explanation */}
              {result.explanation && (
                <div style={styles.section}>
                  <div style={styles.sectionTitle}>Verified Explanation</div>
                  <div style={styles.explanationBox}>
                    {result.explanation}
                  </div>
                </div>
              )}

              {/* Audit */}
              <div style={styles.section}>
                <div style={styles.sectionTitle}>Audit Result</div>
                <div style={styles.auditBadge(result.audit.verdict)}>
                  {result.audit.verdict}
                </div>
                {result.audit.violations.map((v, i) => (
                  <div key={i} style={styles.violationRow}>
                    <div style={styles.violationRule}>
                      [{v.severity}] {v.rule}
                    </div>
                    <div style={styles.violationDetail}>Expected: {v.expected}</div>
                    <div style={styles.violationDetail}>Actual: {v.actual}</div>
                  </div>
                ))}
                {result.audit.violations.length === 0 && (
                  <div style={styles.allGood}>No violations found!</div>
                )}
              </div>

              {/* Trace */}
              <div style={styles.section}>
                <div style={styles.sectionTitle}>
                  Execution Trace
                  <span style={styles.traceCount}>
                    {result.trace.total_steps} steps â€” returned index {result.trace.result}
                  </span>
                </div>
                <div style={styles.traceBox}>
                  {result.trace.steps.map((step, i) => (
                    <div key={i} style={styles.traceRow}>
                      <span style={styles.traceStepNum}>Step {step.step}</span>
                      {Object.entries(step.variables)
                        .filter(([k]) => !["arr", "target"].includes(k))
                        .map(([k, v]) => (
                          <span key={k} style={styles.traceVar}>
                            {k}=<span style={styles.traceVal}>{String(v)}</span>
                          </span>
                        ))}
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { background: "#070b12", minHeight: "100vh", color: "#e2e8f0", fontFamily: "'JetBrains Mono', 'Fira Code', monospace" },
  header: { borderBottom: "1px solid #1a2640", padding: "20px 32px", background: "#080d18" },
  headerInner: { display: "flex", justifyContent: "space-between", alignItems: "center", maxWidth: 1400, margin: "0 auto" },
  title: { margin: 0, fontSize: 24, fontWeight: 800, color: "#00d4ff" },
  subtitle: { margin: "6px 0 0", color: "#4a6080", fontSize: 13 },
  badge: { display: "flex", alignItems: "center", gap: 8, background: "#031a0f", border: "1px solid #10b981", borderRadius: 20, padding: "6px 14px", fontSize: 12, color: "#10b981" },
  badgeDot: { width: 8, height: 8, borderRadius: "50%", background: "#10b981", display: "inline-block" },
  main: { display: "flex", gap: 24, padding: "24px 32px", maxWidth: 1400, margin: "0 auto" },
  left: { flex: "0 0 520px" },
  right: { flex: 1, minWidth: 0 },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  cardTitle: { fontSize: 14, fontWeight: 700, color: "#00d4ff" },
  cardHint: { fontSize: 11, color: "#4a6080" },
  editorWrapper: { borderRadius: 8, overflow: "hidden", border: "1px solid #1a2640", marginBottom: 12 },
  examplesRow: { display: "flex", alignItems: "center", gap: 8, marginBottom: 12, flexWrap: "wrap" },
  examplesLabel: { fontSize: 11, color: "#4a6080" },
  exampleBtn: { fontSize: 11, padding: "4px 10px", borderRadius: 6, border: "1px solid #1a2640", background: "#0d1420", color: "#94a3b8", cursor: "pointer" },
  analyzeBtn: { width: "100%", padding: 14, borderRadius: 8, border: "none", background: "#00d4ff", color: "#000", fontSize: 15, fontWeight: 800, transition: "all 0.2s" },
  emptyState: { textAlign: "center", padding: "40px 24px", border: "1px dashed #1a2640", borderRadius: 12 },
  emptyIcon: { fontSize: 40, marginBottom: 12, color: "#00d4ff" },
  emptyTitle: { fontSize: 16, fontWeight: 700, color: "#e2e8f0", margin: "0 0 8px" },
  emptyDesc: { fontSize: 13, color: "#4a6080", lineHeight: 1.6, margin: "0 0 20px" },
  stepsPreview: { display: "flex", flexDirection: "column", gap: 8, textAlign: "left", maxWidth: 240, margin: "0 auto" },
  stepPreviewItem: { fontSize: 12, color: "#4a6080", display: "flex", alignItems: "center", gap: 8 },
  stepNum: { background: "#0d1f35", border: "1px solid #1a2640", borderRadius: 4, padding: "2px 7px", fontSize: 11, color: "#00d4ff" },
  loadingStep: { fontSize: 13, color: "#4a6080", margin: "6px 0", display: "flex", alignItems: "center", gap: 8 },
  loadingDot: { width: 6, height: 6, borderRadius: "50%", background: "#00d4ff", display: "inline-block" },
  verdictBox: { borderRadius: 12, padding: "24px", textAlign: "center", marginBottom: 16 },
  verdictLabel: { fontSize: 20, fontWeight: 800, marginBottom: 6 },
  verdictDesc: { fontSize: 13, color: "#94a3b8" },
  hintBox: { marginTop: 12, fontSize: 12, color: "#f59e0b", background: "#1a1200", padding: "8px 12px", borderRadius: 6 },
  section: { background: "#0a0f1a", border: "1px solid #1a2640", borderRadius: 10, padding: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 12, display: "flex", justifyContent: "space-between", alignItems: "center" },
  hallRow: { display: "flex", alignItems: "center", gap: 12, marginBottom: 12 },
  hallLabel: { fontSize: 11, color: "#4a6080" },
  hallBugName: { fontSize: 14, fontWeight: 700, color: "#ef4444", background: "#1a0505", padding: "4px 12px", borderRadius: 6, border: "1px solid #ef4444" },
  hallCard: { background: "#070b12", border: "1px solid #1a2640", borderRadius: 8, padding: 12, marginBottom: 8 },
  hallCardTitle: { fontSize: 11, fontWeight: 700, color: "#94a3b8", marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 },
  hallCardText: { fontSize: 13, color: "#cbd5e1", lineHeight: 1.6 },
  explanationBox: { background: "#031a0f", border: "1px solid #10b981", borderRadius: 8, padding: 14, fontSize: 13, color: "#10b981", lineHeight: 1.7 },
  auditBadge: (v) => ({ display: "inline-block", padding: "3px 12px", borderRadius: 6, fontSize: 12, fontWeight: 700, marginBottom: 10, background: v === "PASS" ? "#031a0f" : "#1a0505", color: v === "PASS" ? "#10b981" : "#ef4444", border: `1px solid ${v === "PASS" ? "#10b981" : "#ef4444"}` }),
  violationRow: { background: "#070b12", borderRadius: 6, padding: 10, marginBottom: 6 },
  violationRule: { fontSize: 12, color: "#ef4444", marginBottom: 4 },
  violationDetail: { fontSize: 11, color: "#4a6080" },
  allGood: { fontSize: 13, color: "#10b981" },
  traceCount: { fontSize: 11, color: "#4a6080", fontWeight: 400 },
  traceBox: { background: "#070b12", borderRadius: 6, padding: 10, maxHeight: 180, overflowY: "auto" },
  traceRow: { display: "flex", gap: 12, alignItems: "center", padding: "4px 0", borderBottom: "1px solid #0d1420", flexWrap: "wrap" },
  traceStepNum: { fontSize: 11, color: "#00d4ff", minWidth: 52 },
  traceVar: { fontSize: 11, color: "#94a3b8" },
  traceVal: { color: "#f59e0b" },
};



