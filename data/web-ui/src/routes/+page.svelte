<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { notifications } from '$lib/stores/notifications';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import StatsCards from '$lib/components/llm/StatsCards.svelte';
  import HealthStatus from '$lib/components/llm/HealthStatus.svelte';
  import type { DashboardStats, LlmHealth, LlmStats } from '$lib/types';
  import { formatBytes, formatNumber } from '$lib/utils';

  let loading = true;
  let dashboardStats: DashboardStats | null = null;
  let llmHealth: LlmHealth | null = null;
  let llmStats: LlmStats | null = null;
  let refreshInterval: number;

  async function loadDashboard() {
    try {
      loading = true;

      // Load all data in parallel
      const [stats, health, llm] = await Promise.allSettled([
        api.getDashboardStats(),
        api.getLlmHealth(),
        api.getLlmStats(),
      ]);

      if (stats.status === 'fulfilled') {
        dashboardStats = stats.value;
      }

      if (health.status === 'fulfilled') {
        llmHealth = health.value;

        // Show notification if system is degraded
        if (health.value.status === 'degraded') {
          notifications.warning('System Degraded', 'Some LLM components are not functioning properly');
        } else if (health.value.status === 'error') {
          notifications.error('System Error', 'LLM system is currently unavailable');
        }
      }

      if (llm.status === 'fulfilled') {
        llmStats = llm.value;
      }
    } catch (error: any) {
      notifications.error('Failed to load dashboard', error.message);
    } finally {
      loading = false;
    }
  }

  function setupAutoRefresh() {
    // Refresh every 30 seconds
    refreshInterval = setInterval(loadDashboard, 30000);
  }

  onMount(() => {
    loadDashboard();
    setupAutoRefresh();

    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  });
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold">Dashboard</h1>
      <p class="text-muted-foreground mt-1">Welcome to your AI-powered email management system</p>
    </div>
    <Button on:click={loadDashboard} disabled={loading}>
      <svg class="w-4 h-4" class:animate-spin={loading} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
      </svg>
      Refresh
    </Button>
  </div>

  {#if loading && !dashboardStats}
    <!-- Loading State -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {#each Array(6) as _}
        <Card class="h-32 skeleton"></Card>
      {/each}
    </div>
  {:else if dashboardStats}
    <!-- System Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Mailboxes -->
      <Card class="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-medium opacity-90">Mailboxes</h3>
            <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
            </svg>
          </div>
          <p class="text-3xl font-bold">{formatNumber(dashboardStats.mailboxes.total)}</p>
          <p class="text-xs opacity-75">{dashboardStats.mailboxes.active} active</p>
        </div>
      </Card>

      <!-- Domains -->
      <Card class="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-medium opacity-90">Domains</h3>
            <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
            </svg>
          </div>
          <p class="text-3xl font-bold">{formatNumber(dashboardStats.domains.total)}</p>
          <p class="text-xs opacity-75">{dashboardStats.domains.active} active</p>
        </div>
      </Card>

      <!-- Storage Usage -->
      <Card class="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-medium opacity-90">Storage</h3>
            <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
            </svg>
          </div>
          <p class="text-3xl font-bold">{formatBytes(dashboardStats.mailboxes.quota_used)}</p>
          <p class="text-xs opacity-75">of {formatBytes(dashboardStats.mailboxes.quota_total)}</p>
        </div>
      </Card>

      <!-- Spam Filtered -->
      <Card class="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-medium opacity-90">Spam Filtered</h3>
            <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
            </svg>
          </div>
          <p class="text-3xl font-bold">{formatNumber(dashboardStats.spam_stats.quarantined)}</p>
          <p class="text-xs opacity-75">{dashboardStats.spam_stats.rejected} rejected</p>
        </div>
      </Card>
    </div>

    <!-- LLM Section -->
    <div class="space-y-4">
      <div class="flex items-center gap-2">
        <svg class="w-6 h-6 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <h2 class="text-2xl font-bold">AI Intelligence</h2>
        {#if llmHealth}
          <Badge variant={llmHealth.status === 'healthy' ? 'success' : llmHealth.status === 'degraded' ? 'warning' : 'danger'}>
            {llmHealth.status}
          </Badge>
        {/if}
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- LLM Health -->
        {#if llmHealth}
          <div class="lg:col-span-1">
            <HealthStatus health={llmHealth} />
          </div>
        {/if}

        <!-- LLM Stats -->
        {#if llmStats}
          <div class="lg:col-span-2">
            <StatsCards stats={llmStats} />
          </div>
        {/if}
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Recent Analyses -->
      {#if llmStats && llmStats.recent_analyses.length > 0}
        <Card>
          <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Recent AI Analyses
          </h3>
          <div class="space-y-3">
            {#each llmStats.recent_analyses.slice(0, 5) as analysis}
              <div class="flex items-center justify-between p-3 bg-secondary rounded-lg">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{analysis.mailbox}</p>
                  <p class="text-xs text-muted-foreground">
                    Priority: {analysis.priority_score}/10
                    {#if analysis.is_phishing}
                      <Badge variant="danger" size="sm" class="ml-2">Phishing</Badge>
                    {/if}
                  </p>
                </div>
                <span class="text-xs text-muted-foreground">{analysis.processing_time.toFixed(2)}s</span>
              </div>
            {/each}
          </div>
          <Button variant="outline" class="w-full mt-4" href="/llm">
            View All Analyses
          </Button>
        </Card>
      {/if}

      <!-- Quick Actions -->
      <Card>
        <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
          Quick Actions
        </h3>
        <div class="grid grid-cols-2 gap-3">
          <Button variant="outline" class="h-auto py-4 flex-col" href="/mailboxes">
            <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <span class="text-sm">New Mailbox</span>
          </Button>

          <Button variant="outline" class="h-auto py-4 flex-col" href="/llm">
            <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span class="text-sm">AI Settings</span>
          </Button>

          <Button variant="outline" class="h-auto py-4 flex-col" href="/quarantine">
            <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <span class="text-sm">Quarantine</span>
          </Button>

          <Button variant="outline" class="h-auto py-4 flex-col" href="/domains">
            <svg class="w-6 h-6 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
            </svg>
            <span class="text-sm">Domains</span>
          </Button>
        </div>
      </Card>
    </div>
  {/if}
</div>
