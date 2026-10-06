/**
 * Mock model definition for the second-order mechanical system.
 */

export interface ModelStructure {
  states: { name: string; description: string }[];
  inputs: { name: string; description: string }[];
  parameters: { name: string; description: string }[];
  outputs: string[];
  equations: { label: string; expr: string }[];
  valid: boolean;
  validMessage: string;
}

export const model: ModelStructure = {
  states: [
    { name: "x1", description: "位移" },
    { name: "x2", description: "速度" },
  ],
  inputs: [{ name: "u", description: "力" }],
  parameters: [
    { name: "m", description: "质量" },
    { name: "c", description: "阻尼" },
    { name: "k", description: "刚度" },
  ],
  outputs: ["y = x1"],
  equations: [
    { label: "dx1/dt", expr: "x2" },
    { label: "dx2/dt", expr: "-(k/m) * x1 - (c/m) * x2 + (1/m) * u" },
  ],
  valid: true,
  validMessage: "模型有效",
};
