import jQuery from "jquery";

(($) => {
  const container = $("#global-activities");
  if (container.length) {
    const url = container.data("url");
    fetch(url, { method: "get" }).then(async (resp) => {
      if (resp.ok) {
        const content = await resp.text();
        container.append(content);
      }
    });
  }
})(jQuery);

(($) => {
  const container = $("#project-activities");
  if (container.length) {
    const url = container.data("url");
    fetch(url, { method: "get" }).then(async (resp) => {
      if (resp.ok) {
        const content = await resp.text();
        container.append(content);
      }
    });
  }
})(jQuery);

(($) => {
  const container = $("#notification-activities");
  if (container.length) {
    const url = container.data("url");
    fetch(url, { method: "get" }).then(async (resp) => {
      if (resp.ok) {
        const content = await resp.text();
        container.append(content);
      }
    });
  }
})(jQuery);
