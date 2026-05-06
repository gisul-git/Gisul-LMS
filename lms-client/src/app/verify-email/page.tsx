"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { authService } from "@/services/auth.service";
import { Alert } from "@/components/ui/Alert";

export default function VerifyEmailPage() {
  const params = useSearchParams();
  const token = params.get("token") ?? "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Verification token is missing.");
      return;
    }
    authService
      .verifyEmail(token)
      .then((res) => {
        setStatus("success");
        setMessage(res.message);
      })
      .catch(() => {
        setStatus("error");
        setMessage("Verification link is invalid or has expired.");
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Email Verification</h1>

        {status === "loading" && (
          <p className="text-gray-500">Verifying your email...</p>
        )}

        {status !== "loading" && (
          <>
            <Alert type={status === "success" ? "success" : "error"} message={message} />
            <Link
              href="/login"
              className="mt-6 inline-block text-sm text-primary-600 hover:underline"
            >
              Go to login
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
