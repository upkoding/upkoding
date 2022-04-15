<script>
    import { onMount, createEventDispatcher, tick } from "svelte";
    import MarkdownEditor from "./MarkdownEditor.svelte";

    export let key = 0; // to make sure modal has unique ID
    export let thread = { title: "", description: "" };
    export let theme = "info";
    export let title;
    export let backdrop = true;
    export let show = false;
    export let loading = false;
    export let errors = null;
    export let resetOnClose = false;
    export let btnText;
    export let btnTextLoading = "Loading...";

    let modalId = "thread-form-modal" + key;
    let modalIdSelector = "#" + modalId;
    let resetMarkdownEditor = 0;

    const dispatch = createEventDispatcher();
    onMount(() => {
        jQuery(modalIdSelector).on("hide.bs.modal", async () => {
            if (resetOnClose) resetForm();
            show = false;
        });
    });

    $: if (show) {
        jQuery(modalIdSelector).modal({ backdrop: backdrop });
    } else {
        jQuery(modalIdSelector).modal("hide");
    }

    function submit() {
        dispatch("submit", thread);
    }

    function resetForm() {
        errors = null;
        thread = {};
        resetMarkdownEditor += 1;
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
                        placeholder="Judul pertanyaan"
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
                        reset={resetMarkdownEditor}
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
