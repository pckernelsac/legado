import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { z } from "zod";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useConfirmPasswordReset } from "@/features/auth/hooks";
import { getErrorMessage } from "@/lib/api";

const schema = z
  .object({
    new_password: z.string().min(12, "Mínimo 12 caracteres"),
    confirm: z.string(),
  })
  .refine((d) => d.new_password === d.confirm, {
    message: "Las contraseñas no coinciden",
    path: ["confirm"],
  });

type FormValues = z.infer<typeof schema>;

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const navigate = useNavigate();
  const confirm = useConfirmPasswordReset();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    await confirm.mutateAsync({ token, new_password: values.new_password });
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

        {confirm.isSuccess ? (
          <div className="flex flex-col items-center gap-3 text-center">
            <CheckCircle2 className="h-12 w-12 text-brand" />
            <h1 className="text-xl font-bold">Contraseña actualizada</h1>
            <p className="text-sm text-foreground-muted">
              Ya puedes iniciar sesión con tu nueva contraseña.
            </p>
            <Button className="mt-4 w-full" onClick={() => navigate("/login")}>
              Iniciar sesión
            </Button>
          </div>
        ) : !token ? (
          <div className="text-center">
            <h1 className="text-xl font-bold">Enlace inválido</h1>
            <p className="mt-2 text-sm text-foreground-muted">
              Falta el token en el enlace. Solicita uno nuevo.
            </p>
            <Button asChild variant="outline" className="mt-4 w-full">
              <Link to="/recuperar-contrasena">Solicitar nuevo enlace</Link>
            </Button>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-bold">Nueva contraseña</h1>
            <p className="mt-1 text-sm text-foreground-muted">
              Elige una contraseña segura de al menos 12 caracteres.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">Nueva contraseña</label>
                <Input type="password" placeholder="••••••••" {...register("new_password")} />
                {errors.new_password && (
                  <p className="mt-1 text-xs text-destructive">
                    {errors.new_password.message}
                  </p>
                )}
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium">Repite la contraseña</label>
                <Input type="password" placeholder="••••••••" {...register("confirm")} />
                {errors.confirm && (
                  <p className="mt-1 text-xs text-destructive">{errors.confirm.message}</p>
                )}
              </div>

              {confirm.isError && (
                <p className="text-sm text-destructive">{getErrorMessage(confirm.error)}</p>
              )}

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Guardando…" : "Restablecer contraseña"}
              </Button>
            </form>
          </>
        )}
      </motion.div>
    </div>
  );
}
