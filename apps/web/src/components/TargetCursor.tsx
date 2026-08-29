import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import './TargetCursor.css';

interface Props {
  targetSelector?: string;
  cursorColor?: string;
}

export default function TargetCursor({
  targetSelector = '.hero-cursor-target',
  cursorColor = '#FFB066',
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);
  const bracketsRef = useRef<HTMLDivElement>(null);
  const [isHoveredTarget, setIsHoveredTarget] = useState(false);

  useEffect(() => {
    // 1. Mobile check — do not render custom cursor on touch devices
    const isMobile =
      window.matchMedia('(pointer: coarse)').matches ||
      window.innerWidth < 768 ||
      'ontouchstart' in window;

    if (isMobile) {
      document.body.style.cursor = '';
      return;
    }

    // 2. Hide default OS cursor while TargetCursor is mounted in Hero
    document.body.style.cursor = 'none';

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let currentTargetEl: HTMLElement | null = null;

    const onMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      const target = (e.target as HTMLElement)?.closest(targetSelector) as HTMLElement | null;

      if (target) {
        if (currentTargetEl !== target) {
          currentTargetEl = target;
          setIsHoveredTarget(true);
        }
        const rect = target.getBoundingClientRect();
        // Snap brackets around target element
        gsap.to(containerRef.current, {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
          duration: 0.25,
          ease: 'power2.out',
        });
        gsap.to(bracketsRef.current, {
          width: rect.width + 16,
          height: rect.height + 16,
          rotation: 0,
          duration: 0.3,
          ease: 'back.out(1.7)',
        });
        gsap.to(dotRef.current, {
          scale: 0,
          duration: 0.15,
        });
      } else {
        if (currentTargetEl !== null) {
          currentTargetEl = null;
          setIsHoveredTarget(false);
        }
        // Free float with cursor
        gsap.to(containerRef.current, {
          x: mouseX,
          y: mouseY,
          duration: 0.15,
          ease: 'power1.out',
        });
        gsap.to(bracketsRef.current, {
          width: 36,
          height: 36,
          duration: 0.25,
          ease: 'power2.out',
        });
        gsap.to(dotRef.current, {
          scale: 1,
          duration: 0.15,
        });
      }
    };

    // Spin animation when floating
    const spinTween = gsap.to(bracketsRef.current, {
      rotation: 360,
      duration: 8,
      repeat: -1,
      ease: 'none',
    });

    window.addEventListener('mousemove', onMouseMove, { passive: true });

    // Cleanup when component unmounts (e.g. when hero leaves viewport or user scrolls)
    return () => {
      document.body.style.cursor = '';
      window.removeEventListener('mousemove', onMouseMove);
      spinTween.kill();
    };
  }, [targetSelector]);

  return (
    <div
      ref={containerRef}
      className={`target-cursor-wrapper ${isHoveredTarget ? 'target-cursor-wrapper--snapped' : ''}`}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        pointerEvents: 'none',
        zIndex: 9999,
        transform: 'translate(-50%, -50%)',
      }}
    >
      {/* Center Dot */}
      <div
        ref={dotRef}
        className="target-cursor-dot"
        style={{ backgroundColor: cursorColor }}
      />

      {/* Target Corner Brackets */}
      <div
        ref={bracketsRef}
        className="target-cursor-brackets"
        style={{ borderColor: cursorColor }}
      >
        <span className="bracket bracket-tl" style={{ borderColor: cursorColor }} />
        <span className="bracket bracket-tr" style={{ borderColor: cursorColor }} />
        <span className="bracket bracket-bl" style={{ borderColor: cursorColor }} />
        <span className="bracket bracket-br" style={{ borderColor: cursorColor }} />
      </div>
    </div>
  );
}
