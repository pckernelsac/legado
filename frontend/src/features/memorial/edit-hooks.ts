import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Memorial } from "@/features/memorial/hooks";

export interface MemorialDetail extends Memorial {
  birth_place: string | null;
  death_place: string | null;
  epitaph: string | null;
  cover_photo_url: string | null;
  visibility: string;
}

export interface MemorialFormValues {
  full_name: string;
  birth_date?: string | null;
  death_date?: string | null;
  birth_place?: string | null;
  death_place?: string | null;
  profession?: string | null;
  biography?: string | null;
  epitaph?: string | null;
  cemetery_name?: string | null;
  location_address?: string | null;
  visibility?: string;
  status?: string;
}

export function useMemorial(id: string) {
  return useQuery({
    queryKey: ["memorial", id],
    queryFn: async () => (await api.get<MemorialDetail>(`/memorials/${id}`)).data,
    enabled: Boolean(id),
  });
}

export function useUpdateMemorial(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (values: Partial<MemorialFormValues>) =>
      (await api.patch<MemorialDetail>(`/memorials/${id}`, values)).data,
    onSuccess: (data) => {
      qc.setQueryData(["memorial", id], data);
      void qc.invalidateQueries({ queryKey: ["memorials"] });
    },
  });
}

/* --- Línea de tiempo (gestión) ------------------------------------------- */

export interface TimelineEvent {
  id: string;
  year: number | null;
  event_date: string | null;
  title: string;
  description: string | null;
  position: number;
}

export interface TimelineEventInput {
  year?: number | null;
  event_date?: string | null;
  title: string;
  description?: string | null;
}

export function useTimeline(memorialId: string) {
  return useQuery({
    queryKey: ["timeline", memorialId],
    queryFn: async () =>
      (await api.get<TimelineEvent[]>(`/memorials/${memorialId}/timeline`)).data,
    enabled: Boolean(memorialId),
  });
}

export function useCreateTimelineEvent(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: TimelineEventInput) =>
      (await api.post<TimelineEvent>(`/memorials/${memorialId}/timeline`, input)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["timeline", memorialId] }),
  });
}

export function useDeleteTimelineEvent(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (eventId: string) =>
      api.delete(`/memorials/${memorialId}/timeline/${eventId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["timeline", memorialId] }),
  });
}

/* --- Moderación de condolencias ------------------------------------------ */

export interface AdminCondolence {
  id: string;
  author_name: string;
  author_email: string | null;
  message: string;
  signature: string | null;
  photo_url: string | null;
  moderation_status: "pending" | "approved" | "rejected" | "auto_approved";
  created_at: string;
}

export function useModerationCondolences(memorialId: string) {
  return useQuery({
    queryKey: ["moderation", memorialId],
    queryFn: async () =>
      (await api.get<AdminCondolence[]>(`/memorials/${memorialId}/condolences`)).data,
    enabled: Boolean(memorialId),
  });
}

export function useModerateCondolence(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, approve }: { id: string; approve: boolean }) =>
      api.post(`/memorials/${memorialId}/condolences/${id}/moderate`, { approve }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["moderation", memorialId] }),
  });
}

/* --- Árbol genealógico ---------------------------------------------------- */

export interface FamilyMember {
  id: string;
  full_name: string;
  relationship_type: string | null;
  birth_year: number | null;
  death_year: number | null;
  parent_member_id: string | null;
}

export interface FamilyMemberInput {
  full_name: string;
  relationship_type?: string | null;
  birth_year?: number | null;
  death_year?: number | null;
  parent_member_id?: string | null;
}

export function useFamily(memorialId: string) {
  return useQuery({
    queryKey: ["family", memorialId],
    queryFn: async () =>
      (await api.get<FamilyMember[]>(`/memorials/${memorialId}/family`)).data,
    enabled: Boolean(memorialId),
  });
}

export function useCreateFamilyMember(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: FamilyMemberInput) =>
      (await api.post<FamilyMember>(`/memorials/${memorialId}/family`, input)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["family", memorialId] }),
  });
}

export function useDeleteFamilyMember(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (memberId: string) =>
      api.delete(`/memorials/${memorialId}/family/${memberId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["family", memorialId] }),
  });
}

/* --- Códigos QR ----------------------------------------------------------- */

export type QRFormat = "png" | "svg" | "pdf";

export interface QRCode {
  id: string;
  format: QRFormat;
  target_url: string;
  label: string | null;
  qr_url: string | null;
}

export function useQRCodes(memorialId: string) {
  return useQuery({
    queryKey: ["qr", memorialId],
    queryFn: async () =>
      (await api.get<QRCode[]>(`/memorials/${memorialId}/qr`)).data,
    enabled: Boolean(memorialId),
  });
}

export function useGenerateQR(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { format: QRFormat; label?: string }) =>
      (await api.post<QRCode>(`/memorials/${memorialId}/qr`, input)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["qr", memorialId] }),
  });
}
