<script lang="ts">
  import { cn } from '$lib/utils';

  export let padding = true;
  export let hover = false;

  $: classes = cn(
    'card',
    padding && 'p-6',
    hover && 'hover:shadow-lg cursor-pointer transition-smooth',
    $$props.class
  );
</script>

<div class={classes} on:click>
  <slot />
</div>
