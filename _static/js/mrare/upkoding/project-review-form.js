import "regenerator-runtime/runtime"; // fix: https://flaviocopes.com/parcel-regeneratorruntime-not-defined/
import jQuery from "jquery";

const projectReviewForm = (($) => {
  const reviewForm = $("#timeline-form");
  const reviewFormMessage = $("#timeline-form #timeline-input-message");
  const reviewActionBtn = $("#timeline-form .timeline-btn-action");
  const reviewAlertMessage = $("#timeline-form #timeline-alert");

  let loading = false;

  function showAlert(alertType, message) {
    reviewAlertMessage
      .removeClass("alert-success alert-danger")
      .text(message)
      .addClass(alertType)
      .removeClass("d-none");
  }

  function runReviewAction(target) {
    if (loading) return;

    const btn = $(target);
    const action = btn.data("action");
    btn.text(btn.data("loading-text"));

    fetch(reviewForm.data("url"), {
      method: "post",
      headers: {
        "x-CSRFToken": window.csrfmiddlewaretoken,
        "Content-Type": "application/javascript",
      },
      body: JSON.stringify({
        action: action,
        message: reviewFormMessage.val(),
      }),
    })
      .then(async (resp) => {
        if (resp.ok) {
          const { message, html } = await resp.json();
          if (message !== null) showAlert("alert-success", message);
          if (html !== null) reviewForm.before(html);
        } else {
          showAlert("alert-danger", await resp.text());
        }
      })
      .finally(() => {
        loading = false;
        reviewFormMessage.val("");
        btn.text(btn.data("text"));
      });
  }

  reviewActionBtn.on("click", (e) => {
    runReviewAction(e.target);
  });
})(jQuery);

export default projectReviewForm;
