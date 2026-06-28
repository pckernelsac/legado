import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Logo } from "@/components/brand/Logo";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { label: "Cómo funciona", href: "#como-funciona" },
  { label: "Beneficios", href: "#beneficios" },
  { label: "Historias", href: "#historias" },
  { label: "Planes", href: "#planes" },
  { label: "Preguntas", href: "#faq" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-lg"
    >
      <nav className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <Logo className="h-8 w-8" />
          <span className="text-lg font-bold tracking-tight">Legado Eterno</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-foreground-muted transition-colors hover:text-brand"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Button asChild variant="ghost" size="sm">
            <Link to="/login">Iniciar sesión</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/registro">Crear memorial</Link>
          </Button>
        </div>

        <button
          className="md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Menú"
        >
          {open ? <X /> : <Menu />}
        </button>
      </nav>

      <div
        className={cn(
          "overflow-hidden border-t border-border bg-card md:hidden",
          open ? "max-h-96" : "max-h-0",
          "transition-[max-height] duration-300",
        )}
      >
        <div className="container flex flex-col gap-4 py-4">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="text-sm font-medium text-foreground-muted"
            >
              {link.label}
            </a>
          ))}
          <div className="flex gap-3 pt-2">
            <Button asChild variant="outline" size="sm" className="flex-1">
              <Link to="/login">Entrar</Link>
            </Button>
            <Button asChild size="sm" className="flex-1">
              <Link to="/registro">Crear</Link>
            </Button>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
