import React, { useState } from 'react';
import { RotateCcw } from 'lucide-react';
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui';
import { apiFetch, ApiClientError } from '@/services/apiClient';
import type { AssessmentDetailResponse, ScenarioResultDto } from '@/types';

export interface CounterfactualSimulatorProps {
  readonly assessment: AssessmentDetailResponse;
}

export const CounterfactualSimulator: React.FC<CounterfactualSimulatorProps> = ({ assessment }) => {
  const [bp, setBp] = useState<number>(assessment.resting_bp);
  const [chol, setChol] = useState<number>(assessment.serum_cholesterol);
  const [result, setResult] = useState<ScenarioResultDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const runSimulation = async (nextBp: number, nextChol: number): Promise<void> => {
    setError(null);
    setIsSimulating(true);
    try {
      const sim = await apiFetch<ScenarioResultDto>(`/assessments/${assessment.id}/simulate`, {
        method: 'POST',
        body: JSON.stringify({
          modified_features: {
            resting_bp: nextBp,
            serum_cholesterol: nextChol,
          },
        }),
      });
      setResult(sim);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Simulation failed.');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = (): void => {
    setBp(assessment.resting_bp);
    setChol(assessment.serum_cholesterol);
    setResult(null);
    setError(null);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle as="h2">Hypothetical What-If Model Input Simulator</CardTitle>
        <CardDescription>
          Exploratory mathematical perturbation of model inputs keeping Age ({assessment.age}), Sex,
          and Clinical History locked. Hypothetical model scenarios only — NEVER treatment advice or
          clinical prescriptions.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {error && <Alert severity="warning" title="Simulation Notice" description={error} />}
        {result?.is_biological_clamp_violated && result.violation_message && (
          <Alert
            severity="warning"
            title="Physiological Clamp Enforced"
            description={result.violation_message}
          />
        )}

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <label htmlFor="sim-bp-slider" className="font-medium text-slate-900">
              Resting Systolic BP (Floor: 90 mmHg)
            </label>
            <span className="font-mono font-semibold tabular-clinical">{bp} mmHg</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              aria-label="Decrease simulated blood pressure by 5 mmHg"
              onClick={() => setBp((v) => Math.max(90, v - 5))}
            >
              -5
            </Button>
            <input
              id="sim-bp-slider"
              type="range"
              min={90}
              max={220}
              step={1}
              value={bp}
              onChange={(e) => setBp(Number(e.target.value))}
              className="w-full accent-sky-600"
            />
            <Button
              variant="outline"
              size="sm"
              aria-label="Increase simulated blood pressure by 5 mmHg"
              onClick={() => setBp((v) => Math.min(220, v + 5))}
            >
              +5
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <label htmlFor="sim-chol-slider" className="font-medium text-slate-900">
              Serum Cholesterol (Floor: 120 mg/dL)
            </label>
            <span className="font-mono font-semibold tabular-clinical">{chol} mg/dL</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              aria-label="Decrease simulated cholesterol by 10 mg/dL"
              onClick={() => setChol((v) => Math.max(120, v - 10))}
            >
              -10
            </Button>
            <input
              id="sim-chol-slider"
              type="range"
              min={120}
              max={450}
              step={1}
              value={chol}
              onChange={(e) => setChol(Number(e.target.value))}
              className="w-full accent-sky-600"
            />
            <Button
              variant="outline"
              size="sm"
              aria-label="Increase simulated cholesterol by 10 mg/dL"
              onClick={() => setChol((v) => Math.min(450, v + 10))}
            >
              +10
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => runSimulation(bp, chol)} isLoading={isSimulating}>
            Run Scenario Simulation
          </Button>
          <Button variant="outline" onClick={handleReset} leftIcon={<RotateCcw className="h-4 w-4" />}>
            Reset to Baseline
          </Button>
        </div>

        {result && !result.is_biological_clamp_violated && (
          <div
            role="status"
            aria-live="polite"
            className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-sky-200 bg-sky-50 p-4"
          >
            <div className="space-y-1 text-sm">
              <p className="font-semibold text-slate-900">
                Hypothetical Simulated Model Score: {result.simulated_likelihood_percent.toFixed(1)}%
              </p>
              <p className="text-xs text-slate-700">
                Model delta from baseline ({result.baseline_likelihood_percent.toFixed(1)}%):{' '}
                <span className="font-mono font-semibold">
                  {result.delta_percent >= 0 ? '+' : ''}
                  {result.delta_percent.toFixed(2)}%
                </span>
              </p>
            </div>
            <Badge variant="verified">Feasibility: {(result.feasibility_score * 100).toFixed(0)}%</Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
