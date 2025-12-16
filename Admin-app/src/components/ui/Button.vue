<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'warning', 'outline', 'ghost'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  disabled: Boolean,
  loading: Boolean,
  fullWidth: Boolean,
  icon: String,
});

const variantClasses = {
  primary: 'bg-gradient-button text-white hover:opacity-90',
  secondary: 'bg-white/10 text-white border border-white/20 hover:bg-white/20',
  danger: 'bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30',
  warning: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 hover:bg-yellow-500/30',
  outline: 'bg-transparent text-white border border-white/30 hover:bg-white/10',
  ghost: 'bg-transparent text-white hover:bg-white/10',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};
</script>

<template>
  <button
    :class="[
      'inline-flex items-center justify-center rounded-lg font-semibold transition-all',
      'focus:outline-none focus:ring-2 focus:ring-primary/50',
      variantClasses[variant],
      sizeClasses[size],
      fullWidth && 'w-full',
      (disabled || loading) && 'opacity-50 cursor-not-allowed',
    ]"
    :disabled="disabled || loading"
  >
    <i v-if="loading" class="fas fa-spinner fa-spin mr-2"></i>
    <i v-else-if="icon" :class="[icon, 'mr-2']"></i>
    <slot />
  </button>
</template>

