export default function toast(message) {
    const toastMain = jQuery("#toast-main");
    const toastMainText = jQuery("#toast-main .toast-main-text");
    toastMainText.text(message);
    toastMain.toast("show");
};