import type { Metadata } from "next";
import { DashboardShell } from "@/components/dashboard/DashboardShell";

export const metadata: Metadata = { title: "Student Dashboard — LMS" };

export default function StudentDashboardPage() {
  return (
    <DashboardShell title="Student Dashboard">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        {[
          { label: "Enrolled Courses", value: "0" },
          { label: "Completed", value: "0" },
          { label: "Certificates", value: "0" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-6">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">My Courses</h2>
        <p className="text-sm text-gray-500">No courses enrolled yet.</p>
      </div>
    </DashboardShell>
  );
}
