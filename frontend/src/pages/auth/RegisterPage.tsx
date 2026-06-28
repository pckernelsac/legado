import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRegister } from "@/features/auth/hooks";
import { getErrorMessage } from "@/lib/api";

const schema = z.object({
  full_name: z.string().min(2, "Ingresa tu nombre completo"),
  email: z.string().email("Correo inválido"),
  password: z
    .string()
    .min(12, "Mínimo 12 caracteres")
    .regex(/[a-z]/, "Incluye una minúscula")
    .regex(/[A-Z]/, "Incluye una mayúscula")
    .regex(/\d/, "Incluye un número")
    .regex(/[^\w\s]/, "Incluye un símbolo"),
});

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const [done, setDone] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    await registerMutation.mutateAsync(values);
    setDone(true);
    setTimeout(() => navigate("/login"), 2500);
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

        {done ? (
          <div className="py-8 text-center">
            <h1 className="text-2xl font-bold">¡Cuenta creada! 🎉</h1>
            <p className="mt-2 text-sm text-foreground-muted">
              Revisa tu correo para verificar tu cuenta. Te llevamos al inicio de sesión…
            </p>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-bold">Crea tu cuenta</h1>
            <p className="mt-1 text-sm text-foreground-muted">
              Comienza a honrar a quienes amas. 14 días gratis.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">Nombre completo</label>
                <Input placeholder="Tu nombre" {...register("full_name")} />
                {errors.full_name && (
                  <p className="mt-1 text-xs text-destructive">{errors.full_name.message}</p>
                )}
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Correo</label>
                <Input type="email" placeholder="tu@correo.com" {...register("email")} />
                {errors.email && (
                  <p className="mt-1 text-xs text-destructive">{errors.email.message}</p>
                )}
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Contraseña</label>
                <Input type="password" placeholder="••••••••" {...register("password")} />
                {errors.password && (
                  <p className="mt-1 text-xs text-destructive">{errors.password.message}</p>
                )}
              </div>

              {registerMutation.isError && (
                <p className="text-sm text-destructive">
                  {getErrorMessage(registerMutation.error)}
                </p>
              )}

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Creando cuenta…" : "Crear cuenta"}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-foreground-muted">
              ¿Ya tienes cuenta?{" "}
              <Link to="/login" className="font-semibold text-brand hover:underline">
                Iniciar sesión
              </Link>
            </p>
          </>
        )}
      </motion.div>
    </div>
  );
}
