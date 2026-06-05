<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { applyTenantBranding, getTenantContext } from '$lib/tenant/context';
	import Header from '$lib/components/layout/Header.svelte';
	import Toast from '$lib/components/ui/Toast.svelte';
	import '$lib/../app.css';

	let { children } = $props();
	let tenantDisplayName = $state('MaiMaiL');

	onMount(() => {
		// Initialize auth and theme
		auth.init();
		theme.init();
		const tenantContext = getTenantContext();
		tenantDisplayName = tenantContext.branding.displayName || 'MaiMaiL';
		applyTenantBranding(tenantContext);
	});
</script>

<svelte:head>
	<title>{tenantDisplayName} - MaiMaiL Dashboard</title>
	<meta name="description" content="The most advanced email serving platform from the year 2200" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="theme-color" content="#2563eb" />
	<link rel="manifest" href="/manifest.json" />
	<link rel="apple-touch-icon" href="/icon-192.png" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Header />
	<main class="container mx-auto px-4 py-6">
		{@render children()}
	</main>
	<Toast />
</div>
