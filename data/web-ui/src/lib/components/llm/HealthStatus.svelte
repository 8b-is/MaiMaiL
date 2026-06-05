<script lang="ts">
  import type { LlmHealth } from '$lib/types';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Card from '$lib/components/ui/Card.svelte';

  export let health: LlmHealth;

  const statusColors = {
    healthy: 'success',
    degraded: 'warning',
    error: 'danger',
  };

  const componentStatus = {
    ok: { color: 'success', icon: '✓' },
    error: { color: 'danger', icon: '✗' },
  } as const;

  const colorClasses: Record<'success' | 'danger', string> = {
    success: 'text-success-500',
    danger: 'text-danger-500',
  };
</script>

<Card>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold flex items-center gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        LLM System Health
      </h3>
      <Badge variant={statusColors[health.status]}>
        {health.status.toUpperCase()}
      </Badge>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <!-- Ollama Status -->
      <div class="flex items-center gap-2">
        <span class={`${colorClasses[componentStatus[health.ollama].color]} font-bold`}>
          {componentStatus[health.ollama].icon}
        </span>
        <span class="text-sm">Ollama</span>
      </div>

      <!-- MySQL Status -->
      <div class="flex items-center gap-2">
        <span class={`${colorClasses[componentStatus[health.mysql].color]} font-bold`}>
          {componentStatus[health.mysql].icon}
        </span>
        <span class="text-sm">MySQL</span>
      </div>

      <!-- Redis Status -->
      <div class="flex items-center gap-2">
        <span class={`${colorClasses[componentStatus[health.redis].color]} font-bold`}>
          {componentStatus[health.redis].icon}
        </span>
        <span class="text-sm">Redis</span>
      </div>

      <!-- Model Info -->
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <span class="text-sm font-mono">{health.model}</span>
      </div>
    </div>

    {#if health.uptime}
      <div class="pt-2 border-t text-xs text-muted-foreground">
        Uptime: {Math.floor(health.uptime / 3600)}h {Math.floor((health.uptime % 3600) / 60)}m
      </div>
    {/if}
  </div>
</Card>
