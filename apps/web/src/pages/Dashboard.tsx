import { useState, useEffect, useCallback, lazy, Suspense, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import { api, type Metrics, type RecoveryCase, type Compliance } from '../api/client';
import Header from '../components/Header';
import MetricsRow from '../components/MetricsRow';
import RecoveryFunnel from '../components/RecoveryFunnel';
import CaseTable from '../components/CaseTable';
import CompliancePanel from '../components/CompliancePanel';
import LiveTicker from '../components/LiveTicker';
import ApprovalQueue from '../components/ApprovalQueue';
import LiveProcessingFeed, { type LogItem } from '../components/LiveProcessingFeed';
import TargetCursor from '../components/TargetCursor';
import './Dashboard.css';

// Lazy-load R3F 3D Hero component for instant headline first-paint
const MoltenHero3D = lazy(() => import('../components/MoltenHero3D'));

const HEADLINE_WORDS = ["Autonomous", "Revenue", "Recovery", "Agent"];

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const wordVariants: Variants = {
  hidden: { opacity: 0, y: 30, filter: 'blur(8px)' },
  visible: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [cases, setCases] = useState<RecoveryCase[]>([]);
  const [compliance, setCompliance] = useState<Compliance | null>(null);
  const [pendingCases, setPendingCases] = useState<RecoveryCase[]>([]);
  const [processing, setProcessing] = useState(false);
  const [feedLogs, setFeedLogs] = useState<LogItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Scoped Custom Cursor state (Active ONLY while Hero is in viewport)
  const [isHeroVisible, setIsHeroVisible] = useState(true);
  const heroRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsHeroVisible(entry.isIntersecting);
        if (!entry.isIntersecting) {
          document.body.style.cursor = '';
        }
      },
      { threshold: 0.1 }
    );

    if (heroRef.current) {
      observer.observe(heroRef.current);
    }

    return () => {
      observer.disconnect();
      document.body.style.cursor = '';
    };
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const [m, c, comp, aq] = await Promise.all([
        api.getMetrics(),
        api.getCases({ limit: 100 }),
        api.getCompliance(),
        api.getApprovalQueue(),
      ]);
      setMetrics(m);
      setCases(c.cases || []);
      setCompliance(comp);
      setPendingCases(aq.cases || []);
    } catch (e) {
      setError('Could not connect to agent service. Make sure it is running on port 8000.');
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleProcessBatch = async () => {
    setProcessing(true);
    setError(null);
    setFeedLogs([]);

    try {
      const eventSource = new EventSource('/api/process-batch-stream?count=100');

      eventSource.onmessage = async (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === 'summary') {
            eventSource.close();
            await fetchData();
            setProcessing(false);
            setTimeout(() => {
              const tickerEl = document.getElementById('live-ticker') || document.getElementById('metrics-row');
              tickerEl?.scrollIntoView({ behavior: 'smooth' });
            }, 300);
          } else if (data.index) {
            setFeedLogs((prev) => [...prev, data]);
          }
        } catch (err) {
          // ignore
        }
      };

      eventSource.onerror = async () => {
        eventSource.close();
        // Fallback to standard batch API if stream closes
        try {
          await api.processBatch(100);
          await fetchData();
        } catch (err) {
          setError('Failed to process batch.');
        } finally {
          setProcessing(false);
        }
      };
    } catch (e) {
      setError('Failed to process batch. Check agent service status.');
      setProcessing(false);
    }
  };

  const handleApprove = async (caseId: string) => {
    await api.approveCase(caseId);
    await fetchData();
  };

  const handleReject = async (caseId: string) => {
    await api.rejectCase(caseId);
    await fetchData();
  };

  return (
    <div className="layout">
      <Header />

      <main className="layout__main">
        {/* Full-Bleed 100vh Hero Section */}
        <section className="hero" ref={heroRef}>
          {/* TargetCursor active ONLY while Hero is in viewport */}
          {isHeroVisible && (
            <TargetCursor targetSelector=".hero-cursor-target" cursorColor="#FFB066" />
          )}

          {/* Lazy-loaded Real 3D Depth WebGL Scene */}
          <Suspense fallback={null}>
            <MoltenHero3D />
          </Suspense>

          <div className="hero__content">
            <div className="hero__eyebrow">
              <span className="hero__eyebrow-dot" />
              <span>LANGGRAPH-POWERED AGENT · REAL-TIME DECISION ENGINE</span>
            </div>

            <motion.h1
              className="hero__title"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
            >
              {HEADLINE_WORDS.map((word, i) => (
                <motion.span key={i} variants={wordVariants} className="hero__title-word">
                  {word}{' '}
                </motion.span>
              ))}
            </motion.h1>

            <p className="hero__subtitle">
              <strong>Vaapsi (वापसी) — <em>"Jo paisa gaya, wapas aayega."</em></strong> Autonomous revenue recovery agent detecting payment failures, diagnosing root causes, and recovering revenue with compliance guardrails and multi-language voice calls.
            </p>

            <div className="hero__actions">
              <button
                className="btn--cta-molten hero-cursor-target"
                onClick={handleProcessBatch}
                disabled={processing}
                id="process-batch-btn"
              >
                <span>
                  {processing
                    ? `⏳ AGENT RUNNING: ${feedLogs.length}/100 (${Math.min(100, Math.round((feedLogs.length / 100) * 100))}%)`
                    : '⚡ PROCESS 100 EVENTS'}
                </span>
              </button>

              {metrics && metrics.total_cases > 0 && (
                <div className="hero__stat-pill">
                  <span className="text-mono" style={{ color: 'var(--molten-highlight)' }}>
                    {metrics.total_cases}
                  </span>
                  <span style={{ opacity: 0.7 }}>CASES PROCESSED</span>
                </div>
              )}
            </div>

            <div style={{ marginTop: 'var(--space-md)' }}>
              <span className="hero__cta-helper" style={{ fontSize: '0.8125rem', color: 'rgba(245, 241, 232, 0.65)', fontFamily: 'var(--font-mono)' }}>
                ⚡ Run this first to execute the 7-node LangGraph agent live
              </span>
            </div>
          </div>

          {/* Scroll Affordance */}
          <div className="hero__scroll-cue hero-cursor-target">
            <span>SCROLL TO EXPLORE</span>
            <svg className="hero__scroll-chevron" viewBox="0 0 24 24" fill="none">
              <path d="M19 9l-7 7-7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </section>

        {error && (
          <div className="error-banner">
            <span className="text-body-sm">{error}</span>
          </div>
        )}

        {/* Demo Methodology Disclosure Banner */}
        <div className="synthetic-data-disclosure" id="synthetic-disclosure">
          <span className="synthetic-disclosure__icon">⚡</span>
          <span className="text-body-sm" style={{ opacity: 0.95 }}>
            <strong>DEMO METHODOLOGY:</strong> Runs against synthetically generated test transactions — executing real rules engine, real Groq/Gemini LLM calls, real compliance guardrail checks, and real gTTS voice synthesis.
          </span>
        </div>

        {/* Live Processing Stream Feed Terminal */}
        <LiveProcessingFeed
          isProcessing={processing}
          logs={feedLogs}
          totalEvents={100}
        />

        {/* Empty/Active State Guidance Banner */}
        {!metrics || metrics.total_cases === 0 ? (
          <div className="guidance-banner guidance-banner--empty" id="dashboard-guidance-banner">
            <span className="guidance-banner__icon">⚡</span>
            <div className="guidance-banner__content">
              <strong>No cases processed in this session yet</strong> — Click{' '}
              <button className="guidance-banner__btn" onClick={handleProcessBatch} disabled={processing}>
                Process 100 Events
              </button>{' '}
              above to run the agent live and populate this dashboard.
            </div>
          </div>
        ) : (
          <div className="guidance-banner guidance-banner--active" id="dashboard-guidance-banner">
            <span className="guidance-banner__icon">✓</span>
            <div className="guidance-banner__content">
              <strong>{metrics.total_cases} cases processed live</strong> — All metrics, funnel stages, compliance guardrails, and audit trails derived from real agent pipeline execution.
            </div>
          </div>
        )}

        {metrics && (
          <AnimatePresence>
            {/* Live Ticker (Sticky Top) */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <LiveTicker metrics={metrics} />
            </motion.div>

            {/* Top Stat Strip: 6 Metric Cards Full Width */}
            <div id="metrics-row" style={{ marginTop: 'var(--space-lg)', marginBottom: 'var(--space-lg)' }}>
              <MetricsRow metrics={metrics} />
            </div>

            {/* Human-in-the-loop Approval Queue (if cases exist) */}
            {pendingCases.length > 0 && (
              <div style={{ marginBottom: 'var(--space-xl)' }}>
                <ApprovalQueue
                  cases={pendingCases}
                  onApprove={handleApprove}
                  onReject={handleReject}
                />
              </div>
            )}

            {/* Two-Column Section: Recovery Funnel on Left, Compliance Panel on Right */}
            <motion.div
              className="dashboard-grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="dashboard-grid__left">
                <RecoveryFunnel metrics={metrics} />
              </div>
              <div className="dashboard-grid__right">
                <CompliancePanel compliance={compliance} />
              </div>
            </motion.div>

            {/* Full Width Section: Recovery Cases Table */}
            <div style={{ marginTop: 'var(--space-xl)', marginBottom: 'var(--space-2xl)' }}>
              <CaseTable
                cases={cases}
                onCaseClick={(c) => navigate(`/case/${c.case_id}`)}
              />
            </div>
          </AnimatePresence>
        )}
      </main>
    </div>
  );
}
