// HeartXAI 2.0 — End-to-End Synthetic Patient Journey (Playwright Specification, Milestone 20)
// Operates strictly on Category B synthetic personas (zero real PHI).
import { test, expect } from '@playwright/test';

const SYNTHETIC_EMAIL = `synthetic.uat.${Date.now()}@synthetic.heartxai.local`;
const SYNTHETIC_PASS = 'SyntheticUatPass!2026';

test.describe('Synthetic Patient UAT Journey (DEC-005 Safe)', () => {
  test('registers synthetic user, runs 5-step intake, inspects SHAP & counterfactuals', async ({
    page,
  }) => {
    await page.goto('/register');
    await expect(page.getByText(/SYNTHETIC DATA ONLY/i)).toBeVisible();

    await page.getByLabel(/Synthetic Persona Name/i).fill('Synthetic UAT Persona');
    await page.getByLabel(/Email Address/i).fill(SYNTHETIC_EMAIL);
    await page.getByLabel(/Password/i).fill(SYNTHETIC_PASS);
    await page.getByRole('checkbox').check();
    await page.getByRole('button', { name: /Create Account/i }).click();

    await expect(page).toHaveURL(/\/login/);
    await page.getByLabel(/Email Address/i).fill(SYNTHETIC_EMAIL);
    await page.getByLabel(/Password/i).fill(SYNTHETIC_PASS);
    await page.getByRole('button', { name: /Sign In/i }).click();

    await expect(page).toHaveURL(/\/dashboard/);
    await page.getByRole('link', { name: /Start New Assessment/i }).click();

    // Traverse 5-step intake wizard
    for (let step = 0; step < 4; step++) {
      await page.getByRole('button', { name: 'Next' }).click();
    }
    await page.getByRole('button', { name: /Run Task A Assessment/i }).click();

    await expect(page).toHaveURL(/\/assessments\//);
    await expect(page.getByText(/Task A Cardiovascular Assessment Results/i)).toBeVisible();
    await expect(page.getByText(/No prospective 10-year cardiovascular risk/i)).toBeVisible();

    // Verify SHAP Accessible Table fallback
    await page.getByRole('button', { name: /Accessible Data Table/i }).click();
    await expect(page.getByRole('table')).toBeVisible();

    // Run Counterfactual Scenario Simulation
    await page.getByRole('button', { name: /Run Scenario Simulation/i }).click();
    await expect(page.getByText(/Simulated Task A Association/i)).toBeVisible();
  });
});
