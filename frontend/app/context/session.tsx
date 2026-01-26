'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface SessionContextType {
  user: any;
  token: string | null;
  login: (token: string, userData: any) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Function to handle token updates from localStorage
  const handleTokenChange = (newToken: string | null) => {
    if (newToken) {
      setToken(newToken);
      setIsAuthenticated(true);
      // Decode token to get user info
      try {
        // JWT tokens have 3 parts separated by dots: header.payload.signature
        const parts = newToken.split('.');
        if (parts.length === 3) {
          // Decode the payload (second part)
          const payload = parts[1];
          // Add padding if needed
          const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
          const decoded = JSON.parse(atob(paddedPayload));
          setUser(decoded);
        } else {
          // If not a standard JWT, just set a basic user object
          setUser({ token: newToken });
        }
      } catch (e) {
        console.error('Error decoding token', e);
        setUser({ token: newToken });
      }
    } else {
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  useEffect(() => {
    // Check for existing token in localStorage on initial load
    // Only run in browser environment to prevent SSR errors
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('access_token');
      if (storedToken) {
        handleTokenChange(storedToken);
      }
    }
  }, []);

  // Listen for storage events (when token is set from another tab/window or during login)
  useEffect(() => {
    // Only run in browser environment to prevent SSR errors
    if (typeof window !== 'undefined') {
      const handleStorageChange = (e: StorageEvent) => {
        if (e.key === 'access_token') {
          handleTokenChange(e.newValue);
        }
      };

      window.addEventListener('storage', handleStorageChange);

      return () => {
        window.removeEventListener('storage', handleStorageChange);
      };
    }
  }, []);

  const login = (token: string, userData: any) => {
    // Update state first
    setToken(token);
    setUser(userData || { token }); // Use provided userData or create basic object
    setIsAuthenticated(true);

    // Then update localStorage
    localStorage.setItem('access_token', token);
    // Manually dispatch a storage event to notify other tabs/components
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'access_token',
      newValue: token,
      oldValue: null,
    }));
  };

  const logout = () => {
    // Update state first
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);

    // Then update localStorage
    localStorage.removeItem('access_token');
    // Manually dispatch a storage event to notify other tabs/components
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'access_token',
      newValue: null,
      oldValue: token,
    }));
  };

  return (
    <SessionContext.Provider value={{ user, token, login, logout, isAuthenticated }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}