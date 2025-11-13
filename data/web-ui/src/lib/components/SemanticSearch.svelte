<script lang="ts">
  import { onMount } from 'svelte';
  import Card from './Card.svelte';
  import Badge from './Badge.svelte';

  let searchQuery = '';
  let searchResults: any[] = [];
  let searching = false;
  let hasSearched = false;

  async function handleSearch() {
    if (!searchQuery.trim()) return;

    try {
      searching = true;
      hasSearched = true;
      const response = await fetch(
        `http://llm-processor-mailcow:8080/semantic-search?query=${encodeURIComponent(searchQuery)}&limit=20`,
        { method: 'POST' }
      );

      if (response.ok) {
        const data = await response.json();
        searchResults = data.results || [];
      }
    } catch (err) {
      console.error('Search failed:', err);
      searchResults = [];
    } finally {
      searching = false;
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSearch();
    }
  }

  function highlightMatch(text: string, query: string): string {
    if (!query || !text) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  }
</script>

<div class="space-y-6">
  <Card>
    <div class="space-y-4">
      <h2 class="text-2xl font-bold">🔍 Semantic Email Search</h2>
      <p class="text-gray-600">
        Search your emails using natural language. Ask questions like "meetings next week" or "urgent finance emails"
      </p>

      <div class="flex gap-2">
        <input
          type="text"
          bind:value={searchQuery}
          on:keypress={handleKeyPress}
          placeholder="Search emails naturally..."
          class="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          on:click={handleSearch}
          disabled={searching || !searchQuery.trim()}
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      <!-- Quick Searches -->
      <div class="flex flex-wrap gap-2">
        <span class="text-sm text-gray-600">Quick searches:</span>
        <button
          on:click={() => { searchQuery = 'urgent emails'; handleSearch(); }}
          class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm"
        >
          urgent emails
        </button>
        <button
          on:click={() => { searchQuery = 'meeting requests'; handleSearch(); }}
          class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm"
        >
          meeting requests
        </button>
        <button
          on:click={() => { searchQuery = 'tasks and action items'; handleSearch(); }}
          class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm"
        >
          tasks and action items
        </button>
        <button
          on:click={() => { searchQuery = 'positive feedback'; handleSearch(); }}
          class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm"
        >
          positive feedback
        </button>
      </div>
    </div>
  </Card>

  {#if searching}
    <Card>
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Searching through your emails...</p>
        </div>
      </div>
    </Card>
  {:else if hasSearched}
    {#if searchResults.length === 0}
      <Card>
        <div class="text-center py-12">
          <p class="text-gray-600 text-lg mb-2">No results found</p>
          <p class="text-gray-500 text-sm">Try a different search query</p>
        </div>
      </Card>
    {:else}
      <div class="space-y-3">
        <div class="text-sm text-gray-600">
          Found {searchResults.length} relevant emails
        </div>

        {#each searchResults as result (result.email_id)}
          <Card>
            <div class="space-y-3">
              <!-- Header -->
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <Badge variant="blue">
                      Relevance: {(result.relevance_score * 100).toFixed(0)}%
                    </Badge>
                    {#if result.priority_score >= 7}
                      <Badge variant="red">High Priority</Badge>
                    {/if}
                    {#if result.tone}
                      <Badge variant="gray">{result.tone}</Badge>
                    {/if}
                  </div>

                  <h3 class="font-semibold text-lg mb-1">{result.mailbox}</h3>
                </div>

                <span class="text-sm text-gray-500">
                  {new Date(result.analyzed_at).toLocaleDateString()}
                </span>
              </div>

              <!-- Summary -->
              <p class="text-gray-700">
                {@html highlightMatch(result.summary || 'No summary available', searchQuery)}
              </p>

              <!-- Categories -->
              {#if result.categories}
                {@const cats = JSON.parse(result.categories || '[]')}
                <div class="flex flex-wrap gap-2">
                  {#each cats as category}
                    <span class="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm">
                      {category}
                    </span>
                  {/each}
                </div>
              {/if}

              <!-- Metadata -->
              <div class="flex items-center gap-4 text-sm text-gray-600 pt-2 border-t">
                <span>📊 Priority: {result.priority_score}/10</span>
                {#if result.sentiment_score}
                  <span>❤️ Sentiment: {result.sentiment_score.toFixed(2)}</span>
                {/if}
                {#if result.language}
                  <span>🌐 {result.language}</span>
                {/if}
              </div>
            </div>
          </Card>
        {/each}
      </div>
    {/if}
  {:else}
    <Card>
      <div class="text-center py-12 text-gray-500">
        <p class="text-lg mb-2">Start searching your emails</p>
        <p class="text-sm">Use natural language to find exactly what you're looking for</p>
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

  :global(mark) {
    background-color: #fef08a;
    padding: 0 2px;
    border-radius: 2px;
  }
</style>
