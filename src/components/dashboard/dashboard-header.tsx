"use client";

import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import { LogOut, Activity } from "lucide-react";

export function DashboardHeader() {
  const { logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between px-6 border-b border-border/50 bg-background/60 backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/20">
          <Activity className="w-5 h-5 text-primary" />
        </div>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">
          Vigil <span className="text-primary font-bold">Summit</span>
        </h1>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={logout}
        className="text-muted-foreground hover:text-foreground"
      >
        <LogOut className="w-4 h-4 mr-2" />
        Sair
      </Button>
    </header>
  );
}
