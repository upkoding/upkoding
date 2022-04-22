<script>
	import { onMount, tick, setContext } from "svelte";
	import {
		getTopicForProject,
		createTopicForProject,
		createOrUpdateThread,
		listThread,
	} from "../common/api";
	import EmptyThreads from "./EmptyThreads.svelte";
	import ThreadFormModal from "./ThreadFormModal.svelte";
	import ThreadItem from "./ThreadItem.svelte";

	// app props
	export let current_user_id;
	export let project_id;

	setContext("currentUserId", current_user_id);

	// local vars
	let loading = false;
	let topic = null;
	let threads = [];
	let nextThreadsURL;
	let showNewThreadModal = false;
	let saving = false;
	let savingErrors = null;

	async function getThreads(refresh) {
		if (loading) return;

		loading = true;
		if (topic === null) {
			const { ok, data } = await getTopicForProject(project_id);
			topic = ok ? data : null;
		}

		if (topic) {
			const { ok, data } = await listThread(
				{ topic: topic.id },
				refresh ? null : nextThreadsURL
			);
			if (ok) {
				threads = refresh
					? data.results
					: [...threads, ...data.results];
				nextThreadsURL = data.next;
			}
		}
		loading = false;
	}

	// on mounted: fetch threads
	onMount(async () => {
		await getThreads(true);
	});

	// on thread deleted: remove from list
	function onDelete(thread) {
		threads = threads.filter((t) => t.id !== thread.id);
		// in case all thread deleted, pull from server if there's left.
		if (threads.length == 0) {
			getThreads(true);
		}
	}

	function openForm() {
		showNewThreadModal = true;
	}

	function closeForm() {
		showNewThreadModal = false;
		savingErrors = null;
	}

	async function newThread(thread) {
		if (saving) return;

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
			savingErrors = null;
		} else {
			savingErrors = data;
		}
	}
</script>

{#if showNewThreadModal}
	<ThreadFormModal
		theme="info"
		title="Ajukan Pertanyaan"
		btnText="Submit Pertanyaan"
		btnTextLoading="Submitting..."
		loading={saving}
		errors={savingErrors}
		onClose={closeForm}
		onSubmit={newThread}
	/>
{/if}

<div class="card shadow-sm mb-3">
	<div class="card-header d-flex justify-content-between">
		<span class="mt-1">FORUM DISKUSI</span>
		<button class="btn btn-info" on:click={openForm}>
			Ajukan Pertanyaan
		</button>
	</div>
	{#if threads.length > 0}
		<div class="list-group list-group-flush">
			{#each threads as thread (thread.id)}
				<ThreadItem {thread} {onDelete} />
			{/each}
			{#if nextThreadsURL}
				<div class="media chat-item d-flex justify-content-center">
					<a
						href={"#"}
						on:click|preventDefault={() => {
							getThreads(false);
						}}
					>
						<span class="material-icons-x mr-1">arrow_downward</span
						>{loading ? "Memuat..." : "Muat diskusi sebelumnya"}
					</a>
				</div>
			{/if}
		</div>
	{:else}
		<EmptyThreads {loading} />
	{/if}
</div>

<style>
	:global(.hljs) {
		background: #0d1117 !important;
	}
</style>
