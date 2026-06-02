"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

type AuthContextType = {
  isAuthenticated: boolean;
  login: (email: string, password: string) => boolean;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isReady, setIsReady] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check session storage on mount
    const authStatus = sessionStorage.getItem("vigil_auth") === "true";
    setIsAuthenticated(authStatus);
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) return;

    if (!isAuthenticated && pathname !== "/login") {
      router.push("/login");
    } else if (isAuthenticated && pathname === "/login") {
      router.push("/");
    }
  }, [isAuthenticated, pathname, isReady, router]);

  const login = (email: string, password: string) => {
    if (email === "admin@vigilsummit.com" && password === "admin") {
      sessionStorage.setItem("vigil_auth", "true");
      setIsAuthenticated(true);
      return true;
    }
    return false;
  };

  const logout = () => {
    sessionStorage.removeItem("vigil_auth");
    setIsAuthenticated(false);
    router.push("/login");
  };

  if (!isReady) {
    return <div className="min-h-screen bg-background flex items-center justify-center">Carregando...</div>;
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
