<script>
    import { createEventDispatcher } from "svelte";
    import { parse } from "../common/markdown";
    import { createOrUpdateReply, deleteReply } from "../common/api";
    import dayjs from "../common/dayjs";
    import ThreadSubReplyItem from "./ThreadSubReplyItem.svelte";

    const dispatch = createEventDispatcher();

    // props
    export let currentUserId;
    export let classes = "";
    export let allowReply = false;
    export let allowActions = false;
    export let reply;

    // local vars
    let subReplies = reply.replies ? reply.replies : [];

    // reply toggle
    let showNewReplyInput = false;
    function toggleInput() {
        showNewReplyInput = !showNewReplyInput;
    }

    // new reply
    let newReplyMessage = "";
    let loadingReplyThis = false;
    async function replyThis() {
        if (loadingReplyThis) return;

        const newReply = {
            message: newReplyMessage,
            thread: reply.thread,
            parent: reply.id,
        };
        loadingReplyThis = true;
        const { ok, data } = await createOrUpdateReply(newReply);
        loadingReplyThis = false;
        if (ok) {
            subReplies = [...subReplies, data];
            newReplyMessage = "";
            showNewReplyInput = false;
        }
    }

    // delete reply
    let loadingDeleteThis = false;
    async function deleteThis() {
        if (loadingDeleteThis) return;
        loadingDeleteThis = true;
        const { ok } = await deleteReply(reply.id);
        loadingDeleteThis = false;
        if (ok) {
            dispatch("delete", reply);
        }
    }

    // sub-reply deleted
    function onSubReplyDeleted({ detail }) {
        subReplies = subReplies.filter((sr) => sr.id !== detail.id);
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
                <a href={"#"}>edit</a>
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
        {@html parse(reply.message)}
        <div class="mt-4 bg-light">
            <!-- sub replies -->
            {#if subReplies.length > 0}
                <div class="mb-1 text-muted">Komentar</div>
                {#each subReplies as sr, index (sr.id)}
                    <ThreadSubReplyItem
                        {index}
                        reply={sr}
                        allowActions={currentUserId === sr.user.id}
                        on:delete={onSubReplyDeleted}
                    />
                {/each}
            {/if}

            <!-- input -->
            {#if showNewReplyInput}
                <div class="mt-2">
                    <textarea
                        rows="2"
                        placeholder="Beri komentar..."
                        class="form-control"
                        bind:value={newReplyMessage}
                    />
                    <div class="d-flex justify-content-end pt-1">
                        <a href={"#"} on:click|preventDefault={replyThis}>
                            <small>
                                {loadingReplyThis ? "Submitting..." : "Submit"}
                                <span class="material-icons-x">
                                    arrow_right
                                </span>
                            </small>
                        </a>
                    </div>
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
