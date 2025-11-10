<script lang="ts">
  import { cn } from '$lib/utils';

  export let type = 'text';
  export let value = '';
  export let placeholder = '';
  export let disabled = false;
  export let error: string | undefined = undefined;
  export let label: string | undefined = undefined;
  export let id: string | undefined = undefined;
  export let required = false;

  $: classes = cn(
    'input',
    error && 'border-danger-500 focus-visible:ring-danger-500',
    $$props.class
  );
</script>

<div class="space-y-2">
  {#if label}
    <label for={id} class="block text-sm font-medium">
      {label}
      {#if required}
        <span class="text-danger-500">*</span>
      {/if}
    </label>
  {/if}

  <input
    {id}
    {type}
    {placeholder}
    {disabled}
    {required}
    bind:value
    class={classes}
    on:input
    on:change
    on:focus
    on:blur
    on:keydown
  />

  {#if error}
    <p class="text-sm text-danger-500">{error}</p>
  {/if}
</div>
