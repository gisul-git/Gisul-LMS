import api from "./api";
import type {
  ApiResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  User,
} from "@/types/auth";

export const authService = {
  async register(data: RegisterRequest): Promise<ApiResponse<User>> {
    const res = await api.post<ApiResponse<User>>("/auth/register", data);
    return res.data;
  },

  async login(data: LoginRequest): Promise<LoginResponse> {
    const res = await api.post<LoginResponse>("/auth/login", data);
    return res.data;
  },

  async logout(): Promise<void> {
    await api.post("/auth/logout");
  },

  async refresh(): Promise<void> {
    await api.post("/auth/refresh");
  },

  async getMe(): Promise<ApiResponse<User>> {
    const res = await api.get<ApiResponse<User>>("/auth/me");
    return res.data;
  },

  async verifyEmail(token: string): Promise<ApiResponse<null>> {
    const res = await api.post<ApiResponse<null>>("/auth/verify-email", { token });
    return res.data;
  },

  async forgotPassword(email: string): Promise<ApiResponse<null>> {
    const res = await api.post<ApiResponse<null>>("/auth/forgot-password", { email });
    return res.data;
  },

  async resetPassword(token: string, new_password: string): Promise<ApiResponse<null>> {
    const res = await api.post<ApiResponse<null>>("/auth/reset-password", {
      token,
      new_password,
    });
    return res.data;
  },
};
