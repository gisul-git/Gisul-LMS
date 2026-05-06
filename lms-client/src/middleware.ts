import { NextRequest, NextResponse } from "next/server";

const PUBLIC_ROUTES = ["/login", "/register", "/verify-email", "/forgot-password", "/reset-password"];

const ROLE_ROUTES: Record<string, string[]> = {
  "/student-dashboard": ["student", "admin"],
  "/instructor-dashboard": ["instructor", "admin"],
  "/admin-dashboard": ["admin"],
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (PUBLIC_ROUTES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next();
  }

  // Check access token cookie
  const accessToken = request.cookies.get("access_token")?.value;
  if (!accessToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Decode JWT payload (no verification — server handles that)
  try {
    const [, payloadB64] = accessToken.split(".");
    const payload = JSON.parse(
      Buffer.from(payloadB64, "base64url").toString("utf-8")
    );
    const role: string = payload.role ?? "";
    const exp: number = payload.exp ?? 0;

    // Treat expired token as unauthenticated — force refresh via client
    if (Date.now() / 1000 > exp) {
      // Don't redirect here — let the Axios interceptor handle silent refresh
      // Only redirect if no refresh cookie exists
      const refreshToken = request.cookies.get("refresh_token")?.value;
      if (!refreshToken) {
        return NextResponse.redirect(new URL("/login", request.url));
      }
    }

    // Check role-based access
    for (const [route, allowedRoles] of Object.entries(ROLE_ROUTES)) {
      if (pathname.startsWith(route) && !allowedRoles.includes(role)) {
        // Redirect to their own dashboard
        const dashboardMap: Record<string, string> = {
          student: "/student-dashboard",
          instructor: "/instructor-dashboard",
          admin: "/admin-dashboard",
        };
        return NextResponse.redirect(
          new URL(dashboardMap[role] ?? "/login", request.url)
        );
      }
    }
  } catch {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
