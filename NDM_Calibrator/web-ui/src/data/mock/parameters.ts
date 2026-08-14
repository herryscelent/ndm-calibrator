/**
 * Mock parameter configuration for the second-order mechanical system.
 */

export type ParamStatus = "Free" | "Fixed";

export interface ParameterConfig {
  name: string;
  initial: number;
  lower: number;
  upper: number;
  status: ParamStatus;
  unit: string;
  description: string;
}

export const parameters: ParameterConfig[] = [
  {
    name: "k",
    initial: 2.0,
    lower: 0.1,
    upper: 10.0,
    status: "Free",
    unit: "N/m",
    description: "弹簧刚度",
  },
  {
    name: "c",
    initial: 0.2,
    lower: 0.01,
    upper: 3.0,
    status: "Free",
    unit: "N·s/m",
    description: "阻尼系数",
  },
  {
    name: "m",
    initial: 1.0,
    lower: Number.NaN,
    upper: Number.NaN,
    status: "Fixed",
    unit: "kg",
    description: "质量 (固定)",
  },
];
