import { useState } from 'react';
import type { RecoveryCase } from '../api/client';
import './CaseTable.css';

interface Props {
  cases: RecoveryCase[];
  onCaseClick: (c: RecoveryCase) => void;
}

const STATUS_BADGE: Record<string, string> = {
  recovered: 'badge--recovered',
  failed: 'badge--failed',
  blocked: 'badge--blocked',
  pending_approval: 'badge--pending',
};

const formatINR = (n: number) =>
  new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);

export default function CaseTable({ cases, onCaseClick }: Props) {
  const [methodFilter, setMethodFilter] = useState<'all' | 'rule' | 'llm_fallback'>('all');

  const ruleCount = cases.filter((c) => c.diagnosis_method === 'rule').length;
  const llmCount = cases.filter((c) => c.diagnosis_method === 'llm_fallback').length;

  const filteredCases = cases.filter((c) => {
    if (methodFilter === 'all') return true;
    return c.diagnosis_method === methodFilter;
  });

  return (
    <div className="card card--flat case-table-wrap" id="case-table">
      <div className="case-table-header">
        <div>
          <h2 className="text-heading">Recovery Cases</h2>
          <span className="text-body-sm" style={{ color: 'var(--text-tertiary)' }}>
            Showing {filteredCases.length} of {cases.length} cases
          </span>
        </div>

        {/* Method Filter Chips */}
        <div className="case-table-filters">
          <button
            className={`case-filter-chip ${methodFilter === 'all' ? 'case-filter-chip--active' : ''}`}
            onClick={() => setMethodFilter('all')}
          >
            ALL ({cases.length})
          </button>
          <button
            className={`case-filter-chip ${methodFilter === 'rule' ? 'case-filter-chip--active' : ''}`}
            onClick={() => setMethodFilter('rule')}
          >
            ⚡ RULE ({ruleCount})
          </button>
          <button
            className={`case-filter-chip case-filter-chip--llm ${methodFilter === 'llm_fallback' ? 'case-filter-chip--llm-active' : ''}`}
            onClick={() => setMethodFilter('llm_fallback')}
          >
            🤖 LLM FALLBACK ({llmCount})
          </button>
        </div>
      </div>

      {/* Explicit Judge Tip Guidance Banner */}
      <div className="case-table-judge-tip" id="judge-tip-cases">
        <span className="case-table-judge-tip__icon">💡</span>
        <span className="text-body-sm">
          <strong>JUDGE TIP:</strong> Click any case row below to inspect its 7-node LangGraph decision trace, Groq LLM model reasoning, compliance interventions, and live multi-language voice call synthesis (gTTS).
        </span>
      </div>

      <div className="case-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Type</th>
              <th>Root Cause</th>
              <th>Diagnosis Method</th>
              <th>Amount</th>
              <th>Channel</th>
              <th>Status</th>
              <th>Recovered</th>
            </tr>
          </thead>
          <tbody>
            {filteredCases.map((c) => (
              <tr
                key={c.case_id}
                onClick={() => onCaseClick(c)}
                className="case-row"
                role="button"
                tabIndex={0}
              >
                <td>
                  <span className="text-mono" style={{ fontSize: '0.75rem' }}>
                    {c.case_id}
                  </span>
                </td>
                <td>
                  <span className="badge badge--rule">{c.event_type.replace(/_/g, ' ')}</span>
                </td>
                <td>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 500 }}>
                    {(c.root_cause || 'unknown').replace(/_/g, ' ')}
                  </span>
                </td>
                <td>
                  {c.diagnosis_method === 'llm_fallback' ? (
                    <span className="badge badge--llm-highlight">
                      🤖 LLM ({c.diagnosis_provider?.includes('gpt-oss') ? 'gpt-oss-120b' : c.diagnosis_provider?.split('/').pop() || 'gpt-oss-120b'})
                    </span>
                  ) : (
                    <span className="badge badge--rule">⚡ RULE</span>
                  )}
                </td>
                <td className="text-mono" style={{ textAlign: 'right' }}>
                  {formatINR(c.amount_at_risk)}
                </td>
                <td>{c.recovery_channel || '—'}</td>
                <td>
                  <span className={`badge ${STATUS_BADGE[c.case_status] || 'badge--rule'}`}>
                    {c.case_status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="text-mono" style={{ textAlign: 'right', color: c.recovery_amount > 0 ? 'var(--signal-green)' : 'var(--text-tertiary)' }}>
                  {c.recovery_amount > 0 ? formatINR(c.recovery_amount) : '—'}
                </td>
              </tr>
            ))}

            {filteredCases.length === 0 && (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-tertiary)' }}>
                  No cases match the selected method filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
