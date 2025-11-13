<script lang="ts">
  import Card from './Card.svelte';
  import Badge from './Badge.svelte';

  interface AutomationRule {
    id: string;
    name: string;
    enabled: boolean;
    trigger: {
      type: 'priority' | 'category' | 'sender' | 'keyword' | 'sentiment';
      condition: string;
      value: any;
    };
    actions: Array<{
      type: 'move' | 'label' | 'forward' | 'reply' | 'notify' | 'archive';
      value: string;
    }>;
    createdAt: string;
    executionCount: number;
  }

  let rules: AutomationRule[] = [
    {
      id: '1',
      name: 'Auto-archive newsletters',
      enabled: true,
      trigger: { type: 'category', condition: 'contains', value: 'newsletter' },
      actions: [
        { type: 'label', value: 'newsletters' },
        { type: 'archive', value: '' }
      ],
      createdAt: new Date().toISOString(),
      executionCount: 42
    },
    {
      id: '2',
      name: 'Urgent priority notifications',
      enabled: true,
      trigger: { type: 'priority', condition: '>=', value: 8 },
      actions: [
        { type: 'notify', value: 'push' },
        { type: 'label', value: 'urgent' }
      ],
      createdAt: new Date().toISOString(),
      executionCount: 15
    },
    {
      id: '3',
      name: 'Forward meeting requests',
      enabled: true,
      trigger: { type: 'category', condition: 'contains', value: 'meeting' },
      actions: [
        { type: 'forward', value: 'calendar@example.com' },
        { type: 'label', value: 'meetings' }
      ],
      createdAt: new Date().toISOString(),
      executionCount: 8
    },
    {
      id: '4',
      name: 'Positive sentiment auto-reply',
      enabled: false,
      trigger: { type: 'sentiment', condition: '>', value: 0.7 },
      actions: [
        { type: 'reply', value: 'Thank you for your positive feedback!' }
      ],
      createdAt: new Date().toISOString(),
      executionCount: 3
    }
  ];

  let showNewRuleModal = false;
  let newRule: Partial<AutomationRule> = {
    name: '',
    enabled: true,
    trigger: { type: 'priority', condition: '>=', value: 5 },
    actions: []
  };

  function toggleRule(rule: AutomationRule) {
    rule.enabled = !rule.enabled;
    rules = rules;
  }

  function deleteRule(ruleId: string) {
    rules = rules.filter(r => r.id !== ruleId);
  }

  function addNewRule() {
    const rule: AutomationRule = {
      id: Date.now().toString(),
      name: newRule.name || 'New Rule',
      enabled: newRule.enabled || true,
      trigger: newRule.trigger || { type: 'priority', condition: '>=', value: 5 },
      actions: newRule.actions || [],
      createdAt: new Date().toISOString(),
      executionCount: 0
    };
    rules = [...rules, rule];
    showNewRuleModal = false;
    resetNewRule();
  }

  function resetNewRule() {
    newRule = {
      name: '',
      enabled: true,
      trigger: { type: 'priority', condition: '>=', value: 5 },
      actions: []
    };
  }

  function getTriggerDescription(trigger: AutomationRule['trigger']): string {
    const typeLabels: Record<string, string> = {
      'priority': 'Priority',
      'category': 'Category',
      'sender': 'Sender',
      'keyword': 'Keyword',
      'sentiment': 'Sentiment'
    };

    return `${typeLabels[trigger.type]} ${trigger.condition} ${trigger.value}`;
  }

  function getActionDescription(action: AutomationRule['actions'][0]): string {
    const typeLabels: Record<string, string> = {
      'move': '📁 Move to',
      'label': '🏷️ Label as',
      'forward': '↪️ Forward to',
      'reply': '↩️ Auto-reply',
      'notify': '🔔 Send notification',
      'archive': '📦 Archive'
    };

    return `${typeLabels[action.type]} ${action.value}`.trim();
  }
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h2 class="text-2xl font-bold">⚡ Automation Engine</h2>
      <p class="text-gray-600 mt-1">Create intelligent email workflows</p>
    </div>
    <button
      on:click={() => showNewRuleModal = true}
      class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
    >
      + New Rule
    </button>
  </div>

  <!-- Stats -->
  <Card>
    <div class="grid grid-cols-3 gap-4 text-center">
      <div>
        <div class="text-3xl font-bold text-blue-600">{rules.length}</div>
        <div class="text-sm text-gray-600">Total Rules</div>
      </div>
      <div>
        <div class="text-3xl font-bold text-green-600">{rules.filter(r => r.enabled).length}</div>
        <div class="text-sm text-gray-600">Active</div>
      </div>
      <div>
        <div class="text-3xl font-bold text-purple-600">
          {rules.reduce((sum, r) => sum + r.executionCount, 0)}
        </div>
        <div class="text-sm text-gray-600">Total Executions</div>
      </div>
    </div>
  </Card>

  <!-- Rules List -->
  <div class="space-y-3">
    {#each rules as rule (rule.id)}
      <Card>
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <!-- Header -->
            <div class="flex items-center gap-3 mb-3">
              <input
                type="checkbox"
                checked={rule.enabled}
                on:change={() => toggleRule(rule)}
                class="w-5 h-5 rounded border-gray-300 text-blue-600"
              />
              <h3 class="text-lg font-semibold">{rule.name}</h3>
              <Badge variant={rule.enabled ? 'green' : 'gray'}>
                {rule.enabled ? 'Active' : 'Disabled'}
              </Badge>
              <span class="text-sm text-gray-500">
                Executed {rule.executionCount} times
              </span>
            </div>

            <!-- Trigger -->
            <div class="mb-3 p-3 bg-blue-50 rounded-lg">
              <span class="text-sm font-medium text-blue-900">When: </span>
              <span class="text-sm text-blue-700">{getTriggerDescription(rule.trigger)}</span>
            </div>

            <!-- Actions -->
            <div class="space-y-2">
              <span class="text-sm font-medium text-gray-700">Then:</span>
              {#each rule.actions as action}
                <div class="pl-4 py-2 border-l-4 border-green-500 bg-green-50 rounded">
                  <span class="text-sm text-green-700">{getActionDescription(action)}</span>
                </div>
              {/each}
            </div>

            <!-- Metadata -->
            <div class="mt-3 text-xs text-gray-500">
              Created {new Date(rule.createdAt).toLocaleDateString()}
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-2">
            <button class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded">
              Edit
            </button>
            <button
              on:click={() => deleteRule(rule.id)}
              class="px-3 py-1 text-sm bg-red-100 text-red-700 hover:bg-red-200 rounded"
            >
              Delete
            </button>
          </div>
        </div>
      </Card>
    {/each}
  </div>

  <!-- Pre-built Automation Templates -->
  <Card>
    <h3 class="text-xl font-bold mb-4">📋 Automation Templates</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="p-4 border-2 border-dashed rounded-lg hover:border-blue-500 cursor-pointer transition-colors">
        <h4 class="font-semibold mb-2">🚨 VIP Sender Alerts</h4>
        <p class="text-sm text-gray-600">Get instant notifications for emails from important contacts</p>
      </div>
      <div class="p-4 border-2 border-dashed rounded-lg hover:border-blue-500 cursor-pointer transition-colors">
        <h4 class="font-semibold mb-2">📅 Smart Calendar Integration</h4>
        <p class="text-sm text-gray-600">Automatically create calendar events from meeting requests</p>
      </div>
      <div class="p-4 border-2 border-dashed rounded-lg hover:border-blue-500 cursor-pointer transition-colors">
        <h4 class="font-semibold mb-2">🗂️ Smart Filing</h4>
        <p class="text-sm text-gray-600">Auto-organize emails by project, client, or category</p>
      </div>
      <div class="p-4 border-2 border-dashed rounded-lg hover:border-blue-500 cursor-pointer transition-colors">
        <h4 class="font-semibold mb-2">🤖 AI Auto-Responses</h4>
        <p class="text-sm text-gray-600">Generate and send contextual replies to routine emails</p>
      </div>
    </div>
  </Card>
</div>

<!-- New Rule Modal (Simplified) -->
{#if showNewRuleModal}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
      <h3 class="text-2xl font-bold mb-4">Create Automation Rule</h3>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">Rule Name</label>
          <input
            type="text"
            bind:value={newRule.name}
            placeholder="e.g., Archive old newsletters"
            class="w-full px-4 py-2 border rounded-lg"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Trigger Type</label>
          <select
            bind:value={newRule.trigger.type}
            class="w-full px-4 py-2 border rounded-lg"
          >
            <option value="priority">Priority</option>
            <option value="category">Category</option>
            <option value="sender">Sender</option>
            <option value="keyword">Keyword</option>
            <option value="sentiment">Sentiment</option>
          </select>
        </div>

        <div class="flex gap-4">
          <button
            on:click={addNewRule}
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Create Rule
          </button>
          <button
            on:click={() => { showNewRuleModal = false; resetNewRule(); }}
            class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Modal animation could go here */
</style>
