import { Download, ExternalLink, Loader2, QrCode } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useGenerateQR,
  useQRCodes,
  type QRCode,
  type QRFormat,
} from "@/features/memorial/edit-hooks";
import { cn } from "@/lib/utils";

const FORMATS: { value: QRFormat; label: string; hint: string }[] = [
  { value: "png", label: "PNG", hint: "Imagen para web e impresión" },
  { value: "svg", label: "SVG", hint: "Vectorial, ideal para grabado" },
  { value: "pdf", label: "PDF", hint: "Listo para imprimir" },
];

export function QRPanel({ memorialId }: { memorialId: string }) {
  const { data: codes = [], isLoading } = useQRCodes(memorialId);
  const generate = useGenerateQR(memorialId);
  const [format, setFormat] = useState<QRFormat>("png");
  const [label, setLabel] = useState("");

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-muted/30 p-5">
        <h3 className="flex items-center gap-2 font-semibold">
          <QrCode className="h-4 w-4 text-brand" /> Generar código QR
        </h3>
        <p className="mt-1 text-sm text-foreground-muted">
          Imprímelo en la lápida, nicho o recordatorio. Al escanearlo abre este
          memorial.
        </p>

        <div className="mt-4 grid gap-2 sm:grid-cols-3">
          {FORMATS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFormat(f.value)}
              className={cn(
                "rounded-md border p-3 text-left transition-colors",
                format === f.value
                  ? "border-brand bg-brand-light"
                  : "border-border bg-card hover:border-brand/40",
              )}
            >
              <p className="font-semibold">{f.label}</p>
              <p className="text-xs text-foreground-muted">{f.hint}</p>
            </button>
          ))}
        </div>

        <Input
          className="mt-3"
          placeholder="Etiqueta (opcional, ej. 'Lápida principal')"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          maxLength={120}
        />

        <Button
          className="mt-3"
          onClick={() => generate.mutate({ format, label: label.trim() || undefined })}
          disabled={generate.isPending}
        >
          {generate.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <QrCode className="h-4 w-4" />
          )}
          Generar QR
        </Button>
        {generate.isError && (
          <p className="mt-2 text-sm text-destructive">
            No se pudo generar el QR. Inténtalo de nuevo.
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton aspect-square rounded-lg" />
          ))}
        </div>
      ) : codes.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-10 text-center text-foreground-muted">
          <QrCode className="h-9 w-9 opacity-40" />
          <p className="text-sm">Aún no has generado ningún código QR.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {codes.map((qr) => (
            <QRCard key={qr.id} qr={qr} />
          ))}
        </div>
      )}
    </div>
  );
}

function QRCard({ qr }: { qr: QRCode }) {
  const isPreviewable = qr.format === "png" || qr.format === "svg";
  return (
    <div className="flex flex-col rounded-lg border border-border bg-card p-4 shadow-card">
      <div className="flex aspect-square items-center justify-center overflow-hidden rounded-md bg-white">
        {isPreviewable && qr.qr_url ? (
          <img src={qr.qr_url} alt="Código QR" className="h-full w-full object-contain p-2" />
        ) : (
          <QrCode className="h-12 w-12 text-foreground-muted" />
        )}
      </div>
      <div className="mt-3 flex items-center justify-between">
        <div className="min-w-0">
          <p className="text-sm font-semibold uppercase">{qr.format}</p>
          {qr.label && (
            <p className="truncate text-xs text-foreground-muted">{qr.label}</p>
          )}
        </div>
        {qr.qr_url && (
          <div className="flex gap-1">
            <a
              href={qr.qr_url}
              target="_blank"
              rel="noreferrer"
              title="Abrir"
              className="rounded-md p-1.5 text-brand transition-colors hover:bg-brand-light"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
            <a
              href={qr.qr_url}
              download={`qr-${qr.format}.${qr.format}`}
              title="Descargar"
              className="rounded-md p-1.5 text-brand transition-colors hover:bg-brand-light"
            >
              <Download className="h-4 w-4" />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
