import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { PageLoader } from "@/components/feedback/PageLoader";
import { AdminRoute } from "@/features/auth/AdminRoute";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";

const LandingPage = lazy(() => import("@/pages/landing/LandingPage"));
const LoginPage = lazy(() => import("@/pages/auth/LoginPage"));
const RegisterPage = lazy(() => import("@/pages/auth/RegisterPage"));
const VerifyEmailPage = lazy(() => import("@/pages/auth/VerifyEmailPage"));
const ForgotPasswordPage = lazy(() => import("@/pages/auth/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("@/pages/auth/ResetPasswordPage"));
const DashboardPage = lazy(() => import("@/pages/dashboard/DashboardPage"));
const MemorialEditPage = lazy(
  () => import("@/pages/dashboard/memorial-edit/MemorialEditPage"),
);
const PublicMemorialPage = lazy(() => import("@/pages/memorial/PublicMemorialPage"));
const AdminPage = lazy(() => import("@/pages/admin/AdminPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));

export function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/recuperar-contrasena" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/m/:slug" element={<PublicMemorialPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/memorial/:id/edit"
          element={
            <ProtectedRoute>
              <MemorialEditPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminPage />
            </AdminRoute>
          }
        />

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}
