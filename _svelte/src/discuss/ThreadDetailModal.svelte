<script>
    import { onMount, onDestroy, getContext } from "svelte";
    import { listReply, createOrUpdateReply } from "../common/api";
    import ThreadReplyItem from "./ThreadReplyItem.svelte";
    import MarkdownEditor from "./MarkdownEditor.svelte";

    export let thread;
    export let theme = "info";
    export let title;
    export let backdrop = true;
    export let onClose;

    const currentUserId = getContext("currentUserId");
    let modalId = "thread-detail-modal";
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

    function onDeleteReply(reply) {
        replies = replies.filter((r) => r.id !== reply.id);
    }

    function onDeleteNewReply(reply) {
        newReplies = newReplies.filter((r) => r.id !== reply.id);
    }

    onMount(async () => {
        jQuery(modalIdSelector)
            .on("hide.bs.modal", async () => {
                onClose();
            })
            .modal({ backdrop: backdrop });

        // if replies is not empty (we already open the modal previously), don't call the API
        if (replies.length == 0) {
            await getReplies();
        }
    });

    onDestroy(() => {
        jQuery(modalIdSelector).modal("hide");
    });
</script>

<div class="modal fade" id={modalId} tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
            <div class="modal-header bg-{theme} d-flex justify-content-between">
                <h5 class="modal-title">{title}</h5>
                <a href={"#"}>
                    <span
                        class="material-icons text-light"
                        on:click|preventDefault={onClose}
                    >
                        close
                    </span>
                </a>
            </div>
            <div class="modal-body p-0">
                <ThreadReplyItem
                    reply={{
                        user: thread.user,
                        created: thread.created,
                        message: thread.description,
                    }}
                    onDelete={() => {}}
                />

                {#each replies as reply (reply.id)}
                    <ThreadReplyItem
                        {reply}
                        allowReply={currentUserId !== null}
                        allowActions={currentUserId == reply.user.id}
                        classes="bg-light border-top"
                        onDelete={onDeleteReply}
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
                        {reply}
                        classes="bg-light border-top"
                        allowReply={currentUserId !== null}
                        allowActions={currentUserId == reply.user.id}
                        onDelete={onDeleteNewReply}
                    />
                {/each}
            </div>

            <div class="p-4">
                {#if currentUserId}
                    <h5>Jawaban kamu</h5>
                    <MarkdownEditor
                        reset={replyEditorReset}
                        onChange={(v) => (replyMessage = v)}
                    />
                    {#if submitReplyErrors && submitReplyErrors.message}
                        <small class="form-text text-danger">
                            {submitReplyErrors.message}
                        </small>
                    {/if}

                    <div class="d-flex justify-content-between mt-2">
                        <small>Format jawaban ditulis dalam Markdown.</small>
                        <button class="btn btn-info" on:click={submitReply}>
                            {submittingReply
                                ? "Submitting..."
                                : "Submit Jawaban"}
                        </button>
                    </div>
                {:else}
                    <p class="text-center text-muted">
                        <span class="material-icons-x">lock</span>
                        Silahkan <a href="/account/login/">login</a> untuk memberi
                        komentar.
                    </p>
                {/if}
            </div>
        </div>
    </div>
</div>
