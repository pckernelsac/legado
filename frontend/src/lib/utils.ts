import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Combina clases de Tailwind resolviendo conflictos. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formatea un rango de fechas de vida ("1940 — 2021"). */
export function formatLifespan(birth?: string | null, death?: string | null): string {
  const year = (d?: string | null) => (d ? new Date(d).getFullYear() : "?");
  if (!birth && !death) return "";
  return `${year(birth)} — ${year(death)}`;
}

export function formatDate(value?: string | null, locale = "es-ES"): string {
  if (!value) return "";
  return new Date(value).toLocaleDateString(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
