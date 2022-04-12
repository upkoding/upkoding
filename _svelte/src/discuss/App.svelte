<script>
	import { onMount } from "svelte";
	import {
		getTopicForProject,
		createTopicForProject,
		getTopicThreads,
	} from "../common/api";
	import NoComments from "./NoComments.svelte";
	import CommentForm from "./CommentForm.svelte";
	import CommentItem from "./CommentItem.svelte";

	// app props
	export let is_authenticated;
	export let project_id;

	// local vars
	let loading = true;
	let topic = null;
	let comments = [];

	// on mounted
	onMount(async () => {
		topic = await getTopicForProject(project_id);
		if (topic != null) {
			const result = await getTopicThreads(topic.id);
			comments = result.results;
		}
		loading = false;
	});
</script>

<div class="card shadow-sm mb-3">
	<div class="card-header">FORUM DISKUSI</div>
	{#if comments.length > 0}
		<div class="list-group list-group-flush">
			{#each comments as comment (comment.id)}
				<CommentItem {comment} />
			{/each}
		</div>
	{:else}
		<NoComments {loading} />
	{/if}

	{#if is_authenticated}
		<CommentForm />
	{/if}
</div>
