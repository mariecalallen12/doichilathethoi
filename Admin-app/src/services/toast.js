// Toast Notification Service
class ToastService {
  constructor() {
    this.toasts = [];
    this.listeners = [];
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify(toasts) {
    this.listeners.forEach(listener => listener(toasts));
  }

  addToast(toast) {
    const id = Date.now() + Math.random();
    const newToast = {
      id,
      ...toast,
      duration: toast.duration || 5000,
    };

    this.toasts.push(newToast);
    this.notify([...this.toasts]);

    // Auto dismiss
    if (newToast.duration > 0) {
      setTimeout(() => {
        this.removeToast(id);
      }, newToast.duration);
    }

    return id;
  }

  removeToast(id) {
    this.toasts = this.toasts.filter(t => t.id !== id);
    this.notify([...this.toasts]);
  }

  success(message, duration = 5000) {
    return this.addToast({
      type: 'success',
      message,
      duration,
    });
  }

  error(message, duration = 5000) {
    return this.addToast({
      type: 'error',
      message,
      duration,
    });
  }

  warning(message, duration = 5000) {
    return this.addToast({
      type: 'warning',
      message,
      duration,
    });
  }

  info(message, duration = 5000) {
    return this.addToast({
      type: 'info',
      message,
      duration,
    });
  }

  clear() {
    this.toasts = [];
    this.notify([]);
  }
}

export default new ToastService();

