import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { tokenStore } from "@/features/auth/token-store";
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
} from "@/features/auth/types";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get<User>("/auth/me")).data,
    enabled: tokenStore.isAuthenticated(),
    staleTime: 5 * 60_000,
  });
}

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: LoginPayload) =>
      (await api.post<TokenResponse>("/auth/login", payload)).data,
    onSuccess: (data) => {
      tokenStore.setTokens(data.access_token, data.refresh_token);
      void qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (payload: RegisterPayload) =>
      (await api.post<User>("/auth/register", payload)).data,
  });
}

export function useVerifyEmail() {
  return useMutation({
    mutationFn: async (token: string) =>
      (await api.post("/auth/verify-email", { token })).data,
  });
}

export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: async (email: string) =>
      (await api.post("/auth/password-reset", { email })).data,
  });
}

export function useConfirmPasswordReset() {
  return useMutation({
    mutationFn: async (payload: { token: string; new_password: string }) =>
      (await api.post("/auth/password-reset/confirm", payload)).data,
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const refresh = tokenStore.getRefreshToken();
      if (refresh) await api.post("/auth/logout", { refresh_token: refresh });
    },
    onSettled: () => {
      tokenStore.clear();
      qc.clear();
    },
  });
}
