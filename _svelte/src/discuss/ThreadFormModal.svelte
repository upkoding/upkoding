<script>
    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import MarkdownEditor from "./MarkdownEditor.svelte";

    export let thread = { title: "", description: "" };
    export let theme = "info";
    export let title;
    export let backdrop = true;
    export let loading = false;
    export let errors = null;
    export let btnText;
    export let btnTextLoading = "Loading...";

    let modalId = "thread-form-modal";
    let modalIdSelector = "#" + modalId;

    const dispatch = createEventDispatcher();

    function submit() {
        dispatch("submit", thread);
    }

    function close() {
        dispatch("close");
    }

    onMount(() => {
        jQuery(modalIdSelector)
            .on("hide.bs.modal", () => {
                close();
            })
            .modal({ backdrop: backdrop });
    });

    onDestroy(() => {
        jQuery(modalIdSelector).modal("hide");
    });
</script>

<div
    class="modal fade"
    id={modalId}
    tabindex="-1"
    aria-hidden="true"
>
    <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
        <div class="modal-content">
            <div class="modal-header bg-{theme}">
                <h5 class="modal-title">{title}</h5>
            </div>
            <div class="modal-body">
                <form class="chat-form">
                    <label for="title">
                        <strong>Judul pertanyaan</strong>
                    </label>
                    <input
                        id="title"
                        type="text"
                        class="form-control form-control-lg"
                        required
                        bind:value={thread.title}
                    />
                    <small class="form-text text-muted">
                        Berusahalah spesifik tentang yang kamu tanyakan.
                    </small>
                    {#if errors && errors.title}
                        <small class="form-text text-danger">
                            Judul tidak boleh kosong.
                        </small>
                    {/if}

                    <div class="mt-3" />
                    <label for="description">
                        <strong>Detail pertanyaan</strong>
                    </label>
                    <MarkdownEditor
                        id="description"
                        bind:value={thread.description}
                    />
                    <small class="form-text text-muted">
                        Sertakan informasi yang cukup untuk mempermudah orang
                        lain menjawab pertanyaan kamu. (format: Markdown)
                    </small>
                    {#if errors && errors.description}
                        <small class="form-text text-danger">
                            Detail pertanyaan tidak boleh kosong.
                        </small>
                    {/if}
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-{theme}" type="submit" on:click={submit}>
                    {loading ? btnTextLoading : btnText}
                </button>
            </div>
        </div>
    </div>
</div>
