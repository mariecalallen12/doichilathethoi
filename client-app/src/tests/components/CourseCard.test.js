import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CourseCard from '../../components/education/CourseCard.vue';
import { createPinia, setActivePinia } from 'pinia';

describe('CourseCard', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('renders video course correctly', () => {
    const course = {
      id: 1,
      title: 'Test Video',
      description: 'Test Description',
      thumbnail: 'test.jpg',
      duration: 3600,
      views: 1000,
      rating: 4.5,
    };

    const wrapper = mount(CourseCard, {
      props: {
        course,
        type: 'video',
      },
    });

    expect(wrapper.text()).toContain('Test Video');
    expect(wrapper.text()).toContain('Test Description');
  });

  it('renders ebook course correctly', () => {
    const course = {
      id: 1,
      title: 'Test Ebook',
      description: 'Test Description',
      pages: 100,
    };

    const wrapper = mount(CourseCard, {
      props: {
        course,
        type: 'ebook',
      },
    });

    expect(wrapper.text()).toContain('Test Ebook');
    expect(wrapper.text()).toContain('100 trang');
  });

  it('emits click event when clicked', async () => {
    const course = {
      id: 1,
      title: 'Test Course',
      description: 'Test Description',
    };

    const wrapper = mount(CourseCard, {
      props: {
        course,
        type: 'video',
      },
    });

    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});

