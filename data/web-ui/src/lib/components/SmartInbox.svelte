<script lang="ts">
  import { onMount } from 'svelte';
  import Card from './Card.svelte';
  import Badge from './Badge.svelte';

  export let mailbox: string = '';

  let emails: any[] = [];
  let loading = true;
  let filter: 'all' | 'urgent' | 'tasks' | 'meetings' = 'all';
  let sortBy: 'date' | 'priority' | 'sentiment' = 'date';

  onMount(async () => {
    await loadEmails();
  });

  async function loadEmails() {
    try {
      loading = true;
      const response = await fetch('http://llm-processor-mailcow:8080/stats');
      if (response.ok) {
        const data = await response.json();
        emails = data.recent_analyses || [];
      }
    } catch (err) {
      console.error('Failed to load emails:', err);
    } finally {
      loading = false;
    }
  }

  $: filteredEmails = emails
    .filter(email => {
      if (filter === 'urgent') return email.priority_score >= 7;
      if (filter === 'tasks') return email.tasks && JSON.parse(email.tasks || '[]').length > 0;
      if (filter === 'meetings') return email.meeting_request !== null;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'priority') return b.priority_score - a.priority_score;
      if (sortBy === 'sentiment') return (b.sentiment_score || 0) - (a.sentiment_score || 0);
      return new Date(b.analyzed_at).getTime() - new Date(a.analyzed_at).getTime();
    });

  function getPriorityColor(score: number): string {
    if (score >= 8) return 'red';
    if (score >= 6) return 'yellow';
    if (score >= 4) return 'blue';
    return 'gray';
  }

  function getToneEmoji(tone: string): string {
    const emojiMap: Record<string, string> = {
      'formal': '📋',
      'casual': '😊',
      'concerned': '😟',
      'positive': '✨',
      'neutral': '📧'
    };
    return emojiMap[tone] || '📧';
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }
</script>

<div class="space-y-4">
  <!-- Smart Controls -->
  <Card>
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex gap-2">
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'all'}
        >
          All Emails
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'urgent' ? 'bg-red-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'urgent'}
        >
          🚨 Urgent
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'tasks' ? 'bg-purple-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'tasks'}
        >
          ✓ Tasks
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'meetings' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'meetings'}
        >
          📅 Meetings
        </button>
      </div>

      <select
        bind:value={sortBy}
        class="px-4 py-2 border rounded-lg bg-white"
      >
        <option value="date">Sort by Date</option>
        <option value="priority">Sort by Priority</option>
        <option value="sentiment">Sort by Sentiment</option>
      </select>
    </div>
  </Card>

  <!-- Email List -->
  {#if loading}
    <Card>
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    </Card>
  {:else if filteredEmails.length === 0}
    <Card>
      <div class="text-center py-12 text-gray-500">
        No emails found matching your filters
      </div>
    </Card>
  {:else}
    <div class="space-y-3">
      {#each filteredEmails as email (email.email_id)}
        <Card>
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Email Details -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-2xl">{getToneEmoji(email.tone)}</span>
                <Badge variant={getPriorityColor(email.priority_score)}>
                  Priority {email.priority_score}
                </Badge>
                {#if email.is_phishing}
                  <Badge variant="red">⚠️ Phishing Risk</Badge>
                {/if}
                {#if email.language && email.language !== 'english'}
                  <Badge variant="blue">{email.language}</Badge>
                {/if}
              </div>

              <h3 class="font-semibold text-lg mb-1 truncate">{email.mailbox}</h3>
              <p class="text-gray-700 mb-2 line-clamp-2">{email.summary}</p>

              <!-- Categories -->
              {#if email.categories}
                {@const cats = JSON.parse(email.categories || '[]')}
                <div class="flex flex-wrap gap-2 mb-2">
                  {#each cats as category}
                    <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                      {category}
                    </span>
                  {/each}
                </div>
              {/if}

              <!-- AI Insights -->
              <div class="flex items-center gap-4 text-sm text-gray-600">
                <span>📊 Sentiment: {email.sentiment_score?.toFixed(2) || 'N/A'}</span>
                <span>⏱️ {formatDate(email.analyzed_at)}</span>
                {#if email.conversation_id}
                  <span>💬 Thread</span>
                {/if}
              </div>
            </div>

            <!-- Right: Quick Actions -->
            <div class="flex flex-col gap-2">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                View
              </button>
              <button class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm">
                Reply
              </button>
            </div>
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
