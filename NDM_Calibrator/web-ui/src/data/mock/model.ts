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
    { name: "x1", description: "position 位置" },
    { name: "x2", description: "velocity 速度" },
  ],
  inputs: [{ name: "u", description: "force 力" }],
  parameters: [
    { name: "m", description: "mass 质量" },
    { name: "c", description: "damping 阻尼" },
    { name: "k", description: "stiffness 刚度" },
  ],
  outputs: ["y = x1"],
  equations: [
    { label: "dx1/dt", expr: "x2" },
    { label: "dx2/dt", expr: "-(k/m) * x1 - (c/m) * x2 + (1/m) * u" },
  ],
  valid: true,
  validMessage: "Model valid",
};
