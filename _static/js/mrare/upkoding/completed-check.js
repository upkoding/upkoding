import jQuery from "jquery";

(($) => {
  const challenges = $(".fetch-completion-status");
  if (challenges.length) {
    const ids = [];
    challenges.each(function () {
      ids.push($(this).data("id"));
    });
    fetch("/challenges/statuses/?" + new URLSearchParams({ ids: ids }), {
      method: "get",
    }).then(async (resp) => {
      if (resp.ok) {
        const { statuses } = await resp.json();
        statuses
          .filter((s) => s.complete === true)
          .forEach((status) => {
            $(".project-stats-" + status.id).addClass("d-none");
            $(".project-completed-" + status.id).removeClass("d-none");
          });
      }
    });
  }
})(jQuery);
