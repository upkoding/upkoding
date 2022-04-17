<script>
    import { onMount } from "svelte";
    import { listReply, createOrUpdateReply } from "../common/api";
    import ThreadReplyItem from "./ThreadReplyItem.svelte";
    import MarkdownEditor from "./MarkdownEditor.svelte";

    export let key = 0; // to make sure modal has unique ID
    export let thread;
    export let theme = "info";
    export let title;
    export let backdrop = true;
    export let show = false;

    let modalId = "thread-detail-modal" + key;
    let modalIdSelector = "#" + modalId;

    // all replies that comes from API
    let replies = [];
    // all replies created by current user inside this UI
    let newReplies = [];
    let loadingReplies = false;
    let nextRepliesURL;
    let replyMessage;
    let submitReplyErrors;
    let submittingReply;
    let replyEditorReset = 0;

    async function getReplies() {
        loadingReplies = true;
        const { ok, data } = await listReply(
            {
                thread: thread.id,
                level: 0,
            },
            nextRepliesURL
        );
        loadingReplies = false;
        if (ok) {
            nextRepliesURL = data.next;
            // if no more items (we're on last page), empty newreplies because newest replies will be included in this last page.
            // not perfect / there are edge cases but should be fine for now.
            if (nextRepliesURL === null) {
                newReplies = [];
            }
            replies = [...replies, ...data.results];
        }
    }

    async function submitReply() {
        if (submittingReply) return;

        const reply = {
            thread: thread.id,
            message: replyMessage,
        };
        submittingReply = true;
        const { ok, data } = await createOrUpdateReply(reply);
        submittingReply = false;
        if (ok) {
            newReplies = [...newReplies, data];
            replyEditorReset += 1;
            submitReplyErrors = null;
        } else {
            submitReplyErrors = data;
        }
    }

    onMount(async () => {
        jQuery(modalIdSelector).on("hide.bs.modal", async () => {
            show = false;
        });

        // call api only when modal is showing
        jQuery(modalIdSelector).on("show.bs.modal", async () => {
            // if replies is not empty (we already open the modal previously), don't call the API
            if (replies.length == 0) {
                await getReplies();
            }
        });
    });

    $: if (show) {
        jQuery(modalIdSelector).modal({ backdrop: backdrop });
    } else {
        jQuery(modalIdSelector).modal("hide");
    }
</script>

<div
    class="modal model-{theme} fade"
    id={modalId}
    tabindex="-1"
    aria-hidden="true"
>
    <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
            <div class="modal-header bg-{theme} d-flex justify-content-between">
                <h5 class="modal-title">{title}</h5>
                <a href="javascript;">
                    <span
                        class="material-icons text-light"
                        on:click|preventDefault={() => (show = false)}
                    >
                        close
                    </span>
                </a>
            </div>
            <div class="modal-body p-0">
                <ThreadReplyItem
                    user={thread.user}
                    message={thread.description}
                    created={thread.created}
                />
                {#if replies.length > 0 && !loadingReplies}
                    {#each replies as reply (reply.id)}
                        <ThreadReplyItem
                            user={reply.user}
                            message={reply.message}
                            created={reply.created}
                            classes="bg-light border-top"
                        />
                    {/each}
                    {#if nextRepliesURL}
                        <div
                            class="py-2 d-flex justify-content-center border-top border-bottom"
                        >
                            <a href={"#"} on:click|preventDefault={getReplies}>
                                <span class="material-icons-x mr-1">
                                    arrow_downward
                                </span>
                                {loadingReplies
                                    ? "Memuat..."
                                    : "Muat jawaban lainnya"}
                            </a>
                        </div>
                    {/if}
                    {#each newReplies as reply (reply.id)}
                        <ThreadReplyItem
                            user={reply.user}
                            message={reply.message}
                            created={reply.created}
                            classes="bg-light border-top"
                        />
                    {/each}
                {/if}
            </div>
            <div class="p-4">
                <h5>Jawaban kamu</h5>
                <MarkdownEditor
                    id={"thread-reply-" + thread.id}
                    reset={replyEditorReset}
                    bind:value={replyMessage}
                />
                {#if submitReplyErrors && submitReplyErrors.message}
                    <small class="form-text text-danger">
                        {submitReplyErrors.message}
                    </small>
                {/if}

                <div class="d-flex justify-content-between mt-2">
                    <small>Format jawaban ditulis dalam Markdown.</small>
                    <button class="btn btn-info" on:click={submitReply}>
                        {submittingReply ? "Submitting..." : "Submit Jawaban"}
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
