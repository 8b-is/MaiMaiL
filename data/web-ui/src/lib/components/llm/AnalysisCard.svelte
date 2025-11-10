<script lang="ts">
  import type { LlmAnalysis } from '$lib/types';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { getPriorityColor, getPriorityLabel, getPhishingRiskLevel, getCategoryColor } from '$lib/utils';

  export let analysis: LlmAnalysis;

  $: priorityColor = getPriorityColor(analysis.priority_score);
  $: priorityLabel = getPriorityLabel(analysis.priority_score);
  $: phishingRisk = getPhishingRiskLevel(analysis.phishing_score);

  const phishingColors = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger',
  };
</script>

<Card padding={false} class="overflow-hidden">
  <div class="p-4 space-y-4">
    <!-- Priority Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium text-muted-foreground">Priority:</span>
        <Badge variant={priorityColor}>
          {priorityLabel} ({analysis.priority_score}/10)
        </Badge>
      </div>

      {#if analysis.is_phishing}
        <Badge variant={phishingColors[phishingRisk]}>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          Phishing Risk: {Math.round(analysis.phishing_score * 100)}%
        </Badge>
      {/if}
    </div>

    <!-- Summary -->
    {#if analysis.summary}
      <div class="space-y-1">
        <h4 class="text-sm font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          AI Summary
        </h4>
        <p class="text-sm text-muted-foreground leading-relaxed">{analysis.summary}</p>
      </div>
    {/if}

    <!-- Categories -->
    {#if analysis.categories && analysis.categories.length > 0}
      <div class="space-y-2">
        <h4 class="text-sm font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
          </svg>
          Categories
        </h4>
        <div class="flex flex-wrap gap-2">
          {#each analysis.categories as category}
            <Badge variant={getCategoryColor(category)} size="sm">
              {category}
            </Badge>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Warnings -->
    <div class="space-y-2">
      {#if analysis.sensitive_data}
        <div class="flex items-start gap-2 p-3 bg-warning-50 dark:bg-warning-900/20 rounded-lg border border-warning-200 dark:border-warning-800">
          <svg class="w-5 h-5 text-warning-600 dark:text-warning-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          <div>
            <p class="text-sm font-semibold text-warning-900 dark:text-warning-100">Sensitive Data Detected</p>
            <p class="text-xs text-warning-800 dark:text-warning-200 mt-1">This email may contain passwords, credit cards, or other sensitive information.</p>
          </div>
        </div>
      {/if}

      {#if analysis.is_phishing}
        <div class="flex items-start gap-2 p-3 bg-danger-50 dark:bg-danger-900/20 rounded-lg border border-danger-200 dark:border-danger-800">
          <svg class="w-5 h-5 text-danger-600 dark:text-danger-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <div>
            <p class="text-sm font-semibold text-danger-900 dark:text-danger-100">Potential Phishing Attempt</p>
            <p class="text-xs text-danger-800 dark:text-danger-200 mt-1">This email has been flagged as potentially malicious. Do not click any links or download attachments.</p>
          </div>
        </div>
      {/if}
    </div>

    <!-- Auto Reply Suggestion -->
    {#if analysis.auto_reply_suggestion}
      <div class="space-y-2 pt-2 border-t">
        <h4 class="text-sm font-semibold flex items-center gap-2">
          <svg class="w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
          </svg>
          Suggested Reply
        </h4>
        <div class="p-3 bg-secondary rounded-lg">
          <p class="text-sm text-muted-foreground italic">{analysis.auto_reply_suggestion}</p>
        </div>
      </div>
    {/if}

    <!-- Processing Info -->
    <div class="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
      <span>Processed in {analysis.processing_time.toFixed(2)}s</span>
      <span>{new Date(analysis.analyzed_at).toLocaleString()}</span>
    </div>
  </div>
</Card>
