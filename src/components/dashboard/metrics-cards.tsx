"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, UserCheck, CalendarCheck, CalendarDays } from "lucide-react";
import { mockMetrics } from "@/lib/mock-data";

export function MetricsCards() {
  const metrics = [
    {
      title: "Inscritos (Captação)",
      value: mockMetrics.enrolled,
      icon: Users,
      description: "Total de leads captados",
    },
    {
      title: "Confirmados (Engajamento)",
      value: mockMetrics.confirmed,
      icon: UserCheck,
      description: "Confirmaram presença",
    },
    {
      title: "Presentes (Check-in)",
      value: mockMetrics.attended,
      icon: CalendarCheck,
      description: "Fizeram check-in no evento",
    },
    {
      title: "Reuniões (Follow-up)",
      value: mockMetrics.meetingsScheduled,
      icon: CalendarDays,
      description: "Agendamentos comerciais",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <Card key={index} className="bg-card/40 backdrop-blur-md border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {metric.title}
              </CardTitle>
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon className="w-4 h-4 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">{metric.value.toLocaleString('pt-BR')}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {metric.description}
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
