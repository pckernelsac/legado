import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useUpdateMemorial,
  type MemorialDetail,
} from "@/features/memorial/edit-hooks";
import { getErrorMessage } from "@/lib/api";

const schema = z.object({
  full_name: z.string().min(2, "Ingresa el nombre completo"),
  birth_date: z.string().optional().or(z.literal("")),
  death_date: z.string().optional().or(z.literal("")),
  birth_place: z.string().optional().or(z.literal("")),
  death_place: z.string().optional().or(z.literal("")),
  profession: z.string().optional().or(z.literal("")),
  epitaph: z.string().max(500).optional().or(z.literal("")),
  biography: z.string().optional().or(z.literal("")),
  cemetery_name: z.string().optional().or(z.literal("")),
  location_address: z.string().optional().or(z.literal("")),
});

type FormValues = z.infer<typeof schema>;

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
    </div>
  );
}

export function MemorialDetailsForm({ memorial }: { memorial: MemorialDetail }) {
  const update = useUpdateMemorial(memorial.id);
  const [saved, setSaved] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: memorial.full_name,
      birth_date: memorial.birth_date ?? "",
      death_date: memorial.death_date ?? "",
      birth_place: memorial.birth_place ?? "",
      death_place: memorial.death_place ?? "",
      profession: memorial.profession ?? "",
      epitaph: memorial.epitaph ?? "",
      biography: memorial.biography ?? "",
      cemetery_name: "",
      location_address: "",
    },
  });

  useEffect(() => {
    if (saved) {
      const t = setTimeout(() => setSaved(false), 2500);
      return () => clearTimeout(t);
    }
  }, [saved]);

  const onSubmit = async (values: FormValues) => {
    const payload = Object.fromEntries(
      Object.entries(values).map(([k, v]) => [k, v === "" ? null : v]),
    );
    const data = await update.mutateAsync(payload);
    reset({
      full_name: data.full_name,
      birth_date: data.birth_date ?? "",
      death_date: data.death_date ?? "",
      birth_place: data.birth_place ?? "",
      death_place: data.death_place ?? "",
      profession: data.profession ?? "",
      epitaph: data.epitaph ?? "",
      biography: data.biography ?? "",
      cemetery_name: values.cemetery_name,
      location_address: values.location_address,
    });
    setSaved(true);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-5 md:grid-cols-2">
        <div className="md:col-span-2">
          <Field label="Nombre completo" error={errors.full_name?.message}>
            <Input {...register("full_name")} placeholder="Nombre y apellidos" />
          </Field>
        </div>
        <Field label="Fecha de nacimiento">
          <Input type="date" {...register("birth_date")} />
        </Field>
        <Field label="Fecha de fallecimiento">
          <Input type="date" {...register("death_date")} />
        </Field>
        <Field label="Lugar de nacimiento">
          <Input {...register("birth_place")} placeholder="Ciudad, país" />
        </Field>
        <Field label="Lugar de fallecimiento">
          <Input {...register("death_place")} placeholder="Ciudad, país" />
        </Field>
        <Field label="Profesión">
          <Input {...register("profession")} placeholder="A qué se dedicó" />
        </Field>
        <Field label="Lugar de descanso">
          <Input {...register("cemetery_name")} placeholder="Cementerio / nicho" />
        </Field>
        <div className="md:col-span-2">
          <Field label="Epitafio" error={errors.epitaph?.message}>
            <Input {...register("epitaph")} placeholder="Una frase para recordarle" />
          </Field>
        </div>
        <div className="md:col-span-2">
          <Field label="Biografía">
            <Textarea
              rows={6}
              {...register("biography")}
              placeholder="Cuenta su historia, sus pasiones, lo que lo hacía único…"
            />
          </Field>
        </div>
        <div className="md:col-span-2">
          <Field label="Dirección (para el mapa)">
            <Input {...register("location_address")} placeholder="Dirección del lugar de descanso" />
          </Field>
        </div>
      </div>

      {update.isError && (
        <p className="text-sm text-destructive">{getErrorMessage(update.error)}</p>
      )}

      <div className="flex items-center gap-3">
        <Button type="submit" disabled={update.isPending || !isDirty}>
          {update.isPending ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Guardando…
            </>
          ) : (
            "Guardar cambios"
          )}
        </Button>
        {saved && (
          <span className="flex items-center gap-1 text-sm font-medium text-brand">
            <Check className="h-4 w-4" /> Guardado
          </span>
        )}
      </div>
    </form>
  );
}
