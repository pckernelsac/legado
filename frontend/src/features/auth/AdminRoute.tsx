import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { PageLoader } from "@/components/feedback/PageLoader";
import { useCurrentUser } from "@/features/auth/hooks";
import { tokenStore } from "@/features/auth/token-store";

const ADMIN_ROLES = ["super_admin", "admin"];

export function AdminRoute({ children }: { children: ReactNode }) {
  const { data: user, isLoading } = useCurrentUser();

  if (!tokenStore.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  if (isLoading) return <PageLoader />;
  if (!user || !ADMIN_ROLES.includes(user.role.name)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}
