import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export type MediaType = "photo" | "video" | "audio";
export type MediaStatus = "pending" | "processing" | "ready" | "failed" | "quarantined";

export interface MediaItem {
  id: string;
  media_type: MediaType;
  status: MediaStatus;
  url: string | null;
  thumbnail_url: string | null;
  caption: string | null;
  position: number;
  content_type: string | null;
  original_filename: string | null;
}

interface UploadInitResponse {
  media_id: string;
  upload_url: string;
  storage_key: string;
  expires_in: number;
}

export function useMemorialMedia(memorialId: string) {
  return useQuery({
    queryKey: ["media", memorialId],
    queryFn: async () =>
      (await api.get<MediaItem[]>(`/memorials/${memorialId}/media`)).data,
    enabled: Boolean(memorialId),
  });
}

function mediaTypeForFile(file: File): MediaType {
  if (file.type.startsWith("video/")) return "video";
  if (file.type.startsWith("audio/")) return "audio";
  return "photo";
}

/**
 * Subida en 3 pasos:
 *   1. POST /upload-url  → URL prefirmada
 *   2. PUT directo a MinIO (sin Authorization — es otro origen)
 *   3. POST /confirm     → marca READY y encola el procesamiento
 */
export function useUploadMedia(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const init = (
        await api.post<UploadInitResponse>(`/memorials/${memorialId}/media/upload-url`, {
          media_type: mediaTypeForFile(file),
          original_filename: file.name,
          content_type: file.type,
          file_size: file.size,
        })
      ).data;

      const put = await fetch(init.upload_url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });
      if (!put.ok) throw new Error("Fallo al subir el archivo al almacenamiento.");

      return (
        await api.post<MediaItem>(
          `/memorials/${memorialId}/media/${init.media_id}/confirm`,
        )
      ).data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["media", memorialId] }),
  });
}

export function useDeleteMedia(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mediaId: string) =>
      api.delete(`/memorials/${memorialId}/media/${mediaId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["media", memorialId] }),
  });
}

export function useSetMainPhoto(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mediaId: string) =>
      api.post(`/memorials/${memorialId}/media/${mediaId}/set-main`),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["memorial", memorialId] });
      void qc.invalidateQueries({ queryKey: ["memorials"] });
    },
  });
}

export function useSetCoverPhoto(memorialId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mediaId: string) =>
      api.post(`/memorials/${memorialId}/media/${mediaId}/set-cover`),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["memorial", memorialId] });
      void qc.invalidateQueries({ queryKey: ["memorials"] });
    },
  });
}
