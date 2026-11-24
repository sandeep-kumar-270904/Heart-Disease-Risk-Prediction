import React from 'react';
import { AlertOctagon, AlertTriangle, CheckCircle2, Info, ShieldCheck } from 'lucide-react';
import { cn } from '@/lib/cn';

export type BadgeVariant = 'low' | 'moderate' | 'elevated' | 'verified' | 'neutral';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  readonly variant?: BadgeVariant;
  readonly icon?: React.ReactNode;
  readonly hideDefaultIcon?: boolean;
}

const badgeStyles: Record<BadgeVariant, string> = {
  low: 'bg-emerald-50 border-emerald-600 text-emerald-700',
  moderate: 'bg-amber-50 border-amber-600 text-amber-700',
  elevated: 'bg-crimson-50 border-crimson-600 text-crimson-700',
  verified: 'bg-sky-50 border-sky-600 text-sky-700',
  neutral: 'bg-slate-100 border-slate-300 text-slate-700',
};

const defaultIcons: Record<BadgeVariant, React.ReactNode> = {
  low: <CheckCircle2 className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />,
  moderate: <AlertTriangle className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />,
  elevated: <AlertOctagon className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />,
  verified: <ShieldCheck className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />,
  neutral: <Info className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />,
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  icon,
  hideDefaultIcon = false,
  className,
  children,
  ...props
}) => {
  const renderedIcon = icon ?? (hideDefaultIcon ? null : defaultIcons[variant]);

  return (
    <span
      className={cn(
        'inline-flex min-h-[24px] items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium leading-4',
        badgeStyles[variant],
        className
      )}
      {...props}
    >
      {renderedIcon}
      <span>{children}</span>
    </span>
  );
};
