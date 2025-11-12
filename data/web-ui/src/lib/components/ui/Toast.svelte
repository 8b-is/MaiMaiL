<script lang="ts">
  import { notifications } from '$lib/stores/notifications';
  import { fade, fly } from 'svelte/transition';
  import { cn } from '$lib/utils';

  const icons = {
    success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`,
    error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`,
    warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`,
    info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
  };

  const colors = {
    success: 'bg-success-50 text-success-900 border-success-200 dark:bg-success-900/20 dark:text-success-100 dark:border-success-800',
    error: 'bg-danger-50 text-danger-900 border-danger-200 dark:bg-danger-900/20 dark:text-danger-100 dark:border-danger-800',
    warning: 'bg-warning-50 text-warning-900 border-warning-200 dark:bg-warning-900/20 dark:text-warning-100 dark:border-warning-800',
    info: 'bg-primary-50 text-primary-900 border-primary-200 dark:bg-primary-900/20 dark:text-primary-100 dark:border-primary-800',
  };
</script>

<div class="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
  {#each $notifications.slice(0, 3) as notification (notification.id)}
    <div
      transition:fly={{ x: 300, duration: 300 }}
      class={cn(
        'rounded-lg border p-4 shadow-lg backdrop-blur-sm',
        colors[notification.type]
      )}
    >
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          {@html icons[notification.type]}
        </div>

        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold">{notification.title}</p>
          <p class="text-sm mt-1 opacity-90">{notification.message}</p>

          {#if notification.action}
            <a
              href={notification.action.href}
              class="text-sm font-medium underline mt-2 inline-block hover:opacity-80"
            >
              {notification.action.label}
            </a>
          {/if}
        </div>

        <button
          on:click={() => notifications.remove(notification.id)}
          class="flex-shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
  {/each}
</div>
