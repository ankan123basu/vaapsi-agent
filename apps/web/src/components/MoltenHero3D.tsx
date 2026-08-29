import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Icosahedron, Float } from '@react-three/drei';
import * as THREE from 'three';
import MoltenMetal from './MoltenMetal';
import './MoltenHero3D.css';

function MoltenBlob() {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<any>(null);

  const targetMouse = useRef({ x: 0, y: 0 });
  const currentMouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      targetMouse.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      targetMouse.current.y = -(e.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useFrame((_, delta) => {
    currentMouse.current.x += (targetMouse.current.x - currentMouse.current.x) * 0.06;
    currentMouse.current.y += (targetMouse.current.y - currentMouse.current.y) * 0.06;

    if (meshRef.current) {
      // Continuous ambient rotation + subtle cursor tilt (mouseStrength <= 0.3)
      meshRef.current.rotation.y += delta * 0.3;
      meshRef.current.rotation.x = currentMouse.current.y * 0.22;
      meshRef.current.rotation.z = currentMouse.current.x * 0.22;
    }

    if (materialRef.current) {
      const dist = 0.42 + Math.abs(currentMouse.current.x) * 0.12;
      materialRef.current.distort = THREE.MathUtils.lerp(materialRef.current.distort, dist, 0.05);
    }
  });

  return (
    <Float speed={1.8} rotationIntensity={0.35} floatIntensity={0.5}>
      {/* Positioned cleanly inside hero bounds [1.5, 0.05, 0] to prevent overflow bleeding */}
      <Icosahedron ref={meshRef} args={[1.65, 64]} position={[1.5, 0.05, 0]}>
        <MeshDistortMaterial
          ref={materialRef}
          color="#140A06"
          emissive="#FF4500"
          emissiveIntensity={1.1}
          roughness={0.08}
          metalness={0.98}
          clearcoat={1.0}
          clearcoatRoughness={0.04}
          distort={0.42}
          speed={2.5}
        />
      </Icosahedron>
    </Float>
  );
}

export default function MoltenHero3D() {
  const prefersReducedMotion = useMemo(() => {
    return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  return (
    <div className="molten-hero-3d-wrapper">
      {/* Secondary 2D background atmosphere shader layer */}
      <MoltenMetal
        color1="#1A0A04"
        color2="#7A2D0E"
        color3="#FFB066"
        colorMode="ember"
        speed={0.2}
        scale={3.5}
        glow={1.4}
        brightness={1.1}
        grain={true}
        grainIntensity={0.03}
        mouseInteraction={false}
        opacity={0.65}
      />

      {/* Primary 3D R3F Depth Scene */}
      {!prefersReducedMotion && (
        <div className="r3f-canvas-container">
          <Canvas
            camera={{ position: [0, 0, 5.2], fov: 45 }}
            gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
          >
            {/* Multi-point PBR specular lighting for high-gloss liquid metal highlights */}
            <ambientLight intensity={0.35} />
            <pointLight position={[5, 4, 5]} color="#FFB066" intensity={4.5} />
            <pointLight position={[-4, 2, -2]} color="#FF4500" intensity={3.0} />
            <spotLight position={[0, 6, 2]} color="#FFA500" intensity={3.5} angle={0.7} penumbra={0.8} />
            <directionalLight position={[0, -3, 3]} color="#B24A1D" intensity={1.8} />

            <MoltenBlob />
          </Canvas>
        </div>
      )}
    </div>
  );
}
