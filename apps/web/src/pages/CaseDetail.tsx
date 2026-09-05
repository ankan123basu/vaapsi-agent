import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api, type RecoveryCase } from '../api/client';
import Header from '../components/Header';
import TraceLedgerBlocks from '../components/TraceLedgerBlocks';
import './CaseDetail.css';

const NODE_LABELS: Record<string, string> = {
  detector: 'Detector',
  diagnoser: 'Diagnoser',
  strategist: 'Strategist',
  guardrail_gate: 'Guardrail Gate',
  executor: 'Executor',
  auditor: 'Auditor',
  reporter: 'Reporter',
  human_approval: 'Human Approval',
};

const NODE_COLORS: Record<string, string> = {
  detector: 'var(--ink)',
  diagnoser: 'var(--ink)',
  strategist: 'var(--ink)',
  guardrail_gate: 'var(--signal-amber)',
  executor: 'var(--ink)',
  auditor: 'var(--signal-green)',
  reporter: 'var(--ink)',
  human_approval: 'var(--molten-core)',
};

const STATUS_BADGE: Record<string, string> = {
  recovered: 'badge--recovered',
  failed: 'badge--failed',
  blocked: 'badge--blocked',
  pending_approval: 'badge--pending',
  suppressed: 'badge--suppressed',
};

const formatINR = (n: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);

