<script lang="ts">
  import { cn } from '$lib/utils';

  export let variant: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'outline' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';

  const baseClasses = 'badge';

  const variants = {
    primary: 'badge-primary',
    secondary: 'badge-secondary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    outline: 'border-current',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-0.5',
    lg: 'text-base px-3 py-1',
  };

  $: classes = cn(baseClasses, variants[variant], sizes[size], $$props.class);
</script>

<span class={classes}>
  <slot />
</span>
