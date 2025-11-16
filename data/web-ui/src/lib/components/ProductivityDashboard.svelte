<script lang="ts">
  import { onMount } from 'svelte';
  import Card from './Card.svelte';
  import { buildLlmApiUrl } from '$lib/config/llm';

  let analytics: any = null;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    await loadAnalytics();
  });

  async function loadAnalytics() {
    try {
      loading = true;
      const url = buildLlmApiUrl('/analytics/productivity');
      const response = await fetch(url);
      if (response.ok) {
        analytics = await response.json();
      }
    } catch (err) {
      error = `Failed to load productivity analytics: ${err}`;
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function formatTime(minutes: number): string {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  }

  function formatSentiment(score: number): string {
    if (score > 0.3) return 'Positive';
    if (score < -0.3) return 'Negative';
    return 'Neutral';
  }

  function getSentimentColor(score: number): string {
    if (score > 0.3) return 'text-green-600';
    if (score < -0.3) return 'text-red-600';
    return 'text-gray-600';
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold">Productivity Analytics</h2>
    <button
      on:click={loadAnalytics}
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
    >
      Refresh
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  {:else if error}
    <Card>
      <div class="text-center py-8 text-red-600">
        {error}
      </div>
    </Card>
  {:else if analytics}
    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <div class="text-sm text-gray-600 mb-1">Avg Response Time</div>
        <div class="text-3xl font-bold text-blue-600">
          {formatTime(Math.round(analytics.overview.avg_response_time || 0))}
        </div>
      </Card>

      <Card>
        <div class="text-sm text-gray-600 mb-1">Total Emails (7d)</div>
        <div class="text-3xl font-bold text-purple-600">
          {analytics.overview.total_emails || 0}
        </div>
      </Card>

      <Card>
        <div class="text-sm text-gray-600 mb-1">Urgent Emails</div>
        <div class="text-3xl font-bold text-red-600">
          {analytics.overview.urgent_emails || 0}
        </div>
      </Card>

      <Card>
        <div class="text-sm text-gray-600 mb-1">Active Threads</div>
        <div class="text-3xl font-bold text-green-600">
          {analytics.overview.active_threads || 0}
        </div>
      </Card>
    </div>

    <!-- Sentiment Trends -->
    <Card>
      <h3 class="text-xl font-bold mb-4">Sentiment Trends (30 days)</h3>
      <div class="space-y-2">
        {#each analytics.sentiment_trends.slice(0, 10) as trend}
          <div class="flex items-center justify-between py-2 border-b">
            <span class="text-sm text-gray-600">{trend.date}</span>
            <div class="flex items-center gap-4">
              <span class="text-sm text-gray-500">{trend.email_count} emails</span>
              <span class="font-semibold {getSentimentColor(trend.avg_sentiment)}">
                {formatSentiment(trend.avg_sentiment)} ({trend.avg_sentiment.toFixed(2)})
              </span>
            </div>
          </div>
        {/each}
      </div>
    </Card>

    <!-- Daily Volume Chart -->
    <Card>
      <h3 class="text-xl font-bold mb-4">Daily Email Volume (30 days)</h3>
      <div class="space-y-1">
        {@const maxCount = Math.max(1, ...analytics.daily_volume.map(d => d.count))}
        {#each analytics.daily_volume.slice(0, 15) as day}
          <div class="flex items-center gap-4">
            <span class="text-sm text-gray-600 w-32">{day.date}</span>
            <div class="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
              <div
                class="bg-blue-600 h-full rounded-full transition-all"
                style="width: {Math.min(100, (day.count / maxCount) * 100)}%"
              ></div>
            </div>
            <span class="text-sm font-semibold w-16 text-right">{day.count}</span>
          </div>
        {/each}
      </div>
    </Card>

    <!-- Category Distribution -->
    <Card>
      <h3 class="text-xl font-bold mb-4">Top Email Categories (7 days)</h3>
      <div class="space-y-3">
        {#each analytics.category_distribution.slice(0, 10) as category}
          {#try}
            {@const cats = JSON.parse(category.categories || '[]')}
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex flex-wrap gap-2">
                {#each cats as cat}
                  <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {cat}
                  </span>
                {/each}
              </div>
              <span class="text-lg font-bold text-gray-700">{category.count}</span>
            </div>
          {:catch}
            <!-- Silently ignore JSON parse errors -->
          {/try}
        {/each}
      </div>
    </Card>
  {/if}
</div>

<style>
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
