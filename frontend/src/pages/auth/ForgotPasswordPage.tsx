import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { CheckCircle2, MailCheck } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRequestPasswordReset } from "@/features/auth/hooks";

const schema = z.object({ email: z.string().email("Correo inválido") });
type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const request = useRequestPasswordReset();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    await request.mutateAsync(values.email);
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-brand-gradient px-6 py-12">
      <PatternBackground />
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md rounded-lg border border-border bg-card p-8 shadow-soft"
      >
        <Link to="/" className="mb-8 flex items-center gap-2">
          <Logo className="h-8 w-8" />
          <span className="text-lg font-bold">Legado Eterno</span>
        </Link>

        {request.isSuccess ? (
          <div className="flex flex-col items-center gap-3 text-center">
            <CheckCircle2 className="h-12 w-12 text-brand" />
            <h1 className="text-xl font-bold">Revisa tu correo</h1>
            <p className="text-sm text-foreground-muted">
              Si existe una cuenta con ese correo, te enviamos un enlace para
              restablecer tu contraseña. El enlace expira en 1 hora.
            </p>
            <Button asChild variant="outline" className="mt-4 w-full">
              <Link to="/login">Volver a iniciar sesión</Link>
            </Button>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <MailCheck className="h-5 w-5 text-brand" />
              <h1 className="text-2xl font-bold">¿Olvidaste tu contraseña?</h1>
            </div>
            <p className="mt-1 text-sm text-foreground-muted">
              Ingresa tu correo y te enviaremos instrucciones para restablecerla.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">Correo</label>
                <Input type="email" placeholder="tu@correo.com" {...register("email")} />
                {errors.email && (
                  <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Enviando…" : "Enviar enlace"}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-foreground-muted">
              <Link to="/login" className="font-semibold text-brand hover:underline">
                Volver a iniciar sesión
              </Link>
            </p>
          </>
        )}
      </motion.div>
    </div>
  );
}
