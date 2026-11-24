import React, { useEffect, useState } from 'react';
import { PhoneCall, Search } from 'lucide-react';
import {
  Alert,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Select,
} from '@/components/ui';
import { apiFetch } from '@/services/apiClient';
import { useAuthStore } from '@/stores/authStore';
import type { DoctorProfileDto, HospitalFacilityDto } from '@/types';

const HOTLINES: Record<string, { readonly number: string; readonly label: string }> = {
  US: { number: '911', label: 'US Emergency Services (911)' },
  IN: { number: '112', label: 'India National Emergency (112)' },
  GB: { number: '999', label: 'UK Emergency Services (999)' },
};

export const DirectoryPage: React.FC = () => {
  const defaultCountry = useAuthStore((s) => s.countryCode);
  const [country, setCountry] = useState<string>(defaultCountry);
  const [city, setCity] = useState<string>('');
  const [doctors, setDoctors] = useState<DoctorProfileDto[]>([]);
  const [hospitals, setHospitals] = useState<HospitalFacilityDto[]>([]);

  const loadDirectory = async (selectedCountry: string, cityQuery: string): Promise<void> => {
    const params = new URLSearchParams();
    if (selectedCountry) params.set('country_code', selectedCountry);
    if (cityQuery.trim()) params.set('city', cityQuery.trim());
    try {
      const [docs, hosps] = await Promise.all([
        apiFetch<DoctorProfileDto[]>(`/directory/doctors?${params.toString()}`),
        apiFetch<HospitalFacilityDto[]>(`/directory/hospitals?${params.toString()}`),
      ]);
      setDoctors(docs);
      setHospitals(hosps);
    } catch {
      setDoctors([]);
      setHospitals([]);
    }
  };

  useEffect(() => {
    void loadDirectory(country, '');
  }, [country]);

  const hotline = HOTLINES[country] ?? HOTLINES.US!;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Localized Healthcare Directory &amp; Emergency Care
          </h1>
          <p className="text-sm text-slate-600">
            Demonstration directory profiles aligned with DEC-004 (synthetic seed records only).
          </p>
        </div>
        <a
          href={`tel:${hotline.number}`}
          className="inline-flex min-h-[44px] items-center gap-2 rounded-md bg-crimson-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-crimson-700"
        >
          <PhoneCall className="h-4 w-4" aria-hidden="true" />
          <span>{hotline.label}</span>
        </a>
      </div>

      <Alert
        severity="info"
        title="Synthetic Regional Directory"
        description="External commercial provider APIs are disabled. Results reflect verified synthetic seed entries."
      />

      <Card>
        <CardHeader>
          <CardTitle as="h2">Filter Care Providers</CardTitle>
          <CardDescription>Filter cardiologists and emergency facilities by country and city.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          <Select
            label="Country Adapter"
            value={country}
            onValueChange={setCountry}
            options={[
              { value: 'US', label: 'United States (US)' },
              { value: 'IN', label: 'India (IN)' },
              { value: 'GB', label: 'United Kingdom (GB)' },
            ]}
          />
          <Input
            label="City / Region"
            placeholder="e.g., Boston, New Delhi, London"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          />
          <div className="flex items-end">
            <Button
              onClick={() => void loadDirectory(country, city)}
              leftIcon={<Search className="h-4 w-4" />}
            >
              Search Directory
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle as="h2">Cardiology Specialists ({doctors.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {doctors.length === 0 ? (
              <p className="text-sm text-slate-500">No providers matched current filters.</p>
            ) : (
              doctors.map((doc) => (
                <div key={doc.id} className="rounded-lg border border-slate-200 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold text-slate-900">{doc.full_name}</p>
                    <Badge variant="verified">{doc.country_code}</Badge>
                  </div>
                  <p className="text-xs text-slate-600">{doc.specialization}</p>
                  <p className="mt-1 text-xs text-slate-700">
                    {doc.hospital_affiliation} • {doc.city}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle as="h2">Cardiac Emergency Hospitals ({hospitals.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {hospitals.length === 0 ? (
              <p className="text-sm text-slate-500">No facilities matched current filters.</p>
            ) : (
              hospitals.map((hosp) => (
                <div key={hosp.id} className="rounded-lg border border-slate-200 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-semibold text-slate-900">{hosp.name}</p>
                    <Badge variant="elevated">Emergency: {hosp.emergency_phone}</Badge>
                  </div>
                  <p className="text-xs text-slate-600">{hosp.accreditation}</p>
                  <p className="mt-1 text-xs text-slate-700">
                    {hosp.address}, {hosp.city} ({hosp.country_code})
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
