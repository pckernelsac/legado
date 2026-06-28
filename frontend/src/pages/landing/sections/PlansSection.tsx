import { Check } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Reveal } from "@/components/motion/reveal";
import { cn } from "@/lib/utils";

const PLANS = [
  {
    name: "Básico",
    price: "4.99",
    description: "Para honrar a un ser querido.",
    features: ["1 memorial", "20 fotos", "QR PNG", "Libro de condolencias", "Velas virtuales"],
    highlighted: false,
  },
  {
    name: "Familiar",
    price: "9.99",
    description: "Para toda la familia.",
    features: [
      "5 memoriales",
      "100 fotos por memorial",
      "Videos y audios",
      "QR PNG, SVG y PDF",
      "Árbol genealógico",
      "Línea de tiempo",
    ],
    highlighted: true,
  },
  {
    name: "Premium",
    price: "19.99",
    description: "La experiencia completa.",
    features: [
      "20 memoriales",
      "500 fotos por memorial",
      "Funciones de IA",
      "Restauración de fotos",
      "Soporte prioritario",
      "Dominio personalizado",
    ],
    highlighted: false,
  },
  {
    name: "Corporativo",
    price: "99",
    description: "Para funerarias y cementerios.",
    features: [
      "Memoriales ilimitados",
      "Multi-usuario",
      "Marca propia",
      "API y panel admin",
      "QR masivos",
      "Gestor de cuenta",
    ],
    highlighted: false,
  },
];

export function PlansSection() {
  return (
    <section id="planes" className="bg-brand-light/40 py-24">
      <div className="container">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            Planes para cada legado
          </h2>
          <p className="mt-4 text-lg text-foreground-muted">
            Comienza gratis durante 14 días. Cancela cuando quieras.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-6 lg:grid-cols-4">
          {PLANS.map((plan, i) => (
            <Reveal key={plan.name} delay={i * 0.08}>
              <div
                className={cn(
                  "relative flex h-full flex-col rounded-lg border bg-card p-7 shadow-card transition-all hover:shadow-soft",
                  plan.highlighted
                    ? "border-brand ring-2 ring-brand/20"
                    : "border-border",
                )}
              >
                {plan.highlighted && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand px-3 py-1 text-xs font-semibold text-white">
                    Más popular
                  </span>
                )}
                <h3 className="text-lg font-semibold">{plan.name}</h3>
                <p className="mt-1 text-sm text-foreground-muted">{plan.description}</p>
                <div className="mt-5 flex items-baseline gap-1">
                  <span className="text-4xl font-extrabold">${plan.price}</span>
                  <span className="text-sm text-foreground-muted">/mes</span>
                </div>
                <ul className="mt-6 flex-1 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-brand" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  asChild
                  variant={plan.highlighted ? "default" : "outline"}
                  className="mt-7 w-full"
                >
                  <Link to="/registro">Elegir {plan.name}</Link>
                </Button>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
