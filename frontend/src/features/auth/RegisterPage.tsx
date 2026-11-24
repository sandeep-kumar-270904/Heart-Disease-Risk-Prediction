import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Alert,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Select,
} from '@/components/ui';
import { apiFetch, ApiClientError } from '@/services/apiClient';
import type { UserProfileResponse } from '@/types';

export const RegisterPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [countryCode, setCountryCode] = useState('US');
  const [consentGiven, setConsentGiven] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent): Promise<void> => {
    event.preventDefault();
    if (!consentGiven) {
      setError('You must confirm the educational non-diagnostic boundary notice to register.');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await apiFetch<UserProfileResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          full_name: fullName,
          email,
          password,
          country_code: countryCode,
          consent_given: true,
        }),
      });
      navigate('/login');
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Registration failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md py-6">
      <Card elevated>
        <CardHeader>
          <CardTitle as="h1">Create Synthetic Demo Account</CardTitle>
          <CardDescription>Do NOT enter real patient health information (Category C prohibited).</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <Alert severity="warning" title="Registration Issue" description={error} />}
            <Input
              label="Synthetic Persona Name"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            <Input
              label="Email Address"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              label="Password (min 12 chars)"
              type="password"
              required
              minLength={12}
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Select
              label="Country Adapter Profile"
              value={countryCode}
              onValueChange={setCountryCode}
              options={[
                { value: 'US', label: 'United States (US)' },
                { value: 'IN', label: 'India (IN)' },
                { value: 'GB', label: 'United Kingdom (GB)' },
              ]}
            />
            <label className="flex items-start gap-2.5 text-xs text-slate-700">
              <input
                type="checkbox"
                checked={consentGiven}
                onChange={(e) => setConsentGiven(e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-slate-300"
              />
              <span>
                I acknowledge HeartXAI 2.0 is a non-diagnostic educational decision-support tool
                operating strictly on synthetic data.
              </span>
            </label>
            <Button type="submit" className="w-full" isLoading={isSubmitting} loadingText="Creating...">
              Create Account
            </Button>
            <p className="text-center text-xs text-slate-600">
              Already registered?{' '}
              <Link to="/login" className="font-semibold text-sky-700 underline">
                Sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
