"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

import { authService } from "@/services/auth.service";
import { AUTH_QUERY_KEY } from "@/hooks/useAuth";
import { extractErrorMessage } from "@/utils/errors";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import type { UserRole } from "@/types/auth";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type FormData = z.infer<typeof schema>;

const DASHBOARD_MAP: Record<UserRole, string> = {
  student: "/student-dashboard",
  instructor: "/instructor-dashboard",
  admin: "/admin-dashboard",
};

export function LoginForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setServerError("");
    try {
      const res = await authService.login(data);
      // Seed the React Query cache with the user returned from login
      // so useAuth doesn't need to fire a separate /me request
      queryClient.setQueryData(AUTH_QUERY_KEY, res.user);
      router.push(DASHBOARD_MAP[res.user.role]);
    } catch (err) {
      setServerError(extractErrorMessage(err, "Login failed. Please try again."));
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      {serverError && <Alert type="error" message={serverError} />}

      <Input
        label="Email address"
        type="email"
        autoComplete="email"
        error={errors.email?.message}
        {...register("email")}
      />

      <Input
        label="Password"
        type="password"
        autoComplete="current-password"
        error={errors.password?.message}
        {...register("password")}
      />

      <div className="flex items-center justify-between text-sm">
        <Link href="/forgot-password" className="text-primary-600 hover:underline">
          Forgot password?
        </Link>
      </div>

      <Button type="submit" className="w-full" isLoading={isSubmitting}>
        Sign in
      </Button>

      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-primary-600 hover:underline font-medium">
          Sign up
        </Link>
      </p>
    </form>
  );
}
