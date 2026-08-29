import type { Metrics } from '../api/client';
import './RecoveryFunnel.css';

interface Props {
  metrics: Metrics;
}

export default function RecoveryFunnel({ metrics }: Props) {
  const stages = [
    { label: 'Detected', count: metrics.total_cases, color: 'var(--ink)' },
    { label: 'Diagnosed', count: metrics.total_cases - (metrics.status_distribution?.['detected'] || 0), color: 'var(--ink)' },
    { label: 'Strategy Set', count: metrics.recovered_cases + metrics.failed_cases + metrics.blocked_cases + metrics.pending_approval, color: 'var(--ink)' },
    { label: 'Executed', count: metrics.recovered_cases + metrics.failed_cases, color: 'var(--ink)' },
    { label: 'Recovered', count: metrics.recovered_cases, color: 'var(--signal-green)' },
  ];

  const maxCount = Math.max(...stages.map((s) => s.count), 1);

  return (
    <div className="card funnel" id="recovery-funnel">
      <h2 className="text-heading funnel__title">Recovery Funnel</h2>
      <div className="funnel__stages">
        {stages.map((stage) => (
          <div key={stage.label} className="funnel__stage">
            <div className="funnel__stage-header">
              <span className="text-body-sm">{stage.label}</span>
              <span className="text-mono">{stage.count}</span>
            </div>
            <div className="funnel__bar-track">
              <div
                className="funnel__bar-fill"
                style={{
                  width: `${(stage.count / maxCount) * 100}%`,
                  backgroundColor: stage.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Root cause breakdown */}
      {metrics.root_cause_distribution && Object.keys(metrics.root_cause_distribution).length > 0 && (
        <div className="funnel__breakdown">
          <h3 className="text-label" style={{ marginBottom: 'var(--space-sm)', marginTop: 'var(--space-lg)' }}>
            Root Cause Breakdown
          </h3>
          {Object.entries(metrics.root_cause_distribution)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 8)
            .map(([cause, count]) => (
              <div key={cause} className="funnel__cause-row">
                <span className="text-mono" style={{ fontSize: '0.75rem' }}>
                  {cause.replace(/_/g, ' ')}
                </span>
                <span className="text-mono" style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                  {count}
                </span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
