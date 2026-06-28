import { Link } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";

const COLUMNS = [
  {
    title: "Producto",
    links: [
      { label: "Cómo funciona", href: "#como-funciona" },
      { label: "Planes", href: "#planes" },
      { label: "Ejemplo de memorial", href: "/m/ejemplo" },
      { label: "Códigos QR", href: "#beneficios" },
    ],
  },
  {
    title: "Empresa",
    links: [
      { label: "Sobre nosotros", href: "#historias" },
      { label: "Contacto", href: "#contacto" },
      { label: "Blog", href: "#" },
      { label: "Trabaja con nosotros", href: "#" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Términos", href: "#" },
      { label: "Privacidad", href: "#" },
      { label: "Cookies", href: "#" },
      { label: "Seguridad", href: "#" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="container grid gap-10 py-16 md:grid-cols-5">
        <div className="md:col-span-2">
          <Link to="/" className="flex items-center gap-2">
            <Logo className="h-8 w-8" />
            <span className="text-lg font-bold">Legado Eterno</span>
          </Link>
          <p className="mt-4 max-w-xs text-sm text-foreground-muted">
            Memoriales digitales que celebran la vida, la familia y el recuerdo.
            Un legado que permanece para siempre.
          </p>
        </div>

        {COLUMNS.map((col) => (
          <div key={col.title}>
            <h4 className="mb-4 text-sm font-semibold">{col.title}</h4>
            <ul className="space-y-3">
              {col.links.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-foreground-muted transition-colors hover:text-brand"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="border-t border-border">
        <div className="container flex flex-col items-center justify-between gap-4 py-6 text-sm text-foreground-muted md:flex-row">
          <p>© {new Date().getFullYear()} Legado Eterno. Todos los derechos reservados.</p>
          <p>Hecho con cariño para honrar a quienes amamos.</p>
        </div>
      </div>
    </footer>
  );
}
