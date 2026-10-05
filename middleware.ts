import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyJWT } from '@/lib/auth';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  // Verify token signature and expiration
  const payload = token ? await verifyJWT(token) : null;

  if (!payload) {
    // Redirect unauthenticated users to login page
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

// Routes to protect with middleware
export const config = {
  matcher: ['/dashboard/:path*', '/profile/:path*'],
};
