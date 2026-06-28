import { AnimatePresence, motion } from "framer-motion";
import {
  BookOpen,
  Cake,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock,
  Cross,
  Flame,
  Globe,
  Heart,
  ImageIcon,
  ImagePlus,
  Loader2,
  MapPin,
  MessageCircle,
  Quote,
  Share2,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import { Logo } from "@/components/brand/Logo";
import { PatternBackground } from "@/components/brand/PatternBackground";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { PageLoader } from "@/components/feedback/PageLoader";
import { getErrorMessage } from "@/lib/api";
import {
  useAddCondolence,
  useLightCandle,
  usePublicCandlesByCountry,
  usePublicCondolences,
  usePublicFamily,
  usePublicMedia,
  usePublicMemorial,
  usePublicTimeline,
  type Condolence,
  type FamilyMember,
  type PublicMediaItem,
  type PublicMemorial,
  type TimelineItem,
} from "@/features/memorial/hooks";

function shortDate(value?: string | null): string {
  if (!value) return "";
  return new Date(value).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function PublicMemorialPage() {
  const { slug = "" } = useParams();
  const { data: memorial, isLoading, isError } = usePublicMemorial(slug);

  if (isLoading) return <PageLoader />;

  if (isError || !memorial) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background text-center">
        <Logo className="h-14 w-14 opacity-60" />
        <h1 className="text-2xl font-bold">Memorial no disponible</h1>
        <p className="max-w-sm text-foreground-muted">
          Este memorial no existe o aún no ha sido publicado.
        </p>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-background pb-24">
      <PatternBackground />
      {/* Portada */}
      <div className="relative h-72 overflow-hidden bg-gradient-to-br from-brand/20 via-brand-light to-brand-gold/25 md:h-[22rem]">
        {memorial.cover_photo_url && (
          <img
            src={memorial.cover_photo_url}
            alt={`Portada de ${memorial.full_name}`}
            className="absolute inset-0 h-full w-full object-cover"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/30 to-black/10" />
        <Sparkles className="absolute right-6 top-6 h-6 w-6 text-white/70 drop-shadow md:right-10 md:top-10" />
      </div>

      {/* Tarjeta de perfil superpuesta */}
      <div className="container relative z-10 -mt-24">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex max-w-xl flex-col items-center gap-5 rounded-lg border border-border bg-card p-6 text-center shadow-soft sm:flex-row sm:text-left"
        >
          <div className="relative shrink-0">
            <div className="absolute -inset-1 rounded-full bg-gradient-to-br from-brand via-brand-gold to-brand-hover opacity-70 blur-[2px]" />
            {memorial.main_photo_url ? (
              <img
                src={memorial.main_photo_url}
                alt={memorial.full_name}
                className="relative h-28 w-28 rounded-full border-4 border-card object-cover shadow-glow"
              />
            ) : (
              <div className="relative flex h-28 w-28 items-center justify-center rounded-full border-4 border-card bg-gradient-to-br from-brand to-brand-gold text-3xl font-bold text-white shadow-glow">
                {memorial.full_name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-gradient md:text-3xl">
              {memorial.full_name}
            </h1>
            {memorial.profession && (
              <p className="mt-0.5 text-sm text-foreground-muted">{memorial.profession}</p>
            )}
            <div className="mt-3 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 sm:justify-start">
              {memorial.birth_date && (
                <DateBadge icon={Cake} label="Nació" value={shortDate(memorial.birth_date)} />
              )}
              {memorial.death_date && (
                <DateBadge icon={Cross} label="Partió" value={shortDate(memorial.death_date)} />
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Cuerpo: sidebar + pestañas */}
      <div className="container relative z-10 mt-8 grid gap-8 lg:grid-cols-3">
        <MemorialSidebar memorial={memorial} slug={slug} />

        <div className="lg:col-span-2">
          {memorial.biography && (
            <section className="mb-6 rounded-lg border border-border bg-card p-6 shadow-card">
              <SectionHeader icon={BookOpen} title="Su historia" />
              <p className="mt-4 whitespace-pre-line leading-relaxed text-foreground-muted">
                {memorial.biography}
              </p>
            </section>
          )}

          <Tabs defaultValue="recuerdos">
            <TabsList className="flex-wrap">
              <TabsTrigger value="recuerdos">
                <ImageIcon className="h-4 w-4" /> Recuerdos
              </TabsTrigger>
              <TabsTrigger value="condolencias">
                <MessageCircle className="h-4 w-4" /> Condolencias
              </TabsTrigger>
              <TabsTrigger value="arbol">
                <Users className="h-4 w-4" /> Árbol Genealógico
              </TabsTrigger>
            </TabsList>

            <TabsContent value="recuerdos">
              <RecuerdosPanel slug={slug} fullName={memorial.full_name} />
            </TabsContent>

            <TabsContent value="condolencias">
              <CondolencesPanel slug={slug} />
            </TabsContent>

            <TabsContent value="arbol">
              <FamilyTreePanel slug={slug} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Sidebar "En Memoria de"                                                    */
/* -------------------------------------------------------------------------- */

function MemorialSidebar({
  memorial,
  slug,
}: {
  memorial: PublicMemorial;
  slug: string;
}) {
  return (
    <aside className="space-y-6 lg:col-span-1">
      <div className="rounded-lg border border-border bg-card p-6 shadow-card">
        <p className="text-xs font-semibold uppercase tracking-wide text-brand">
          En memoria de
        </p>
        <p className="text-lg font-semibold">{memorial.full_name}</p>

        {memorial.epitaph && (
          <div className="relative mt-4 rounded-md bg-brand-light/50 px-5 py-4">
            <Quote className="absolute left-2 top-2 h-4 w-4 text-brand/40" />
            <p className="text-sm italic leading-relaxed text-brand-hover">
              {memorial.epitaph}
            </p>
          </div>
        )}

        {memorial.memorable_quotes && memorial.memorable_quotes.length > 0 && (
          <ul className="mt-4 space-y-2">
            {memorial.memorable_quotes.map((q, i) => (
              <li key={i} className="flex gap-2 text-sm italic text-foreground-muted">
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-brand-gold" />
                {q}
              </li>
            ))}
          </ul>
        )}

        {(memorial.location_address || memorial.cemetery_name) && (
          <div className="mt-4 flex items-start gap-2 border-t border-border pt-4 text-sm text-foreground-muted">
            <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-brand" />
            <span>
              {memorial.cemetery_name && <strong>{memorial.cemetery_name}. </strong>}
              {memorial.location_address}
            </span>
          </div>
        )}

        <div className="mt-6 flex flex-col items-center gap-1 border-t border-border pt-5 text-foreground-muted">
          <Logo className="h-7 w-7 opacity-80" />
          <span className="text-sm font-semibold">Legado Eterno</span>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard icon={Flame} value={memorial.candle_count} label="Velas" />
        <StatCard icon={MessageCircle} value={memorial.condolence_count} label="Mensajes" />
        <StatCard icon={Heart} value={memorial.view_count} label="Visitas" />
      </div>

      <CandlesByCountry slug={slug} />

      <SidebarActions slug={slug} fullName={memorial.full_name} />
    </aside>
  );
}

function flagEmoji(code: string | null): string {
  if (!code || code.length !== 2) return "🕯️";
  return String.fromCodePoint(
    ...[...code.toUpperCase()].map((c) => 127397 + c.charCodeAt(0)),
  );
}

function CandlesByCountry({ slug }: { slug: string }) {
  const { data = [] } = usePublicCandlesByCountry(slug);
  if (data.length === 0) return null;

  return (
    <div className="rounded-lg border border-border bg-card p-5 shadow-card">
      <h3 className="flex items-center gap-2 text-sm font-semibold">
        <Globe className="h-4 w-4 text-brand" /> Velas alrededor del mundo
      </h3>
      <ul className="mt-3 space-y-2">
        {data.map((c) => (
          <li key={c.country} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <span className="text-base">{flagEmoji(c.country_code)}</span>
              {c.country}
            </span>
            <span className="font-semibold text-brand">{c.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SidebarActions({ slug, fullName }: { slug: string; fullName: string }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [shared, setShared] = useState(false);
  const candle = useLightCandle(slug);

  const share = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) {
        await navigator.share({ title: `En memoria de ${fullName}`, url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setShared(true);
      setTimeout(() => setShared(false), 2500);
    } catch {
      /* cancelado */
    }
  };

  return (
    <div className="rounded-lg border border-border bg-card p-5 shadow-card">
      <div className="flex flex-col gap-2">
        <Button
          onClick={() => {
            candle.reset();
            setOpen((v) => !v);
          }}
        >
          <Flame className="h-4 w-4" /> Encender una vela
        </Button>
        <Button variant="outline" onClick={share}>
          {shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}
          {shared ? "¡Enlace copiado!" : "Compartir"}
        </Button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="mt-4 flex flex-col gap-3">
              {candle.isSuccess ? (
                <p className="flex items-center gap-2 text-sm font-medium text-brand-hover">
                  <Flame className="h-4 w-4" /> Has encendido una vela. 🕯️
                </p>
              ) : (
                <>
                  <Input
                    placeholder="Tu nombre (opcional)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    maxLength={150}
                  />
                  <Textarea
                    placeholder="Un pensamiento (opcional)"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    maxLength={300}
                  />
                  {candle.isError && (
                    <p className="text-sm text-destructive">{getErrorMessage(candle.error)}</p>
                  )}
                  <Button
                    onClick={() =>
                      candle.mutate({
                        lit_by_name: name.trim() || undefined,
                        message: message.trim() || undefined,
                      })
                    }
                    disabled={candle.isPending}
                  >
                    {candle.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Flame className="h-4 w-4" />
                    )}
                    Encender vela
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Pestaña Recuerdos: línea de tiempo + galería                               */
/* -------------------------------------------------------------------------- */

function RecuerdosPanel({ slug, fullName }: { slug: string; fullName: string }) {
  const { data: timeline = [], isLoading: loadingTimeline } = usePublicTimeline(slug);
  const { data: media = [], isLoading: loadingMedia } = usePublicMedia(slug);
  const [lightbox, setLightbox] = useState<number | null>(null);

  return (
    <div className="space-y-8">
      <section className="rounded-lg border border-border bg-card p-6 shadow-card">
        <SectionHeader
          icon={Clock}
          title={`Momentos importantes en la vida de ${fullName}`}
        />
        {loadingTimeline ? (
          <Skeletons className="mt-6 h-24" count={2} />
        ) : timeline.length === 0 ? (
          <EmptyState
            icon={Clock}
            text="Aún no se han añadido momentos a la línea de tiempo."
            bare
          />
        ) : (
          <ol className="mt-6 space-y-6 border-l-2 border-brand-light pl-6">
            {timeline.map((ev) => (
              <TimelineRow key={ev.id} event={ev} />
            ))}
          </ol>
        )}
      </section>

      <section className="rounded-lg border border-border bg-card p-6 shadow-card">
        <SectionHeader icon={ImageIcon} title="Galería de recuerdos" />
        {loadingMedia ? (
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="skeleton aspect-square rounded-lg" />
            ))}
          </div>
        ) : media.length === 0 ? (
          <EmptyState icon={ImageIcon} text="Aún no hay fotos en la galería." bare />
        ) : (
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {media.map((item, i) => (
              <PhotoTile key={item.id} item={item} onOpen={() => setLightbox(i)} />
            ))}
          </div>
        )}
      </section>

      <Lightbox
        items={media}
        index={lightbox}
        onClose={() => setLightbox(null)}
        onIndexChange={setLightbox}
      />
    </div>
  );
}

function Lightbox({
  items,
  index,
  onClose,
  onIndexChange,
}: {
  items: PublicMediaItem[];
  index: number | null;
  onClose: () => void;
  onIndexChange: (i: number) => void;
}) {
  const isOpen = index !== null;

  const go = useCallback(
    (delta: number) => {
      if (index === null || items.length === 0) return;
      onIndexChange((index + delta + items.length) % items.length);
    },
    [index, items.length, onIndexChange],
  );

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") go(1);
      if (e.key === "ArrowLeft") go(-1);
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [isOpen, go, onClose]);

  const current = index !== null ? items[index] : null;

  return (
    <AnimatePresence>
      {current && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
        >
          <button
            onClick={onClose}
            aria-label="Cerrar"
            className="absolute right-4 top-4 flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-white transition-colors hover:bg-white/20"
          >
            <X className="h-5 w-5" />
          </button>

          {items.length > 1 && (
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  go(-1);
                }}
                aria-label="Anterior"
                className="absolute left-3 flex h-11 w-11 items-center justify-center rounded-full bg-white/10 text-white transition-colors hover:bg-white/20 md:left-6"
              >
                <ChevronLeft className="h-6 w-6" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  go(1);
                }}
                aria-label="Siguiente"
                className="absolute right-3 flex h-11 w-11 items-center justify-center rounded-full bg-white/10 text-white transition-colors hover:bg-white/20 md:right-6"
              >
                <ChevronRight className="h-6 w-6" />
              </button>
            </>
          )}

          <motion.figure
            key={current.id}
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="flex max-h-[90vh] max-w-4xl flex-col items-center gap-3"
          >
            {current.url && (
              <img
                src={current.url}
                alt={current.caption ?? current.original_filename ?? "recuerdo"}
                className="max-h-[80vh] w-auto rounded-lg object-contain shadow-2xl"
              />
            )}
            <figcaption className="text-center text-sm text-white/80">
              {current.caption ?? current.original_filename}
              {items.length > 1 && (
                <span className="ml-2 text-white/50">
                  {(index ?? 0) + 1} / {items.length}
                </span>
              )}
            </figcaption>
          </motion.figure>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function TimelineRow({ event }: { event: TimelineItem }) {
  const label = shortDate(event.event_date) || (event.year ? String(event.year) : "");
  return (
    <li className="relative">
      <span className="absolute -left-[31px] top-1 flex h-4 w-4 items-center justify-center rounded-full border-2 border-brand bg-card">
        <span className="h-1.5 w-1.5 rounded-full bg-brand" />
      </span>
      {label && (
        <p className="text-xs font-semibold uppercase tracking-wide text-brand">{label}</p>
      )}
      <p className="font-semibold">{event.title}</p>
      {event.description && (
        <p className="mt-1 text-sm text-foreground-muted">{event.description}</p>
      )}
      {event.image_url && (
        <img
          src={event.image_url}
          alt={event.title}
          loading="lazy"
          className="mt-3 max-h-56 rounded-md object-cover"
        />
      )}
    </li>
  );
}

function PhotoTile({ item, onOpen }: { item: PublicMediaItem; onOpen: () => void }) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="group relative aspect-square overflow-hidden rounded-lg border border-border bg-muted"
    >
      {item.url ? (
        <img
          src={item.thumbnail_url ?? item.url}
          alt={item.caption ?? item.original_filename ?? "recuerdo"}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center text-xs text-foreground-muted">
          {item.media_type}
        </div>
      )}
      <span className="absolute inset-0 bg-black/0 transition-colors group-hover:bg-black/15" />
      {item.caption && (
        <p className="absolute inset-x-0 bottom-0 truncate bg-gradient-to-t from-black/70 to-transparent px-2 py-1.5 text-left text-xs text-white">
          {item.caption}
        </p>
      )}
    </button>
  );
}

/* -------------------------------------------------------------------------- */
/* Pestaña Árbol genealógico                                                   */
/* -------------------------------------------------------------------------- */

function FamilyTreePanel({ slug }: { slug: string }) {
  const { data: members = [], isLoading } = usePublicFamily(slug);

  if (isLoading) {
    return <Skeletons className="h-16" count={3} />;
  }
  if (members.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="Árbol genealógico"
        text="Aún no se han añadido familiares a este memorial."
      />
    );
  }

  const childrenOf = (parentId: string | null) =>
    members.filter((m) => m.parent_member_id === parentId);

  return (
    <div className="rounded-lg border border-border bg-card p-6 shadow-card">
      <SectionHeader icon={Users} title="Árbol genealógico" />
      <div className="mt-6 space-y-4">
        {childrenOf(null).map((root) => (
          <FamilyNode key={root.id} member={root} childrenOf={childrenOf} depth={0} />
        ))}
      </div>
    </div>
  );
}

function FamilyNode({
  member,
  childrenOf,
  depth,
}: {
  member: FamilyMember;
  childrenOf: (parentId: string | null) => FamilyMember[];
  depth: number;
}) {
  const kids = childrenOf(member.id);
  return (
    <div className={depth > 0 ? "border-l-2 border-brand-light pl-5" : ""}>
      <div className="flex items-center gap-3 rounded-md border border-border bg-card p-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-light font-semibold text-brand">
          {member.full_name.charAt(0).toUpperCase()}
        </span>
        <div>
          <p className="font-medium">
            {member.full_name}
            {member.relationship_type && (
              <span className="ml-2 text-xs font-normal text-foreground-muted">
                · {member.relationship_type}
              </span>
            )}
          </p>
          {(member.birth_year || member.death_year) && (
            <p className="text-xs text-foreground-muted">
              {[member.birth_year, member.death_year].filter(Boolean).join(" — ")}
            </p>
          )}
        </div>
      </div>
      {kids.length > 0 && (
        <div className="mt-3 space-y-3">
          {kids.map((kid) => (
            <FamilyNode
              key={kid.id}
              member={kid}
              childrenOf={childrenOf}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Pestaña Condolencias                                                        */
/* -------------------------------------------------------------------------- */

const PHOTO_ACCEPT = "image/jpeg,image/png,image/webp";
const PHOTO_MAX_BYTES = 8 * 1024 * 1024; // 8 MB — debe coincidir con el backend

function CondolencesPanel({ slug }: { slug: string }) {
  const { data: condolences = [], isLoading } = usePublicCondolences(slug);
  const add = useAddCondolence(slug);
  const [name, setName] = useState("");
  const [message, setMessage] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [photoError, setPhotoError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const canSubmit = name.trim().length >= 2 && message.trim().length >= 2;

  function selectPhoto(file: File | null) {
    setPhotoError(null);
    if (photoPreview) URL.revokeObjectURL(photoPreview);
    if (!file) {
      setPhoto(null);
      setPhotoPreview(null);
      return;
    }
    if (!PHOTO_ACCEPT.split(",").includes(file.type)) {
      setPhotoError("Formato no admitido. Usa JPG, PNG o WebP.");
      return;
    }
    if (file.size > PHOTO_MAX_BYTES) {
      setPhotoError("La imagen supera los 8 MB.");
      return;
    }
    setPhoto(file);
    setPhotoPreview(URL.createObjectURL(file));
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-border bg-card p-6 shadow-card">
        <SectionHeader icon={MessageCircle} title="Deja un mensaje de condolencia" />
        {add.isSuccess ? (
          <p className="mt-5 flex items-center gap-2 text-sm font-medium text-brand-hover">
            <Check className="h-4 w-4" /> Gracias por tu mensaje. Se publicará tras la
            moderación.
          </p>
        ) : (
          <div className="mt-5 flex flex-col gap-3">
            <Input
              placeholder="Tu nombre"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={150}
            />
            <Textarea
              placeholder="Escribe tu mensaje…"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              maxLength={2000}
            />

            {photoPreview ? (
              <div className="relative w-fit">
                <img
                  src={photoPreview}
                  alt="Vista previa"
                  className="h-32 w-32 rounded-md object-cover"
                />
                <button
                  type="button"
                  onClick={() => selectPhoto(null)}
                  aria-label="Quitar foto"
                  className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-card shadow-card ring-1 ring-border"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="inline-flex w-fit items-center gap-2 rounded-md border border-dashed border-border px-3 py-2 text-sm text-foreground-muted transition-colors hover:border-brand hover:text-brand"
              >
                <ImagePlus className="h-4 w-4" /> Adjuntar una foto (opcional)
              </button>
            )}
            <input
              ref={fileRef}
              type="file"
              accept={PHOTO_ACCEPT}
              className="hidden"
              onChange={(e) => selectPhoto(e.target.files?.[0] ?? null)}
            />
            {photoError && <p className="text-sm text-destructive">{photoError}</p>}

            {add.isError && (
              <p className="text-sm text-destructive">{getErrorMessage(add.error)}</p>
            )}
            <Button
              className="self-start"
              disabled={!canSubmit || add.isPending}
              onClick={() =>
                add.mutate({
                  author_name: name.trim(),
                  message: message.trim(),
                  photo,
                })
              }
            >
              {add.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <MessageCircle className="h-4 w-4" />
              )}
              Enviar mensaje
            </Button>
          </div>
        )}
      </section>

      {isLoading ? (
        <Skeletons className="h-20" count={3} />
      ) : condolences.length === 0 ? (
        <EmptyState
          icon={MessageCircle}
          text="Sé el primero en dejar un mensaje de condolencia."
        />
      ) : (
        <ul className="space-y-3">
          {condolences.map((c) => (
            <CondolenceCard key={c.id} condolence={c} />
          ))}
        </ul>
      )}
    </div>
  );
}

function CondolenceCard({ condolence }: { condolence: Condolence }) {
  return (
    <li className="rounded-lg border border-border bg-card p-5 shadow-card">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-light font-semibold text-brand">
          {condolence.author_name.charAt(0).toUpperCase()}
        </span>
        <div>
          <p className="font-medium">{condolence.author_name}</p>
          <p className="text-xs text-foreground-muted">{shortDate(condolence.created_at)}</p>
        </div>
      </div>
      <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-foreground-muted">
        {condolence.message}
      </p>
      {condolence.photo_url && (
        <a
          href={condolence.photo_url}
          target="_blank"
          rel="noreferrer"
          className="mt-3 block w-fit"
        >
          <img
            src={condolence.photo_url}
            alt={`Foto compartida por ${condolence.author_name}`}
            loading="lazy"
            className="max-h-64 rounded-md object-cover"
          />
        </a>
      )}
      {condolence.signature && (
        <p className="mt-2 text-sm italic text-brand-hover">— {condolence.signature}</p>
      )}
    </li>
  );
}

/* -------------------------------------------------------------------------- */
/* Componentes auxiliares                                                      */
/* -------------------------------------------------------------------------- */

function DateBadge({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-light text-brand">
        <Icon className="h-4 w-4" />
      </span>
      <div className="leading-tight">
        <p className="text-[10px] font-medium uppercase tracking-wide text-foreground-muted">
          {label}
        </p>
        <p className="text-sm font-semibold text-foreground">{value}</p>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  value,
  label,
}: {
  icon: LucideIcon;
  value: number;
  label: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card py-4 shadow-card">
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-light text-brand">
        <Icon className="h-4 w-4" />
      </span>
      <p className="text-lg font-bold text-foreground">{value}</p>
      <p className="text-[11px] text-foreground-muted">{label}</p>
    </div>
  );
}

function SectionHeader({ icon: Icon, title }: { icon: LucideIcon; title: string }) {
  return (
    <h2 className="flex items-center gap-3 text-lg font-semibold">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-light text-brand">
        <Icon className="h-5 w-5" />
      </span>
      {title}
    </h2>
  );
}

function EmptyState({
  icon: Icon,
  title,
  text,
  bare = false,
}: {
  icon: LucideIcon;
  title?: string;
  text: string;
  bare?: boolean;
}) {
  return (
    <div
      className={
        bare
          ? "flex flex-col items-center gap-2 py-10 text-center text-foreground-muted"
          : "flex flex-col items-center gap-2 rounded-lg border border-dashed border-border bg-card py-12 text-center text-foreground-muted"
      }
    >
      <Icon className="h-9 w-9 opacity-40" />
      {title && <p className="font-medium text-foreground">{title}</p>}
      <p className="max-w-xs text-sm">{text}</p>
    </div>
  );
}

function Skeletons({ count, className }: { count: number; className?: string }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`skeleton rounded-lg ${className ?? "h-16"}`} />
      ))}
    </div>
  );
}
