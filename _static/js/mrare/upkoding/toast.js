const showMainToast = ($, title, message) => {
  const toastMain = $("#toast-main");
  const toastMainText = $("#toast-main .toast-main-text");
  toastMainText.text(message);
  toastMain.toast({ delay: 5000 });
  toastMain.toast("show");
};

export default showMainToast;
