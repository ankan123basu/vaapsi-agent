import { useState } from 'react';
import type { RecoveryCase } from '../api/client';
import './ApprovalQueue.css';

interface Props {
  cases: RecoveryCase[];
  onApprove: (caseId: string) => void;
  onReject: (caseId: string) => void;
}

const formatINR = (n: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);

const PAGE_SIZE = 5;

export default function ApprovalQueue({ cases, onApprove, onReject }: Props) {
  const [currentPage, setCurrentPage] = useState(1);

  if (cases.length === 0) return null;

  const totalPages = Math.ceil(cases.length / PAGE_SIZE);
  const startIdx = (currentPage - 1) * PAGE_SIZE;
  const pageCases = cases.slice(startIdx, startIdx + PAGE_SIZE);

  return (
    <div className="card approval-queue" id="approval-queue">
      <div className="approval-queue__header">
        <div className="approval-queue__title-group">
          <h2 className="text-heading">Needs Your Approval</h2>
          <span className="badge badge--pending">{cases.length} pending</span>
        </div>

        {totalPages > 1 && (
          <div className="approval-queue__pagination">
            <button
              className="btn btn--sm btn--ghost"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => p - 1)}
            >
              Prev
            </button>

            <span className="text-mono text-caption">
              {currentPage} / {totalPages}
            </span>

            <button
              className="btn btn--sm btn--ghost"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Explicit Judge Tip Banner for Human-in-the-Loop Governance */}
      <div className="case-table-judge-tip" style={{ margin: 'var(--space-sm) var(--space-md) var(--space-md) var(--space-md)' }}>
        <span className="case-table-judge-tip__icon">💡</span>
        <span className="text-body-sm">
          <strong>JUDGE TIP (Human-in-the-Loop):</strong> High-value transactions (&gt; ₹5,000) are automatically held by the Compliance Gate for human approval. Click <strong>APPROVE</strong> or <strong>REJECT</strong> to test live governance.
        </span>
      </div>

      <div className="approval-table-wrapper">
        <table className="approval-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Flags</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>

          <tbody>
            {pageCases.map((c) => {
              const flags = c.guardrail_violations.map((v) => v.split(':')[0]);

              return (
                <tr key={c.case_id}>
                  <td className="text-mono" title={c.case_id}>
                    {c.case_id}
                  </td>

                  <td className="customer-name">
                    {c.customer_name || c.customer_email || 'Customer'}
                  </td>

                  <td className="text-mono amount">
                    {formatINR(c.amount_at_risk)}
                  </td>

                  <td>
                    <div className="flags-cell">
                      {flags.length > 0 ? (
                        flags.map((flag, i) => (
                          <span key={i} className={`flag-badge flag-badge--${flag.toLowerCase()}`}>
                            {flag}
                          </span>
                        ))
                      ) : (
                        <span className="text-tertiary">—</span>
                      )}
                    </div>
                  </td>

                  <td>
                    <div className="action-cell">
                      <button
                        className="btn btn--approve-sm"
                        onClick={() => onApprove(c.case_id)}
                      >
                        Approve
                      </button>

                      <button
                        className="btn btn--reject-sm"
                        onClick={() => onReject(c.case_id)}
                      >
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
