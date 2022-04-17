<script>
    import { marked } from "marked";
    import hljs from "highlight.js";
    import "highlight.js/styles/github-dark.css";
    import dayjs from "../common/dayjs";

    export let user;
    export let created;
    export let message;
    export let classes = "";

    marked.setOptions({
        highlight: function (code, lang) {
            const language = hljs.getLanguage(lang) ? lang : "plaintext";
            return hljs.highlight(code, { language }).value;
        },
        langPrefix: "hljs language-",
    });
</script>

<div class="card-note p-3 {classes}">
    <div class="card-header">
        <a href={user.url}>
            <div class="media align-items-center">
                <img
                    alt="{user.username} avatar"
                    src={user.avatar}
                    class="avatar"
                />
                <div class="media-body">
                    <h6 class="mb-0">{user.username}</h6>
                </div>
            </div>
        </a>
        <div class="d-flex align-items-center">
            <span>{dayjs(created).fromNow()}</span>
        </div>
    </div>
    <div class="card-body svelte">
        {@html marked.parse(message)}
    </div>
</div>

<style>
    :global(.hljs) {
        background: #0d1117 !important;
    }
</style>
