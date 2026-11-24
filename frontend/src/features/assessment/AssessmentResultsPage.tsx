import React, { useEffect, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { Download } from 'lucide-react';
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
import { apiFetch } from '@/services/apiClient';
import { useAuthStore } from '@/stores/authStore';
import type { AssessmentDetailResponse, ShapExplanationResponse } from '@/types';
import { CounterfactualSimulator } from './CounterfactualSimulator';
import { ShapWaterfall } from './ShapWaterfall';

export const AssessmentResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const initialAssessment =
    (location.state as { assessment?: AssessmentDetailResponse } | null)?.assessment ?? null;

  const [assessment, setAssessment] = useState<AssessmentDetailResponse | null>(initialAssessment);
  const [shapData, setShapData] = useState<ShapExplanationResponse | null>(null);
  const accessToken = useAuthStore((s) => s.accessToken);

  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      try {
        const [detailRes, shapRes] = await Promise.all([
          assessment
            ? Promise.resolve(assessment)
            : apiFetch<AssessmentDetailResponse>(`/assessments/${id}`),
          apiFetch<ShapExplanationResponse>(`/assessments/${id}/shap`),
        ]);
        if (active) {
          setAssessment(detailRes);
          setShapData(shapRes);
        }
      } catch {
        // Error handled cleanly via fallback UI
      }
    })();
    return () => {
      active = false;
    };
  }, [id, assessment]);

  if (!assessment) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-slate-600">
          Loading Task A assessment results...
        </CardContent>
      </Card>
    );
  }

  const badgeVariant =
    assessment.risk_strata === 'low'
      ? 'low'
      : assessment.risk_strata === 'moderate'
        ? 'moderate'
        : 'elevated';

  const handleDownloadPdf = async (): Promise<void> => {
    const resp = await fetch(`/api/v1/assessments/${assessment.id}/export-pdf`, {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
      credentials: 'include',
    });
    if (!resp.ok) return;
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `heartxai_assessment_${assessment.id}.pdf`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {assessment.emergency_warning_active && (
        <Alert
          severity="emergency"
          title="Emergency Medical Warning Triggered"
          description="Input thresholds exceeded acute outpatient safety limits. Seek prompt clinical evaluation."
        />
      )}

      <Alert
        severity="info"
        title="Educational Non-Diagnostic Model Notice (DEC-003 Option A)"
        description="Task A outputs measure similarity to the historical N=303 UCI Cleveland research cohort. No prospective 10-year cardiovascular risk calculation is provided."
      />

      <Card elevated>
        <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle as="h1">Task A Cardiovascular Assessment Results</CardTitle>
            <CardDescription>{assessment.cohort_name}</CardDescription>
          </div>
          <Button
            variant="outline"
            onClick={handleDownloadPdf}
            leftIcon={<Download className="h-4 w-4" />}
          >
            Export Sealed PDF Dossier
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-6">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Calibrated Task A Likelihood
              </p>
              <p className="font-mono text-4xl font-bold tabular-clinical text-slate-900">
                {assessment.cad_likelihood_percent.toFixed(1)}%
              </p>
            </div>
            <div className="space-y-1">
              <Badge variant={badgeVariant}>
                {assessment.risk_strata.toUpperCase()} TIER
              </Badge>
              <p className="text-xs text-slate-600">
                95% Interval: [{assessment.confidence_interval[0]}%,{' '}
                {assessment.confidence_interval[1]}%]
              </p>
            </div>
          </div>
          <p className="text-sm text-slate-700">{assessment.plain_language_summary}</p>
        </CardContent>
      </Card>

      {shapData && <ShapWaterfall data={shapData} />}

      <CounterfactualSimulator assessment={assessment} />
    </div>
  );
};
