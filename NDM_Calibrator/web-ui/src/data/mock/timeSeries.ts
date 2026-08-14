/**
 * Fixed synthetic time-series data for the second-order mechanical system.
 * Deterministic (written out, not randomized at render time).
 */

export interface SeriesPoint {
  t: number;
  measured: number;
  simulated: number;
}

/** Downsampled measured vs simulated output over the experiment window. */
export const measuredSimulated: SeriesPoint[] = [
  { t: 0.0, measured: 0.000, simulated: 0.000 },
  { t: 0.5, measured: 0.082, simulated: 0.071 },
  { t: 1.0, measured: 0.251, simulated: 0.263 },
  { t: 1.5, measured: 0.512, simulated: 0.520 },
  { t: 2.0, measured: 0.811, simulated: 0.829 },
  { t: 2.5, measured: 1.142, simulated: 1.150 },
  { t: 3.0, measured: 1.481, simulated: 1.493 },
  { t: 3.5, measured: 1.804, simulated: 1.822 },
  { t: 4.0, measured: 2.117, simulated: 2.130 },
  { t: 4.5, measured: 2.412, simulated: 2.424 },
  { t: 5.0, measured: 2.687, simulated: 2.701 },
  { t: 6.0, measured: 3.188, simulated: 3.199 },
  { t: 7.0, measured: 3.622, simulated: 3.634 },
  { t: 8.0, measured: 3.989, simulated: 4.002 },
  { t: 9.0, measured: 4.291, simulated: 4.305 },
  { t: 10.0, measured: 4.541, simulated: 4.553 },
  { t: 12.0, measured: 4.904, simulated: 4.918 },
  { t: 14.0, measured: 5.127, simulated: 5.141 },
  { t: 16.0, measured: 5.263, simulated: 5.277 },
  { t: 18.0, measured: 5.341, simulated: 5.354 },
  { t: 20.0, measured: 5.387, simulated: 5.400 },
  { t: 25.0, measured: 5.442, simulated: 5.455 },
  { t: 30.0, measured: 5.461, simulated: 5.474 },
  { t: 40.0, measured: 5.478, simulated: 5.490 },
  { t: 50.0, measured: 5.483, simulated: 5.496 },
];

export interface RawRow {
  time: number;
  u: number;
  position: number;
  velocity: number;
}

/** Deterministic rows for the data table preview (20–30 rows). */
export const dataRows: RawRow[] = (() => {
  const rows: RawRow[] = [];
  for (let i = 0; i < 24; i++) {
    const t = i * 0.5;
    const u = t < 2 ? 0 : 1;
    // Second-order step response (k=2.5, c=0.18, m=1) plus tiny fixed noise pattern.
    const omega = Math.sqrt(2.514);
    const damp = 0.176 / 2;
    const y = 1 / 2.514 * (1 - Math.exp(-damp * t) * Math.cos(omega * t));
    const pos = Math.min(0.4, Math.max(0, y)) * 5;
    const vel = i === 0 ? 0 : +(rows[i - 1].velocity + (pos - (i ? rows[i - 1].position : 0)) / 0.5).toFixed(3);
    rows.push({
      time: +t.toFixed(1),
      u,
      position: +(pos + (i % 5) * 0.001).toFixed(3),
      velocity: +vel.toFixed(3),
    });
  }
  return rows;
})();

export const dataSummary = {
  rows: 4860,
  columns: 4,
  missing: 0,
  durationMin: 81,
};

export const columnMappings: { column: string; role: string }[] = [
  { column: "time", role: "Time" },
  { column: "u", role: "Input" },
  { column: "position", role: "Output" },
  { column: "velocity", role: "State" },
];
