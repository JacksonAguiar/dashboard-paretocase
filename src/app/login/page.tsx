"use client";

import { useState } from "react";
import { useAuth } from "@/components/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const { login } = useAuth();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!login(email, password)) {
      setError(true);
    }
  };

  const handleChange = () => {
    if (error) setError(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-background relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/20 rounded-full blur-[120px] pointer-events-none" />

      <Card className="w-full max-w-md border-border bg-card/40 backdrop-blur-xl z-10">
        <CardHeader className="space-y-1 flex flex-col items-center">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
            <Activity className="w-6 h-6 text-primary" />
          </div>
          <CardTitle className="text-2xl font-semibold tracking-tight text-foreground">
            Vigil <span className="text-primary font-bold">Summit</span>
          </CardTitle>
          <CardDescription className="text-muted-foreground text-center">
            Acesse com suas credenciais para monitorar o funil.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-3">
              <Input
                type="email"
                placeholder="E-mail"
                value={email}
                onChange={(e) => { setEmail(e.target.value); handleChange(); }}
                className={`bg-background/50 border-border focus-visible:ring-primary ${error ? "border-destructive" : ""}`}
                required
              />
              <Input
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => { setPassword(e.target.value); handleChange(); }}
                className={`bg-background/50 border-border focus-visible:ring-primary ${error ? "border-destructive" : ""}`}
                required
              />
              {error && (
                <p className="text-sm text-destructive font-medium">
                  Credenciais inválidas. Verifique e-mail e senha.
                </p>
              )}
            </div>
            <Button type="submit" className="w-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
              Entrar
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
