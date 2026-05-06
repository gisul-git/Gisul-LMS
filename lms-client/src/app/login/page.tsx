import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = { title: "Sign In — LMS" };

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 h-12 w-12 rounded-xl bg-primary-600 flex items-center justify-center">
              <span className="text-white text-xl font-bold">L</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Welcome back</h1>
            <p className="mt-1 text-sm text-gray-500">Sign in to your account</p>
          </div>
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
