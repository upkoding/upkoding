<script>
    import { onMount, createEventDispatcher, onDestroy } from "svelte";

    export let theme = "danger";
    export let backdrop = true;
    export let title = "Konfirmasi";
    export let message = null;
    export let loading = false;
    export let btnText;
    export let btnTextLoading = "Loading...";

    let modalId = "confirm-modal";
    let modalIdSelector = "#" + modalId;

    const dispatch = createEventDispatcher();

    function confirm() {
        dispatch("confirm");
    }

    function close() {
        dispatch("close");
    }

    onMount(() => {
        jQuery(modalIdSelector).on("hide.bs.modal", (e) => {
            close();
        });
        jQuery(modalIdSelector).modal({ backdrop: backdrop });
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
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header bg-{theme}">
                <h5 class="modal-title">{title}</h5>
            </div>
            {#if message}
                <div class="modal-body">
                    <p>{message}</p>
                </div>
            {/if}
            <div class="modal-footer">
                <button
                    class="btn btn-{theme}"
                    type="submit"
                    on:click={confirm}
                >
                    {loading ? btnTextLoading : btnText}
                </button>
            </div>
        </div>
    </div>
</div>
