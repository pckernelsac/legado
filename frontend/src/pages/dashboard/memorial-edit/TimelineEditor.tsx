import { Clock, Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useCreateTimelineEvent,
  useDeleteTimelineEvent,
  useTimeline,
} from "@/features/memorial/edit-hooks";

export function TimelineEditor({ memorialId }: { memorialId: string }) {
  const { data: events = [], isLoading } = useTimeline(memorialId);
  const create = useCreateTimelineEvent(memorialId);
  const remove = useDeleteTimelineEvent(memorialId);

  const [title, setTitle] = useState("");
  const [year, setYear] = useState("");
  const [date, setDate] = useState("");
  const [description, setDescription] = useState("");

  const canAdd = title.trim().length >= 1;

  const add = async () => {
    if (!canAdd) return;
    await create.mutateAsync({
      title: title.trim(),
      year: year ? Number(year) : null,
      event_date: date || null,
      description: description.trim() || null,
    });
    setTitle("");
    setYear("");
    setDate("");
    setDescription("");
  };

  return (
    <div className="space-y-6">
      {/* Formulario de alta */}
      <div className="rounded-lg border border-border bg-muted/30 p-5">
        <h3 className="flex items-center gap-2 font-semibold">
          <Plus className="h-4 w-4 text-brand" /> Añadir momento
        </h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <Input
            placeholder="Título (ej. Nacimiento)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              type="number"
              placeholder="Año"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />
            <Input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
        </div>
        <Textarea
          className="mt-3"
          placeholder="Descripción (opcional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <Button className="mt-3" onClick={add} disabled={!canAdd || create.isPending}>
          {create.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          Añadir a la línea de tiempo
        </Button>
      </div>

      {/* Lista de eventos */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-lg" />
          ))}
        </div>
      ) : events.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-10 text-center text-foreground-muted">
          <Clock className="h-9 w-9 opacity-40" />
          <p className="text-sm">Aún no hay momentos. Añade el primero arriba.</p>
        </div>
      ) : (
        <ol className="space-y-3 border-l-2 border-brand-light pl-6">
          {events.map((ev) => (
            <li key={ev.id} className="relative">
              <span className="absolute -left-[31px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full border-2 border-brand bg-card">
                <span className="h-1.5 w-1.5 rounded-full bg-brand" />
              </span>
              <div className="flex items-start justify-between gap-3 rounded-md border border-border bg-card p-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-brand">
                    {ev.event_date ?? ev.year ?? ""}
                  </p>
                  <p className="font-semibold">{ev.title}</p>
                  {ev.description && (
                    <p className="mt-1 text-sm text-foreground-muted">{ev.description}</p>
                  )}
                </div>
                <button
                  onClick={() => remove.mutate(ev.id)}
                  title="Eliminar"
                  className="rounded-md p-1.5 text-destructive transition-colors hover:bg-destructive/10"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
