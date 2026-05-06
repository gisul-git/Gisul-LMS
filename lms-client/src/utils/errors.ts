import { AxiosError } from "axios";
import type { ApiError } from "@/types/auth";

export function extractErrorMessage(error: unknown, fallback = "Something went wrong"): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiError | undefined;
    return data?.message ?? fallback;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
