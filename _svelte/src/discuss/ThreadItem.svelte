<script>
    import { createEventDispatcher, tick } from "svelte";
    import dayjs from "../common/dayjs";
    import { deleteThread, createOrUpdateThread } from "../common/api";
    import ConfirmationModal from "./ConfirmationModal.svelte";
    import ThreadFormModal from "./ThreadFormModal.svelte";
    import ThreadDetailModal from "./ThreadDetailModal.svelte";

    export let thread;
    export let current_user_id;

    const dispatch = createEventDispatcher();
    let showEditModal = false;
    let showConfirmDeleteModal = false;
    let showDetailModal = false;
    let loading = false;
    let errors;

    $: reply_count =
        thread.stats && thread.stats.reply_count ? thread.stats.reply_count : 0;

    async function _deleteThread() {
        loading = true;
        const { ok } = await deleteThread(thread.id);
        loading = false;
        if (ok) {
            showConfirmDeleteModal = false;
            await tick();
            dispatch("delete", thread);
        } else {
            alert("Gagal menghapus pertanyaan!");
        }
    }

    async function _updateThread(e) {
        if (loading) return;

        loading = true;
        const { ok, data } = await createOrUpdateThread(e.detail);
        loading = false;
        if (ok) {
            showEditModal = false;
            await tick();
            thread = data;
        } else {
            errors = data;
        }
    }
</script>

<div class="media chat-item px-2 py-2 m-0 d-flex justify-content-between">
    <div class="media-body" on:click={() => (showDetailModal = true)}>
        <div class="chat-item-body">
            <h6>
                <i class="material-icons-x mr-1">question_answer</i>
                {thread.title}
            </h6>
        </div>
        <div class="chat-item-title mx-3 mb-0">
            <small class="text-small">
                oleh <a href={thread.user.url}>{thread.user.username}</a>
                {dayjs(thread.created).fromNow()}
                &middot;
                <span>{reply_count} jawaban</span>
            </small>
        </div>
    </div>

    {#if thread.user.id === current_user_id}
        <div class="ml-1 dropdown card-options">
            <button
                class="btn-options"
                type="button"
                id="..."
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
            >
                <i class="material-icons">more_vert</i>
            </button>
            <div class="dropdown-menu dropdown-menu-right">
                <span
                    class="dropdown-item"
                    on:click={() => (showEditModal = true)}
                >
                    Edit
                </span>
                <span
                    class="dropdown-item text-danger"
                    on:click={() => (showConfirmDeleteModal = true)}
                >
                    Hapus
                </span>
            </div>
        </div>
    {/if}
</div>

{#if showConfirmDeleteModal}
    <ConfirmationModal
        title="Hapus pertanyaan kamu?"
        btnText="Hapus"
        btnTextLoading="Menghapus..."
        {loading}
        on:close={() => (showConfirmDeleteModal = false)}
        on:confirm={_deleteThread}
    />
{/if}

{#if showEditModal}
    <ThreadFormModal
        theme="info"
        title="Edit Pertanyaan"
        {thread}
        btnText="Simpan"
        btnTextLoading="Menyimpan..."
        {loading}
        {errors}
        on:close={() => (showEditModal = false)}
        on:submit={_updateThread}
    />
{/if}

{#if showDetailModal}
    <ThreadDetailModal
        theme="info"
        title={thread.title}
        {thread}
        on:close={() => (showDetailModal = false)}
    />
{/if}

<style>
    .dropdown-item,
    h6,
    .media-body {
        cursor: pointer;
    }

    .text-small {
        font-size: smaller;
    }
</style>
