'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from './context/session';

export default function NotFound() {
  const router = useRouter();
  const { session, loading } = useSession();

  useEffect(() => {
    if (!loading) {
      if (session?.user) {
        // Authenticated user - redirect to dashboard
        router.push('/dashboard');
      } else {
        // Unauthenticated user - redirect to login
        router.push('/login');
      }
    }
  }, [session, loading, router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Page Not Found</p>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Redirecting...</p>
      </div>
    </div>
  );
}