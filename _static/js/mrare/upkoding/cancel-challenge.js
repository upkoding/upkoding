import jQuery from "jquery";
import showMainToast from "./toast";

(($) => {
  const btn = $(".cancel-challenge");
  const url = btn.data("challenge-url");

  btn.on("click", (e) => {
    showMainToast($, "Mohon ditunggu", "Sedang membatalkan tantangan...");

    const data = new FormData();
    data.append("action", "delete");
    data.append("csrfmiddlewaretoken", window.csrfmiddlewaretoken);

    fetch(url, {
      method: "post",
      body: data,
    }).then(async (resp) => {
      if (resp.ok) {
        window.location.href = await resp.text();
      } else {
        showMainToast($, "Oops!", "Gagal membatalkan tantangan.");
      }
    });
  });
})(jQuery);
