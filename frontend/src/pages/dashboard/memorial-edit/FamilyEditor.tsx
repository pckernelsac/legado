import { Loader2, Plus, Trash2, Users } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useCreateFamilyMember,
  useDeleteFamilyMember,
  useFamily,
} from "@/features/memorial/edit-hooks";

const RELATIONSHIPS = [
  "Padre",
  "Madre",
  "Hijo",
  "Hija",
  "Hermano",
  "Hermana",
  "Abuelo",
  "Abuela",
  "Cónyuge",
  "Nieto",
  "Nieta",
  "Otro",
];

export function FamilyEditor({ memorialId }: { memorialId: string }) {
  const { data: members = [], isLoading } = useFamily(memorialId);
  const create = useCreateFamilyMember(memorialId);
  const remove = useDeleteFamilyMember(memorialId);

  const [name, setName] = useState("");
  const [relationship, setRelationship] = useState("");
  const [birth, setBirth] = useState("");
  const [death, setDeath] = useState("");
  const [parentId, setParentId] = useState("");

  const canAdd = name.trim().length >= 1;

  const add = async () => {
    if (!canAdd) return;
    await create.mutateAsync({
      full_name: name.trim(),
      relationship_type: relationship || null,
      birth_year: birth ? Number(birth) : null,
      death_year: death ? Number(death) : null,
      parent_member_id: parentId || null,
    });
    setName("");
    setRelationship("");
    setBirth("");
    setDeath("");
    setParentId("");
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-muted/30 p-5">
        <h3 className="flex items-center gap-2 font-semibold">
          <Plus className="h-4 w-4 text-brand" /> Añadir familiar
        </h3>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <Input
            placeholder="Nombre completo"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={200}
          />
          <select
            value={relationship}
            onChange={(e) => setRelationship(e.target.value)}
            className="h-11 rounded-md border border-input bg-card px-3 text-sm"
          >
            <option value="">Parentesco…</option>
            {RELATIONSHIPS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-3">
            <Input
              type="number"
              placeholder="Año nac."
              value={birth}
              onChange={(e) => setBirth(e.target.value)}
            />
            <Input
              type="number"
              placeholder="Año fall."
              value={death}
              onChange={(e) => setDeath(e.target.value)}
            />
          </div>
          <select
            value={parentId}
            onChange={(e) => setParentId(e.target.value)}
            className="h-11 rounded-md border border-input bg-card px-3 text-sm"
          >
            <option value="">Sin ascendiente (raíz)</option>
            {members.map((m) => (
              <option key={m.id} value={m.id}>
                Hijo/a de {m.full_name}
              </option>
            ))}
          </select>
        </div>
        <Button className="mt-3" onClick={add} disabled={!canAdd || create.isPending}>
          {create.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          Añadir familiar
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton h-14 rounded-lg" />
          ))}
        </div>
      ) : members.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-10 text-center text-foreground-muted">
          <Users className="h-9 w-9 opacity-40" />
          <p className="text-sm">Aún no has añadido familiares.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {members.map((m) => {
            const parent = members.find((p) => p.id === m.parent_member_id);
            return (
              <li
                key={m.id}
                className="flex items-center justify-between rounded-md border border-border bg-card p-3"
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-light font-semibold text-brand">
                    {m.full_name.charAt(0).toUpperCase()}
                  </span>
                  <div>
                    <p className="font-medium">
                      {m.full_name}
                      {m.relationship_type && (
                        <span className="ml-2 text-xs font-normal text-foreground-muted">
                          · {m.relationship_type}
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-foreground-muted">
                      {[m.birth_year, m.death_year].filter(Boolean).join(" — ")}
                      {parent && ` · hijo/a de ${parent.full_name}`}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => remove.mutate(m.id)}
                  title="Eliminar"
                  className="rounded-md p-1.5 text-destructive transition-colors hover:bg-destructive/10"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
