import api from "./api";
import type { ApiResponse, User, UserRole } from "@/types/auth";

export const adminService = {
  async getUsersByRole(role: UserRole): Promise<ApiResponse<User[]>> {
    const res = await api.get<ApiResponse<User[]>>(`/admin/users/by-role/${role}`);
    return res.data;
  },
};
