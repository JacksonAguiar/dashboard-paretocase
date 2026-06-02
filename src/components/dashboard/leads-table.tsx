"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { mockLeads, type FunnelStatus, type Lead } from "@/lib/mock-data";
import { Users, ChevronRight } from "lucide-react";
import { LeadDetailsModal } from "@/components/dashboard/lead-details-modal";

export function LeadsTable() {
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  const getStatusBadge = (status: FunnelStatus) => {
    switch (status) {
      case "captação":
        return <Badge variant="outline" className="bg-slate-500/10 text-slate-400 border-slate-500/20">Captação</Badge>;
      case "qualificação":
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20">Qualificação</Badge>;
      case "engajamento":
        return <Badge variant="outline" className="bg-indigo-500/10 text-indigo-400 border-indigo-500/20">Engajamento</Badge>;
      case "agendamento":
        return <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20">Agendamento</Badge>;
      case "check-in":
        return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Check-in</Badge>;
      default:
        return <Badge variant="outline">Desconhecido</Badge>;
    }
  };

  return (
    <>
      <Card className="bg-card/40 backdrop-blur-md border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            <CardTitle className="text-lg font-semibold">Leads Recentes</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-border/50 hover:bg-transparent">
                  <TableHead className="text-muted-foreground">Nome</TableHead>
                  <TableHead className="text-muted-foreground">Empresa</TableHead>
                  <TableHead className="text-muted-foreground">Cargo</TableHead>
                  <TableHead className="text-muted-foreground">Status</TableHead>
                  <TableHead className="text-muted-foreground w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockLeads.map((lead) => (
                  <TableRow key={lead.id} className="border-border/20 hover:bg-muted/30">
                    <TableCell className="font-medium text-foreground">{lead.name}</TableCell>
                    <TableCell className="text-muted-foreground">{lead.company}</TableCell>
                    <TableCell className="text-muted-foreground">{lead.role}</TableCell>
                    <TableCell>{getStatusBadge(lead.status)}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedLead(lead)}
                        className="text-muted-foreground hover:text-foreground h-7 px-2 gap-1"
                      >
                        Detalhes
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {selectedLead && (
        <LeadDetailsModal lead={selectedLead} onClose={() => setSelectedLead(null)} />
      )}
    </>
  );
}
