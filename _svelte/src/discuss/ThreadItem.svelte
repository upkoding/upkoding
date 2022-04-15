<script>
    import { createEventDispatcher, tick } from "svelte";
    import dayjs from "../common/dayjs";
    import { deleteThread, createOrUpdateThread } from "../common/api";
    import ConfirmationModal from "./ConfirmationModal.svelte";
    import ThreadFormModal from "./ThreadFormModal.svelte";

    export let thread;
    export let current_user_id;

    const dispatch = createEventDispatcher();
    let showEditModal = false;
    let showConfirmDeleteModal = false;
    let loading = false;
    let errors;

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

<div class="media chat-item px-2 py-3 m-0 d-flex justify-content-between">
    <!-- <img alt={thread.user.username} src={thread.user.avatar} class="avatar" /> -->

    <div class="media-body">
        <div class="chat-item-body">
            <h6>
                <i class="material-icons-x mr-1">question_answer</i>
                {thread.title}
            </h6>
        </div>
        <div class="chat-item-title mx-3 mb-0">
            <!-- <span class="chat-item-author"></span> -->
            <span class="text-small">
                oleh <a href={thread.user.url}>{thread.user.username}</a>
                {dayjs(thread.created).fromNow()} &middot;
                <a href="">2 balasan</a>
            </span>
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

<ConfirmationModal
    key={thread.id}
    title="Hapus pertanyaan kamu?"
    btnText="Hapus"
    btnTextLoading="Menghapus..."
    {loading}
    bind:show={showConfirmDeleteModal}
    on:confirm={_deleteThread}
/>

<ThreadFormModal
    key={thread.id}
    theme="primary"
    title="Edit Pertanyaan"
    {thread}
    btnText="Simpan"
    btnTextLoading="Menyimpan..."
    {loading}
    {errors}
    bind:show={showEditModal}
    on:submit={_updateThread}
/>

<style>
    .dropdown-item,
    h6 {
        cursor: pointer;
    }
</style>
