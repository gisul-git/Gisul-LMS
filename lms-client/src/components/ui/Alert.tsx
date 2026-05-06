import { cn } from "@/utils/cn";

interface AlertProps {
  type: "error" | "success" | "info";
  message: string;
  className?: string;
}

const styles = {
  error: "bg-red-50 border-red-300 text-red-800",
  success: "bg-green-50 border-green-300 text-green-800",
  info: "bg-blue-50 border-blue-300 text-blue-800",
};

export function Alert({ type, message, className }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-lg border px-4 py-3 text-sm",
        styles[type],
        className
      )}
    >
      {message}
    </div>
  );
}
