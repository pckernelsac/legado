import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";

export type PlanTier = "basic" | "family" | "premium";

export interface Plan {
  id: string;
  tier: PlanTier;
  name: string;
  description: string | null;
  price_monthly: number;
  price_yearly: number;
  currency: string;
  max_memorials: number;
  max_media_per_memorial: number;
  max_storage_mb: number;
  allow_video: boolean;
  allow_custom_qr: boolean;
  allow_ai_features: boolean;
}

export interface SubscriptionOverview {
  plan: Plan;
  status: string;
  billing_cycle: string;
  current_period_end: string | null;
  memorials_used: number;
  memorials_limit: number;
}

export function usePlans() {
  return useQuery({
    queryKey: ["plans"],
    queryFn: async () => (await api.get<Plan[]>("/plans")).data,
    staleTime: 10 * 60_000,
  });
}

export function useSubscription() {
  return useQuery({
    queryKey: ["subscription"],
    queryFn: async () =>
      (await api.get<SubscriptionOverview>("/billing/subscription")).data,
  });
}

export function useSubscribe() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { tier: PlanTier; billing_cycle?: string }) =>
      (await api.post<SubscriptionOverview>("/billing/subscribe", input)).data,
    onSuccess: (data) => {
      qc.setQueryData(["subscription"], data);
    },
  });
}
