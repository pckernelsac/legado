import { motion } from "framer-motion";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { useVerifyEmail } from "@/features/auth/hooks";

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const verify = useVerifyEmail();
  const ran = useRef(false);

  useEffect(() => {
    if (ran.current || !token) return;
    ran.current = true;
    verify.mutate(token);
  }, [token, verify]);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-brand-gradient px-6 py-12">
      <PatternBackground />
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md rounded-lg border border-border bg-card p-8 text-center shadow-soft"
      >
        <Logo className="mx-auto h-10 w-10" />

        {!token ? (
          <Status
            icon={<XCircle className="h-12 w-12 text-destructive" />}
            title="Enlace inválido"
            text="Falta el token de verificación en el enlace."
          />
        ) : verify.isPending ? (
          <Status
            icon={<Loader2 className="h-12 w-12 animate-spin text-brand" />}
            title="Verificando tu correo…"
            text="Un momento, estamos confirmando tu cuenta."
          />
        ) : verify.isSuccess ? (
          <Status
            icon={<CheckCircle2 className="h-12 w-12 text-brand" />}
            title="¡Correo verificado!"
            text="Tu cuenta está activa. Ya puedes iniciar sesión."
          />
        ) : (
          <Status
            icon={<XCircle className="h-12 w-12 text-destructive" />}
            title="No se pudo verificar"
            text="El enlace es inválido o ya fue utilizado."
          />
        )}

        <Button asChild className="mt-6 w-full">
          <Link to="/login">Ir a iniciar sesión</Link>
        </Button>
      </motion.div>
    </div>
  );
}

function Status({
  icon,
  title,
  text,
}: {
  icon: ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="mt-6 flex flex-col items-center gap-3">
      {icon}
      <h1 className="text-xl font-bold">{title}</h1>
      <p className="text-sm text-foreground-muted">{text}</p>
    </div>
  );
}
