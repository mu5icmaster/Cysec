import { NextRequest } from "next/server";
import { updateSession } from "./app/_lib/supabase/middleware";

export async function middleware(req: NextRequest) {
  return await updateSession(req);
}

export const config = {
  matcher: ["/account/:path*", "/login", "/signup", "/cart/checkout"],
};
