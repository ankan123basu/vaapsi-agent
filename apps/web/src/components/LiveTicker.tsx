import type { Metrics } from '../api/client';
import './LiveTicker.css';

interface Props {
  metrics: Metrics;
}

export default function LiveTicker({ metrics }: Props) {
  const recoveredFormatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(metrics.total_recovered);

  return (
    <div className="ticker" id="live-ticker">
      <div className="ticker__row">
        <span className="ticker__label text-label">Recovered</span>
        <span className="ticker__value">{recoveredFormatted}</span>
        <span className="ticker__divider" />
        <span className="ticker__label text-label">Rate</span>
        <span className="ticker__value ticker__value--secondary">{metrics.recovery_rate.toFixed(1)}%</span>
        <span className="ticker__divider" />
        <span className="ticker__label text-label">Cases</span>
        <span className="ticker__value ticker__value--secondary">{metrics.total_cases}</span>
        <span className="ticker__divider" />
        <span className="ticker__label text-label">Rules</span>
        <span className="ticker__value ticker__value--secondary">{metrics.rule_hit_ratio.toFixed(0)}%</span>
        <span className="ticker__divider" />
        <span className="ticker__label text-label">Violations</span>
        <span className={`ticker__value ${metrics.compliance_violations === 0 ? 'ticker__value--green' : 'ticker__value--red'}`}>
          {metrics.compliance_violations}
        </span>
      </div>
    </div>
  );
}
