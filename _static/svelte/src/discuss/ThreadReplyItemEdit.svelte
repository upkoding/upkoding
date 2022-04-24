<script>
    import { createOrUpdateReply } from "../common/api";
    import MarkdownEditor from "./MarkdownEditor.svelte";

    export let reply;
    export let parent = null;
    export let onCancel;
    export let onCreate;
    export let onUpdate;
    export let useMarkdownEditor = true;

    let message = reply.message;
    let loading = false;

    // new reply
    async function create() {
        if (loading) return;

        const newReply = {
            message: message,
            thread: parent.thread,
            parent: parent.id,
        };
        loading = true;
        const { ok, data } = await createOrUpdateReply(newReply);
        loading = false;
        if (ok) {
            onCreate(data);
            message = "";
        }
    }

    async function update() {
        if (loading) return;
        loading = true;
        const r = Object.assign(reply, { message: message });
        const { ok, data } = await createOrUpdateReply(r);
        loading = false;
        if (ok) {
            onUpdate(data);
        }
    }

    async function createOrUpdate() {
        if (reply.id) {
            await update();
        } else {
            await create();
        }
    }
</script>

{#if useMarkdownEditor}
    <MarkdownEditor value={message} onChange={(msg) => (message = msg)} />
{:else}
    <textarea
        rows="2"
        placeholder="Beri komentar..."
        class="form-control"
        bind:value={message}
    />
{/if}
<div class="d-flex justify-content-end pt-1">
    <a href={"#"} on:click|preventDefault={onCancel} class="text-muted mr-2">
        <small> Batal </small>
    </a>
    <a href={"#"} on:click|preventDefault={createOrUpdate}>
        <small>
            {loading ? "Submitting..." : "Submit"}
            <span class="material-icons-x"> arrow_right </span>
        </small>
    </a>
</div>
