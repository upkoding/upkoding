<script>
    export let loading;
</script>

<div class="media align-items-center text-center py-3">
    <div class="media-body">
        <h5 class="mb-1 text-muted">
            <i class="material-icons">question_answer</i>
        </h5>
        <p>{loading ? "Memuat diskusi..." : "Belum ada diskusi."}</p>
    </div>
</div>
