import React, { useEffect, useState } from 'react';
import {
  Alert,
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui';
import { apiFetch, ApiClientError } from '@/services/apiClient';

interface AuditRow {
  readonly id: string;
  readonly timestamp: string;
  readonly role: string;
  readonly action_type: string;
  readonly endpoint: string;
  readonly status_code: number;
}

export const AdminConsolePage: React.FC = () => {
  const [logs, setLogs] = useState<AuditRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch<AuditRow[]>('/admin/audit-logs?limit=25');
        setLogs(res);
      } catch (err) {
        setError(
          err instanceof ApiClientError
            ? err.message
            : 'Administrator credentials required to inspect audit trail.'
        );
      }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Administrative Console &amp; Immutable Audit Trail
        </h1>
        <p className="text-sm text-slate-600">
          Append-only security event log. Strictly restricted to ADMINISTRATOR role.
        </p>
      </div>

      {error && <Alert severity="warning" title="Access Restricted" description={error} />}

      <Card>
        <CardHeader>
          <CardTitle as="h2">Security &amp; Access Audit Log ({logs.length})</CardTitle>
          <CardDescription>Read-only audit ledger; modifications and deletions disabled.</CardDescription>
        </CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-sm text-slate-500">No audit entries available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="p-2 font-semibold">Timestamp</th>
                    <th className="p-2 font-semibold">Role</th>
                    <th className="p-2 font-semibold">Action</th>
                    <th className="p-2 font-semibold">Endpoint</th>
                    <th className="p-2 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((row) => (
                    <tr key={row.id} className="border-b border-slate-100">
                      <td className="p-2 font-mono">{row.timestamp}</td>
                      <td className="p-2">{row.role}</td>
                      <td className="p-2 font-medium">{row.action_type}</td>
                      <td className="p-2 font-mono">{row.endpoint}</td>
                      <td className="p-2">
                        <Badge variant={row.status_code < 400 ? 'low' : 'elevated'}>
                          {row.status_code}
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
    </div>
  );
};
