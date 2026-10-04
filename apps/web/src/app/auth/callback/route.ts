import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

/**
 * Auth Callback Route Handler
 *
 * Supabase redirects here after:
 * - Email verification (sign-up confirmation)
 * - Password reset (recovery link)
 * - OAuth sign-in (future)
 *
 * This server-side handler exchanges the auth code for a session,
 * then redirects the user to the appropriate destination.
 */
export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);

  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/home';

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (!error) {
      // Successful code exchange → redirect to destination
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  // Auth code exchange failed — redirect to sign-in with error
  return NextResponse.redirect(`${origin}/sign-in?error=auth_callback_failed`);
}
