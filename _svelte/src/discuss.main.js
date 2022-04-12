import App from './discuss/App.svelte';

const app = new App({
	target: document.getElementById("discuss-target"),
	props: JSON.parse(document.getElementById("discuss-props").textContent),
});

export default app;