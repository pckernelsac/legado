import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { tokenStore } from "@/features/auth/token-store";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const location = useLocation();
  if (!tokenStore.isAuthenticated()) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return <>{children}</>;
}
