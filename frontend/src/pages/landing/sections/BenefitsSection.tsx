import {
  CalendarClock,
  Flame,
  Images,
  MapPin,
  ShieldCheck,
  TreeDeciduous,
} from "lucide-react";

import { Reveal } from "@/components/motion/reveal";

const BENEFITS = [
  {
    icon: Images,
    title: "Galería multimedia",
    description: "Fotos, videos y audios en alta calidad, optimizados automáticamente.",
  },
  {
    icon: CalendarClock,
    title: "Línea de tiempo",
    description: "Cada etapa de su vida narrada de forma visual y emotiva.",
  },
  {
    icon: TreeDeciduous,
    title: "Árbol genealógico",
    description: "Conecta generaciones con un árbol interactivo y navegable.",
  },
  {
    icon: Flame,
    title: "Velas virtuales",
    description: "Enciende una vela desde cualquier lugar del mundo, en cualquier momento.",
  },
  {
    icon: MapPin,
    title: "Ubicación y mapa",
    description: "Indica el lugar de descanso con OpenStreetMap y cómo llegar.",
  },
  {
    icon: ShieldCheck,
    title: "Privado y seguro",
    description: "Tus recuerdos protegidos con cifrado y enlaces opacos imposibles de adivinar.",
  },
];

export function BenefitsSection() {
  return (
    <section id="beneficios" className="bg-brand-light/40 py-24">
      <div className="container">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            Todo lo que necesitas para honrar su memoria
          </h2>
          <p className="mt-4 text-lg text-foreground-muted">
            Una plataforma pensada para celebrar la vida, no para recordar la pérdida.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {BENEFITS.map((b, i) => (
            <Reveal key={b.title} delay={(i % 3) * 0.08}>
              <div className="h-full rounded-lg border border-border bg-card p-7 shadow-card transition-all hover:shadow-soft">
                <div className="flex h-12 w-12 items-center justify-center rounded-md bg-brand text-white">
                  <b.icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{b.title}</h3>
                <p className="mt-2 text-sm text-foreground-muted">{b.description}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
