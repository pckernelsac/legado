import { ChevronDown } from "lucide-react";
import { useState } from "react";

import { Reveal } from "@/components/motion/reveal";
import { cn } from "@/lib/utils";

const FAQS = [
  {
    q: "¿El memorial es permanente?",
    a: "Sí. Mientras tu suscripción esté activa, el memorial permanece accesible para siempre, con todos sus recuerdos y multimedia respaldados de forma segura.",
  },
  {
    q: "¿Cómo funciona el código QR?",
    a: "Generamos un QR único de alta resolución que puedes imprimir o grabar en lápidas, nichos y mausoleos. Al escanearlo, cualquier persona accede al memorial digital completo.",
  },
  {
    q: "¿Quién puede ver el memorial?",
    a: "Tú decides. Puede ser público, accesible solo con el enlace, o privado para familiares invitados. Los enlaces usan códigos imposibles de adivinar.",
  },
  {
    q: "¿Puedo invitar a otros familiares a colaborar?",
    a: "Por supuesto. Puedes invitar a familiares para que agreguen fotos, recuerdos y mensajes, construyendo el memorial entre todos.",
  },
  {
    q: "¿Mis datos están seguros?",
    a: "Totalmente. Usamos cifrado, almacenamiento redundante y las mejores prácticas de seguridad de la industria para proteger cada recuerdo.",
  },
];

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="py-24">
      <div className="container max-w-3xl">
        <Reveal className="text-center">
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            Preguntas frecuentes
          </h2>
          <p className="mt-4 text-lg text-foreground-muted">
            Resolvemos las dudas más comunes sobre Legado Eterno.
          </p>
        </Reveal>

        <div className="mt-12 space-y-3">
          {FAQS.map((faq, i) => {
            const isOpen = open === i;
            return (
              <Reveal key={faq.q} delay={i * 0.05}>
                <div className="overflow-hidden rounded-lg border border-border bg-card">
                  <button
                    onClick={() => setOpen(isOpen ? null : i)}
                    className="flex w-full items-center justify-between gap-4 p-5 text-left"
                  >
                    <span className="font-semibold">{faq.q}</span>
                    <ChevronDown
                      className={cn(
                        "h-5 w-5 shrink-0 text-brand transition-transform",
                        isOpen && "rotate-180",
                      )}
                    />
                  </button>
                  <div
                    className={cn(
                      "grid transition-all duration-300",
                      isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]",
                    )}
                  >
                    <div className="overflow-hidden">
                      <p className="px-5 pb-5 text-sm text-foreground-muted">{faq.a}</p>
                    </div>
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
