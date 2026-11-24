import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { HeartPulse, LogOut, ShieldAlert } from 'lucide-react';
import { Button, TooltipProvider } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/cn';

export interface AppShellProps {
  readonly children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { user, isAuthenticated, countryCode, setCountryCode, clearSession } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = (): void => {
    clearSession();
    navigate('/login');
  };

  return (
    <TooltipProvider>
      <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
        {/* WCAG 2.2 Bypass Blocks Skip Link */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-tooltip focus:rounded-md focus:bg-sky-700 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        >
          Skip to main content
        </a>

        {/* Mandatory Synthetic Environment Watermark (DEC-005 / Phase 10 Isolation Rule) */}
        <div
          role="status"
          className="border-b border-amber-600 bg-amber-50 px-4 py-1.5 text-center text-xs font-semibold tracking-wide text-amber-900"
        >
          [TEST ENVIRONMENT — SYNTHETIC DATA ONLY — NOT FOR REAL CLINICAL USE]
        </div>

        <header
          role="banner"
          className="sticky top-0 z-header border-b border-slate-200 bg-white/95 backdrop-blur"
        >
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <div className="flex items-center gap-6">
              <Link
                to="/dashboard"
                className="flex items-center gap-2 text-lg font-bold tracking-tight text-slate-900"
              >
                <HeartPulse className="h-6 w-6 text-sky-600" aria-hidden="true" />
                <span>HeartXAI 2.0</span>
              </Link>

              {isAuthenticated && (
                <nav aria-label="Main Navigation" className="hidden items-center gap-1 md:flex">
                  {[
                    { to: '/dashboard', label: 'Dashboard' },
                    { to: '/intake', label: 'New Assessment' },
                    { to: '/directory', label: 'Care Directory' },
                    { to: '/doctor', label: 'Clinician Portal' },
                    { to: '/admin', label: 'Audit Console' },
                  ].map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        cn(
                          'inline-flex min-h-[40px] items-center rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                          isActive
                            ? 'bg-sky-50 text-sky-800'
                            : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                        )
                      }
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </nav>
              )}
            </div>

            <div className="flex items-center gap-3">
              <div
                role="note"
                className="inline-flex min-h-[40px] items-center gap-1.5 rounded-md border border-crimson-600 bg-crimson-50 px-3 py-1.5 text-xs font-semibold text-crimson-700"
              >
                <ShieldAlert className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span>Demo Only — Medical Emergency? Call Local EMS</span>
              </div>

              <label htmlFor="global-country-select" className="sr-only">
                Select Region
              </label>
              <select
                id="global-country-select"
                aria-label="Select Region"
                value={countryCode}
                onChange={(e) => setCountryCode(e.target.value as 'US' | 'IN' | 'GB')}
                className="min-h-[40px] rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-800"
              >
                <option value="US">US (mg/dL)</option>
                <option value="IN">IN (mg/dL)</option>
                <option value="GB">UK (mmol/L)</option>
              </select>

              {isAuthenticated && (
                <div className="flex items-center gap-2">
                  <span className="hidden text-xs font-medium text-slate-600 sm:inline">
                    {user?.full_name ?? 'Synthetic User'}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleLogout}
                    leftIcon={<LogOut className="h-3.5 w-3.5" />}
                  >
                    Sign Out
                  </Button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main id="main-content" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
          {children}
        </main>

        <footer
          role="contentinfo"
          className="border-t border-slate-200 bg-white px-4 py-6 text-xs text-slate-600 sm:px-6"
        >
          <div className="mx-auto flex max-w-7xl flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <p className="font-medium text-slate-700">
              Educational Decision-Support Platform — Non-diagnostic informational outputs only. Not
              a substitute for qualified clinical evaluation.
            </p>
            <p className="font-mono text-slate-500">Task A Retrospective CAD Model • DEC-005 Safe</p>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  );
};
