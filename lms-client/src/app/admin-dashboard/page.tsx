import type { Metadata } from "next";
import { DashboardShell } from "@/components/dashboard/DashboardShell";

export const metadata: Metadata = { title: "Admin Dashboard — LMS" };

export default function AdminDashboardPage() {
  return (
    <DashboardShell title="Admin Dashboard">
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
        {[
          { label: "Total Users", value: "—" },
          { label: "Students", value: "—" },
          { label: "Instructors", value: "—" },
          { label: "Courses", value: "—" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-6">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">User Management</h2>
        <p className="text-sm text-gray-500">User list will appear here.</p>
      </div>
    </DashboardShell>
  );
}
