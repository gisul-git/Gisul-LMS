"use client";

import { useAuth } from "@/hooks/useAuth";

interface DashboardShellProps {
  title: string;
  children: React.ReactNode;
}

export function DashboardShell({ title, children }: DashboardShellProps) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">L</span>
          </div>
          <span className="font-semibold text-gray-900">LMS Platform</span>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500 capitalize">{user.role}</p>
              </div>
              <div className="h-9 w-9 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-primary-700 text-sm font-semibold">
                  {user.full_name.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
          )}
          <button
            onClick={logout}
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            Sign out
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">{title}</h1>
        {children}
      </main>
    </div>
  );
}
