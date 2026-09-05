/**
 * Recoup — API Client.
 * Communicates with the FastAPI agent-service backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8005';

export interface RecoveryCase {
  case_id: string;
  event_id: string;
  event_type: string;
  customer_id: string;
  customer_email: string;
  customer_phone: string;
  customer_name: string;
  amount_at_risk: number;
  currency: string;
  decline_reason_raw: string;
  root_cause: string;
  root_cause_confidence: number;
  diagnosis_method: string;
  diagnosis_reasoning: string;
  diagnosis_provider: string;
  diagnosis_latency_ms: number;
  recovery_channel: string;
  recovery_action: string;
  message_content: string;
  scheduled_at: string;
  guardrail_status: string;
  guardrail_violations: string[];
  execution_status: string;
  execution_result: Record<string, unknown>;
  recovery_amount: number;
  self_resolution_probability: number;
  contact_suppressed: boolean;
  suppression_reasoning: string;
  case_status: string;
  retry_count: number;
  audit_trail: AuditEntry[];
  created_at: string;
  updated_at: string;
}

export interface AuditEntry {
  node_name: string;
  input_summary: string;
  output_summary: string;
  reasoning: string;
  provider: string;
  latency_ms: number;
  timestamp: string;
}

export interface Metrics {
  total_at_risk: number;
  total_recovered: number;
  recovery_rate: number;
  total_cases: number;
  recovered_cases: number;
  failed_cases: number;
  blocked_cases: number;
  pending_approval: number;
  compliance_violations: number;
  rule_hit_count: number;
  llm_fallback_count: number;
  rule_hit_ratio: number;
  avg_latency_ms: number;
  suppressed_cases: number;
  suppression_rate: number;
  root_cause_distribution: Record<string, number>;
  channel_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
}

export interface Compliance {
  total_cases_checked: number;
  violations: number;
  guardrails: Record<string, {
    rule: string;
    status: string;
    violations: number;
  }>;
}

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getCases: (params?: { status?: string; limit?: number; offset?: number }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set('status', params.status);
    if (params?.limit) qs.set('limit', String(params.limit));
    if (params?.offset) qs.set('offset', String(params.offset));
    return apiFetch<{ cases: RecoveryCase[]; total: number }>(`/api/cases?${qs}`);
  },

  getCase: (caseId: string) =>
    apiFetch<RecoveryCase>(`/api/cases/${caseId}`),

  getMetrics: () =>
    apiFetch<Metrics>('/api/metrics'),

  getCompliance: () =>
    apiFetch<Compliance>('/api/compliance'),

  getApprovalQueue: () =>
    apiFetch<{ cases: RecoveryCase[]; total: number }>('/api/approval-queue'),

  approveCase: (caseId: string) =>
    apiFetch<{ case_id: string; status: string }>(`/api/cases/${caseId}/approve`, { method: 'POST' }),

  rejectCase: (caseId: string) =>
    apiFetch<{ case_id: string; status: string }>(`/api/cases/${caseId}/reject`, { method: 'POST' }),

  processBatch: (count: number = 50) =>
    apiFetch<{ status: string; events_processed: number; metrics_summary: Record<string, number> }>(
      `/api/process-batch?count=${count}`, { method: 'POST' }
    ),

  synthesizeVoice: (payload: { text?: string; customer_name?: string; amount?: number; reason?: string; lang?: string }) =>
    apiFetch<{ success: boolean; text: string; language: string; audio_format: string; audio_base64: string; size_bytes: number }>(
      '/api/synthesize-voice', { method: 'POST', body: JSON.stringify(payload) }
    ),

  getVoiceLanguages: () =>
    apiFetch<{ languages: { code: string; label: string }[] }>('/api/voice-languages'),
};
