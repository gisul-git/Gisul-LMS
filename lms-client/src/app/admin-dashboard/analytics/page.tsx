import type { Metadata } from "next";
import { UserTable } from "@/components/admin/UserTable";

export const metadata: Metadata = { title: "Analytics — Admin" };

export default function AnalyticsPage() {
  return (
    <>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Analytics</h1>
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-900">Students</h2>
        </div>
        <UserTable role="student" emptyMessage="No students registered yet." />
      </div>
    </>
  );
}
