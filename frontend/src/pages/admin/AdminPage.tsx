import {
  ArrowLeft,
  Download,
  ExternalLink,
  Eye,
  Flame,
  ImageIcon,
  Loader2,
  MessageSquare,
  QrCode,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useAdminMemorials,
  useAdminStats,
  useAdminUsers,
  useGenerateAdminQR,
  useAdminMemorialQR,
  useSetMemorialStatus,
  useSetUserActive,
  type AdminMemorial,
} from "@/features/admin/hooks";
import type { QRFormat } from "@/features/memorial/edit-hooks";
import { cn } from "@/lib/utils";

const STATUSES = ["draft", "published", "archived", "suspended"] as const;

export default function AdminPage() {
  const { data: stats } = useAdminStats();
  const [qrFor, setQrFor] = useState<AdminMemorial | null>(null);

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <Logo className="h-8 w-8" />
            <span className="font-bold">Legado Eterno · Admin</span>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4" /> Mi panel
            </Link>
          </Button>
        </div>
      </header>

      <main className="container py-10">
        <h1 className="text-2xl font-bold">Panel de administración</h1>

        {/* Métricas globales */}
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <Stat icon={Users} value={stats?.total_users} label="Usuarios" />
          <Stat icon={ImageIcon} value={stats?.total_memorials} label="Memoriales" />
          <Stat icon={Eye} value={stats?.published_memorials} label="Publicados" />
          <Stat icon={Flame} value={stats?.total_candles} label="Velas" />
          <Stat icon={MessageSquare} value={stats?.total_condolences} label="Condolencias" />
          <Stat icon={MessageSquare} value={stats?.pending_condolences} label="Pendientes" />
        </div>

        <Tabs defaultValue="memorials" className="mt-10">
          <TabsList>
            <TabsTrigger value="memorials">
              <ImageIcon className="h-4 w-4" /> Memoriales
            </TabsTrigger>
            <TabsTrigger value="users">
              <Users className="h-4 w-4" /> Usuarios
            </TabsTrigger>
          </TabsList>

          <TabsContent value="memorials">
            <MemorialsTable onQR={setQrFor} />
          </TabsContent>
          <TabsContent value="users">
            <UsersTable />
          </TabsContent>
        </Tabs>
      </main>

      {qrFor && <QRModal memorial={qrFor} onClose={() => setQrFor(null)} />}
    </div>
  );
}

function Stat({
  icon: Icon,
  value,
  label,
}: {
  icon: typeof Users;
  value?: number;
  label: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-light text-brand">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-xl font-bold">{value ?? "—"}</p>
          <p className="text-xs text-foreground-muted">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function MemorialsTable({ onQR }: { onQR: (m: AdminMemorial) => void }) {
  const { data: memorials = [], isLoading } = useAdminMemorials();
  const setStatus = useSetMemorialStatus();

  if (isLoading) return <TableSkeleton />;

  return (
    <div className="mt-6 overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-muted/50 text-left text-xs uppercase text-foreground-muted">
          <tr>
            <th className="px-4 py-3">Memorial</th>
            <th className="px-4 py-3">Propietario</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3">Métricas</th>
            <th className="px-4 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {memorials.map((m) => (
            <tr key={m.id} className="hover:bg-muted/30">
              <td className="px-4 py-3 font-medium">{m.full_name}</td>
              <td className="px-4 py-3 text-foreground-muted">{m.owner_email}</td>
              <td className="px-4 py-3">
                <select
                  value={m.status}
                  onChange={(e) => setStatus.mutate({ id: m.id, status: e.target.value })}
                  className="rounded-md border border-input bg-card px-2 py-1 text-xs"
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-4 py-3 text-xs text-foreground-muted">
                👁 {m.view_count} · 🕯️ {m.candle_count} · 💬 {m.condolence_count}
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-1">
                  <a
                    href={`/m/${m.public_slug}`}
                    target="_blank"
                    rel="noreferrer"
                    title="Ver público"
                    className="rounded-md p-1.5 text-brand hover:bg-brand-light"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                  <button
                    onClick={() => onQR(m)}
                    title="Códigos QR"
                    className="rounded-md p-1.5 text-brand hover:bg-brand-light"
                  >
                    <QrCode className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UsersTable() {
  const { data: users = [], isLoading } = useAdminUsers();
  const setActive = useSetUserActive();

  if (isLoading) return <TableSkeleton />;

  return (
    <div className="mt-6 overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-muted/50 text-left text-xs uppercase text-foreground-muted">
          <tr>
            <th className="px-4 py-3">Usuario</th>
            <th className="px-4 py-3">Rol</th>
            <th className="px-4 py-3">Memoriales</th>
            <th className="px-4 py-3">Estado</th>
            <th className="px-4 py-3 text-right">Acción</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {users.map((u) => (
            <tr key={u.id} className="hover:bg-muted/30">
              <td className="px-4 py-3">
                <p className="font-medium">{u.full_name}</p>
                <p className="text-xs text-foreground-muted">{u.email}</p>
              </td>
              <td className="px-4 py-3">
                <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{u.role}</span>
              </td>
              <td className="px-4 py-3">{u.memorials_count}</td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    u.is_active
                      ? "bg-brand-light text-brand-hover"
                      : "bg-destructive/10 text-destructive",
                  )}
                >
                  {u.is_active ? "Activo" : "Inactivo"}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={u.role === "super_admin"}
                  onClick={() => setActive.mutate({ id: u.id, is_active: !u.is_active })}
                >
                  {u.is_active ? "Desactivar" : "Activar"}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function QRModal({ memorial, onClose }: { memorial: AdminMemorial; onClose: () => void }) {
  const { data: codes = [] } = useAdminMemorialQR(memorial.id, true);
  const generate = useGenerateAdminQR(memorial.id);

  const formats: QRFormat[] = ["png", "svg", "pdf"];

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg rounded-lg border border-border bg-card p-6 shadow-soft"
      >
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold">Códigos QR</h2>
            <p className="text-sm text-foreground-muted">{memorial.full_name}</p>
          </div>
          <button onClick={onClose} className="rounded-md p-1.5 hover:bg-muted">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {formats.map((f) => (
            <Button
              key={f}
              size="sm"
              variant="outline"
              disabled={generate.isPending}
              onClick={() => generate.mutate({ format: f })}
            >
              {generate.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <QrCode className="h-4 w-4" />
              )}
              Generar {f.toUpperCase()}
            </Button>
          ))}
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {codes.length === 0 ? (
            <p className="col-span-full py-6 text-center text-sm text-foreground-muted">
              Genera un QR para imprimirlo en la lápida.
            </p>
          ) : (
            codes.map((qr) => (
              <div
                key={qr.id}
                className="flex flex-col rounded-lg border border-border bg-card p-3"
              >
                <div className="flex aspect-square items-center justify-center overflow-hidden rounded-md bg-white">
                  {(qr.format === "png" || qr.format === "svg") && qr.qr_url ? (
                    <img src={qr.qr_url} alt="QR" className="h-full w-full object-contain p-1" />
                  ) : (
                    <QrCode className="h-10 w-10 text-foreground-muted" />
                  )}
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase">{qr.format}</span>
                  {qr.qr_url && (
                    <a
                      href={qr.qr_url}
                      download={`qr-${memorial.public_slug}.${qr.format}`}
                      title="Descargar"
                      className="rounded-md p-1.5 text-brand hover:bg-brand-light"
                    >
                      <Download className="h-4 w-4" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function TableSkeleton() {
  return (
    <div className="mt-6 space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="skeleton h-12 rounded-md" />
      ))}
    </div>
  );
}
