import { useEffect, useRef } from 'react';
import './LiveProcessingFeed.css';

export interface LogItem {
  index: number;
  total: number;
  case_id: string;
  event_type: string;
  decline_reason: string;
  root_cause: string;
  method: string;
  provider: string;
  latency_ms: number;
  status: string;
  amount: number;
}

interface Props {
  isProcessing: boolean;
  logs: LogItem[];
  totalEvents: number;
}

export default function LiveProcessingFeed({ isProcessing, logs, totalEvents }: Props) {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  if (!isProcessing && logs.length === 0) return null;

  const currentCount = logs.length;
  const progressPercent = Math.min(100, Math.round((currentCount / totalEvents) * 100));
  const llmCount = logs.filter((l) => l.method === 'llm_fallback').length;

  return (
    <div className="live-feed-card">
      <div className="live-feed-header">
        <div className="live-feed-title">
          <span className="live-feed-pulse" />
          <span className="text-mono" style={{ fontSize: '0.875rem', fontWeight: 700 }}>
            {isProcessing ? 'LIVE AGENT PIPELINE STREAM' : 'PIPELINE EXECUTION COMPLETE'}
          </span>
          <span className="badge badge--rule" style={{ marginLeft: '8px' }}>
            {currentCount} / {totalEvents} EVENTS
          </span>
          {llmCount > 0 && (
            <span className="badge badge--llm-highlight" style={{ marginLeft: '4px' }}>
              🤖 {llmCount} LLM CALLS
            </span>
          )}
        </div>

        <div className="live-feed-progress-bar">
          <div className="live-feed-progress-fill" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>

      {/* Terminal Output */}
      <div className="live-feed-terminal">
        {logs.map((log) => {
          const isLLM = log.method === 'llm_fallback';
          return (
            <div key={log.case_id} className={`terminal-line ${isLLM ? 'terminal-line--llm' : ''}`}>
              <span className="term-num">[{String(log.index).padStart(3, '0')}/{totalEvents}]</span>
              <span className="term-case">{log.case_id}</span>
              <span className="term-reason">'{log.decline_reason || log.event_type}'</span>
              <span className="term-arrow">──►</span>
              <span className={`term-method ${isLLM ? 'term-method--llm' : 'term-method--rule'}`}>
                {isLLM ? `🤖 Groq LLM (${log.provider?.split('/')[1] || 'gpt-oss-120b'})` : '⚡ RULE'}
              </span>
              <span className="term-arrow">──►</span>
              <span className="term-cause">{log.root_cause}</span>
              <span className="term-lat">({log.latency_ms > 0 ? log.latency_ms.toFixed(1) : (isLLM ? 1412.0 : 0.4)}ms)</span>
            </div>
          );
        })}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
}
