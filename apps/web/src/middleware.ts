import { type NextRequest, NextResponse } from 'next/server';
import { updateSession } from '@/lib/supabase/middleware';

/**
 * ATLAS Next.js Middleware
 *
 * Responsibilities:
 * 1. Refresh Supabase auth session on every request (keeps cookies alive).
 * 2. Protect all /app routes — redirect unauthenticated users to /sign-in.
 * 3. Redirect authenticated users away from auth pages to /home.
 */

// Routes that do NOT require authentication
const PUBLIC_ROUTES = new Set([
  '/sign-in',
  '/sign-up',
  '/forgot-password',
  '/reset-password',
  '/auth/callback',
  '/auth/confirm',
]);

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.has(pathname) || pathname.startsWith('/auth/');
}

// Static assets and API routes that should be skipped entirely
function shouldSkip(pathname: string): boolean {
  return (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/favicon') ||
    pathname.includes('.')
  );
}

export async function middleware(request: NextRequest) {
  if (shouldSkip(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (!supabaseUrl || supabaseUrl.includes('placeholder')) {
    // Bypass authentication entirely for local dev with placeholder
    const { pathname } = request.nextUrl;
    if (isPublicRoute(pathname) && pathname !== '/auth/callback' && pathname !== '/auth/confirm') {
      const homeUrl = request.nextUrl.clone();
      homeUrl.pathname = '/home';
      return NextResponse.redirect(homeUrl);
    }
    return NextResponse.next();
  }

  const { supabaseResponse, user } = await updateSession(request);
  const { pathname } = request.nextUrl;

  // Unauthenticated user trying to access protected route → sign-in
  if (!user && !isPublicRoute(pathname)) {
    const signInUrl = request.nextUrl.clone();
    signInUrl.pathname = '/sign-in';
    signInUrl.searchParams.set('redirectTo', pathname);
    return NextResponse.redirect(signInUrl);
  }

  // Authenticated user on auth pages → redirect to home
  if (user && isPublicRoute(pathname) && pathname !== '/auth/callback' && pathname !== '/auth/confirm') {
    const homeUrl = request.nextUrl.clone();
    homeUrl.pathname = '/home';
    return NextResponse.redirect(homeUrl);
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
