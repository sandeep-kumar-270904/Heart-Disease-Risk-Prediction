import React from 'react';
import { AlertOctagon, AlertTriangle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '@/lib/cn';

export type AlertSeverity = 'emergency' | 'warning' | 'info' | 'success';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  readonly severity?: AlertSeverity;
  readonly title: string;
  readonly description?: string;
  readonly action?: React.ReactNode;
  readonly onDismiss?: () => void;
}

const severityStyles: Record<
  AlertSeverity,
  { container: string; title: string; body: string; icon: React.ReactNode; role: 'alert' | 'status' }
> = {
  emergency: {
    container: 'bg-crimson-50 border-2 border-crimson-600 text-crimson-900',
    title: 'text-crimson-900 font-semibold',
    body: 'text-crimson-700',
    icon: <AlertOctagon className="h-5 w-5 shrink-0 text-crimson-600" aria-hidden="true" />,
    role: 'alert',
  },
  warning: {
    container: 'bg-amber-50 border border-amber-600 text-amber-900',
    title: 'text-amber-900 font-semibold',
    body: 'text-amber-700',
    icon: <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600" aria-hidden="true" />,
    role: 'alert',
  },
  info: {
    container: 'bg-sky-50 border border-sky-600 text-sky-900',
    title: 'text-sky-900 font-semibold',
    body: 'text-sky-700',
    icon: <Info className="h-5 w-5 shrink-0 text-sky-600" aria-hidden="true" />,
    role: 'status',
  },
  success: {
    container: 'bg-emerald-50 border border-emerald-600 text-emerald-900',
    title: 'text-emerald-900 font-semibold',
    body: 'text-emerald-700',
    icon: <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" aria-hidden="true" />,
    role: 'status',
  },
};

export const Alert: React.FC<AlertProps> = ({
  severity = 'info',
  title,
  description,
  action,
  onDismiss,
  className,
  children,
  ...props
}) => {
  const styles = severityStyles[severity];

  return (
    <div
      role={styles.role}
      aria-live={styles.role === 'alert' ? 'assertive' : 'polite'}
      className={cn('flex items-start gap-3 rounded-lg p-4 shadow-sm', styles.container, className)}
      {...props}
    >
      <div className="mt-0.5">{styles.icon}</div>
      <div className="min-w-0 flex-1 space-y-1">
        <p className={cn('text-sm leading-5', styles.title)}>{title}</p>
        {description && <p className={cn('text-sm leading-5', styles.body)}>{description}</p>}
        {children && <div className={cn('text-sm leading-5', styles.body)}>{children}</div>}
        {action && <div className="pt-2">{action}</div>}
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label={`Dismiss ${title}`}
          className="inline-flex min-h-[36px] min-w-[36px] items-center justify-center rounded-md text-slate-700 transition-colors hover:bg-black/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
