import React, { useState } from 'react';
import { Activity, HelpCircle, HeartPulse } from 'lucide-react';
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Modal,
  Select,
  Tooltip,
  TooltipProvider,
} from './index';

export const DesignSystemShowcase: React.FC = () => {
  const [unit, setUnit] = useState<string>('mg_dl');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  return (
    <TooltipProvider>
      <main id="main-content" className="mx-auto max-w-5xl space-y-8 p-6">
        <header className="space-y-2 border-b border-slate-200 pb-4">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
            HeartXAI 2.0 Design System Primitives
          </h1>
          <p className="text-sm text-slate-600">
            WCAG 2.2 Level AA UI primitives built with Tailwind CSS design tokens and Radix UI.
          </p>
        </header>

        <section aria-labelledby="showcase-alerts" className="space-y-3">
          <h2 id="showcase-alerts" className="text-xl font-semibold text-slate-900">
            Clinical Safety Alerts
          </h2>
          <Alert
            severity="emergency"
            title="Immediate Attention Required"
            description="Severe resting chest pain requires urgent clinical evaluation. Contact emergency services (911 / 112 / 999)."
          />
          <Alert
            severity="warning"
            title="Optional Imaging Missing"
            description="Fluoroscopy vessel count was omitted and will use training-fold median imputation."
          />
          <Alert
            severity="info"
            title="Educational Platform Notice"
            description="Outputs support cardiovascular health literacy and are non-diagnostic."
          />
        </section>

        <section aria-labelledby="showcase-badges" className="space-y-3">
          <h2 id="showcase-badges" className="text-xl font-semibold text-slate-900">
            Risk & Verification Badges
          </h2>
          <div className="flex flex-wrap gap-3">
            <Badge variant="low">Low Risk (&lt; 30%)</Badge>
            <Badge variant="moderate">Moderate Risk (30–69%)</Badge>
            <Badge variant="elevated">Elevated Risk (≥ 70%)</Badge>
            <Badge variant="verified">Clinician Verified</Badge>
            <Badge variant="neutral">Synthetic Fixture (Category B)</Badge>
          </div>
        </section>

        <section aria-labelledby="showcase-controls">
          <Card elevated>
            <CardHeader>
              <CardTitle>Biomarker Form & Interactive Primitives</CardTitle>
              <CardDescription>
                Accessible inputs with unit affixes, tooltips, and Radix Select dropdowns.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2">
              <Input
                label="Serum Cholesterol"
                type="number"
                required
                unitAffix={unit === 'mg_dl' ? 'mg/dL' : 'mmol/L'}
                leftIcon={<HeartPulse className="h-4 w-4" />}
                defaultValue="210"
                helperText="Typical fasting range: 125–200 mg/dL"
              />
              <Input
                label="Resting Systolic Blood Pressure"
                type="number"
                unitAffix="mmHg"
                leftIcon={<Activity className="h-4 w-4" />}
                defaultValue="310"
                error="Resting blood pressure must be between 70 and 240 mmHg."
              />
              <Select
                label="Preferred Cholesterol Unit"
                value={unit}
                onValueChange={setUnit}
                helperText="Select regional measurement unit convention."
                options={[
                  { value: 'mg_dl', label: 'US Customary (mg/dL)' },
                  { value: 'mmol_l', label: 'SI Metric (mmol/L)' },
                ]}
              />
              <div className="flex items-end gap-3">
                <Tooltip content="Calibrated XGBoost Task A classification explanation">
                  <Button variant="outline" leftIcon={<HelpCircle className="h-4 w-4" />}>
                    Explain Model
                  </Button>
                </Tooltip>
                <Modal
                  open={isModalOpen}
                  onOpenChange={setIsModalOpen}
                  trigger={<Button variant="primary">Open Disclaimer Dialog</Button>}
                  title="Non-Diagnostic Clinical Support Notice"
                  description="Review educational boundaries prior to assessment."
                  footer={
                    <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                      Acknowledge
                    </Button>
                  }
                >
                  <p className="text-sm text-slate-700">
                    HeartXAI 2.0 operates strictly on Category B synthetic test fixtures during
                    development and staging.
                  </p>
                </Modal>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="secondary">Cancel</Button>
              <div className="flex gap-2">
                <Button variant="ghost">Reset</Button>
                <Button variant="danger">Revoke Access</Button>
              </div>
            </CardFooter>
          </Card>
        </section>
      </main>
    </TooltipProvider>
  );
};
