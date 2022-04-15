<script>
    import { onMount, createEventDispatcher } from "svelte";

    export let key = 0; // to make sure modal has unique ID
    export let theme = "danger";
    export let backdrop = true;
    export let show = false;
    export let title = "Konfirmasi";
    export let message = null;
    export let loading = false;
    export let btnText;
    export let btnTextLoading = "Loading...";

    let modalId = "confirm-modal" + key;
    let modalIdSelector = "#" + modalId;

    const dispatch = createEventDispatcher();
    onMount(() => {
        jQuery(modalIdSelector).on("hide.bs.modal", (e) => {
            show = false;
        });
    });

    $: if (show) {
        jQuery(modalIdSelector).modal({ backdrop: backdrop });
    } else {
        jQuery(modalIdSelector).modal("hide");
    }

    function confirm() {
        dispatch("confirm", true);
    }
</script>

<div
    class="modal model-{theme} fade"
    id={modalId}
    tabindex="-1"
    aria-hidden="true"
>
    <div class="modal-dialog" role="document">
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
