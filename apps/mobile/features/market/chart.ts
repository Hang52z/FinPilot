export type ChartBox = { width: number; height: number; padding: number };

/**
 * SVG path for a line chart of `values`, scaled to fill the box.
 * Long series are reduced to about one point per pixel; the last value is always kept.
 */
export function linePath(values: number[], { width, height, padding }: ChartBox): string {
  if (values.length < 2 || width <= 0 || height <= 0) return '';

  const step = Math.max(1, Math.floor(values.length / width));
  const points = values.filter((_, i) => i % step === 0);
  if ((values.length - 1) % step !== 0) points.push(values[values.length - 1]);

  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const innerH = height - padding * 2;
  const x = (i: number) => (i / (points.length - 1)) * width;
  const y = (v: number) => padding + (1 - (v - min) / span) * innerH;

  return points
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .join(' ');
}

/** Percent change from the first to the last value, or null when it cannot be computed. */
export function rangeChangePct(values: number[]): number | null {
  if (values.length < 2 || values[0] <= 0) return null;
  return (values[values.length - 1] / values[0] - 1) * 100;
}
