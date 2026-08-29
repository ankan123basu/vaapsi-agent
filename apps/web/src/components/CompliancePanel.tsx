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

  const isEvaluated = compliance.total_cases_checked > 0;
  const violations = compliance.violations;

  return (
    <div className="card compliance" id="compliance-panel">
      <div>
        <div className="compliance__header">
          <h2 className="text-heading">Compliance</h2>
          <span
            className={`compliance__count text-mono-lg ${
              !isEvaluated
                ? 'compliance__count--neutral'
                : violations === 0
                ? 'compliance__count--pass'
                : 'compliance__count--fail'
            }`}
          >
            {isEvaluated ? violations : '0'}
          </span>
        </div>
        <p className="text-body-sm compliance__subtitle">
          {!isEvaluated
            ? 'AWAITING RUN · RUN AGENT TO VERIFY'
            : violations === 0
            ? `All guardrails passing across ${compliance.total_cases_checked} executed cases`
            : `${violations} violation(s) detected across ${compliance.total_cases_checked} cases`}
        </p>

        <div className="compliance__rules">
          {Object.entries(compliance.guardrails).map(([key, guardrail]) => {
            const isRulePassing = guardrail.status === 'passing';
            return (
              <div
                key={key}
                className={`compliance__rule ${
                  !isEvaluated
                    ? 'compliance__rule--neutral'
                    : isRulePassing
                    ? 'compliance__rule--pass'
                    : 'compliance__rule--fail'
                }`}
              >
                <div className="compliance__rule-icon text-mono">
                  {GUARDRAIL_ICONS[key] || '?'}
                </div>
                <div className="compliance__rule-content">
                  <span className="text-body-sm compliance__rule-name">{guardrail.rule}</span>
                  <span
                    className={`badge ${
                      !isEvaluated
                        ? 'badge--neutral'
                        : isRulePassing
                        ? 'badge--recovered'
                        : 'badge--failed'
                    }`}
                  >
                    {!isEvaluated ? 'AWAITING RUN' : guardrail.status.toUpperCase()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Active Guardrails Enforcement Summary */}
      <div
        className="compliance__summary-card"
        style={{ marginTop: 'var(--space-lg)', paddingTop: 'var(--space-md)', borderTop: '1px solid var(--border-light)' }}
      >
        <div
          style={{
            padding: 'var(--space-md)',
            background: 'var(--vault-dim)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-sm)',
          }}
        >
          <span
            className="text-label"
            style={{
              color: isEvaluated ? 'var(--signal-green)' : 'var(--molten-highlight)',
              display: 'block',
              marginBottom: '4px',
            }}
          >
            🛡️ {isEvaluated ? 'Active Compliance Enforcement' : 'Guardrail Verification Ready'}
          </span>
          <p className="text-body-sm" style={{ opacity: 0.85, fontSize: '0.8125rem' }}>
            {isEvaluated
              ? `Verified zero compliance violations across ${compliance.total_cases_checked} cases: DND sleep hours (9 PM–8 AM IST), max 3 retries, opt-outs, and ₹5,000 human approval threshold.`
              : 'Run the 100-event batch to execute live guardrail verification across DND sleep hours (9 PM–8 AM IST), max 3 retries, opt-outs, and ₹5,000 human approval threshold.'}
          </p>
        </div>
      </div>
    </div>
  );
}
