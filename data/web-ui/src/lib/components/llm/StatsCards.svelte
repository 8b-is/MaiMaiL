<script lang="ts">
  import type { LlmStats } from '$lib/types';
  import Card from '$lib/components/ui/Card.svelte';
  import { formatNumber } from '$lib/utils';

  export let stats: LlmStats;
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <!-- Total Analyzed -->
  <Card class="bg-gradient-to-br from-primary-500 to-primary-600 text-white">
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-medium opacity-90">Total Analyzed</h3>
        <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      </div>
      <p class="text-3xl font-bold">{formatNumber(stats.total_analyzed)}</p>
      <p class="text-xs opacity-75">Emails processed by AI</p>
    </div>
  </Card>

  <!-- Phishing Detected -->
  <Card class="bg-gradient-to-br from-danger-500 to-danger-600 text-white">
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-medium opacity-90">Phishing Detected</h3>
        <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
      </div>
      <p class="text-3xl font-bold">{formatNumber(stats.phishing_detected)}</p>
      <p class="text-xs opacity-75">
        {stats.total_analyzed > 0
          ? `${((stats.phishing_detected / stats.total_analyzed) * 100).toFixed(1)}% of total`
          : 'No threats yet'}
      </p>
    </div>
  </Card>

  <!-- Avg Processing Time -->
  <Card class="bg-gradient-to-br from-success-500 to-success-600 text-white">
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-medium opacity-90">Avg. Processing</h3>
        <svg class="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <p class="text-3xl font-bold">{stats.avg_processing_time.toFixed(2)}s</p>
      <p class="text-xs opacity-75">Per email analysis</p>
    </div>
  </Card>
</div>
