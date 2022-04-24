<script>
    import { parseInline } from "../common/markdown";
    import { deleteReply } from "../common/api";
    import dayjs from "../common/dayjs";
    import ThreadReplyItemEdit from "./ThreadReplyItemEdit.svelte";
    import ItemAction from "./ItemAction.svelte";

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
        <div class="d-flex justify-content-between">
            <div>
                {@html parseInline(reply.message)}
                -
                <small>
                    <a href={reply.user.url}>{reply.user.username}</a>
                    <span class="text-muted">
                        &middot; {dayjs(reply.created).fromNow()}
                    </span>
                </small>
            </div>
            {#if allowActions}
                <ItemAction
                    onEdit={toggleEditMode}
                    onDelete={deleteThis}
                    loading={loadingDeleteThis}
                />
            {/if}
        </div>
    {/if}
</div>
