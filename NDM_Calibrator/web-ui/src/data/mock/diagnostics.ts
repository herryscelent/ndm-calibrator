/**
 * Mock residual and diagnostics data.
 */

export const residualSummary = {
  mean: 0.0012,
  std: 0.0417,
  maxAbs: 0.129,
  acfPeak: 0.087,
};

export interface ResidualPoint {
  t: number;
  residual: number;
}

export const residuals: ResidualPoint[] = (() => {
  const out: ResidualPoint[] = [];
  for (let i = 0; i < 60; i++) {
    const t = i * 0.5;
    // Fixed deterministic residual pattern with mild autocorrelation.
    const r =
      Math.sin(t * 0.6) * 0.02 +
      Math.sin(t * 2.1 + 0.5) * 0.012 +
      ((i * 37) % 11) * 0.002 - 0.01;
    out.push({ t, residual: +r.toFixed(4) });
  }
  return out;
})();

export const residualHistogram: { bin: string; count: number }[] = [
  { bin: "-0.15", count: 1 },
  { bin: "-0.12", count: 4 },
  { bin: "-0.09", count: 9 },
  { bin: "-0.06", count: 16 },
  { bin: "-0.03", count: 24 },
  { bin: "0.00", count: 30 },
  { bin: "0.03", count: 22 },
  { bin: "0.06", count: 13 },
  { bin: "0.09", count: 6 },
  { bin: "0.12", count: 2 },
];

export const sensitivity = {
  k: { rms: 2.31, max: 4.82, rank: 1 },
  c: { rms: 1.14, max: 2.67, rank: 2 },
};

export const identifiability = {
  conditionNumber: 31.7,
  rank: 2,
  rankTotal: 2,
  minSingularValue: 0.184,
  singularValues: [5.84, 0.184],
  note: "No strong local identifiability issue detected in the current mock example.",
};

export const correlation = {
  matrix: [
    [1.0, 0.73],
    [0.73, 1.0],
  ] as number[][],
  names: ["k", "c"],
  highest: { a: "k", b: "c", value: 0.73 },
};
