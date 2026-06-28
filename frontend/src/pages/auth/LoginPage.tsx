import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLogin } from "@/features/auth/hooks";
import { getErrorMessage } from "@/lib/api";

const schema = z.object({
  email: z.string().email("Correo inválido"),
  password: z.string().min(1, "Ingresa tu contraseña"),
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useLogin();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    await login.mutateAsync(values);
    navigate("/dashboard");
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

        <h1 className="text-2xl font-bold">Bienvenido de nuevo</h1>
        <p className="mt-1 text-sm text-foreground-muted">
          Inicia sesión para gestionar tus memoriales.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium">Correo</label>
            <Input type="email" placeholder="tu@correo.com" {...register("email")} />
            {errors.email && (
              <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div>
            <div className="mb-1.5 flex items-center justify-between">
              <label className="block text-sm font-medium">Contraseña</label>
              <Link
                to="/recuperar-contrasena"
                className="text-xs font-medium text-brand hover:underline"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>
            <Input type="password" placeholder="••••••••" {...register("password")} />
            {errors.password && (
              <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>

          {login.isError && (
            <p className="text-sm text-destructive">{getErrorMessage(login.error)}</p>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Ingresando…" : "Iniciar sesión"}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-foreground-muted">
          ¿No tienes cuenta?{" "}
          <Link to="/registro" className="font-semibold text-brand hover:underline">
            Crear cuenta
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
