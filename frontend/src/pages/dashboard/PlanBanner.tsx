import { AnimatePresence, motion } from "framer-motion";
import { Check, Crown, Loader2, Sparkles } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  usePlans,
  useSubscribe,
  useSubscription,
  type Plan,
} from "@/features/billing/hooks";
import { cn } from "@/lib/utils";

export function PlanBanner() {
  const { data: sub, isLoading } = useSubscription();
  const [open, setOpen] = useState(false);

  if (isLoading || !sub) {
    return <div className="skeleton h-24 rounded-lg" />;
  }

  const pct = sub.memorials_limit
    ? Math.min(100, Math.round((sub.memorials_used / sub.memorials_limit) * 100))
    : 0;
  const atLimit = sub.memorials_used >= sub.memorials_limit;

  return (
    <Card className={cn(atLimit && "border-accent")}>
      <CardContent className="p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-brand-light text-brand">
              <Crown className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-foreground-muted">Tu plan</p>
              <p className="text-lg font-bold">{sub.plan.name}</p>
            </div>
          </div>

          <div className="flex-1 sm:max-w-xs">
            <div className="mb-1 flex justify-between text-xs text-foreground-muted">
              <span>Memoriales</span>
              <span>
                {sub.memorials_used} / {sub.memorials_limit}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full rounded-full", atLimit ? "bg-accent" : "bg-brand")}
                style={{ width: `${pct}%` }}
              />
            </div>
            {atLimit && (
              <p className="mt-1 text-xs text-accent-foreground">
                Alcanzaste el límite de tu plan.
              </p>
            )}
          </div>

          <Button variant={atLimit ? "default" : "outline"} onClick={() => setOpen((v) => !v)}>
            <Sparkles className="h-4 w-4" /> Mejorar plan
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
              <PlanPicker currentTier={sub.plan.tier} onDone={() => setOpen(false)} />
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
}

function PlanPicker({
  currentTier,
  onDone,
}: {
  currentTier: string;
  onDone: () => void;
}) {
  const { data: plans = [], isLoading } = usePlans();
  const subscribe = useSubscribe();

  if (isLoading) {
    return (
      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="skeleton h-44 rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <PlanCard
          key={plan.id}
          plan={plan}
          current={plan.tier === currentTier}
          pending={subscribe.isPending}
          onChoose={async () => {
            await subscribe.mutateAsync({ tier: plan.tier });
            onDone();
          }}
        />
      ))}
    </div>
  );
}

function PlanCard({
  plan,
  current,
  pending,
  onChoose,
}: {
  plan: Plan;
  current: boolean;
  pending: boolean;
  onChoose: () => void;
}) {
  const features = [
    `${plan.max_memorials} memorial(es)`,
    `${plan.max_media_per_memorial} archivos/memorial`,
    plan.allow_video ? "Video y audio" : "Solo fotos",
    plan.allow_custom_qr ? "QR personalizado" : "QR estándar",
    ...(plan.allow_ai_features ? ["Funciones de IA"] : []),
  ];

  return (
    <div
      className={cn(
        "flex flex-col rounded-lg border p-4",
        current ? "border-brand bg-brand-light/40" : "border-border bg-card",
      )}
    >
      <div className="flex items-center justify-between">
        <p className="font-semibold">{plan.name}</p>
        {current && (
          <span className="rounded-full bg-brand px-2 py-0.5 text-[10px] font-medium text-white">
            Actual
          </span>
        )}
      </div>
      <p className="mt-1 text-2xl font-extrabold">
        S/{Number(plan.price_monthly)}
        <span className="text-sm font-normal text-foreground-muted">/mes</span>
      </p>
      <ul className="mt-3 flex-1 space-y-1.5 text-xs text-foreground-muted">
        {features.map((f) => (
          <li key={f} className="flex items-start gap-1.5">
            <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand" />
            {f}
          </li>
        ))}
      </ul>
      <Button
        size="sm"
        variant={current ? "outline" : "default"}
        className="mt-4 w-full"
        disabled={current || pending}
        onClick={onChoose}
      >
        {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {current ? "Plan actual" : "Elegir"}
      </Button>
    </div>
  );
}
