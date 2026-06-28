import { motion } from "framer-motion";
import {
  Eye,
  Flame,
  Image as ImageIcon,
  LogOut,
  MessageSquare,
  Plus,
  Shield,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useCurrentUser, useLogout } from "@/features/auth/hooks";
import { useCreateMemorial, useMyMemorials } from "@/features/memorial/hooks";
import { PlanBanner } from "@/pages/dashboard/PlanBanner";
import { getErrorMessage } from "@/lib/api";
import { formatLifespan } from "@/lib/utils";

const METRICS = [
  { key: "view_count", label: "Visitas totales", icon: Eye },
  { key: "candle_count", label: "Velas encendidas", icon: Flame },
  { key: "condolence_count", label: "Condolencias", icon: MessageSquare },
] as const;

export default function DashboardPage() {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const { data, isLoading } = useMyMemorials();
  const logout = useLogout();
  const createMemorial = useCreateMemorial();

  const memorials = data?.items ?? [];
  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreate = async () => {
    setCreateError(null);
    try {
      const created = await createMemorial.mutateAsync({ full_name: "Nuevo memorial" });
      navigate(`/dashboard/memorial/${created.id}/edit`);
    } catch (err) {
      setCreateError(getErrorMessage(err));
    }
  };
  const totals = METRICS.map((m) => ({
    ...m,
    value: memorials.reduce((sum, mem) => sum + (mem[m.key] ?? 0), 0),
  }));

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <PatternBackground />
      <header className="relative z-10 border-b border-border bg-card">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Logo className="h-8 w-8" />
            <span className="font-bold">Legado Eterno</span>
          </div>
          <div className="flex items-center gap-4">
            {user && ["super_admin", "admin"].includes(user.role.name) && (
              <Button asChild variant="ghost" size="sm">
                <Link to="/admin">
                  <Shield className="h-4 w-4" /> Admin
                </Link>
              </Button>
            )}
            <span className="hidden text-sm text-foreground-muted sm:block">
              {user?.full_name}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => logout.mutate(undefined, { onSettled: () => navigate("/") })}
            >
              <LogOut className="h-4 w-4" /> Salir
            </Button>
          </div>
        </div>
      </header>

      <main className="container relative z-10 py-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Hola, {user?.full_name?.split(" ")[0]} 👋</h1>
            <p className="text-sm text-foreground-muted">
              Gestiona los memoriales que mantienen vivo el recuerdo.
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <Button onClick={handleCreate} disabled={createMemorial.isPending}>
              <Plus className="h-4 w-4" /> Nuevo memorial
            </Button>
            {createError && (
              <p className="max-w-xs text-right text-xs text-destructive">{createError}</p>
            )}
          </div>
        </div>

        {/* Plan y uso */}
        <div className="mt-8">
          <PlanBanner />
        </div>

        {/* Métricas */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-md bg-brand-light text-brand">
                <ImageIcon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-2xl font-bold">{memorials.length}</p>
                <p className="text-sm text-foreground-muted">Memoriales</p>
              </div>
            </CardContent>
          </Card>
          {totals.map((m) => (
            <Card key={m.key}>
              <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-md bg-brand-light text-brand">
                  <m.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{m.value.toLocaleString()}</p>
                  <p className="text-sm text-foreground-muted">{m.label}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Lista de memoriales */}
        <h2 className="mt-12 text-lg font-semibold">Tus memoriales</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {isLoading &&
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="skeleton h-48 rounded-lg" />
            ))}

          {!isLoading && memorials.length === 0 && (
            <Card className="md:col-span-3">
              <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
                <Logo className="h-12 w-12 opacity-60" />
                <p className="font-semibold">Aún no has creado un memorial</p>
                <p className="max-w-sm text-sm text-foreground-muted">
                  Comienza creando el primer homenaje para honrar a un ser querido.
                </p>
                <Button className="mt-2" onClick={handleCreate} disabled={createMemorial.isPending}>
                  <Plus className="h-4 w-4" /> Crear mi primer memorial
                </Button>
              </CardContent>
            </Card>
          )}

          {memorials.map((mem, i) => (
            <motion.div
              key={mem.id}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link to={`/dashboard/memorial/${mem.id}/edit`} className="block">
                <Card className="overflow-hidden transition-transform hover:-translate-y-1">
                  <div
                    className="h-28 bg-cover bg-center bg-gradient-to-br from-brand/15 via-brand-light to-brand-gold/20"
                    style={
                      mem.main_photo_url
                        ? { backgroundImage: `url(${mem.main_photo_url})` }
                        : undefined
                    }
                  />
                  <CardContent className="p-5">
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="font-semibold">{mem.full_name}</h3>
                      <span
                        className={
                          mem.status === "published"
                            ? "rounded-full bg-brand-light px-2 py-0.5 text-[10px] font-medium text-brand-hover"
                            : "rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-foreground-muted"
                        }
                      >
                        {mem.status === "published" ? "Publicado" : "Borrador"}
                      </span>
                    </div>
                    <p className="text-sm text-foreground-muted">
                      {formatLifespan(mem.birth_date, mem.death_date)}
                      {mem.profession ? ` · ${mem.profession}` : ""}
                    </p>
                    <div className="mt-3 flex gap-4 text-xs text-foreground-muted">
                      <span>👁 {mem.view_count}</span>
                      <span>🕯️ {mem.candle_count}</span>
                      <span>💬 {mem.condolence_count}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
