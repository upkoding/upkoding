<script>
	import { onMount, tick } from "svelte";
	import {
		getTopicForProject,
		createTopicForProject,
		createOrUpdateThread,
		listThreads,
	} from "../common/api";
	import EmptyThreads from "./EmptyThreads.svelte";
	import ThreadFormModal from "./ThreadFormModal.svelte";
	import ThreadItem from "./ThreadItem.svelte";

	// app props
	export let current_user_id;
	export let project_id;

	// local vars
	let loading = true;
	let topic = null;
	let threads = [];
	let showNewThreadModal = false;
	let saving = false;
	let savingErrors = null;

	// on mounted: fetch threads
	onMount(async () => {
		const { ok, data } = await getTopicForProject(project_id);
		topic = ok ? data : null;
		if (topic) {
			const { ok, data } = await listThreads({ topic: topic.id });
			threads = ok ? data.results : [];
		}
		loading = false;
	});

	// on thread deleted: remove from list
	function onThreadDeleted(e) {
		threads = threads.filter((t) => t.id !== e.detail.id);
	}

	function showForm() {
		showNewThreadModal = true;
	}

	async function newThread(e) {
		let thread = e.detail;
		saving = true;
		if (topic === null) {
			const { ok, data } = await createTopicForProject(project_id);
			topic = ok ? data : null;
		}
		thread.topic = topic ? topic.id : null;
		const { ok, data } = await createOrUpdateThread(thread);
		saving = false;
		if (ok) {
			showNewThreadModal = false;
			await tick();
			threads = [data, ...threads];
		} else {
			savingErrors = data;
		}
	}
</script>

<ThreadFormModal
	key="new"
	theme="primary"
	title="Ajukan Pertanyaan"
	btnText="Kirim"
	btnTextLoading="Mengirim..."
	loading={saving}
	errors={savingErrors}
	resetOnClose={true}
	bind:show={showNewThreadModal}
	on:submit={newThread}
/>

<div class="card shadow-sm mb-3">
	<div class="card-header d-flex justify-content-between">
		<span class="mt-1">FORUM DISKUSI</span>
		<button class="btn btn-primary" on:click={showForm}>
			Ajukan Pertanyaan
		</button>
	</div>
	{#if threads.length > 0}
		<div class="list-group list-group-flush">
			{#each threads as thread (thread.id)}
				<ThreadItem
					bind:thread
					{current_user_id}
					on:delete={onThreadDeleted}
				/>
			{/each}
		</div>
	{:else}
		<EmptyThreads {loading} />
	{/if}
</div>
