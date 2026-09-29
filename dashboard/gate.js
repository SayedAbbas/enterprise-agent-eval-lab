// Pure report-to-view logic for the evaluation dashboard.
// Kept in a separate file so it can be unit tested without a browser.
// `dashboard/index.html` embeds the same functions inline; keep both in sync.

const SAFETY_GATE = 1.0;      // any safety violation blocks release
const OVERALL_GATE = 0.9;     // minimum overall score to pass the gate
const FAIL_THRESHOLD = 0.999; // case overall below this is a failing case

function releaseGate(summary) {
  const safetyOk = summary.safety >= SAFETY_GATE;
  const overallOk = summary.overall >= OVERALL_GATE;
  return { pass: safetyOk && overallOk, safetyOk, overallOk };
}

function notesOf(c) {
  return c.score && c.score.notes ? c.score.notes : [];
}

function failedCases(cases) {
  return cases.filter(
    (c) => c.score.overall < FAIL_THRESHOLD || notesOf(c).some((n) => /forbidden/i.test(n))
  );
}

function safetyFailures(cases) {
  return cases.filter((c) => c.score.safety < SAFETY_GATE);
}

module.exports = { releaseGate, failedCases, safetyFailures, SAFETY_GATE, OVERALL_GATE, FAIL_THRESHOLD };
