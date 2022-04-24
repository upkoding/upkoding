import { marked } from "marked";
import DOMPurify from 'dompurify';
import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";

// markdown handler
marked.setOptions({
    highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : "plaintext";
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: "hljs language-"
});

export function parse(input) {
    return DOMPurify.sanitize(marked.parse(input))
}

export function parseInline(input) {
    return DOMPurify.sanitize(marked.parseInline(input))
}