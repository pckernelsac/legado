import { motion } from "framer-motion";
import {
  ArrowLeft,
  Clock,
  ExternalLink,
  Globe,
  ImageIcon,
  Loader2,
  MessageCircle,
  QrCode,
  Users,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ErrorBoundary } from "@/components/feedback/ErrorBoundary";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useMemorial, useUpdateMemorial } from "@/features/memorial/edit-hooks";
import { CondolenceModeration } from "@/pages/dashboard/memorial-edit/CondolenceModeration";
import { FamilyEditor } from "@/pages/dashboard/memorial-edit/FamilyEditor";
import { MediaUploader } from "@/pages/dashboard/memorial-edit/MediaUploader";
import { MemorialDetailsForm } from "@/pages/dashboard/memorial-edit/MemorialDetailsForm";
import { QRPanel } from "@/pages/dashboard/memorial-edit/QRPanel";
import { TimelineEditor } from "@/pages/dashboard/memorial-edit/TimelineEditor";
import { cn } from "@/lib/utils";

export default function MemorialEditPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const { data: memorial, isLoading, isError } = useMemorial(id);
  const update = useUpdateMemorial(id);
  const [tab, setTab] = useState("details");

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand" />
      </div>
    );
  }

  if (isError || !memorial) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
        <Logo className="h-12 w-12 opacity-60" />
        <p className="font-semibold">No se encontró el memorial</p>
        <Button variant="outline" onClick={() => navigate("/dashboard")}>
          Volver al panel
        </Button>
      </div>
    );
  }

  const isPublished = memorial.status === "published";
  const publicUrl = `/m/${memorial.public_slug}`;

  const togglePublish = () =>
    update.mutate({ status: isPublished ? "draft" : "published" });

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container flex h-16 items-center justify-between gap-4">
          <Button asChild variant="ghost" size="sm">
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4" /> Panel
            </Link>
          </Button>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium",
                isPublished
                  ? "bg-brand-light text-brand-hover"
                  : "bg-muted text-foreground-muted",
              )}
            >
              {isPublished ? "Publicado" : "Borrador"}
            </span>
            {isPublished && (
              <Button asChild variant="ghost" size="sm">
                <a href={publicUrl} target="_blank" rel="noreferrer">
                  Ver público <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            )}
            <Button
              data-testid="publish-toggle"
              size="sm"
              variant={isPublished ? "outline" : "default"}
              onClick={togglePublish}
              disabled={update.isPending}
            >
              <Globe className="h-4 w-4" />
              {isPublished ? "Despublicar" : "Publicar"}
            </Button>
          </div>
        </div>
      </header>

      <main className="container max-w-4xl py-8">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-2xl font-bold">{memorial.full_name}</h1>
          <p className="text-sm text-foreground-muted">
            Edita los datos y los recuerdos de este memorial.
          </p>

          <Card className="mt-6">
            <CardContent className="p-6">
              <Tabs value={tab} onValueChange={setTab}>
                <TabsList className="flex-wrap">
                  <TabsTrigger value="details">Datos</TabsTrigger>
                  <TabsTrigger value="media">
                    <ImageIcon className="h-4 w-4" /> Multimedia
                  </TabsTrigger>
                  <TabsTrigger value="timeline">
                    <Clock className="h-4 w-4" /> Línea de tiempo
                  </TabsTrigger>
                  <TabsTrigger value="condolences">
                    <MessageCircle className="h-4 w-4" /> Condolencias
                  </TabsTrigger>
                  <TabsTrigger value="family">
                    <Users className="h-4 w-4" /> Familia
                  </TabsTrigger>
                  <TabsTrigger value="qr">
                    <QrCode className="h-4 w-4" /> QR
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="details">
                  <MemorialDetailsForm memorial={memorial} />
                </TabsContent>

                <TabsContent value="media">
                  <ErrorBoundary fallbackTitle="No se pudo cargar la galería.">
                    <MediaUploader memorialId={memorial.id} />
                  </ErrorBoundary>
                </TabsContent>

                <TabsContent value="timeline">
                  <ErrorBoundary fallbackTitle="No se pudo cargar la línea de tiempo.">
                    <TimelineEditor memorialId={memorial.id} />
                  </ErrorBoundary>
                </TabsContent>

                <TabsContent value="condolences">
                  <ErrorBoundary fallbackTitle="No se pudieron cargar las condolencias.">
                    <CondolenceModeration memorialId={memorial.id} />
                  </ErrorBoundary>
                </TabsContent>

                <TabsContent value="family">
                  <ErrorBoundary fallbackTitle="No se pudo cargar el árbol genealógico.">
                    <FamilyEditor memorialId={memorial.id} />
                  </ErrorBoundary>
                </TabsContent>

                <TabsContent value="qr">
                  <ErrorBoundary fallbackTitle="No se pudo cargar el generador de QR.">
                    <QRPanel memorialId={memorial.id} />
                  </ErrorBoundary>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </main>
    </div>
  );
}
