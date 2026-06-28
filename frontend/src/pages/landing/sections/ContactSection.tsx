import { Mail, MessageCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Reveal } from "@/components/motion/reveal";

export function ContactSection() {
  return (
    <section id="contacto" className="bg-foreground py-24 text-white">
      <div className="container grid items-center gap-12 md:grid-cols-2">
        <Reveal>
          <h2 className="text-3xl font-bold tracking-tight md:text-h2">
            ¿Listo para crear un legado eterno?
          </h2>
          <p className="mt-4 max-w-md text-lg text-white/70">
            Empieza hoy o escríbenos. Estamos aquí para acompañarte en cada paso de
            este homenaje.
          </p>
          <div className="mt-8 space-y-4">
            <a href="mailto:hola@legadoeterno.com" className="flex items-center gap-3 text-white/90">
              <Mail className="h-5 w-5 text-brand-gold" />
              hola@legadoeterno.com
            </a>
            <a href="#" className="flex items-center gap-3 text-white/90">
              <MessageCircle className="h-5 w-5 text-brand-gold" />
              Chat de soporte en vivo
            </a>
          </div>
        </Reveal>

        <Reveal delay={0.15}>
          <form
            className="rounded-lg bg-card p-7 text-foreground shadow-soft"
            onSubmit={(e) => e.preventDefault()}
          >
            <h3 className="text-lg font-semibold">Déjanos un mensaje</h3>
            <div className="mt-5 space-y-4">
              <Input placeholder="Tu nombre" aria-label="Nombre" />
              <Input type="email" placeholder="Tu correo" aria-label="Correo" />
              <textarea
                placeholder="¿En qué podemos ayudarte?"
                aria-label="Mensaje"
                rows={4}
                className="flex w-full rounded-md border border-input bg-card px-4 py-3 text-sm placeholder:text-foreground-muted focus-visible:border-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/20"
              />
              <Button type="submit" className="w-full">
                Enviar mensaje
              </Button>
            </div>
          </form>
        </Reveal>
      </div>
    </section>
  );
}
