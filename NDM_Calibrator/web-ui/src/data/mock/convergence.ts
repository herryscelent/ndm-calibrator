/**
 * Mock convergence trajectory for the mock identification run.
 * Deterministic progression of objective vs evaluations.
 */

export interface ConvergencePoint {
  evaluations: number;
  objective: number;
}

export const convergence: ConvergencePoint[] = [
  { evaluations: 0, objective: 0.248 },
  { evaluations: 30, objective: 0.121 },
  { evaluations: 60, objective: 0.068 },
  { evaluations: 90, objective: 0.042 },
  { evaluations: 120, objective: 0.023 },
  { evaluations: 150, objective: 0.014 },
  { evaluations: 180, objective: 0.009 },
  { evaluations: 210, objective: 0.006 },
  { evaluations: 240, objective: 0.0045 },
  { evaluations: 270, objective: 0.0038 },
  { evaluations: 318, objective: 0.0031 },
];

/** Deterministic runtime state timeline for the mock identification run. */
export const identificationTimeline = {
  totalEvaluations: 318,
  maxEvaluations: 2000,
  bestObjective: 0.0031,
  elapsedSeconds: 1.72,
  status: "Completed",
};

export const bestParameters = {
  k: 2.514,
  c: 0.176,
};
