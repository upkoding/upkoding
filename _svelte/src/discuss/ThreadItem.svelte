<script>
    import { tick, getContext } from "svelte";
    import dayjs from "../common/dayjs";
    import { deleteThread, createOrUpdateThread } from "../common/api";
    import ConfirmationModal from "./ConfirmationModal.svelte";
    import ThreadFormModal from "./ThreadFormModal.svelte";
    import ThreadDetailModal from "./ThreadDetailModal.svelte";

    export let thread;
    export let onDelete;

    const currentUserId = getContext("currentUserId");
    let showEditModal = false;
    let showConfirmDeleteModal = false;
    let showDetailModal = false;
    let loading = false;
    let errors;

    $: reply_count =
        thread.stats && thread.stats.reply_count ? thread.stats.reply_count : 0;

    function openEditForm() {
        showEditModal = true;
    }

    function closeEditForm() {
        showEditModal = false;
        errors = null;
    }

    function openConfirmForm() {
        showConfirmDeleteModal = true;
    }

    function closeConfirmForm() {
        showConfirmDeleteModal = false;
    }

    function openDetail() {
        showDetailModal = true;
    }
    function closeDetail() {
        showDetailModal = false;
    }

    async function _deleteThread() {
        loading = true;
        const { ok } = await deleteThread(thread.id);
        loading = false;
        if (ok) {
            closeConfirmForm();
            await tick();
            onDelete(thread);
        } else {
            alert("Gagal menghapus pertanyaan!");
        }
    }

    async function _updateThread(t) {
        if (loading) return;

        loading = true;
        const { ok, data } = await createOrUpdateThread(t);
        loading = false;
        if (ok) {
            closeEditForm();
            await tick();
            thread = data;
        } else {
            errors = data;
        }
    }
</script>

<div class="media chat-item px-2 py-2 m-0 d-flex justify-content-between">
    <div class="media-body" on:click={openDetail}>
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

    {#if thread.user.id === currentUserId}
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
                <span class="dropdown-item" on:click={openEditForm}>
                    Edit
                </span>
                <span
                    class="dropdown-item text-danger"
                    on:click={openConfirmForm}
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
        onClose={closeConfirmForm}
        onConfirm={_deleteThread}
    />
{/if}

{#if showEditModal}
    <ThreadFormModal
        theme="info"
        title="Edit Pertanyaan"
        btnText="Simpan"
        btnTextLoading="Menyimpan..."
        {thread}
        {loading}
        {errors}
        onClose={closeEditForm}
        onSubmit={_updateThread}
    />
{/if}

{#if showDetailModal}
    <ThreadDetailModal
        theme="info"
        title={thread.title}
        {thread}
        onClose={closeDetail}
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
