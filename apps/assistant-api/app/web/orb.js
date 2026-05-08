// 3D Canvas Orb Engine

const OrbVisualizer = (function() {
  let canvas, ctx;
  let points = [];
  let width, height;
  let animationId;
  let time = 0;
  
  // State variables
  let orbState = 'IDLE'; // IDLE, LISTENING, RECORDING, PROCESSING, SPEAKING
  let audioData = new Uint8Array(0);
  
  const NUM_POINTS = 350;
  const SPHERE_RADIUS = 100;
  const FOV = 250;
  const ROTATION_SPEED_Y = 0.003;
  const ROTATION_SPEED_X = 0.001;
  let rotX = 0;
  let rotY = 0;

  function init(canvasId) {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    ctx = canvas.getContext('2d');
    
    // Set internal resolution higher for crispness
    const size = 300;
    canvas.width = size * window.devicePixelRatio;
    canvas.height = size * window.devicePixelRatio;
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';
    
    width = canvas.width;
    height = canvas.height;
    
    generatePoints();
    animate();
  }

  function generatePoints() {
    points = [];
    const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle
    
    for (let i = 0; i < NUM_POINTS; i++) {
      const y = 1 - (i / (NUM_POINTS - 1)) * 2; // y goes from 1 to -1
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;
      
      const x = Math.cos(theta) * radiusAtY;
      const z = Math.sin(theta) * radiusAtY;
      
      points.push({
        baseX: x,
        baseY: y,
        baseZ: z,
        currentRadius: SPHERE_RADIUS
      });
    }
  }

  function render() {
    ctx.clearRect(0, 0, width, height);
    
    // Glow settings
    ctx.globalCompositeOperation = 'lighter';
    
    time += 0.05;
    rotY += ROTATION_SPEED_Y;
    rotX += ROTATION_SPEED_X;
    
    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);
    
    const projectedPoints = [];

    // Calculate dynamic radius and project 3D to 2D
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      
      // Calculate Displacement
      let displacement = 0;
      
      if (orbState === 'LISTENING' || orbState === 'RECORDING') {
        // Map audio data to points
        if (audioData.length > 0) {
          // Map point index to frequency bin
          const bin = Math.floor((i / NUM_POINTS) * (audioData.length * 0.5));
          const freq = audioData[bin] || 0;
          displacement = (freq / 255) * 35; // Spike up to 35px
        } else {
           // Gentle breathing if no audio yet
           displacement = Math.sin(time + p.baseY * 5) * 5;
        }
      } else if (orbState === 'PROCESSING' || orbState === 'busy') {
        // High frequency noise
        displacement = Math.sin(time * 3 + p.baseX * 10) * Math.cos(time * 2 + p.baseZ * 10) * 15;
      } else if (orbState === 'SPEAKING' || orbState === 'active') {
        // Smooth large pulses
        displacement = Math.sin(time * 2 - p.baseY * 3) * 20;
      } else {
        // IDLE: gentle breathing
        displacement = Math.sin(time + p.baseY * 3 + p.baseX * 2) * 8;
      }

      const r = SPHERE_RADIUS + displacement;
      const x = p.baseX * r;
      const y = p.baseY * r;
      const z = p.baseZ * r;

      // Rotate Y
      const x1 = x * cosY - z * sinY;
      const z1 = z * cosY + x * sinY;
      
      // Rotate X
      const y2 = y * cosX - z1 * sinX;
      const z2 = z1 * cosX + y * sinX;
      
      // Perspective Projection
      const scale = FOV / (FOV + z2 + SPHERE_RADIUS * 1.5);
      const projX = (width / 2) + x1 * scale * (width / 300);
      const projY = (height / 2) + y2 * scale * (height / 300);
      
      projectedPoints.push({
        x: projX,
        y: projY,
        z: z2,
        scale: scale,
        baseY: p.baseY, // Keep for coloring
        disp: displacement
      });
    }

    // Sort points by Z to draw back to front (Painter's algorithm)
    projectedPoints.sort((a, b) => b.z - a.z);

    // Draw lines between close points (Wireframe)
    // To keep it performant, we only draw lines for a subset or based on distance
    // We'll draw dots with strong glow
    for (let i = 0; i < projectedPoints.length; i++) {
      const p = projectedPoints[i];
      
      // Fade out points in the back
      const depthAlpha = Math.max(0.1, Math.min(1, (p.z + SPHERE_RADIUS * 1.5) / (SPHERE_RADIUS * 3)));
      
      // Color based on height (baseY) and state
      let r, g, b;
      if (orbState === 'PROCESSING' || orbState === 'busy') {
        r = 0; g = 255; b = 255; // Cyan Processing
      } else if (orbState === 'LISTENING' || orbState === 'RECORDING') {
        r = 255; g = Math.max(0, 100 - p.disp*5); b = 255; // Pink/Purple Mic
      } else if (orbState === 'SPEAKING' || orbState === 'active') {
        r = 0; g = 150 + p.disp*5; b = 255; // Bright blue pulse
      } else {
        // Default gradient (Cyan to Purple)
        const t = (p.baseY + 1) / 2; // 0 to 1
        r = Math.floor(t * 192);     // 0 -> 192 (0 to C0)
        g = Math.floor((1 - t) * 136); // 136 -> 0 (88 to 0)
        b = 255;                       // FF
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(0.5, p.scale * 2.5), 0, Math.PI * 2);
      
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${depthAlpha})`;
      
      // Add neon glow
      ctx.shadowBlur = 10 * p.scale;
      ctx.shadowColor = `rgba(${r}, ${g}, ${b}, ${depthAlpha * 0.8})`;
      
      ctx.fill();
    }
  }

  function animate() {
    render();
    animationId = requestAnimationFrame(animate);
  }

  return {
    init,
    setAudioData: (data) => {
      audioData = data;
    },
    setState: (newState) => {
      orbState = newState;
    }
  };
})();

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  OrbVisualizer.init('orbCanvas');
});
