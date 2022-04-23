<script>
    export let onEdit;
    export let onDelete;
    export let loading = false;
</script>

<div class="ml-2 dropdown">
    <button
        class="btn-options"
        type="button"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
    >
        <i class="material-icons">more_vert</i>
    </button>
    <div class="dropdown-menu dropdown-menu-right">
        <span class="dropdown-item" on:click={onEdit}> Edit </span>
        <span class="dropdown-item text-danger" on:click={onDelete}>
            {loading ? "Menghapus..." : "Hapus"}
        </span>
    </div>
</div>

<style>
    .dropdown-item {
        cursor: pointer;
    }
    .material-icons {
        opacity: 0.5;
    }
</style>
