export default function VaapsiLogo({ size = 28, className = "" }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      style={{ display: 'inline-block', verticalAlign: 'middle', filter: 'drop-shadow(0px 2px 8px rgba(255, 106, 26, 0.4))' }}
    >
      {/* Outer returning arc (Vaapsi Loop) */}
      <path
        d="M 52 16 A 34 34 0 1 1 20 42"
        stroke="url(#vaapsi-grad)"
        strokeWidth="11"
        strokeLinecap="round"
      />
      {/* Return Arrow Head pointing back into the loop */}
      <path
        d="M 8 26 L 20 42 L 38 30"
        fill="none"
        stroke="#FF6A1A"
        strokeWidth="11"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Central Rupee Symbol (₹) */}
      <path
        d="M 44 40 L 58 40 M 44 50 L 56 50 M 46 40 L 46 66 M 46 50 C 56 50 58 58 46 66 M 52 58 L 60 68"
        stroke="#FFFFFF"
        strokeWidth="4.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <defs>
        <linearGradient id="vaapsi-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF6A1A" />
          <stop offset="100%" stopColor="#FF9E66" />
        </linearGradient>
      </defs>
    </svg>
  );
}
