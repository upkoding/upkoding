<script>
    import { parseInline } from "../common/markdown";
    import { deleteReply } from "../common/api";
    import dayjs from "../common/dayjs";
    import ThreadReplyItemEdit from "./ThreadReplyItemEdit.svelte";

    // props
    export let index;
    export let reply;
    export let allowActions = true;
    export let onDelete;

    // edit mode
    let editMode = false;
    function toggleEditMode() {
        editMode = !editMode;
    }

    // update
    async function updateThis(r) {
        reply = r;
        toggleEditMode();
    }

    // delete
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
</script>

<div class="border-bottom py-2 sub-reply {index == 0 ? 'border-top' : ''}">
    {#if editMode}
        <ThreadReplyItemEdit
            {reply}
            useMarkdownEditor={false}
            onCreate={() => {}}
            onCancel={toggleEditMode}
            onUpdate={updateThis}
        />
    {:else}
        {@html parseInline(reply.message)}
        -
        <small>
            <a href={reply.user.url}>{reply.user.username}</a>
            <span class="text-muted">
                &middot; {dayjs(reply.created).fromNow()}
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
            </span>
        </small>
    {/if}
</div>
