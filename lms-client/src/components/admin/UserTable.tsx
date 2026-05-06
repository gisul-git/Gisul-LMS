"use client";

import { useQuery } from "@tanstack/react-query";
import { adminService } from "@/services/admin.service";
import type { UserRole } from "@/types/auth";

interface UserTableProps {
  role: UserRole;
  emptyMessage?: string;
}

export function UserTable({ role, emptyMessage = "No users found." }: UserTableProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "users", role],
    queryFn: () => adminService.getUsersByRole(role),
  });

  const users = data?.data ?? [];

  if (isLoading) {
    return (
      <div className="p-6">
        <p className="text-sm text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!users.length) {
    return (
      <div className="p-6">
        <p className="text-sm text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-6 font-medium text-gray-500">Name</th>
            <th className="text-left py-3 px-6 font-medium text-gray-500">Email</th>
            <th className="text-left py-3 px-6 font-medium text-gray-500">Status</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-6 font-medium text-gray-900">{u.full_name}</td>
              <td className="py-3 px-6 text-gray-600">{u.email}</td>
              <td className="py-3 px-6">
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  u.email_verified
                    ? "bg-green-100 text-green-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}>
                  {u.email_verified ? "Verified" : "Unverified"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-gray-400 mt-2 px-6 pb-4">{users.length} total</p>
    </div>
  );
}
