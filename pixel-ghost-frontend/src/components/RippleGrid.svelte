<script>
  // —— Tunables (props) ——————————————————————————————
  export let spacing = 26;           // px between dots
  export let baseRadius = 1;       // base dot radius (px @ 1x DPR)
  export let amplitude = 2.4;        // extra radius when a ripple hits
  export let rippleSpeed = 240;      // px/sec ring expansion
  export let rippleWidth = 18;       // ring thickness (Gaussian sigma, px)
  export let fadeSeconds = 2.2;      // ripple lifetime
  export let color = 'rgba(118,255,3,0.9)'; // EVA neon; use any CSS color
  export let background = 'transparent';    // or e.g. '#0a0b12'
  export let auto = false;            // emit idle pulses automatically
  export let autoEveryMs = 1600;     // ms between idle pulses
  export let zIndex = 0;            // stack under content by default

  let container, canvas, ctx;
  let dpr = 1;
  let width = 0, height = 0;

  // Grid points (pixel coords)
  let points = [];

  // Active ripples: { x, y, t } where t = ms timestamp
  let ripples = [];

  let raf = 0, autoTimer = 0, lastEmit = 0;

  const now = () => performance.now();

  function resize() {
    if (!container || !canvas) return;
    dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1)); // cap at 2 for perf
    const w = container.clientWidth || window.innerWidth;
    const h = container.clientHeight || window.innerHeight;

    width = w; height = h;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';

    ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); // scale drawing by DPR

    buildGrid();
  }

  function buildGrid() {
    points = [];
    // start grid centered
    const cols = Math.ceil(width / spacing);
    const rows = Math.ceil(height / spacing);
    const offsetX = (width - (cols - 1) * spacing) / 2;
    const offsetY = (height - (rows - 1) * spacing) / 2;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        points.push({ x: offsetX + c * spacing, y: offsetY + r * spacing });
      }
    }
  }

  function addRipple(x, y, strength = 1) {
    const t = now();
    // Rate-limit frequent pointermove to ~10Hz
    if (t - lastEmit < 90 && strength < 1.1) return;
    lastEmit = t;
    ripples.push({ x, y, t, strength });
    // prune old ones
    const cutoff = t - fadeSeconds * 1000 * 1.2;
    riplesCleanup(cutoff);
  }

  function riplesCleanup(cutoff) {
    ripples = ripples.filter(r => r.t > cutoff);
  }

  function draw() {
    if (!ctx) return;
    const t = now();
    ctx.clearRect(0, 0, width, height);

    // Fill background if requested
    if (background !== 'transparent') {
      ctx.fillStyle = background;
      ctx.fillRect(0, 0, width, height);
    }

    ctx.fillStyle = color;

    // Precompute active ripple radii / weights
    const active = [];
    for (const r of ripples) {
      const age = (t - r.t) / 1000; // seconds
      if (age > fadeSeconds) continue;
      active.push({
        x: r.x, y: r.y,
        R: age * rippleSpeed,
        sigma: rippleWidth,
        w: Math.exp(-age / fadeSeconds) * (r.strength || 1) // exponential fade
      });
    }

    // Draw each dot
    for (const p of points) {
      let bump = 0;
      let alpha = 0;
      for (const r of active) {
        const dx = p.x - r.x, dy = p.y - r.y;
        const d = Math.hypot(dx, dy);
        // Gaussian ring around radius R
        const g = Math.exp(-((d - r.R) ** 2) / (2 * r.sigma ** 2)) * r.w;
        bump += g;
        alpha = Math.max(alpha, g); // brightest when ring passes
      }
      const rad = Math.max(0.2, baseRadius + amplitude * Math.min(1, bump));
      ctx.globalAlpha = 0.3 + 0.7 * Math.max(0, Math.min(1, alpha));
      ctx.beginPath();
      ctx.arc(p.x, p.y, rad, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    raf = requestAnimationFrame(draw);
  }

  function onPointer(e) {
    const rect = container.getBoundingClientRect();
    addRipple(e.clientX - rect.left, e.clientY - rect.top, 1);
  }
  function onClick(e) {
    const rect = container.getBoundingClientRect();
    addRipple(e.clientX - rect.left, e.clientY - rect.top, 1.6); // stronger pulse
  }

  function startAuto() {
    stopAuto();
    if (!auto) return;
    autoTimer = setInterval(() => {
      // center-ish pulse that drifts a bit
      const x = width * (0.45 + 0.1 * Math.sin(now() / 1200));
      const y = height * (0.45 + 0.1 * Math.cos(now() / 1400));
      addRipple(x, y, 0.9);
    }, autoEveryMs);
  }
  function stopAuto() {
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = 0;
  }

  import { onMount, onDestroy } from 'svelte';
  onMount(() => {
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(container);
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (!reduce.matches) {
      raf = requestAnimationFrame(draw);
      startAuto();
    } else {
      // Reduced motion: render static grid once
      draw();
    }
    window.addEventListener('pointermove', onPointer, { passive: true });
    window.addEventListener('click', onClick, { passive: true });

    return () => {
      ro.disconnect();
      cancelAnimationFrame(raf);
      stopAuto();
      window.removeEventListener('pointermove', onPointer);
      window.removeEventListener('click', onClick);
    };
  });
</script>

<style>
  .wrap {
    position: absolute; inset: 0;
    /* Let it sit as a background layer but still receive pointer events */
  }
  canvas { width: 100%; height: 100%; display: block; }
</style>

<div class="wrap" bind:this={container} style={`z-index:${zIndex};`}>
  <canvas bind:this={canvas} ></canvas>
</div>
