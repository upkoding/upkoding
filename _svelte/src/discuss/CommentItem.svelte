<script>
    import dayjs from "../common/dayjs";

    export let comment;
</script>

<div class="media chat-item px-2 py-3 m-0">
    <!-- <img alt={comment.user.username} src={comment.user.avatar} class="avatar" /> -->
    <div class="media-body">
        <div class="chat-item-body">
            <h6>
                <i class="material-icons-x mr-1">comment</i>
                {comment.title}
            </h6>
        </div>
        <div class="chat-item-title mx-3 mb-0">
            <!-- <span class="chat-item-author"></span> -->
            <span class="text-small">
                oleh <a href={comment.user.url}>{comment.user.username}</a>
                {dayjs(comment.created).fromNow()}
            </span>
        </div>
    </div>
</div>
