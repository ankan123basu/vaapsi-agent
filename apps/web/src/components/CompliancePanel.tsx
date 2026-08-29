import type { Compliance } from '../api/client';
import './CompliancePanel.css';

interface Props {
  compliance: Compliance | null;
}

const GUARDRAIL_ICONS: Record<string, string> = {
  max_retries: '3x',
  dnd_window: '21-08',
  opt_out: 'OPT',
  human_approval: 'INR',
};

export default function CompliancePanel({ compliance }: Props) {
  if (!compliance) return null;

  return (
    <div className="card compliance" id="compliance-panel">
      <div>
        <div className="compliance__header">
          <h2 className="text-heading">Compliance</h2>
          <span className={`compliance__count text-mono-lg ${compliance.violations === 0 ? 'compliance__count--pass' : 'compliance__count--fail'}`}>
            {compliance.violations}
          </span>
        </div>
        <p className="text-body-sm compliance__subtitle">
          {compliance.violations === 0 ? 'All guardrails passing' : `${compliance.violations} violation(s) detected`}
        </p>

        <div className="compliance__rules">
          {Object.entries(compliance.guardrails).map(([key, guardrail]) => (
            <div key={key} className={`compliance__rule ${guardrail.status === 'passing' ? 'compliance__rule--pass' : 'compliance__rule--fail'}`}>
              <div className="compliance__rule-icon text-mono">
                {GUARDRAIL_ICONS[key] || '?'}
              </div>
              <div className="compliance__rule-content">
                <span className="text-body-sm compliance__rule-name">{guardrail.rule}</span>
                <span className={`badge ${guardrail.status === 'passing' ? 'badge--recovered' : 'badge--failed'}`}>
                  {guardrail.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Guardrails Enforcement Summary */}
      <div className="compliance__summary-card" style={{ marginTop: 'var(--space-lg)', paddingTop: 'var(--space-md)', borderTop: '1px solid var(--border-light)' }}>
        <div style={{ padding: 'var(--space-md)', background: 'var(--vault-dim)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-sm)' }}>
          <span className="text-label" style={{ color: 'var(--signal-green)', display: 'block', marginBottom: '4px' }}>
            🛡️ Bound Compliance Enforcement
          </span>
          <p className="text-body-sm" style={{ opacity: 0.85, fontSize: '0.8125rem' }}>
            DND sleep hours (9 PM–8 AM IST) active. Max 3 retries per case enforced. Human approval required for cases over ₹5,000. Zero unhandled compliance violations.
          </p>
        </div>
      </div>
    </div>
  );
}
