import React from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui';
import { LoginPage } from '@/features/auth/LoginPage';
import { RegisterPage } from '@/features/auth/RegisterPage';
import { IntakeWizardPage } from '@/features/intake/IntakeWizardPage';
import { ProtectedRoute } from '@/routes/ProtectedRoute';

const DashboardPlaceholder: React.FC = () => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle as="h1">Cardiovascular Health Workspace</CardTitle>
        <CardDescription>
          Explore Task A CAD likelihood assessments, TreeSHAP explanations, and lifestyle scenarios.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-3">
        <Button asChild>
          <Link to="/intake">Start New Assessment</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/directory">Browse Care Directory</Link>
        </Button>
      </CardContent>
    </Card>
  </div>
);

export const AppRoutes: React.FC = () => (
  <AppShell>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPlaceholder />
          </ProtectedRoute>
        }
      />
      <Route
        path="/intake"
        element={
          <ProtectedRoute>
            <IntakeWizardPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  </AppShell>
);

export const App: React.FC = () => (
  <BrowserRouter>
    <AppRoutes />
  </BrowserRouter>
);

export default App;
