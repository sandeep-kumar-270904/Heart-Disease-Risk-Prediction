import React, { useEffect, useState } from 'react';
import { ShieldOff } from 'lucide-react';
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
} from '@/components/ui';
import { apiFetch, ApiClientError } from '@/services/apiClient';
import { useAuthStore } from '@/stores/authStore';
import type { AssessmentDetailResponse } from '@/types';

interface GrantSummary {
  readonly id: string;
  readonly doctor_id: string;
  readonly status: string;
  readonly expires_at: string;
}

export const DoctorPortalPage: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const [grants, setGrants] = useState<GrantSummary[]>([]);
  const [sharedAssessments, setSharedAssessments] = useState<AssessmentDetailResponse[]>([]);
  const [doctorIdInput, setDoctorIdInput] = useState('');
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const isClinician = user?.role === 'CLINICIAN';

  useEffect(() => {
    (async () => {
      try {
        if (isClinician) {
          const shared = await apiFetch<AssessmentDetailResponse[]>('/consents/doctor/shared');
          setSharedAssessments(shared);
        } else {
          const myGrants = await apiFetch<GrantSummary[]>('/consents');
          setGrants(myGrants);
        }
      } catch {
        // Handled cleanly
      }
    })();
  }, [isClinician]);

  const handleIssueGrant = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setStatusMsg(null);
    try {
      const created = await apiFetch<GrantSummary>('/consents', {
        method: 'POST',
        body: JSON.stringify({ doctor_id: doctorIdInput }),
      });
      setGrants((prev) => [created, ...prev]);
      setDoctorIdInput('');
      setStatusMsg('72-hour sharing grant issued.');
    } catch (err) {
      setStatusMsg(err instanceof ApiClientError ? err.message : 'Unable to issue grant.');
    }
  };

  const handleRevoke = async (grantId: string): Promise<void> => {
    try {
      const updated = await apiFetch<GrantSummary>(`/consents/${grantId}/revoke`, {
        method: 'POST',
      });
      setGrants((prev) => prev.map((g) => (g.id === grantId ? updated : g)));
    } catch {
      // Ignore error
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">
        {isClinician ? 'Clinician Shared Review Portal' : 'Patient Consent & Access Grants'}
      </h1>

      {statusMsg && <Alert severity="info" title="Consent Status" description={statusMsg} />}

      {!isClinician ? (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle as="h2">Grant 72-Hour Clinician Access</CardTitle>
              <CardDescription>
                Share synthetic assessments safely with a verified clinician. Revoke anytime in one
                click.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleIssueGrant} className="flex flex-wrap items-end gap-3">
                <div className="min-w-[260px] flex-1">
                  <Input
                    label="Verified Clinician ID"
                    required
                    value={doctorIdInput}
                    onChange={(e) => setDoctorIdInput(e.target.value)}
                    placeholder="Enter clinician UUID"
                  />
                </div>
                <Button type="submit">Issue 72-Hour Grant</Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle as="h2">Active &amp; Historical Sharing Grants</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {grants.length === 0 ? (
                <p className="text-sm text-slate-500">No clinician consent grants issued.</p>
              ) : (
                grants.map((grant) => (
                  <div
                    key={grant.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 p-4"
                  >
                    <div>
                      <p className="font-mono text-xs text-slate-700">Doctor: {grant.doctor_id}</p>
                      <p className="text-xs text-slate-500">Expires: {grant.expires_at}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant={grant.status === 'ACTIVE' ? 'verified' : 'neutral'}>
                        {grant.status}
                      </Badge>
                      {grant.status === 'ACTIVE' && (
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => void handleRevoke(grant.id)}
                          leftIcon={<ShieldOff className="h-3.5 w-3.5" />}
                        >
                          Revoke Access
                        </Button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle as="h2">Consented Patient Assessments ({sharedAssessments.length})</CardTitle>
            <CardDescription>
              Read-only synthetic review view. Arbitrary free-text clinician notes are disabled in
              the synthetic-only MVP (DEC-005).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {sharedAssessments.length === 0 ? (
              <p className="text-sm text-slate-500">No active consented assessments shared.</p>
            ) : (
              sharedAssessments.map((item) => (
                <div key={item.id} className="rounded-lg border border-slate-200 p-4">
                  <p className="font-semibold text-slate-900">
                    Assessment {item.id} — {item.cad_likelihood_percent.toFixed(1)}%
                  </p>
                  <p className="text-xs text-slate-600">{item.plain_language_summary}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};
