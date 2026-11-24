import React, { useId } from 'react';
import * as SelectPrimitive from '@radix-ui/react-select';
import { AlertCircle, Check, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface SelectOption {
  readonly value: string;
  readonly label: string;
  readonly disabled?: boolean;
}

export interface SelectProps {
  readonly id?: string;
  readonly label: string;
  readonly options: readonly SelectOption[];
  readonly value?: string;
  readonly defaultValue?: string;
  readonly onValueChange?: (value: string) => void;
  readonly placeholder?: string;
  readonly helperText?: string;
  readonly error?: string;
  readonly required?: boolean;
  readonly disabled?: boolean;
  readonly className?: string;
}

export const Select: React.FC<SelectProps> = ({
  id,
  label,
  options,
  value,
  defaultValue,
  onValueChange,
  placeholder = 'Select an option...',
  helperText,
  error,
  required,
  disabled,
  className,
}) => {
  const generatedId = useId();
  const triggerId = id ?? `hx-select-${generatedId}`;
  const labelId = `${triggerId}-label`;
  const helperId = `${triggerId}-help`;
  const errorId = `${triggerId}-error`;

  const describedByIds: string[] = [];
  if (helperText) describedByIds.push(helperId);
  if (error) describedByIds.push(errorId);

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label id={labelId} htmlFor={triggerId} className="text-sm font-medium text-slate-900">
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

      <SelectPrimitive.Root
        value={value}
        defaultValue={defaultValue}
        onValueChange={onValueChange}
        disabled={disabled}
        required={required}
      >
        <SelectPrimitive.Trigger
          id={triggerId}
          aria-labelledby={labelId}
          aria-required={required || undefined}
          aria-invalid={Boolean(error)}
          aria-describedby={describedByIds.length > 0 ? describedByIds.join(' ') : undefined}
          className={cn(
            'inline-flex min-h-[44px] w-full items-center justify-between gap-2 rounded-md border bg-white px-3 py-2 text-left text-base text-slate-900',
            'transition-colors duration-150',
            'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600',
            'disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500',
            'data-[placeholder]:text-slate-500',
            error
              ? 'border-crimson-600 bg-crimson-50 text-crimson-900'
              : 'border-slate-300 hover:border-slate-400'
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon asChild>
            <ChevronDown className="h-4 w-4 shrink-0 text-slate-600" aria-hidden="true" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>

        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            position="popper"
            sideOffset={4}
            className="z-dropdown max-h-64 min-w-[var(--radix-select-trigger-width)] overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg"
          >
            <SelectPrimitive.Viewport className="p-1">
              {options.map((option) => (
                <SelectPrimitive.Item
                  key={option.value}
                  value={option.value}
                  disabled={option.disabled}
                  className={cn(
                    'relative flex min-h-[40px] cursor-pointer select-none items-center rounded-md py-2 pl-8 pr-3 text-sm text-slate-900 outline-none',
                    'focus:bg-sky-50 focus:text-sky-900',
                    'data-[disabled]:pointer-events-none data-[disabled]:opacity-50'
                  )}
                >
                  <span className="absolute left-2.5 flex h-4 w-4 items-center justify-center">
                    <SelectPrimitive.ItemIndicator>
                      <Check className="h-4 w-4 text-sky-600" aria-hidden="true" />
                    </SelectPrimitive.ItemIndicator>
                  </span>
                  <SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText>
                </SelectPrimitive.Item>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>

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
};
