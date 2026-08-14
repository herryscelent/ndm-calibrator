/**
 * Mock uncertainty (multi-start + bootstrap) data.
 */

export const multistart = {
  starts: 20,
  successful: 20,
  successRate: "100%",
  bestRMSE: 0.0418,
  kSamples: [2.48, 2.51, 2.49, 2.53, 2.47, 2.50, 2.52, 2.49, 2.51, 2.50],
  cSamples: [0.17, 0.18, 0.175, 0.182, 0.169, 0.177, 0.174, 0.179, 0.181, 0.176],
};

export interface BootstrapParamRow {
  parameter: string;
  estimate: number;
  median: number;
  p2_5: number;
  p97_5: number;
}

export const bootstrap = {
  samples: 100,
  seed: 42,
  status: "Completed",
  rows: [
    { parameter: "k", estimate: 2.514, median: 2.509, p2_5: 2.41, p97_5: 2.62 },
    { parameter: "c", estimate: 0.176, median: 0.178, p2_5: 0.15, p97_5: 0.21 },
  ] as BootstrapParamRow[],
  distributions: {
    k: {
      bins: ["2.40", "2.44", "2.48", "2.52", "2.56", "2.60"],
      counts: [2, 8, 22, 34, 24, 10],
      median: 2.509,
      lo: 2.41,
      hi: 2.62,
      estimate: 2.514,
    },
    c: {
      bins: ["0.14", "0.15", "0.16", "0.17", "0.18", "0.19", "0.20", "0.21"],
      counts: [1, 4, 9, 21, 32, 22, 8, 3],
      median: 0.178,
      lo: 0.15,
      hi: 0.21,
      estimate: 0.176,
    },
  },
};
