import { Check, MessageCircle, X } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  useModerateCondolence,
  useModerationCondolences,
  type AdminCondolence,
} from "@/features/memorial/edit-hooks";

const STATUS_LABEL: Record<AdminCondolence["moderation_status"], string> = {
  pending: "Pendiente",
  approved: "Aprobada",
  auto_approved: "Aprobada (auto)",
  rejected: "Rechazada",
};

const STATUS_STYLE: Record<AdminCondolence["moderation_status"], string> = {
  pending: "bg-accent/20 text-accent-foreground",
  approved: "bg-brand-light text-brand-hover",
  auto_approved: "bg-brand-light text-brand-hover",
  rejected: "bg-destructive/10 text-destructive",
};

export function CondolenceModeration({ memorialId }: { memorialId: string }) {
  const { data: items = [], isLoading } = useModerationCondolences(memorialId);
  const moderate = useModerateCondolence(memorialId);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="skeleton h-24 rounded-lg" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-12 text-center text-foreground-muted">
        <MessageCircle className="h-9 w-9 opacity-40" />
        <p className="text-sm">Aún no hay condolencias para moderar.</p>
      </div>
    );
  }

  const pending = items.filter((c) => c.moderation_status === "pending").length;

  return (
    <div className="space-y-4">
      {pending > 0 && (
        <p className="text-sm text-foreground-muted">
          Tienes <strong className="text-foreground">{pending}</strong> mensaje(s)
          pendiente(s) de revisión.
        </p>
      )}

      <ul className="space-y-3">
        {items.map((c) => {
          const isPending = c.moderation_status === "pending";
          const isApproved =
            c.moderation_status === "approved" ||
            c.moderation_status === "auto_approved";
          return (
            <li key={c.id} className="rounded-lg border border-border bg-card p-5 shadow-card">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-light font-semibold text-brand">
                    {c.author_name.charAt(0).toUpperCase()}
                  </span>
                  <div>
                    <p className="font-medium">{c.author_name}</p>
                    {c.author_email && (
                      <p className="text-xs text-foreground-muted">{c.author_email}</p>
                    )}
                  </div>
                </div>
                <span
                  className={cn(
                    "rounded-full px-3 py-1 text-xs font-medium",
                    STATUS_STYLE[c.moderation_status],
                  )}
                >
                  {STATUS_LABEL[c.moderation_status]}
                </span>
              </div>

              <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-foreground-muted">
                {c.message}
              </p>

              {c.photo_url && (
                <a
                  href={c.photo_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 block w-fit"
                >
                  <img
                    src={c.photo_url}
                    alt={`Foto adjunta por ${c.author_name}`}
                    loading="lazy"
                    className="max-h-48 rounded-md object-cover"
                  />
                </a>
              )}

              <div className="mt-4 flex gap-2">
                {!isApproved && (
                  <button
                    onClick={() => moderate.mutate({ id: c.id, approve: true })}
                    disabled={moderate.isPending}
                    className="inline-flex items-center gap-1.5 rounded-md bg-brand px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-brand-hover disabled:opacity-50"
                  >
                    <Check className="h-4 w-4" /> Aprobar
                  </button>
                )}
                {isPending || isApproved ? (
                  <button
                    onClick={() => moderate.mutate({ id: c.id, approve: false })}
                    disabled={moderate.isPending}
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 disabled:opacity-50"
                  >
                    <X className="h-4 w-4" /> Rechazar
                  </button>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
