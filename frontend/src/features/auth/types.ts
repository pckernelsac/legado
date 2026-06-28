export type RoleName = "super_admin" | "admin" | "client" | "family_guest";

export interface Role {
  name: RoleName;
  display_name: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_email_verified: boolean;
  mfa_enabled: boolean;
  role: Role;
  last_login_at: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginPayload {
  email: string;
  password: string;
  mfa_code?: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}
