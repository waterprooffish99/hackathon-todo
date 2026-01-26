'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from './context/session';

export default function HomePage() {
  const router = useRouter();
  const { session, loading } = useSession();

  useEffect(() => {
    if (!loading) {
      if (session?.user) {
        // User is authenticated, redirect to dashboard
        router.push('/dashboard');
      } else {
        // User is not authenticated, redirect to login
        router.push('/login');
      }
    }
  }, [session, loading, router]);

  // Render a simple loading state while determining authentication status
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}