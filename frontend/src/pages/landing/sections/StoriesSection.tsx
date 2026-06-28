import { Quote } from "lucide-react";

import { Reveal } from "@/components/motion/reveal";

const STORIES = [
  {
    quote:
      "Pusimos el QR en la lápida de mi padre. Ahora mis hijos pueden conocer su historia, escuchar su voz y ver sus fotos. Es como tenerlo cerca.",
    name: "Carolina Méndez",
    role: "Lima, Perú",
  },
  {
    quote:
      "Reunimos a toda la familia para construir el memorial de mi abuela. Cada uno aportó un recuerdo. Fue sanador y hermoso.",
    name: "Andrés Gutiérrez",
    role: "Bogotá, Colombia",
  },
  {
    quote:
      "Las velas virtuales me sorprendieron. Recibí mensajes de personas en otros países que la conocieron. Su legado realmente trascendió.",
    name: "Lucía Fernández",
    role: "Madrid, España",
  },
];

export function StoriesSection() {
  return (
    <section id="historias" className="py-24">
      <div className="container">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            Historias que siguen vivas
          </h2>
          <p className="mt-4 text-lg text-foreground-muted">
            Miles de familias mantienen vivo el recuerdo de quienes amaron.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {STORIES.map((story, i) => (
            <Reveal key={story.name} delay={i * 0.1}>
              <figure className="flex h-full flex-col rounded-lg border border-border bg-card p-7 shadow-card">
                <Quote className="h-8 w-8 text-brand-gold" />
                <blockquote className="mt-4 flex-1 text-foreground-muted">
                  "{story.quote}"
                </blockquote>
                <figcaption className="mt-6 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-brand to-brand-gold" />
                  <div>
                    <p className="text-sm font-semibold">{story.name}</p>
                    <p className="text-xs text-foreground-muted">{story.role}</p>
                  </div>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
