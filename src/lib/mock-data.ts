export type FunnelStatus = "captação" | "qualificação" | "engajamento" | "agendamento" | "check-in";

export type MessageChannel = "email" | "whatsapp" | "ligação";
export type MessageStatus = "enviado" | "entregue" | "lido" | "respondido";

export interface LeadMessage {
  id: string;
  stage: FunnelStatus;
  channel: MessageChannel;
  subject?: string;
  content: string;
  sentAt: string;
  agent: string;
  status: MessageStatus;
}

export interface Lead {
  id: string;
  name: string;
  company: string;
  role: string;
  status: FunnelStatus;
  updatedAt: string;
  messages: LeadMessage[];
}

export interface ActivityLog {
  id: string;
  time: string;
  agent: string;
  action: string;
  type: "info" | "success" | "warning";
}

export const mockMetrics = {
  enrolled: 1240,
  confirmed: 845,
  attended: 620,
  meetingsScheduled: 112,
};

export const mockLogs: ActivityLog[] = [
  {
    id: "1",
    time: "10:05",
    agent: "Agente Comercial",
    action: "Reunião agendada com sucesso na agenda do executivo.",
    type: "success",
  },
  {
    id: "2",
    time: "09:58",
    agent: "Agente de Engajamento",
    action: "Email de lembrete do evento enviado para 250 confirmados.",
    type: "info",
  },
  {
    id: "3",
    time: "09:22",
    agent: "Agente de Engajamento",
    action: "WhatsApp de confirmação enviado para 'Maria Souza'.",
    type: "info",
  },
  {
    id: "4",
    time: "09:15",
    agent: "Agente de Enriquecimento",
    action: "Lead 'João Silva' atualizado com cargo 'CTO' e empresa 'TechCorp'.",
    type: "info",
  },
  {
    id: "5",
    time: "08:45",
    agent: "Agente de Triagem",
    action: "15 leads reprovados por não atingirem o ICP.",
    type: "warning",
  },
];

