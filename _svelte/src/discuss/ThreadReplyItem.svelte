<script>
    import { getContext } from "svelte";
    import { parse } from "../common/markdown";
    import { deleteReply } from "../common/api";
    import dayjs from "../common/dayjs";
    import ThreadSubReplyItem from "./ThreadSubReplyItem.svelte";
    import ThreadReplyItemEdit from "./ThreadReplyItemEdit.svelte";

    // props
    export let classes = "";
    export let allowReply = false;
    export let allowActions = false;
    export let reply;
    export let onDelete;

    // local vars
    const currentUserId = getContext("currentUserId");
    let subReplies = reply.replies ? reply.replies : [];

    // reply toggle
    let showNewReplyInput = false;
    function toggleInput() {
        showNewReplyInput = !showNewReplyInput;
    }

    // edit mode
    let editMode = false;
    function toggleEditMode() {
        editMode = !editMode;
    }

    // delete this
    let loadingDeleteThis = false;
    async function deleteThis() {
        if (loadingDeleteThis) return;
        loadingDeleteThis = true;
        const { ok } = await deleteReply(reply.id);
        loadingDeleteThis = false;
        if (ok) {
            onDelete(reply);
        }
    }

    // update this
    async function updateThis(r) {
        reply = r;
        toggleEditMode();
    }

    // sub-reply
    function onSubReplyCreated(r) {
        subReplies = [...subReplies, r];
        toggleInput();
    }

    function onSubReplyDeleted(r) {
        subReplies = subReplies.filter((sr) => sr.id !== r.id);
    }
</script>

<div class="card-note p-1 {classes}">
    <div class="card-header">
        <a href={reply.user.url}>
            <div class="media align-items-center">
                <img
                    alt="{reply.user.username} avatar"
                    src={reply.user.avatar}
                    class="avatar"
                />
                <div class="media-body">
                    <h6 class="mb-0">{reply.user.username}</h6>
                </div>
            </div>
        </a>
        <div class="d-flex align-items-center" style="font-size: smaller;">
            <span>{dayjs(reply.created).fromNow()}</span>
            {#if allowActions}
                <span class="mx-1">/</span>
                <a href={"#"} on:click|preventDefault={toggleEditMode}>
                    edit
                </a>
                <span class="mx-1">/</span>
                <a
                    href={"#"}
                    class="text-danger"
                    on:click|preventDefault={deleteThis}
                >
                    {loadingDeleteThis ? "menghapus..." : "hapus"}
                </a>
            {/if}
        </div>
    </div>
    <div class="card-body text-dark">
        {#if editMode && allowActions}
            <ThreadReplyItemEdit
                {reply}
                onCreate={() => {}}
                onUpdate={updateThis}
                onCancel={toggleEditMode}
            />
        {:else}
            {@html parse(reply.message)}
        {/if}
        <div class="mt-4 bg-light">
            <!-- sub replies -->
            {#if subReplies.length > 0}
                <div class="mb-1 text-muted">Komentar</div>
                {#each subReplies as sr, index (sr.id)}
                    <ThreadSubReplyItem
                        {index}
                        reply={sr}
                        allowActions={currentUserId === sr.user.id}
                        onDelete={onSubReplyDeleted}
                    />
                {/each}
            {/if}

            <!-- input -->
            {#if showNewReplyInput}
                <div class="mt-2">
                    <ThreadReplyItemEdit
                        reply={{}}
                        parent={reply}
                        useMarkdownEditor={false}
                        onCreate={onSubReplyCreated}
                        onUpdate={() => {}}
                        onCancel={toggleInput}
                    />
                </div>
            {/if}

            <!-- button -->
            {#if allowReply && !showNewReplyInput}
                <div class="py-1">
                    <a
                        href={"#"}
                        class="text-muted"
                        on:click|preventDefault={toggleInput}
                    >
                        <small> Beri komentar </small>
                    </a>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .sub-reply {
        font-size: smaller;
    }
</style>
