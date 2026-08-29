import type { Metrics } from '../api/client';
import './MetricsRow.css';

interface Props {
  metrics: Metrics;
}

const formatINR = (n: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);

export default function MetricsRow({ metrics }: Props) {
  const cards = [
    {
      label: 'Total at Risk',
      value: formatINR(metrics.total_at_risk),
      variant: '',
    },
    {
      label: 'Recovered',
      value: formatINR(metrics.total_recovered),
      variant: 'molten',
    },
    {
      label: 'Recovery Rate',
      value: `${metrics.recovery_rate.toFixed(1)}%`,
      variant: '',
    },
    {
      label: 'Rule vs LLM',
      value: `${metrics.rule_hit_count} / ${metrics.llm_fallback_count}`,
      variant: '',
      sublabel: `${metrics.rule_hit_ratio.toFixed(0)}% deterministic`,
    },
    {
      label: 'Avg Latency',
      value: `${metrics.avg_latency_ms.toFixed(0)}ms`,
      variant: '',
      sublabel: '~1040ms LLM · 0.4ms Rule',
    },
    {
      label: 'Compliance',
      value: `${metrics.compliance_violations}`,
      variant: metrics.compliance_violations === 0 ? 'green' : 'red',
      sublabel: metrics.compliance_violations === 0 ? 'No violations' : 'Violations found',
    },
  ];

  return (
    <div className="metrics-row" id="metrics-row">
      {cards.map((card, i) => (
        <div
          key={card.label}
          className={`metric-card ${card.variant === 'molten' ? 'metric-card--hero' : ''} stagger-${i + 1} animate-fade-in`}
        >
          <span className="metric-card__label">{card.label}</span>
          <span className={`metric-card__value ${card.variant ? `metric-card__value--${card.variant}` : ''}`}>
            {card.value}
          </span>
          {card.sublabel && (
            <span className="metric-card__delta">{card.sublabel}</span>
          )}
        </div>
      ))}
    </div>
  );
}
