<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const canvasRef = ref(null);
let ctx;
const particles = [];
let frame;
const isError = ref(false);

const createParticles = (width, height, count = 50) => {
  try {
    particles.length = 0;
    for (let i = 0; i < count; i += 1) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 1.5 + 0.8,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        alpha: Math.random() * 0.4 + 0.2,
      });
    }
  } catch (error) {
    console.error('Error creating particles:', error);
    isError.value = true;
  }
};

const draw = () => {
  try {
    if (!ctx || !canvasRef.value || isError.value) return;
    const { width, height } = canvasRef.value;
    if (!width || !height) return;
    
    ctx.clearRect(0, 0, width, height);
    
    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;
      
      ctx.beginPath();
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 4);
      gradient.addColorStop(0, `rgba(59, 130, 246, ${p.alpha})`);
      gradient.addColorStop(0.5, `rgba(139, 92, 246, ${p.alpha * 0.5})`);
      gradient.addColorStop(1, "transparent");
      ctx.fillStyle = gradient;
      ctx.arc(p.x, p.y, p.r * 3, 0, Math.PI * 2);
      ctx.fill();
    });
    
    frame = requestAnimationFrame(draw);
  } catch (error) {
    console.error('Error drawing particles:', error);
    isError.value = true;
    if (frame) {
      cancelAnimationFrame(frame);
    }
  }
};

const resize = () => {
  try {
    if (!canvasRef.value || !canvasRef.value.parentElement) return;
    const { offsetWidth, offsetHeight } = canvasRef.value.parentElement;
    if (offsetWidth > 0 && offsetHeight > 0) {
      canvasRef.value.width = offsetWidth;
      canvasRef.value.height = offsetHeight;
      createParticles(offsetWidth, offsetHeight);
    }
  } catch (error) {
    console.error('Error resizing canvas:', error);
    isError.value = true;
  }
};

onMounted(() => {
  try {
    if (!canvasRef.value) {
      console.warn('Canvas ref not available');
      isError.value = true;
      return;
    }
    
    ctx = canvasRef.value.getContext("2d");
    if (!ctx) {
      console.warn('Could not get 2d context');
      isError.value = true;
      return;
    }
    
    resize();
    window.addEventListener("resize", resize);
    frame = requestAnimationFrame(draw);
  } catch (error) {
    console.error('Error initializing ParticleBackground:', error);
    isError.value = true;
  }
});

onBeforeUnmount(() => {
  try {
    window.removeEventListener("resize", resize);
    if (frame) {
      cancelAnimationFrame(frame);
    }
  } catch (error) {
    console.error('Error cleaning up ParticleBackground:', error);
  }
});
</script>

<template>
  <canvas ref="canvasRef" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
</template>

