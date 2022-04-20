<script>
    import { createEventDispatcher } from "svelte";
    import { parseInline } from "../common/markdown";
    import { createOrUpdateReply } from "../common/api";
    import dayjs from "../common/dayjs";
    export let index;
    export let reply;

    const dispatch = createEventDispatcher();
    async function updateReply() {
        const { ok, data } = await createOrUpdateReply(reply);
        if (ok) {
            reply = data;
        }
    }
</script>

<div class="border-bottom py-2 sub-reply {index == 0 ? 'border-top' : ''}">
    {@html parseInline(reply.message)}
    - <a href={reply.user.url}>{reply.user.username}</a>
    <span class="text-muted">
        &middot; {dayjs(reply.created).fromNow()}
    </span>
</div>
