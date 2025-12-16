import { describe, it, expect, beforeEach } from 'vitest';
import { createRouter, createWebHistory } from 'vue-router';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';

describe('Router', () => {
  let router;
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    setActivePinia(pinia);
    
    // Create a minimal router for testing
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          name: 'Home',
          component: { template: '<div>Home</div>' },
        },
        {
          path: '/market',
          name: 'Market',
          component: { template: '<div>Market</div>' },
        },
        {
          path: '/education',
          name: 'Education',
          component: { template: '<div>Education</div>' },
        },
      ],
    });
  });

  it('navigates to home route', async () => {
    await router.push('/');
    expect(router.currentRoute.value.name).toBe('Home');
  });

  it('navigates to market route', async () => {
    await router.push('/market');
    expect(router.currentRoute.value.name).toBe('Market');
  });

  it('navigates to education route', async () => {
    await router.push('/education');
    expect(router.currentRoute.value.name).toBe('Education');
  });
});

