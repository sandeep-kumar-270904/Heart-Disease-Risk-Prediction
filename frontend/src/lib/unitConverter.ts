/**
 * HeartXAI 2.0 - Clinical Biomarker Unit Conversion Helpers (ADR-009)
 * Matches shared/data-dictionary.json exact conversion constants.
 */

export const CHOLESTEROL_MMOL_FACTOR = 38.67;
export const GLUCOSE_MMOL_FACTOR = 18.016;

export function roundTo(value: number, decimals: number): number {
  const scale = 10 ** decimals;
  return Math.round((value + Number.EPSILON) * scale) / scale;
}

export function cholesterolMgDlToMmolL(mgDl: number, decimals = 4): number {
  return roundTo(mgDl / CHOLESTEROL_MMOL_FACTOR, decimals);
}

export function cholesterolMmolLToMgDl(mmolL: number, decimals = 4): number {
  return roundTo(mmolL * CHOLESTEROL_MMOL_FACTOR, decimals);
}

export function glucoseMgDlToMmolL(mgDl: number, decimals = 4): number {
  return roundTo(mgDl / GLUCOSE_MMOL_FACTOR, decimals);
}

export function glucoseMmolLToMgDl(mmolL: number, decimals = 4): number {
  return roundTo(mmolL * GLUCOSE_MMOL_FACTOR, decimals);
}
