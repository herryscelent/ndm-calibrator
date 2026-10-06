/**
 * Global mock project — synthetic demonstration data.
 * All values are explicitly mock/synthetic; nothing is a real algorithm result.
 */

export interface ProjectInfo {
  name: string;
  description: string;
  tagline: string;
  modelSummary: string;
  lastUpdated: string;
  status: "Ready";
  samples: number;
  inputs: number;
  outputs: number;
  states: number;
  freeParameters: string[];
  fixedParameters: Record<string, number>;
}

export const project: ProjectInfo = {
  name: "二阶机械系统参数校准",
  description: "二阶质量-弹簧-阻尼动态模型",
  tagline: "演示项目",
  modelSummary: "质量-弹簧-阻尼 · x1 位移, x2 速度",
  lastUpdated: "2026-08-13",
  status: "Ready",
  samples: 4860,
  inputs: 1,
  outputs: 1,
  states: 2,
  freeParameters: ["k", "c"],
  fixedParameters: { m: 1.0 },
};

export const estimates = {
  k: 2.514,
  c: 0.176,
  m: 1.0,
};

export const fitMetrics = {
  RMSE: 0.0418,
  MAE: 0.0312,
  R2: 0.9871,
  Runtime: 3.21,
};
