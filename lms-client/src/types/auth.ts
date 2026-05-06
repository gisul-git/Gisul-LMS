export type UserRole = "student" | "instructor" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  email_verified: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user: User;
  token_type: string;
}

export interface ApiResponse<T = null> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiError {
  success: false;
  message: string;
  code?: string;
  errors?: { field: string; message: string }[];
}
