import type { Metadata } from "next";
import { UserTable } from "@/components/admin/UserTable";

export const metadata: Metadata = { title: "Admin Team — Admin" };

export default function AdminsPage() {
  return (
    <>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Team</h1>
      <div className="bg-white rounded-xl border border-gray-200">
        <UserTable role="admin" emptyMessage="No admins found." />
      </div>
    </>
  );
}
