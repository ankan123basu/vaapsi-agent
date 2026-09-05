import { useMemo, useRef, Component, type ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Box, Edges, Line } from '@react-three/drei';
import * as THREE from 'three';

interface Props {
  trail: { node_name: string }[];
  activeIndex: number;
  onSelectNode?: (index: number) => void;
}

class ThreeErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return null; // Gracefully degrade if WebGL or canvas fails
    }
    return this.props.children;
  }
}

const NODE_COLORS: Record<string, string> = {
  detector: '#161412',
  diagnoser: '#161412',
  strategist: '#161412',
  guardrail_gate: '#B8860B',
  executor: '#161412',
  auditor: '#1E7A4C',
  reporter: '#161412',
  human_approval: '#FF6A1A',
};

function ConnectionLine({ start, end, active }: { start: [number, number, number]; end: [number, number, number]; active: boolean }) {
  const lineRef = useRef<any>(null);

  useFrame(({ clock }) => {
    if (lineRef.current?.material) {
      lineRef.current.material.dashOffset = -clock.getElapsedTime() * 2;
    }
  });

  return (
    <Line
      ref={lineRef}
      points={[start, end]}
      color={active ? '#FF6A1A' : '#333333'}
      lineWidth={active ? 2.5 : 1}
      dashed={active}
      dashScale={5}
      dashSize={0.5}
    />
  );
}

function LedgerBlock({
  position,
  active,
  color,
  onClick,
}: {
  position: [number, number, number];
  active: boolean;
  color: string;
  onClick?: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshPhysicalMaterial>(null);

  const targetScale = active ? 1.25 : 1.0;
  const targetY = active ? position[1] + 0.6 : position[1];
  const targetRotY = active ? Math.PI * 0.15 : 0;

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 8);
      meshRef.current.position.y = THREE.MathUtils.lerp(meshRef.current.position.y, targetY, delta * 8);
      meshRef.current.rotation.y = THREE.MathUtils.lerp(meshRef.current.rotation.y, targetRotY, delta * 6);
    }

    if (materialRef.current) {
      const targetEmissive = active ? new THREE.Color('#FF6A1A') : new THREE.Color(0x000000);
      materialRef.current.emissive.lerp(targetEmissive, delta * 6);
      materialRef.current.emissiveIntensity = THREE.MathUtils.lerp(
        materialRef.current.emissiveIntensity,
        active ? 1.5 : 0,
        delta * 6
      );
    }
  });

  return (
    <Box
      ref={meshRef}
      args={[1.1, 0.45, 1.1]}
      position={position}
      castShadow
      receiveShadow
      onClick={onClick}
      onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { document.body.style.cursor = 'auto'; }}
    >
      <meshPhysicalMaterial
        ref={materialRef}
        color={active ? '#FF6A1A' : color}
        roughness={active ? 0.1 : 0.4}
        metalness={active ? 0.9 : 0.2}
        clearcoat={active ? 1 : 0.3}
        clearcoatRoughness={0.1}
      />
      <Edges scale={1.01} threshold={15} color={active ? '#FFB066' : '#444444'} />
    </Box>
  );
}

export default function TraceLedgerBlocks({ trail, activeIndex, onSelectNode }: Props) {
  const prefersReducedMotion = useMemo(() => {
    return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  if (prefersReducedMotion || !trail || trail.length === 0) {
    return null;
  }

  const blockSpacing = 1.6;
  const startX = -((trail.length - 1) * blockSpacing) / 2;

  return (
    <ThreeErrorBoundary>
      <div style={{ width: '100%', height: '140px', marginBottom: '1.25rem', background: '#0A0A0A', border: '2px solid #0A0A0A', boxShadow: '6px 6px 0px #0A0A0A', overflow: 'hidden' }}>
        <Canvas camera={{ position: [0, 4.5, 6.5], fov: 40 }} gl={{ antialias: true, alpha: true }}>
          <ambientLight intensity={0.8} />
          <directionalLight position={[5, 10, 5]} intensity={2.0} castShadow />
          <pointLight position={[-5, -5, -5]} intensity={0.5} />

          {trail.map((entry, i) => {
            const posX = startX + i * blockSpacing;
            const pos: [number, number, number] = [posX, 0, 0];
            const nextPos: [number, number, number] = [startX + (i + 1) * blockSpacing, 0, 0];

            return (
              <group key={`node-block-${entry.node_name}-${i}`}>
                <LedgerBlock
                  position={pos}
                  active={activeIndex === i}
                  color={NODE_COLORS[entry.node_name] || '#161412'}
                  onClick={() => onSelectNode?.(i)}
                />

                {i < trail.length - 1 && (
                  <ConnectionLine start={pos} end={nextPos} active={activeIndex >= i} />
                )}
              </group>
            );
          })}
        </Canvas>
      </div>
    </ThreeErrorBoundary>
  );
}
