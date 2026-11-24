import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';
import {
  Alert,
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
import type { TokenResponse, UserProfileResponse } from '@/types';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setSession = useAuthStore((s) => s.setSession);
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTarget = (location.state as { from?: string } | null)?.from ?? '/dashboard';

  const handleSubmit = async (event: React.FormEvent): Promise<void> => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const tokenRes = await apiFetch<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setSession(tokenRes.access_token);
      const profile = await apiFetch<UserProfileResponse>('/auth/me');
      setSession(tokenRes.access_token, profile);
      navigate(redirectTarget, { replace: true });
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError('Unable to reach authentication server.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md py-8">
      <Card elevated>
        <CardHeader>
          <CardTitle as="h1">Sign In to HeartXAI 2.0</CardTitle>
          <CardDescription>
            Use synthetic demonstration credentials (password copy/paste supported per WCAG 3.3.8).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <Alert severity="emergency" title="Sign-in Failed" description={error} />}

            <Input
              label="Email Address"
              type="email"
              required
              autoComplete="username"
              placeholder="patient.demo@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              label="Password"
              type="password"
              required
              autoComplete="current-password"
              leftIcon={<Lock className="h-4 w-4" />}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button type="submit" className="w-full" isLoading={isSubmitting} loadingText="Signing in...">
              Sign In
            </Button>

            <p className="text-center text-xs text-slate-600">
              Need a synthetic demo account?{' '}
              <Link to="/register" className="font-semibold text-sky-700 underline">
                Register here
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
