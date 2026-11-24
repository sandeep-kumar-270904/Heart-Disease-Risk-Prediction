import React, { useState } from 'react';
import { Table as TableIcon, BarChart2 } from 'lucide-react';
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui';
import type { ShapExplanationResponse } from '@/types';

export interface ShapWaterfallProps {
  readonly data: ShapExplanationResponse;
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ data }) => {
  const [showTable, setShowTable] = useState(false);
  const topFeatures = data.features.slice(0, 8);
  const maxAbs = Math.max(...topFeatures.map((f) => Math.abs(f.shap_value)), 0.01);

  return (
    <Card>
      <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <CardTitle as="h2">Local TreeSHAP Feature Attribution</CardTitle>
          <CardDescription>
            Statistical association contributions in log-odds units (not biological causation).
          </CardDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowTable((prev) => !prev)}
          leftIcon={showTable ? <BarChart2 className="h-4 w-4" /> : <TableIcon className="h-4 w-4" />}
        >
          {showTable ? 'Visual Chart View' : 'Accessible Data Table'}
        </Button>
      </CardHeader>

      <CardContent className="space-y-4">
        {!showTable ? (
          <div className="space-y-2.5" aria-label="TreeSHAP horizontal attribution chart">
            <div className="flex justify-between border-b border-slate-200 pb-2 text-xs font-medium text-slate-600">
              <span>Cohort Baseline Margin E[f(x)]: {data.base_value.toFixed(4)}</span>
              <span>Final Margin f(x): {data.final_likelihood.toFixed(4)}</span>
            </div>
            {topFeatures.map((feat) => {
              const widthPct = Math.max(4, Math.round((Math.abs(feat.shap_value) / maxAbs) * 100));
              const increases = feat.direction === 'increases_likelihood';
              return (
                <div key={feat.feature_name} className="grid grid-cols-12 items-center gap-2 text-xs">
                  <div className="col-span-4 truncate font-medium text-slate-800">
                    {feat.feature_name} ({feat.raw_patient_value})
                  </div>
                  <div className="col-span-5 flex items-center">
                    <div className="h-4 w-full rounded bg-slate-100">
                      <div
                        className={
                          increases ? 'h-4 rounded bg-crimson-600' : 'h-4 rounded bg-sky-600'
                        }
                        style={{ width: `${widthPct}%` }}
                      />
                    </div>
                  </div>
                  <div className="col-span-3 text-right font-mono font-semibold tabular-clinical">
                    <span className={increases ? 'text-crimson-700' : 'text-sky-700'}>
                      {increases ? '▲' : '▼'} {feat.shap_value >= 0 ? '+' : ''}
                      {feat.shap_value.toFixed(4)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs">
              <caption className="pb-2 text-left text-slate-600">
                Exact TreeSHAP attributions comparing patient measurements to UCI Cleveland cohort
                means.
              </caption>
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-800">
                  <th className="p-2 font-semibold">Feature</th>
                  <th className="p-2 font-semibold">Value</th>
                  <th className="p-2 font-semibold">Cohort Mean</th>
                  <th className="p-2 font-semibold">SHAP Value</th>
                  <th className="p-2 font-semibold">Association</th>
                </tr>
              </thead>
              <tbody>
                {data.features.map((feat) => (
                  <tr key={feat.feature_name} className="border-b border-slate-100">
                    <td className="p-2 font-medium text-slate-900">{feat.feature_name}</td>
                    <td className="p-2 font-mono tabular-clinical">{feat.raw_patient_value}</td>
                    <td className="p-2 font-mono tabular-clinical">{feat.cohort_average_value}</td>
                    <td className="p-2 font-mono font-semibold tabular-clinical">
                      {feat.shap_value >= 0 ? '+' : ''}
                      {feat.shap_value.toFixed(4)}
                    </td>
                    <td className="p-2">
                      <Badge variant={feat.direction === 'increases_likelihood' ? 'elevated' : 'low'}>
                        {feat.direction === 'increases_likelihood' ? '▲ Increases' : '▼ Decreases'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
