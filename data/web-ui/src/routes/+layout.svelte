<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import Header from '$lib/components/layout/Header.svelte';
	import Toast from '$lib/components/ui/Toast.svelte';
	import '$lib/../app.css';

	let { children } = $props();

	onMount(() => {
		// Initialize auth and theme
		auth.init();
		theme.init();
	});
</script>

<svelte:head>
	<title>MaiMaiL - AI-Powered Email Management</title>
	<meta name="description" content="Modern email server with AI intelligence" />
</svelte:head>

<div class="min-h-screen bg-background">
	<Header />
	<main class="container mx-auto px-4 py-6">
		{@render children()}
	</main>
	<Toast />
</div>
