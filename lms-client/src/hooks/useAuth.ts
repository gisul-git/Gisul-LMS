"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/auth.store";
import type { User, UserRole } from "@/types/auth";

export const AUTH_QUERY_KEY = ["auth", "me"] as const;

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { clearAuth } = useAuthStore();

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: async () => {
      const res = await authService.getMe();
      return res.data ?? null;
    },
    staleTime: 60 * 1000,
    retry: false, // don't retry on 401 — means user is not logged in
  });

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      queryClient.removeQueries({ queryKey: AUTH_QUERY_KEY });
      clearAuth();
      router.push("/login");
    }
  };

  const redirectToDashboard = (role: UserRole) => {
    const routes: Record<UserRole, string> = {
      student: "/student-dashboard",
      instructor: "/instructor-dashboard",
      admin: "/admin-dashboard",
    };
    router.push(routes[role]);
  };

  return {
    user: user ?? null,
    isLoading,
    isAuthenticated: !!user,
    logout,
    redirectToDashboard,
  };
}
