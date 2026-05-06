"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { authService } from "@/services/auth.service";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";

const schema = z.object({ email: z.string().email("Enter a valid email") });
type FormData = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    await authService.forgotPassword(data.email);
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Reset password</h1>
        <p className="text-sm text-gray-500 mb-6">
          Enter your email and we&apos;ll send a reset link.
        </p>

        {submitted ? (
          <>
            <Alert
              type="success"
              message="If an account with that email exists, a reset link has been sent."
            />
            <Link href="/login" className="mt-4 inline-block text-sm text-primary-600 hover:underline">
              Back to login
            </Link>
          </>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
            <Input
              label="Email address"
              type="email"
              autoComplete="email"
              error={errors.email?.message}
              {...register("email")}
            />
            <Button type="submit" className="w-full" isLoading={isSubmitting}>
              Send reset link
            </Button>
            <Link href="/login" className="block text-center text-sm text-gray-500 hover:underline">
              Back to login
            </Link>
          </form>
        )}
      </div>
    </div>
  );
}
