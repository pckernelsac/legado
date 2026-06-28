import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export interface Memorial {
  id: string;
  public_slug: string;
  full_name: string;
  birth_date: string | null;
  death_date: string | null;
  profession: string | null;
  biography: string | null;
  main_photo_url: string | null;
  status: string;
  view_count: number;
  candle_count: number;
  condolence_count: number;
  created_at: string;
}

export interface PublicMemorial extends Memorial {
  birth_place: string | null;
  death_place: string | null;
  epitaph: string | null;
  memorable_quotes: string[] | null;
  cover_photo_url: string | null;
  location_lat: number | null;
  location_lng: number | null;
  location_address: string | null;
  cemetery_name: string | null;
}

interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export function useMyMemorials() {
  return useQuery({
    queryKey: ["memorials"],
    queryFn: async () => (await api.get<Page<Memorial>>("/memorials")).data,
  });
}

export function useCreateMemorial() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { full_name: string }) =>
      (await api.post<Memorial>("/memorials", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memorials"] }),
  });
}

export function usePublicMemorial(slug: string) {
  return useQuery({
    queryKey: ["public-memorial", slug],
    queryFn: async () =>
      (await api.get<PublicMemorial>(`/public/memorials/${slug}`)).data,
    enabled: Boolean(slug),
  });
}

export interface LightCandlePayload {
  lit_by_name?: string;
  message?: string;
}

export function useLightCandle(slug: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: LightCandlePayload) =>
      (await api.post(`/public/memorials/${slug}/candles`, payload)).data,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["public-memorial", slug] }),
  });
}

export interface PublicMediaItem {
  id: string;
  media_type: "photo" | "video" | "audio";
  url: string | null;
  thumbnail_url: string | null;
  caption: string | null;
  original_filename: string | null;
}

export function usePublicMedia(slug: string) {
  return useQuery({
    queryKey: ["public-media", slug],
    queryFn: async () =>
      (await api.get<PublicMediaItem[]>(`/public/memorials/${slug}/media`)).data,
    enabled: Boolean(slug),
  });
}

export interface TimelineItem {
  id: string;
  year: number | null;
  event_date: string | null;
  title: string;
  description: string | null;
  image_url: string | null;
}

export function usePublicTimeline(slug: string) {
  return useQuery({
    queryKey: ["public-timeline", slug],
    queryFn: async () =>
      (await api.get<TimelineItem[]>(`/public/memorials/${slug}/timeline`)).data,
    enabled: Boolean(slug),
  });
}

export interface Condolence {
  id: string;
  author_name: string;
  message: string;
  signature: string | null;
  photo_url: string | null;
  created_at: string;
}

export function usePublicCondolences(slug: string) {
  return useQuery({
    queryKey: ["public-condolences", slug],
    queryFn: async () =>
      (await api.get<Condolence[]>(`/public/memorials/${slug}/condolences`)).data,
    enabled: Boolean(slug),
  });
}

export interface FamilyMember {
  id: string;
  full_name: string;
  relationship_type: string | null;
  birth_year: number | null;
  death_year: number | null;
  parent_member_id: string | null;
}

export function usePublicFamily(slug: string) {
  return useQuery({
    queryKey: ["public-family", slug],
    queryFn: async () =>
      (await api.get<FamilyMember[]>(`/public/memorials/${slug}/family`)).data,
    enabled: Boolean(slug),
  });
}

export interface CandleCountry {
  country: string;
  country_code: string | null;
  count: number;
}

export function usePublicCandlesByCountry(slug: string) {
  return useQuery({
    queryKey: ["public-candles-country", slug],
    queryFn: async () =>
      (await api.get<CandleCountry[]>(`/public/memorials/${slug}/candles/by-country`))
        .data,
    enabled: Boolean(slug),
  });
}

export interface CondolencePayload {
  author_name: string;
  message: string;
  signature?: string;
  photo?: File | null;
}

export function useAddCondolence(slug: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CondolencePayload) => {
      // multipart/form-data: el endpoint acepta una foto opcional del visitante.
      const form = new FormData();
      form.append("author_name", payload.author_name);
      form.append("message", payload.message);
      if (payload.signature) form.append("signature", payload.signature);
      if (payload.photo) form.append("photo", payload.photo);
      // Forzamos multipart: con el Content-Type JSON por defecto, axios
      // serializaría el FormData a JSON y descartaría el archivo. Al fijarlo a
      // multipart, el navegador añade el boundary correcto.
      return (
        await api.post(`/public/memorials/${slug}/condolences`, form, {
          headers: { "Content-Type": "multipart/form-data" },
        })
      ).data;
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["public-memorial", slug] });
      void qc.invalidateQueries({ queryKey: ["public-condolences", slug] });
    },
  });
}
