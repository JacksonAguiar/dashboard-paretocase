import { MetricsCards } from "@/components/dashboard/metrics-cards";
import { ActivityLog } from "@/components/dashboard/activity-log";

export default function Home() {
  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Visão Geral</h2>
        <p className="text-muted-foreground mt-1">
          Acompanhe os principais indicadores do funil de captação.
        </p>
      </div>

      <MetricsCards />

      <ActivityLog />
    </div>
  );
}
