<script>
    import { createEventDispatcher } from "svelte";
    import { parseInline } from "../common/markdown";
    import { createOrUpdateReply, deleteReply } from "../common/api";
    import dayjs from "../common/dayjs";

    // props
    export let index;
    export let reply;
    export let allowActions = true;

    const dispatch = createEventDispatcher();
    // update
    async function updateThis() {
        const { ok, data } = await createOrUpdateReply(reply);
        if (ok) {
            reply = data;
        }
    }

    // delete
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
</script>

<div class="border-bottom py-2 sub-reply {index == 0 ? 'border-top' : ''}">
    {@html parseInline(reply.message)}
    -
    <small>
        <a href={reply.user.url}>{reply.user.username}</a>
        <span class="text-muted">
            &middot; {dayjs(reply.created).fromNow()}
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
        </span>
    </small>
</div>
