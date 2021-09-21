import jQuery from "jquery";

const projectReviewForm = (($) => {
  const reviewFormMessage = $("#timeline-form #timeline-input-message");
  const approveBtn = $("#timeline-form #timeline-btn-approve");
  const disapproveBtn = $("#timeline-form #timeline-btn-disapprove");
  const sendBtn = $("#timeline-form #timeline-btn-sendmessage");
  const alertMessage = $("#timeline-form #timeline-alert");

  approveBtn.on("click", () => {
    alert("approveBtn");
  });

  disapproveBtn.on("click", () => {
    alert("disapproveBtn");
  });

  sendBtn.on("click", () => {
    alert("sendBtn");
  });
})(jQuery);

export default projectReviewForm;
