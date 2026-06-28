import { AnimatePresence, motion } from "framer-motion";
import { ImageIcon, ImagePlus, Loader2, Star, Trash2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import {
  useDeleteMedia,
  useMemorialMedia,
  useSetCoverPhoto,
  useSetMainPhoto,
  useUploadMedia,
  type MediaItem,
} from "@/features/memorial/media-hooks";
import { cn } from "@/lib/utils";

const ACCEPT = "image/jpeg,image/png,image/webp,image/avif,video/mp4,video/webm,audio/mpeg";

export function MediaUploader({ memorialId }: { memorialId: string }) {
  const { data: media = [], isLoading } = useMemorialMedia(memorialId);
  const upload = useUploadMedia(memorialId);
  const remove = useDeleteMedia(memorialId);
  const setMain = useSetMainPhoto(memorialId);
  const setCover = useSetCoverPhoto(memorialId);

  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files?.length) return;
    setError(null);
    for (const file of Array.from(files)) {
      try {
        await upload.mutateAsync(file);
      } catch {
        setError(`No se pudo subir "${file.name}". Verifica el formato y el tamaño.`);
      }
    }
  };

  return (
    <div>
      {/* Zona de dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          void handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-10 text-center transition-colors",
          dragging
            ? "border-brand bg-brand-light"
            : "border-border bg-muted/40 hover:border-brand/40 hover:bg-brand-light/40",
        )}
      >
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-light text-brand">
          {upload.isPending ? (
            <Loader2 className="h-7 w-7 animate-spin" />
          ) : (
            <UploadCloud className="h-7 w-7" />
          )}
        </div>
        <div>
          <p className="font-semibold">
            {upload.isPending ? "Subiendo…" : "Arrastra fotos, videos o audios aquí"}
          </p>
          <p className="text-sm text-foreground-muted">
            o haz clic para seleccionar · JPG, PNG, WEBP, MP4, MP3
          </p>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          multiple
          className="hidden"
          onChange={(e) => void handleFiles(e.target.files)}
        />
      </div>

      {error && <p className="mt-3 text-sm text-destructive">{error}</p>}

      {/* Galería */}
      <div className="mt-6">
        {isLoading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="skeleton aspect-square rounded-lg" />
            ))}
          </div>
        ) : media.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-12 text-center text-foreground-muted">
            <ImagePlus className="h-10 w-10 opacity-50" />
            <p>Aún no hay recuerdos. Sube la primera foto.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            <AnimatePresence>
              {media.map((item) => (
                <MediaCard
                  key={item.id}
                  item={item}
                  onDelete={() => remove.mutate(item.id)}
                  onSetMain={() => setMain.mutate(item.id)}
                  onSetCover={() => setCover.mutate(item.id)}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}

function MediaCard({
  item,
  onDelete,
  onSetMain,
  onSetCover,
}: {
  item: MediaItem;
  onDelete: () => void;
  onSetMain: () => void;
  onSetCover: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="group relative aspect-square overflow-hidden rounded-lg border border-border bg-muted"
    >
      {item.media_type === "photo" && item.url ? (
        <img
          src={item.thumbnail_url ?? item.url}
          alt={item.caption ?? item.original_filename ?? "recuerdo"}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-xs text-foreground-muted">
          {item.media_type.toUpperCase()}
        </div>
      )}

      {item.status !== "ready" && (
        <span className="absolute left-2 top-2 rounded-full bg-foreground/70 px-2 py-0.5 text-[10px] font-medium text-white">
          {item.status}
        </span>
      )}

      <div className="absolute inset-x-0 bottom-0 flex translate-y-full justify-end gap-1 bg-gradient-to-t from-foreground/70 to-transparent p-2 transition-transform group-hover:translate-y-0">
        {item.media_type === "photo" && (
          <>
            <button
              onClick={onSetMain}
              title="Fijar como foto principal"
              className="rounded-md bg-white/90 p-1.5 text-brand hover:bg-white"
            >
              <Star className="h-4 w-4" />
            </button>
            <button
              onClick={onSetCover}
              title="Fijar como portada"
              className="rounded-md bg-white/90 p-1.5 text-brand hover:bg-white"
            >
              <ImageIcon className="h-4 w-4" />
            </button>
          </>
        )}
        <button
          onClick={onDelete}
          title="Eliminar"
          className="rounded-md bg-white/90 p-1.5 text-destructive hover:bg-white"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </motion.div>
  );
}