export const mockLeads: Lead[] = [
  {
    id: "L-001",
    name: "João Silva",
    company: "TechCorp",
    role: "CTO",
    status: "qualificação",
    updatedAt: "10 min atrás",
    messages: [
      {
        id: "m-001-1",
        stage: "captação",
        channel: "email",
        subject: "Bem-vindo ao Vigil Summit 2025",
        content: "Olá João, foi um prazer ter você inscrito no Vigil Summit. Nos próximos dias enviaremos todas as informações sobre o evento. Esperamos te ver lá!",
        sentAt: "Ontem, 09:00",
        agent: "Agente de Captação",
        status: "lido",
      },
      {
        id: "m-001-2",
        stage: "qualificação",
        channel: "email",
        subject: "Confirmação de perfil — Vigil Summit",
        content: "João, identificamos que você atua como CTO na TechCorp. Gostaríamos de confirmar alguns dados para personalizar sua experiência no evento. Poderia responder este e-mail com seu LinkedIn?",
        sentAt: "Hoje, 08:30",
        agent: "Agente de Enriquecimento",
        status: "enviado",
      },
    ],
  },
  {
    id: "L-002",
    name: "Maria Souza",
    company: "Innova IT",
    role: "Diretora de TI",
    status: "engajamento",
    updatedAt: "45 min atrás",
    messages: [
      {
        id: "m-002-1",
        stage: "captação",
        channel: "email",
        subject: "Bem-vindo ao Vigil Summit 2025",
        content: "Olá Maria, obrigado pela inscrição! Você receberá em breve todos os detalhes do Vigil Summit 2025.",
        sentAt: "2 dias atrás, 10:15",
        agent: "Agente de Captação",
        status: "lido",
      },
      {
        id: "m-002-2",
        stage: "qualificação",
        channel: "whatsapp",
        content: "Oi Maria! Aqui é o assistente do Vigil Summit. Confirmamos seu perfil como Diretora de TI na Innova IT. Tudo certo! 🎯",
        sentAt: "Ontem, 14:00",
        agent: "Agente de Enriquecimento",
        status: "respondido",
      },
      {
        id: "m-002-3",
        stage: "engajamento",
        channel: "email",
        subject: "Sua presença está confirmada — detalhes do evento",
        content: "Maria, sua presença no Vigil Summit está confirmada! O evento acontece no dia 20/06 às 9h. Anexamos o material pré-evento com a agenda completa e as sessões recomendadas para o seu perfil.",
        sentAt: "Hoje, 09:45",
        agent: "Agente de Engajamento",
        status: "lido",
      },
    ],
  },
  {
    id: "L-003",
    name: "Carlos Mendes",
    company: "FinTech SA",
    role: "CEO",
    status: "agendamento",
    updatedAt: "1 hora atrás",
    messages: [
      {
        id: "m-003-1",
        stage: "captação",
        channel: "email",
        subject: "Bem-vindo ao Vigil Summit 2025",
        content: "Olá Carlos, sua inscrição foi recebida com sucesso. Aguarde as próximas comunicações.",
        sentAt: "3 dias atrás, 08:00",
        agent: "Agente de Captação",
        status: "lido",
      },
      {
        id: "m-003-2",
        stage: "qualificação",
        channel: "email",
        subject: "Perfil validado — Carlos Mendes, CEO",
        content: "Carlos, confirmamos sua posição como CEO da FinTech SA. Seu perfil foi aprovado como ICP prioritário para o evento.",
        sentAt: "2 dias atrás, 11:30",
        agent: "Agente de Triagem",
        status: "lido",
      },
      {
        id: "m-003-3",
        stage: "engajamento",
        channel: "whatsapp",
        content: "Carlos, tudo bem? Passando para confirmar sua presença no Vigil Summit no dia 20/06. Você tem 2 minutos para uma ligação rápida hoje?",
        sentAt: "Ontem, 16:00",
        agent: "Agente de Engajamento",
        status: "respondido",
      },
      {
        id: "m-003-4",
        stage: "agendamento",
        channel: "email",
        subject: "Reunião agendada com nosso executivo — Vigil Summit",
        content: "Carlos, conforme combinado, agendamos uma reunião de 30 minutos com nosso diretor comercial para o dia 21/06 às 14h. O convite de calendário foi enviado para o seu e-mail.",
        sentAt: "Hoje, 09:00",
        agent: "Agente Comercial",
        status: "entregue",
      },
    ],
  },
  {
    id: "L-004",
    name: "Ana Oliveira",
    company: "HealthSys",
    role: "CISO",
    status: "check-in",
    updatedAt: "2 horas atrás",
    messages: [
      {
        id: "m-004-1",
        stage: "captação",
        channel: "email",
        subject: "Bem-vindo ao Vigil Summit 2025",
        content: "Olá Ana, obrigado pela inscrição no Vigil Summit! Em breve você receberá mais informações.",
        sentAt: "4 dias atrás, 09:30",
        agent: "Agente de Captação",
        status: "lido",
      },
      {
        id: "m-004-2",
        stage: "qualificação",
        channel: "email",
        subject: "Perfil CISO — acesso especial ao track de segurança",
        content: "Ana, identificamos que você é CISO na HealthSys. Preparamos um track exclusivo de segurança e compliance no evento. Gostaríamos de confirmar seu interesse.",
        sentAt: "3 dias atrás, 10:00",
        agent: "Agente de Enriquecimento",
        status: "respondido",
      },
      {
        id: "m-004-3",
        stage: "engajamento",
        channel: "whatsapp",
        content: "Ana, sua presença foi confirmada! Não esqueça: evento dia 20/06 às 9h. Qualquer dúvida, estamos por aqui. 😊",
        sentAt: "2 dias atrás, 15:00",
        agent: "Agente de Engajamento",
        status: "lido",
      },
      {
        id: "m-004-4",
        stage: "agendamento",
        channel: "ligação",
        content: "Ligação realizada com sucesso. Ana confirmou presença e manifestou interesse em conversar com o time comercial após a palestra principal.",
        sentAt: "Ontem, 11:00",
        agent: "Agente Comercial",
        status: "respondido",
      },
      {
        id: "m-004-5",
        stage: "check-in",
        channel: "whatsapp",
        content: "Check-in realizado! Ana está no evento. QR Code validado às 08:47. Boa sorte e bom evento! 🎉",
        sentAt: "Hoje, 08:47",
        agent: "Agente de Check-in",
        status: "entregue",
      },
    ],
  },
  {
    id: "L-005",
    name: "Ricardo Gomes",
    company: "EduTech BR",
    role: "Engenheiro Sênior",
    status: "captação",
    updatedAt: "5 horas atrás",
    messages: [
      {
        id: "m-005-1",
        stage: "captação",
        channel: "email",
        subject: "Bem-vindo ao Vigil Summit 2025",
        content: "Olá Ricardo, sua inscrição foi recebida! Nos próximos dias entraremos em contato para confirmar seu perfil e garantir a melhor experiência no evento.",
        sentAt: "Hoje, 06:00",
        agent: "Agente de Captação",
        status: "enviado",
      },
    ],
  },
];
