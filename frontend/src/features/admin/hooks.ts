import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { QRCode, QRFormat } from "@/features/memorial/edit-hooks";

export interface AdminStats {
  total_users: number;
  total_memorials: number;
  published_memorials: number;
  total_candles: number;
  total_condolences: number;
  pending_condolences: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_email_verified: boolean;
  memorials_count: number;
  created_at: string;
  last_login_at: string | null;
}

export interface AdminMemorial {
  id: string;
  public_slug: string;
  full_name: string;
  owner_email: string;
  status: string;
  view_count: number;
  candle_count: number;
  condolence_count: number;
  created_at: string;
}

export function useAdminStats() {
  return useQuery({
    queryKey: ["admin", "stats"],
    queryFn: async () => (await api.get<AdminStats>("/admin/stats")).data,
  });
}

export function useAdminUsers() {
  return useQuery({
    queryKey: ["admin", "users"],
    queryFn: async () => (await api.get<AdminUser[]>("/admin/users?limit=200")).data,
  });
}

export function useSetUserActive() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patch(`/admin/users/${id}`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
}

export function useAdminMemorials() {
  return useQuery({
    queryKey: ["admin", "memorials"],
    queryFn: async () =>
      (await api.get<AdminMemorial[]>("/admin/memorials?limit=200")).data,
  });
}

export function useSetMemorialStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) =>
      api.patch(`/admin/memorials/${id}/status`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "memorials"] }),
  });
}

export function useAdminMemorialQR(memorialId: string, enabled: boolean) {
  return useQuery({
    queryKey: ["admin", "qr", memorialId],
    queryFn: async () =>
      (await api.get<QRCode[]>(`/admin/memorials/${memorialId}/qr`)).data,
    enabled: enabled && Boolean(memorialId),
  });
}

export function useGenerateAdminQR(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { format: QRFormat; label?: string }) =>
      (await api.post<QRCode>(`/admin/memorials/${memorialId}/qr`, input)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "qr", memorialId] }),
  });
}
