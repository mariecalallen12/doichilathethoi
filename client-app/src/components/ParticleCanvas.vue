<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const canvasRef = ref(null);
let ctx;
const particles = [];
let frame;

const createParticles = (width, height, count = 40) => {
  particles.length = 0;
  for (let i = 0; i < count; i += 1) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 2 + 1.2,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      alpha: Math.random() * 0.6 + 0.2,
    });
  }
};

const draw = () => {
  if (!ctx || !canvasRef.value) return;
  const { width, height } = canvasRef.value;
  ctx.clearRect(0, 0, width, height);
  particles.forEach((p) => {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0 || p.x > width) p.vx *= -1;
    if (p.y < 0 || p.y > height) p.vy *= -1;
    ctx.beginPath();
    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3);
    gradient.addColorStop(0, `rgba(124, 58, 237, ${p.alpha})`);
    gradient.addColorStop(1, "transparent");
    ctx.fillStyle = gradient;
    ctx.arc(p.x, p.y, p.r * 2, 0, Math.PI * 2);
    ctx.fill();
  });
  frame = requestAnimationFrame(draw);
};

const resize = () => {
  if (!canvasRef.value) return;
  const { offsetWidth, offsetHeight } = canvasRef.value.parentElement;
  canvasRef.value.width = offsetWidth;
  canvasRef.value.height = offsetHeight;
  createParticles(offsetWidth, offsetHeight);
};

onMounted(() => {
  ctx = canvasRef.value.getContext("2d");
  resize();
  window.addEventListener("resize", resize);
  frame = requestAnimationFrame(draw);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  cancelAnimationFrame(frame);
});
</script>

<template>
  <canvas ref="canvasRef" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
</template>

