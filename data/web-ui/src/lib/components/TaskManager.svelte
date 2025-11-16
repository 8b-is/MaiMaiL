<script lang="ts">
  import { onMount } from 'svelte';
  import Card from './Card.svelte';
  import Badge from './Badge.svelte';
  import { buildLlmApiUrl } from '$lib/config/llm';

  interface Task {
    email_id: string;
    mailbox: string;
    description: string;
    deadline: string | null;
    priority: number;
    extracted_at: string;
    completed: boolean;
  }

  let tasks: Task[] = [];
  let loading = true;
  let error: string | null = null;
  let filter: 'all' | 'pending' | 'urgent' | 'today' = 'pending';
  let groupBy: 'priority' | 'deadline' | 'mailbox' = 'priority';

  onMount(async () => {
    await loadTasks();
  });

  async function loadTasks() {
    try {
      loading = true;
      error = null;
      const url = buildLlmApiUrl('/stats');
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        const emails = data.recent_analyses || [];

        // Extract all tasks from emails
        tasks = [];
        for (const email of emails) {
          if (email.tasks) {
            try {
              const emailTasks = JSON.parse(email.tasks);
              for (const task of emailTasks) {
                tasks.push({
                  email_id: email.email_id,
                  mailbox: email.mailbox,
                  description: task.description,
                  deadline: task.deadline,
                  priority: task.priority || 5,
                  extracted_at: task.extracted_at,
                  completed: false
                });
              }
            } catch (e) {
              console.error('Failed to parse tasks:', e);
            }
          }
        }
      }
    } catch (err) {
      error = `Failed to load tasks: ${err}`;
      console.error(err);
    } finally {
      loading = false;
    }
  }

  $: filteredTasks = tasks.filter(task => {
    if (filter === 'pending') return !task.completed;
    if (filter === 'urgent') return !task.completed && task.priority >= 7;
    if (filter === 'today') {
      if (!task.deadline) return false;
      const deadline = new Date(task.deadline);
      const today = new Date();
      return deadline.toDateString() === today.toDateString();
    }
    return true;
  });

  $: groupedTasks = (() => {
    const groups: Record<string, Task[]> = {};

    for (const task of filteredTasks) {
      let key = '';
      if (groupBy === 'priority') {
        if (task.priority >= 8) key = 'Critical (8-10)';
        else if (task.priority >= 6) key = 'High (6-7)';
        else if (task.priority >= 4) key = 'Medium (4-5)';
        else key = 'Low (1-3)';
      } else if (groupBy === 'deadline') {
        if (!task.deadline) key = 'No Deadline';
        else {
          const deadline = new Date(task.deadline);
          const today = new Date();
          const diffDays = Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
          if (diffDays < 0) key = 'Overdue';
          else if (diffDays === 0) key = 'Today';
          else if (diffDays <= 7) key = 'This Week';
          else key = 'Later';
        }
      } else {
        key = task.mailbox;
      }

      if (!groups[key]) groups[key] = [];
      groups[key].push(task);
    }

    return groups;
  })();

  function toggleTask(task: Task) {
    task.completed = !task.completed;
    tasks = tasks; // Trigger reactivity
  }

  function getPriorityColor(priority: number): string {
    if (priority >= 8) return 'red';
    if (priority >= 6) return 'yellow';
    if (priority >= 4) return 'blue';
    return 'gray';
  }

  function formatDeadline(deadline: string | null): string {
    if (!deadline) return 'No deadline';
    const date = new Date(deadline);
    const today = new Date();
    const diffMs = date.getTime() - today.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)}d`;
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays <= 7) return `Due in ${diffDays} days`;
    return date.toLocaleDateString();
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold">✓ Task Manager</h2>
    <button
      on:click={loadTasks}
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      Refresh
    </button>
  </div>

  <!-- Controls -->
  <Card>
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="flex gap-2">
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'pending' ? 'bg-blue-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'pending'}
        >
          Pending ({tasks.filter(t => !t.completed).length})
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'urgent' ? 'bg-red-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'urgent'}
        >
          Urgent ({tasks.filter(t => !t.completed && t.priority >= 7).length})
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'today' ? 'bg-green-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'today'}
        >
          Today
        </button>
        <button
          class="px-4 py-2 rounded-lg font-medium transition-colors {filter === 'all' ? 'bg-purple-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}"
          on:click={() => filter = 'all'}
        >
          All ({tasks.length})
        </button>
      </div>

      <select
        bind:value={groupBy}
        class="px-4 py-2 border rounded-lg bg-white"
      >
        <option value="priority">Group by Priority</option>
        <option value="deadline">Group by Deadline</option>
        <option value="mailbox">Group by Source</option>
      </select>
    </div>
  </Card>

  <!-- Task List -->
  {#if loading}
    <Card>
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    </Card>
  {:else if error}
    <Card>
      <div class="text-center py-8 text-red-600">
        {error}
      </div>
    </Card>
  {:else if Object.keys(groupedTasks).length === 0}
    <Card>
      <div class="text-center py-12">
        <p class="text-gray-600 text-lg mb-2">No tasks found</p>
        <p class="text-gray-500 text-sm">Tasks will be automatically extracted from your emails</p>
      </div>
    </Card>
  {:else}
    <div class="space-y-6">
      {#each Object.entries(groupedTasks) as [groupName, groupTasks]}
        <div class="space-y-3">
          <h3 class="text-lg font-bold text-gray-700 px-2">{groupName}</h3>
          {#each groupTasks as task}
            <Card>
              <div class="flex items-start gap-4">
                <!-- Checkbox -->
                <input
                  type="checkbox"
                  checked={task.completed}
                  on:change={() => toggleTask(task)}
                  class="mt-1 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />

                <!-- Task Details -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-2">
                    <Badge variant={getPriorityColor(task.priority)}>
                      P{task.priority}
                    </Badge>
                    {#if task.deadline}
                      {@const deadline = new Date(task.deadline)}
                      {@const isOverdue = deadline < new Date()}
                      <Badge variant={isOverdue ? 'red' : 'blue'}>
                        ⏰ {formatDeadline(task.deadline)}
                      </Badge>
                    {/if}
                  </div>

                  <p class="text-gray-900 mb-2 {task.completed ? 'line-through opacity-60' : ''}">
                    {task.description}
                  </p>

                  <div class="flex items-center gap-4 text-sm text-gray-600">
                    <span>📧 {task.mailbox}</span>
                    <span>📅 Extracted {new Date(task.extracted_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <!-- Actions -->
                <button class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded">
                  View Email
                </button>
              </div>
            </Card>
          {/each}
        </div>
      {/each}
    </div>
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
