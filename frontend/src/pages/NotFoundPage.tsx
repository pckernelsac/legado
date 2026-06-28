import { Link } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-brand-gradient text-center">
      <Logo className="h-16 w-16" />
      <div>
        <h1 className="text-6xl font-extrabold text-brand">404</h1>
        <p className="mt-2 text-lg text-foreground-muted">
          No encontramos la página que buscas.
        </p>
      </div>
      <Button asChild>
        <Link to="/">Volver al inicio</Link>
      </Button>
    </div>
  );
}
