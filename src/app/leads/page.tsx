import { LeadsTable } from "@/components/dashboard/leads-table";

export default function LeadsPage() {
  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Leads</h2>
        <p className="text-muted-foreground mt-1">
          Gerencie e acompanhe todos os leads do funil de captação.
        </p>
      </div>

      <LeadsTable />
    </div>
  );
}
