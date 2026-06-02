"use client";

import { useEffect } from "react";
import { X, Mail, MessageSquare, Phone, CheckCheck, Send, Eye, Reply } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { type Lead, type FunnelStatus, type MessageChannel, type MessageStatus } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const FUNNEL_ORDER: FunnelStatus[] = ["captação", "qualificação", "engajamento", "agendamento", "check-in"];

const stageLabel: Record<FunnelStatus, string> = {
  "captação": "Captação",
  "qualificação": "Qualificação",
  "engajamento": "Engajamento",
  "agendamento": "Agendamento",
  "check-in": "Check-in",
};

const stageColor: Record<FunnelStatus, string> = {
  "captação": "text-slate-400 border-slate-500/30 bg-slate-500/10",
  "qualificação": "text-blue-400 border-blue-500/30 bg-blue-500/10",
  "engajamento": "text-indigo-400 border-indigo-500/30 bg-indigo-500/10",
  "agendamento": "text-purple-400 border-purple-500/30 bg-purple-500/10",
  "check-in": "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
};

const stageDot: Record<FunnelStatus, string> = {
  "captação": "bg-slate-400",
  "qualificação": "bg-blue-400",
  "engajamento": "bg-indigo-400",
  "agendamento": "bg-purple-400",
  "check-in": "bg-emerald-400",
};

const channelIcon: Record<MessageChannel, React.ReactNode> = {
  email: <Mail className="w-3.5 h-3.5" />,
  whatsapp: <MessageSquare className="w-3.5 h-3.5" />,
  ligação: <Phone className="w-3.5 h-3.5" />,
};

const channelLabel: Record<MessageChannel, string> = {
  email: "E-mail",
  whatsapp: "WhatsApp",
  ligação: "Ligação",
};

const statusIcon: Record<MessageStatus, React.ReactNode> = {
  enviado: <Send className="w-3 h-3" />,
  entregue: <CheckCheck className="w-3 h-3" />,
  lido: <Eye className="w-3 h-3" />,
  respondido: <Reply className="w-3 h-3" />,
};

const statusColor: Record<MessageStatus, string> = {
  enviado: "text-muted-foreground",
  entregue: "text-blue-400",
  lido: "text-indigo-400",
  respondido: "text-emerald-400",
};

interface LeadDetailsModalProps {
  lead: Lead;
  onClose: () => void;
}

export function LeadDetailsModal({ lead, onClose }: LeadDetailsModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const stagesWithMessages = FUNNEL_ORDER.filter((stage) =>
    lead.messages.some((m) => m.stage === stage)
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative h-full w-full max-w-xl bg-background border-l border-border/50 flex flex-col shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between px-6 py-5 border-b border-border/50 shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-foreground">{lead.name}</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {lead.role} · {lead.company}
            </p>
            <div className="mt-2">
              <Badge
                variant="outline"
                className={cn("text-xs", stageColor[lead.status])}
              >
                {stageLabel[lead.status]}
              </Badge>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8">
          {stagesWithMessages.map((stage, stageIndex) => {
            const messages = lead.messages.filter((m) => m.stage === stage);
            const isLast = stageIndex === stagesWithMessages.length - 1;

            return (
              <div key={stage} className="relative flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={cn("w-2.5 h-2.5 rounded-full mt-1 shrink-0", stageDot[stage])} />
                  {!isLast && <div className="w-px flex-1 bg-border/50 mt-2 mb-0" />}
                </div>

                <div className="flex-1 pb-2">
                  <span className={cn("inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded border mb-3", stageColor[stage])}>
                    {stageLabel[stage]}
                  </span>

                  <div className="space-y-3">
                    {messages.map((msg) => (
                      <div
                        key={msg.id}
                        className="rounded-lg border border-border/40 bg-card/30 p-4 space-y-2"
                      >
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            {channelIcon[msg.channel]}
                            <span>{channelLabel[msg.channel]}</span>
                            <span className="text-border/80">·</span>
                            <span>{msg.agent}</span>
                          </div>
                          <div className={cn("flex items-center gap-1 text-xs", statusColor[msg.status])}>
                            {statusIcon[msg.status]}
                            <span className="capitalize">{msg.status}</span>
                          </div>
                        </div>

                        {msg.subject && (
                          <p className="text-sm font-medium text-foreground">{msg.subject}</p>
                        )}

                        <p className="text-sm text-muted-foreground leading-relaxed">{msg.content}</p>

                        <p className="text-xs text-muted-foreground/60">{msg.sentAt}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
