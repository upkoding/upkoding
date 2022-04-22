<script>
    import { onMount } from "svelte";
    import "codemirror/lib/codemirror.css";
    import "codemirror/mode/markdown/markdown";
    import "codemirror/addon/display/autorefresh";
    import CodeMirror from "codemirror";

    export let value = "";
    export let width = "100%";
    export let height = 150;
    export let reset = 0; // if reset value > 0 and keep changing, we'll reset
    export let onChange;

    let textArea;
    let editor;

    onMount(() => {
        editor = CodeMirror.fromTextArea(textArea, {
            lineWrapping: true,
            mode: "markdown",
            autoRefresh: true,
        });
        editor.setSize(width, height);
        editor.on("change", (e) => {
            onChange(e.getDoc().getValue());
        });
        return () => {
            editor.toTextArea();
        };
    });

    $: if (reset > 0 && editor !== undefined) {
        editor.setValue("");
        editor.clearHistory();
    }
</script>

<div class="editor-container">
    <textarea bind:this={textArea} {value} />
</div>

<style>
    .editor-container :global(.cm-header) {
        color: black;
    }

    .editor-container :global(.cm-header-1) {
        font-size: 200%;
    }

    .editor-container :global(.cm-header-2) {
        font-size: 150%;
    }

    .editor-container :global(.cm-header-3) {
        font-size: 120%;
    }

    .editor-container {
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
    }

    .editor-container :global(.CodeMirror-cursor) {
        border-left: 2px solid rgb(26, 154, 240);
    }
</style>
