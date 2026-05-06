import type { Metadata } from "next";
import { UserTable } from "@/components/admin/UserTable";

export const metadata: Metadata = { title: "Instructors — Admin" };

export default function InstructorsPage() {
  return (
    <>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Instructors</h1>
      <div className="bg-white rounded-xl border border-gray-200">
        <UserTable role="instructor" emptyMessage="No instructors found." />
      </div>
    </>
  );
}
