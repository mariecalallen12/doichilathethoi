import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ContactForm from '../../components/support/ContactForm.vue';

describe('ContactForm', () => {
  it('renders form fields correctly', () => {
    const wrapper = mount(ContactForm);
    
    expect(wrapper.find('input[type="text"]').exists()).toBe(true);
    expect(wrapper.find('input[type="email"]').exists()).toBe(true);
    expect(wrapper.find('textarea').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true);
  });

  it('validates required fields', async () => {
    const wrapper = mount(ContactForm);
    const form = wrapper.find('form');
    
    await form.trigger('submit.prevent');
    
    // HTML5 validation should prevent submission
    const nameInput = wrapper.find('input[type="text"]');
    expect(nameInput.element.validity.valid).toBe(false);
  });

  it('emits submit event with form data', async () => {
    const wrapper = mount(ContactForm);
    
    await wrapper.find('input[type="text"]').setValue('Test User');
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('select').setValue('general');
    await wrapper.find('textarea').setValue('Test message');
    
    await wrapper.find('form').trigger('submit.prevent');
    
    expect(wrapper.emitted('submit')).toBeTruthy();
    expect(wrapper.emitted('submit')[0][0]).toMatchObject({
      name: 'Test User',
      email: 'test@example.com',
      subject: 'general',
      message: 'Test message',
    });
  });

  it('resets form after successful submission', async () => {
    const wrapper = mount(ContactForm);
    
    await wrapper.find('input[type="text"]').setValue('Test User');
    await wrapper.find('input[type="email"]').setValue('test@example.com');
    await wrapper.find('textarea').setValue('Test message');
    
    // Mock successful submission
    const emit = vi.spyOn(wrapper.vm, '$emit');
    await wrapper.find('form').trigger('submit.prevent');
    
    // Form should be reset (values should be empty)
    expect(wrapper.find('input[type="text"]').element.value).toBe('');
  });
});

