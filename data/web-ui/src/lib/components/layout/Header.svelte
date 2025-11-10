<script lang="ts">
  import { auth, currentUser } from '$lib/stores/auth';
  import { theme } from '$lib/stores/theme';
  import { notifications as notificationStore } from '$lib/stores/notifications';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { getInitials, stringToColor } from '$lib/utils';

  let showUserMenu = false;
  let showNotifications = false;

  $: unreadCount = $notificationStore.filter((n) => !n.read).length;
  $: userInitials = $currentUser ? getInitials($currentUser.username) : '?';
  $: userColor = $currentUser ? stringToColor($currentUser.username) : '#ccc';

  function toggleTheme() {
    theme.toggle();
  }

  async function handleLogout() {
    await auth.logout();
    window.location.href = '/login';
  }
</script>

<header class="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div class="container mx-auto px-4">
    <div class="flex h-16 items-center justify-between">
      <!-- Logo and Brand -->
      <div class="flex items-center gap-6">
        <a href="/" class="flex items-center gap-2 font-bold text-xl">
          <svg class="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
          </svg>
          <span class="hidden sm:inline">MaiMaiL</span>
        </a>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-1">
          <Button variant="ghost" size="sm" href="/">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
            Dashboard
          </Button>

          <Button variant="ghost" size="sm" href="/mailboxes">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
            </svg>
            Mailboxes
          </Button>

          <Button variant="ghost" size="sm" href="/llm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            AI Intelligence
          </Button>

          <Button variant="ghost" size="sm" href="/quarantine">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            Quarantine
          </Button>
        </nav>
      </div>

      <!-- Right side actions -->
      <div class="flex items-center gap-2">
        <!-- Theme Toggle -->
        <Button variant="ghost" size="sm" on:click={toggleTheme}>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
          </svg>
        </Button>

        <!-- Notifications -->
        <div class="relative">
          <Button variant="ghost" size="sm" on:click={() => (showNotifications = !showNotifications)}>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
            </svg>
            {#if unreadCount > 0}
              <span class="absolute -top-1 -right-1 w-5 h-5 bg-danger-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            {/if}
          </Button>

          {#if showNotifications}
            <div class="absolute right-0 mt-2 w-80 bg-background border rounded-lg shadow-lg max-h-96 overflow-auto">
              <div class="p-4 border-b flex items-center justify-between">
                <h3 class="font-semibold">Notifications</h3>
                {#if $notificationStore.length > 0}
                  <button
                    on:click={() => notificationStore.clear()}
                    class="text-xs text-muted-foreground hover:text-foreground"
                  >
                    Clear all
                  </button>
                {/if}
              </div>
              <div class="divide-y">
                {#if $notificationStore.length === 0}
                  <div class="p-8 text-center text-muted-foreground">
                    <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                    <p class="text-sm">No notifications</p>
                  </div>
                {:else}
                  {#each $notificationStore as notification (notification.id)}
                    <div class="p-3 hover:bg-secondary cursor-pointer" class:bg-secondary={!notification.read}>
                      <p class="text-sm font-medium">{notification.title}</p>
                      <p class="text-xs text-muted-foreground mt-1">{notification.message}</p>
                    </div>
                  {/each}
                {/if}
              </div>
            </div>
          {/if}
        </div>

        <!-- User Menu -->
        <div class="relative">
          <button
            on:click={() => (showUserMenu = !showUserMenu)}
            class="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
              style="background-color: {userColor}"
            >
              {userInitials}
            </div>
            <span class="hidden sm:inline text-sm font-medium">{$currentUser?.username}</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>

          {#if showUserMenu}
            <div class="absolute right-0 mt-2 w-48 bg-background border rounded-lg shadow-lg py-1">
              <div class="px-4 py-2 border-b">
                <p class="text-sm font-medium">{$currentUser?.username}</p>
                <p class="text-xs text-muted-foreground capitalize">{$currentUser?.role}</p>
              </div>

              <a href="/settings" class="block px-4 py-2 text-sm hover:bg-secondary">
                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                Settings
              </a>

              <button
                on:click={handleLogout}
                class="w-full text-left px-4 py-2 text-sm hover:bg-secondary text-danger-600"
              >
                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                </svg>
                Logout
              </button>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</header>
