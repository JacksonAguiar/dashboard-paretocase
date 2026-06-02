"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { mockLogs } from "@/lib/mock-data";
import { Bot, CheckCircle2, Info, AlertTriangle } from "lucide-react";

export function ActivityLog() {
  const getIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "info":
      default:
        return <Info className="w-4 h-4 text-primary" />;
    }
  };

  return (
    <Card className="bg-card/40 backdrop-blur-md border-border/50">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" />
          <CardTitle className="text-lg font-semibold">Log de Operações dos Agentes</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockLogs.map((log) => (
            <div key={log.id} className="flex items-start gap-4 pb-4 border-b border-border/30 last:border-0 last:pb-0">
              <div className="mt-0.5">
                {getIcon(log.type)}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    {log.time}
                  </span>
                  <span className="text-sm font-medium text-foreground">
                    {log.agent}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {log.action}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
