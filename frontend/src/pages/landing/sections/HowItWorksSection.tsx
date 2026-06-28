import { FileHeart, QrCode, Share2, UploadCloud } from "lucide-react";

import { Reveal } from "@/components/motion/reveal";

const STEPS = [
  {
    icon: FileHeart,
    title: "Crea el memorial",
    description:
      "Añade su nombre, biografía, profesión y las frases que mejor lo describen.",
  },
  {
    icon: UploadCloud,
    title: "Sube los recuerdos",
    description: "Fotos, videos, audios y momentos clave en una línea de tiempo elegante.",
  },
  {
    icon: QrCode,
    title: "Genera el QR",
    description: "Descarga tu código en PNG, SVG o PDF, listo para lápidas y nichos.",
  },
  {
    icon: Share2,
    title: "Comparte el legado",
    description: "Familiares y amigos visitan el memorial, encienden velas y dejan mensajes.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="como-funciona" className="py-24">
      <div className="container">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            Crear un legado nunca fue tan sencillo
          </h2>
          <p className="mt-4 text-lg text-foreground-muted">
            En cuatro pasos transformas los recuerdos en un homenaje que perdura.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <Reveal key={step.title} delay={i * 0.1}>
              <div className="group relative h-full rounded-lg border border-border bg-card p-6 shadow-card transition-all hover:-translate-y-1 hover:shadow-soft">
                <div className="flex h-12 w-12 items-center justify-center rounded-md bg-brand-light text-brand transition-colors group-hover:bg-brand group-hover:text-white">
                  <step.icon className="h-6 w-6" />
                </div>
                <span className="absolute right-6 top-6 text-4xl font-bold text-border">
                  0{i + 1}
                </span>
                <h3 className="mt-5 text-lg font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm text-foreground-muted">{step.description}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
