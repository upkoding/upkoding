const showMainToast = ($, title, message) => {
  const toastMain = $("#toast-main");
  const toastMainTitle = $("#toast-main .toast-main-title");
  // const toastMainTime = $("#toast-main .toast-main-time");
  const toastMainText = $("#toast-main .toast-main-text");
  toastMainTitle.text(title);
  toastMainText.text(message);
  toastMain.toast("show");
};

export default showMainToast;
