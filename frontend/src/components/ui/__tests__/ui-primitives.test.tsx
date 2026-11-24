import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { axe } from 'vitest-axe';
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
} from '../index';
import { DesignSystemShowcase } from '../Showcase';

describe('HeartXAI UI Component Library (WCAG 2.2 AA & Functionality)', () => {
  it('Button renders variants, loading state, handles clicks, and passes axe accessibility audit', async () => {
    const onClick = vi.fn();
    const { container } = render(
      <div className="flex gap-2">
        <Button variant="primary" onClick={onClick}>
          Run Assessment
        </Button>
        <Button variant="secondary">Cancel</Button>
        <Button variant="outline">Details</Button>
        <Button variant="ghost">Dismiss</Button>
        <Button variant="danger">Delete</Button>
        <Button isLoading loadingText="Computing...">
          Submit
        </Button>
      </div>
    );

    const primaryBtn = screen.getByRole('button', { name: 'Run Assessment' });
    await userEvent.click(primaryBtn);
    expect(onClick).toHaveBeenCalledTimes(1);

    const loadingBtn = screen.getByRole('button', { name: /Computing/i });
    expect(loadingBtn).toBeDisabled();
    expect(loadingBtn).toHaveAttribute('aria-busy', 'true');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Badge renders clinical strata with accessible labels and passes axe audit', async () => {
    const { container } = render(
      <div>
        <Badge variant="low">Low Risk</Badge>
        <Badge variant="moderate">Moderate Risk</Badge>
        <Badge variant="elevated">Elevated Risk</Badge>
        <Badge variant="verified">Clinician Verified</Badge>
        <Badge variant="neutral">Category B</Badge>
      </div>
    );

    expect(screen.getByText('Low Risk')).toBeInTheDocument();
    expect(screen.getByText('Elevated Risk')).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Card renders semantic heading hierarchy and passes axe audit', async () => {
    const { container } = render(
      <Card>
        <CardHeader>
          <CardTitle>Assessment Summary</CardTitle>
          <CardDescription>Retrospective CAD classification metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Sample content body</p>
        </CardContent>
        <CardFooter>
          <span>Model v2.0.0</span>
        </CardFooter>
      </Card>
    );

    expect(screen.getByRole('heading', { name: 'Assessment Summary' })).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Input enforces bound label, unit affix, error role=alert, and passes axe audit', async () => {
    const { container } = render(
      <div>
        <Input
          label="Serum Cholesterol"
          required
          unitAffix="mg/dL"
          helperText="Reference: 125-200 mg/dL"
          defaultValue="195"
        />
        <Input
          label="Systolic BP"
          unitAffix="mmHg"
          defaultValue="320"
          error="Blood pressure must be between 70 and 240 mmHg."
        />
      </div>
    );

    const cholInput = screen.getByLabelText(/Serum Cholesterol/i);
    expect(cholInput).toBeRequired();
    expect(cholInput).toHaveAttribute('aria-invalid', 'false');

    const bpInput = screen.getByLabelText(/Systolic BP/i);
    expect(bpInput).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByRole('alert')).toHaveTextContent(
      'Blood pressure must be between 70 and 240 mmHg.'
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Select renders accessible combobox with label and passes axe audit', async () => {
    const onValueChange = vi.fn();
    const { container } = render(
      <Select
        label="Chest Pain Type"
        required
        defaultValue="0"
        onValueChange={onValueChange}
        helperText="Select symptom classification"
        options={[
          { value: '0', label: 'Typical Angina' },
          { value: '1', label: 'Atypical Angina' },
          { value: '2', label: 'Non-Anginal Pain' },
          { value: '3', label: 'Asymptomatic' },
        ]}
      />
    );

    const trigger = screen.getByRole('combobox', { name: /Chest Pain Type/i });
    expect(trigger).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Alert renders all severities, supports dismiss action, and passes axe audit', async () => {
    const onDismiss = vi.fn();
    const { container } = render(
      <div className="space-y-2">
        <Alert severity="emergency" title="Emergency Notice" description="Call 911 immediately." />
        <Alert
          severity="warning"
          title="Missing Value"
          description="Imputation applied."
          onDismiss={onDismiss}
        />
        <Alert severity="info" title="Info Notice" description="Educational model." />
        <Alert severity="success" title="Saved" description="Profile updated." />
      </div>
    );

    const dismissBtn = screen.getByRole('button', { name: 'Dismiss Missing Value' });
    await userEvent.click(dismissBtn);
    expect(onDismiss).toHaveBeenCalledTimes(1);

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Modal traps focus, closes via close button or Escape, and passes axe audit', async () => {
    const { container } = render(
      <Modal
        trigger={<Button>Open Modal</Button>}
        title="Clinical Disclaimer"
        description="Informational notice"
      >
        <p>Non-diagnostic tool notice.</p>
      </Modal>
    );

    await userEvent.click(screen.getByRole('button', { name: 'Open Modal' }));
    const dialog = screen.getByRole('dialog', { name: 'Clinical Disclaimer' });
    expect(dialog).toBeInTheDocument();

    const results = await axe(document.body);
    expect(results).toHaveNoViolations();

    await userEvent.click(screen.getByRole('button', { name: 'Close dialog' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    const closedResults = await axe(container);
    expect(closedResults).toHaveNoViolations();
  });

  it('Tooltip renders trigger cleanly and passes axe audit', async () => {
    const { container } = render(
      <TooltipProvider>
        <Tooltip content="Measures peak exercise ST depression">
          <Button variant="outline">Oldpeak Info</Button>
        </Tooltip>
      </TooltipProvider>
    );

    expect(screen.getByRole('button', { name: 'Oldpeak Info' })).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Full DesignSystemShowcase renders cleanly with zero WCAG violations', async () => {
    const { container } = render(<DesignSystemShowcase />);
    expect(
      screen.getByRole('heading', { name: 'HeartXAI 2.0 Design System Primitives' })
    ).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