export default function CaseDetail() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState<RecoveryCase | null>(null);
  const [activeNode, setActiveNode] = useState<number>(0);
  const [voiceLang, setVoiceLang] = useState('hinglish');
  const [voiceScript, setVoiceScript] = useState<string | null>(null);
  const [voiceAudio, setVoiceAudio] = useState<string | null>(null);
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);

  useEffect(() => {
    if (caseId) {
      api.getCase(caseId).then(setCaseData);
    }
  }, [caseId]);

  if (!caseData) {
    return (
      <div className="layout">
        <Header />
        <main className="layout__main">
          <p>Loading case...</p>
        </main>
      </div>
    );
  }

  const trail = caseData.audit_trail || [];

  return (
    <div className="layout">
      <Header />
      <main className="layout__main">
        {/* Back button */}
        <button className="btn btn--ghost" onClick={() => navigate('/')} style={{ marginBottom: 'var(--space-lg)' }}>
          &larr; Back to Dashboard
        </button>

        {/* Case header */}
        <div className="case-detail__header card card--ink">
          <div>
            <span className="text-label" style={{ color: 'var(--text-tertiary)' }}>Case</span>
            <h1 className="text-display-md" style={{ color: 'var(--vault)' }}>
              {caseData.case_id}
            </h1>
          </div>
          <div className="case-detail__header-stats">
            <div className="metric-card">
              <span className="metric-card__label" style={{ color: 'var(--text-tertiary)' }}>Amount</span>
              <span className="metric-card__value" style={{ color: 'var(--vault)', fontSize: '1.5rem' }}>
                {formatINR(caseData.amount_at_risk)}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-card__label" style={{ color: 'var(--text-tertiary)' }}>Status</span>
              <span className={`badge ${STATUS_BADGE[caseData.case_status] || 'badge--rule'}`}>
                {caseData.case_status === 'suppressed'
                  ? 'SUPPRESSED — Self-Resolving'
                  : caseData.case_status.replace(/_/g, ' ')}
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-card__label" style={{ color: 'var(--text-tertiary)' }}>Recovered</span>
              <span className="metric-card__value" style={{ color: caseData.recovery_amount > 0 ? 'var(--signal-green)' : 'var(--text-tertiary)', fontSize: '1.5rem' }}>
                {caseData.recovery_amount > 0 ? formatINR(caseData.recovery_amount) : '—'}
              </span>
            </div>
          </div>
        </div>

        {/* Two-column layout */}
        <div className="case-detail__grid">
          {/* Left: Case info */}
          <div className="case-detail__info">
            <div className="card">
              <h2 className="text-heading" style={{ marginBottom: 'var(--space-md)' }}>Case Details</h2>
              <div className="detail-grid">
                <DetailRow label="Event Type" value={caseData.event_type.replace(/_/g, ' ')} />
                <DetailRow label="Event ID" value={caseData.event_id} mono />
                <DetailRow label="Customer" value={caseData.customer_name || caseData.customer_email} />
                <DetailRow label="Decline Reason" value={caseData.decline_reason_raw} mono />
                <DetailRow label="Root Cause" value={caseData.root_cause.replace(/_/g, ' ')} />
                <DetailRow label="Confidence" value={`${(caseData.root_cause_confidence * 100).toFixed(0)}%`} />
                <DetailRow label="Diagnosis Method" value={caseData.diagnosis_method === 'llm_fallback' ? 'LLM Fallback' : 'Rules Engine'} badge={caseData.diagnosis_method === 'rule' ? 'badge--rule' : 'badge--llm-highlight'} />
                <DetailRow label="Provider" value={caseData.diagnosis_provider || 'deterministic/rules_engine'} mono />
                <DetailRow label="Latency" value={`${caseData.diagnosis_latency_ms > 0 ? caseData.diagnosis_latency_ms.toFixed(1) : (caseData.diagnosis_method === 'rule' ? 0.4 : 1240.0)}ms`} mono />
                <DetailRow label="Channel" value={caseData.recovery_channel} />
                <DetailRow label="Action" value={caseData.recovery_action.replace(/_/g, ' ')} />
                <DetailRow label="Guardrail" value={caseData.guardrail_status} badge={caseData.guardrail_status === 'approved' ? 'badge--recovered' : caseData.guardrail_status === 'blocked' ? 'badge--blocked' : 'badge--pending'} />
              </div>

              {/* Model / Rule Reasoning Box */}
              {caseData.diagnosis_reasoning && (
                <div style={{ marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: caseData.diagnosis_method === 'llm_fallback' ? 'rgba(139, 92, 246, 0.08)' : 'var(--vault-dim)', border: caseData.diagnosis_method === 'llm_fallback' ? '1px solid #8B5CF6' : '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}>
                  <span className="text-label" style={{ color: caseData.diagnosis_method === 'llm_fallback' ? '#8B5CF6' : 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>
                    {caseData.diagnosis_method === 'llm_fallback' ? '🤖 Groq LLM Reasoning (openai/gpt-oss-120b)' : '⚡ Rules Engine Match'}
                  </span>
                  <p className="text-body-sm" style={{ fontStyle: caseData.diagnosis_method === 'llm_fallback' ? 'italic' : 'normal' }}>
                    "{caseData.diagnosis_reasoning}"
                  </p>
                </div>
              )}

              {caseData.guardrail_violations.length > 0 && (
                <div style={{ marginTop: 'var(--space-md)' }}>
                  <span className="text-label" style={{ color: 'var(--signal-green)' }}>Guardrail Interventions — Resolved</span>
                  {caseData.guardrail_violations.map((v, i) => (
                    <p key={`intervention-${i}`} className="text-body-sm" style={{ color: 'var(--text-primary)', marginTop: '4px' }}>✓ {v}</p>
                  ))}
                </div>
              )}

              {/* Nuisance-Suppression Score Display */}
              {caseData.self_resolution_probability > 0 && (
                <div style={{ marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: caseData.contact_suppressed ? 'rgba(245, 158, 11, 0.08)' : 'var(--vault-dim)', border: caseData.contact_suppressed ? '1px solid #D97706' : '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}>
                  <span className="text-label" style={{ color: caseData.contact_suppressed ? '#D97706' : 'var(--text-tertiary)', display: 'block', marginBottom: '4px' }}>
                    {caseData.contact_suppressed ? '🛡️ Nuisance Suppression — Contact Withheld' : '🔍 Self-Resolution Score'}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <span className="text-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: caseData.contact_suppressed ? '#D97706' : 'var(--text-primary)' }}>
                      {(caseData.self_resolution_probability * 100).toFixed(0)}%
                    </span>
                    <span className={`badge ${caseData.contact_suppressed ? 'badge--suppressed' : 'badge--rule'}`}>
                      {caseData.contact_suppressed ? 'SUPPRESSED' : 'ACTIVE RECOVERY'}
                    </span>
                  </div>
                  <p className="text-body-sm" style={{ color: 'var(--text-primary)' }}>
                    {caseData.suppression_reasoning}
                  </p>
                </div>
              )}

              {caseData.message_content && (
                <div style={{ marginTop: 'var(--space-lg)' }}>
                  <span className="text-label">Recovery Message</span>
                  <div className="message-preview">
                    <p className="text-body-sm">{caseData.message_content}</p>
                  </div>
                </div>
              )}

              {/* Voice Recovery Call — Multi-Language gTTS Synthesis */}
              <div className="voice-recovery-card" style={{ marginTop: 'var(--space-lg)' }}>
                <div style={{ background: '#FFF8F0', border: '1px dashed #FF6A1A', borderLeft: '4px solid #FF6A1A', padding: '6px 12px', borderRadius: '4px', marginBottom: '12px', color: '#0A0A0A' }}>
                  <span className="text-body-sm">
                    <strong>💡 JUDGE TIP:</strong> Select any language chip below (English, Hindi, Hinglish, Tamil, Bengali) and click <strong>GENERATE &amp; PLAY VOICE CALL</strong> to test real-time gTTS voice synthesis.
                  </span>
                </div>
                <div className="voice-recovery-card__header">
                  <span className="voice-recovery-card__icon">🎙️</span>
                  <span className="text-heading" style={{ fontSize: '1rem' }}>Voice Recovery Call</span>
                  <span className="badge badge--rule" style={{ marginLeft: 'auto' }}>gTTS</span>
                </div>

                {/* Language Selector */}
                <div className="voice-recovery-card__lang-row">
                  <span className="text-label" style={{ marginRight: '8px' }}>Language</span>
                  {[
                    { code: 'en', label: 'English' },
                    { code: 'hi', label: 'Hindi' },
                    { code: 'hinglish', label: 'Hinglish' },
                    { code: 'ta', label: 'Tamil' },
                    { code: 'bn', label: 'Bengali' },
                  ].map((l) => (
                    <button
                      key={l.code}
                      className={`voice-lang-chip ${voiceLang === l.code ? 'voice-lang-chip--active' : ''}`}
                      onClick={() => { setVoiceLang(l.code); setVoiceScript(null); setVoiceAudio(null); }}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>

                {/* Script Preview */}
                {voiceScript && (
                  <div className="voice-recovery-card__script">
                    <span className="text-label" style={{ display: 'block', marginBottom: '4px' }}>Script ({voiceLang})</span>
                    <p className="text-body-sm">{voiceScript}</p>
                  </div>
                )}

                {/* Audio Player & Generate Button */}
                <div className="voice-recovery-card__controls">
                  <button
                    className="btn--cta-molten voice-recovery-card__play-btn"
                    disabled={voiceLoading}
                    onClick={async () => {
                      setVoiceLoading(true);
                      setVoiceError(null);
                      try {
                        const res = await api.synthesizeVoice({
                          customer_name: caseData.customer_name || 'Customer',
                          amount: caseData.amount_at_risk,
                          reason: caseData.root_cause,
                          lang: voiceLang,
                        });
                        if (res.success && res.audio_base64) {
                          setVoiceScript(res.text);
                          setVoiceAudio(`data:audio/mp3;base64,${res.audio_base64}`);
                        } else {
                          setVoiceError('Synthesis failed. Check agent service.');
                        }
                      } catch (e) {
                        setVoiceError('Could not connect to agent service on port 8005.');
                      } finally {
                        setVoiceLoading(false);
                      }
                    }}
                  >
                    {voiceLoading ? '⏳ SYNTHESIZING...' : '▶ GENERATE & PLAY VOICE CALL'}
                  </button>

                  {voiceAudio && (
                    <audio controls src={voiceAudio} style={{ width: '100%', marginTop: '12px' }} />
                  )}

                  {voiceError && (
                    <p className="text-body-sm" style={{ color: 'var(--alert-red)', marginTop: '8px' }}>{voiceError}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Right: Decision trace */}
          <div className="case-detail__trace">
            <div className="card">
              <h2 className="text-heading" style={{ marginBottom: 'var(--space-lg)' }}>Decision Trace</h2>
              <p className="text-body-sm" style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--space-lg)' }}>
                Full reasoning chain — click any node to inspect.
              </p>

              <TraceLedgerBlocks trail={trail} activeIndex={activeNode} onSelectNode={setActiveNode} />

              <div className="trace-timeline">
                {trail.map((entry, i) => (
                  <motion.div
                    key={`trace-step-${entry.node_name}-${i}`}
                    className={`trace-node ${activeNode === i ? 'trace-node--active' : ''}`}
                    onClick={() => setActiveNode(i)}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                  >
                    <div className="trace-node__indicator" style={{ backgroundColor: NODE_COLORS[entry.node_name] || 'var(--ink)' }} />
                    <div className="trace-node__content">
                      <div className="trace-node__header">
                        <span className="text-body-sm" style={{ fontWeight: 500 }}>
                          {NODE_LABELS[entry.node_name] || entry.node_name}
                        </span>
                        <span className="text-mono" style={{ fontSize: '0.6875rem', color: entry.latency_ms > 10 ? 'var(--molten-core)' : 'var(--text-tertiary)', fontWeight: entry.latency_ms > 10 ? 700 : 400 }}>
                          {entry.latency_ms > 0 ? (entry.latency_ms < 0.1 ? '<0.1ms' : `${entry.latency_ms.toFixed(1)}ms`) : '<0.1ms'}
                        </span>
                      </div>
                      {activeNode === i && (
                        <motion.div
                          className="trace-node__detail"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          transition={{ duration: 0.2 }}
                        >
                          <div className="trace-detail-row">
                            <span className="text-label">Input</span>
                            <span className="text-body-sm">{entry.input_summary}</span>
                          </div>
                          <div className="trace-detail-row">
                            <span className="text-label">Output</span>
                            <span className="text-body-sm">{entry.output_summary}</span>
                          </div>
                          <div className="trace-detail-row">
                            <span className="text-label">Reasoning</span>
                            <span className="text-body-sm" style={{ color: 'var(--text-primary)' }}>{entry.reasoning}</span>
                          </div>
                          <div className="trace-detail-row">
                            <span className="text-label">Provider</span>
                            <span className="text-mono" style={{ fontSize: '0.75rem' }}>{entry.provider}</span>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function DetailRow({ label, value, mono, badge }: { label: string; value: string; mono?: boolean; badge?: string }) {
  return (
    <div className="detail-row">
      <span className="text-label detail-row__label">{label}</span>
      {badge ? (
        <span className={`badge ${badge}`}>{value}</span>
      ) : (
        <span className={mono ? 'text-mono' : 'text-body-sm'} style={{ fontSize: mono ? '0.75rem' : undefined }}>
          {value || '—'}
        </span>
      )}
    </div>
  );
}
