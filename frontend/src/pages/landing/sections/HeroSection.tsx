import { motion } from "framer-motion";
import { ArrowRight, Heart, QrCode, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-brand-gradient">
      <div className="container relative grid items-center gap-12 py-20 md:grid-cols-2 md:py-28">
        {/* Texto */}
        <div>
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full bg-brand-light px-4 py-1.5 text-sm font-medium text-brand-hover"
          >
            <Sparkles className="h-4 w-4" />
            Memoriales digitales con QR inteligente
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.05 }}
            className="mt-6 text-4xl font-extrabold leading-[1.05] tracking-tight md:text-h1"
          >
            Su historia merece <span className="text-gradient">vivir para siempre</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="mt-6 max-w-lg text-lg text-foreground-muted"
          >
            Crea un memorial digital lleno de vida con fotos, videos, su biografía y
            una línea de tiempo. Compártelo con un código QR que conecta el recuerdo
            con cada persona que lo amó.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="mt-8 flex flex-col gap-3 sm:flex-row"
          >
            <Button asChild size="lg">
              <Link to="/registro">
                Crear memorial <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/m/ejemplo">Ver ejemplo</Link>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-10 flex items-center gap-6 text-sm text-foreground-muted"
          >
            <div className="flex items-center gap-2">
              <Heart className="h-4 w-4 text-brand" />
              +10.000 recuerdos honrados
            </div>
            <div className="flex items-center gap-2">
              <QrCode className="h-4 w-4 text-brand" />
              QR para lápidas y nichos
            </div>
          </motion.div>
        </div>

        {/* Tarjeta de memorial flotante */}
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
          className="relative mx-auto w-full max-w-sm"
        >
          <div className="overflow-hidden rounded-lg border border-border bg-card shadow-soft">
            <div className="h-44 bg-gradient-to-br from-brand/15 via-brand-light to-brand-gold/20" />
            <div className="-mt-12 px-6 pb-6">
              <div className="h-24 w-24 rounded-full border-4 border-card bg-gradient-to-br from-brand to-brand-gold shadow-glow" />
              <h3 className="mt-4 text-xl font-bold">María Elena Vargas</h3>
              <p className="text-sm text-foreground-muted">1948 — 2023 · Maestra y abuela</p>
              <p className="mt-3 text-sm leading-relaxed text-foreground-muted">
                "Sembró amor en cada vida que tocó. Su sonrisa sigue iluminando
                nuestros días."
              </p>
              <div className="mt-4 flex items-center gap-4 text-xs text-foreground-muted">
                <span>📷 248 fotos</span>
                <span>🕯️ 1.204 velas</span>
                <span>💬 86 mensajes</span>
              </div>
            </div>
          </div>

          {/* QR flotante */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -bottom-6 -left-6 flex h-24 w-24 items-center justify-center rounded-lg border border-border bg-card shadow-soft"
          >
            <QrCode className="h-12 w-12 text-brand" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
