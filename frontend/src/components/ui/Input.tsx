import React, { useId } from 'react';
import { AlertCircle } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  readonly label: string;
  readonly helperText?: string;
  readonly error?: string;
  readonly unitAffix?: string;
  readonly leftIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      id,
      label,
      helperText,
      error,
      unitAffix,
      leftIcon,
      required,
      disabled,
      className,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id ?? `hx-input-${generatedId}`;
    const helperId = `${inputId}-help`;
    const errorId = `${inputId}-error`;

    const describedByIds: string[] = [];
    if (helperText) describedByIds.push(helperId);
    if (error) describedByIds.push(errorId);

    return (
      <div className="flex flex-col gap-1.5">
        <label htmlFor={inputId} className="text-sm font-medium text-slate-900">
          {label}
          {required && (
            <>
              <span aria-hidden="true" className="ml-1 text-crimson-600">
                *
              </span>
              <span className="sr-only"> (Required)</span>
            </>
          )}
        </label>

        <div className="relative flex items-center">
          {leftIcon && (
            <span
              aria-hidden="true"
              className="pointer-events-none absolute left-3 flex items-center text-slate-500"
            >
              {leftIcon}
            </span>
          )}

          <input
            ref={ref}
            id={inputId}
            required={required}
            disabled={disabled}
            aria-required={required || undefined}
            aria-invalid={Boolean(error)}
            aria-describedby={describedByIds.length > 0 ? describedByIds.join(' ') : undefined}
            className={cn(
              'min-h-[44px] w-full rounded-md border bg-white px-3 py-2 text-base text-slate-900 placeholder:text-slate-400',
              'transition-colors duration-150',
              'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600',
              'disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500',
              error
                ? 'border-crimson-600 bg-crimson-50 text-crimson-900'
                : 'border-slate-300 hover:border-slate-400',
              leftIcon ? 'pl-10' : undefined,
              unitAffix ? 'pr-16 tabular-clinical' : undefined,
              className
            )}
            {...props}
          />

          {unitAffix && (
            <span
              aria-hidden="true"
              className="pointer-events-none absolute right-3 border-l border-slate-200 pl-2.5 font-mono text-xs font-medium text-slate-600"
            >
              {unitAffix}
            </span>
          )}
        </div>

        {helperText && (
          <p id={helperId} className="text-xs leading-4 text-slate-600">
            {helperText}
          </p>
        )}

        {error && (
          <p
            id={errorId}
            role="alert"
            className="flex items-center gap-1.5 text-xs font-medium leading-4 text-crimson-700"
          >
            <AlertCircle className="h-3.5 w-3.5 shrink-0 text-crimson-600" aria-hidden="true" />
            <span>{error}</span>
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
