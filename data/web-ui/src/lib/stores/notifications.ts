import { writable } from 'svelte/store';
import type { Notification, NotificationType } from '$lib/types';
import { generateId } from '$lib/utils';

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);

  return {
    subscribe,

    add(
      type: NotificationType,
      title: string,
      message: string,
      duration = 5000,
      action?: { label: string; href: string }
    ) {
      const notification: Notification = {
        id: generateId(),
        type,
        title,
        message,
        timestamp: new Date(),
        read: false,
        action,
      };

      update((notifications) => [notification, ...notifications]);

      if (duration > 0) {
        setTimeout(() => {
          this.remove(notification.id);
        }, duration);
      }

      return notification.id;
    },

    success(title: string, message: string, duration?: number) {
      return this.add('success', title, message, duration);
    },

    error(title: string, message: string, duration = 0) {
      return this.add('error', title, message, duration);
    },

    warning(title: string, message: string, duration?: number) {
      return this.add('warning', title, message, duration);
    },

    info(title: string, message: string, duration?: number) {
      return this.add('info', title, message, duration);
    },

    remove(id: string) {
      update((notifications) => notifications.filter((n) => n.id !== id));
    },

    markAsRead(id: string) {
      update((notifications) =>
        notifications.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    },

    clear() {
      update(() => []);
    },

    clearRead() {
      update((notifications) => notifications.filter((n) => !n.read));
    },
  };
}

export const notifications = createNotificationStore();
