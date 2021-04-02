function thread() {
  return {
    errors: {},
    alert: {},
    updateThread(e) {
      fetch(e.target.action, {
        method: "POST",
        body: new FormData(e.target),
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs.cancel_edit_thread.click();
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
    deleteThread(id, redirectTo) {
      fetch(`/diskusi/api/threads/${id}`, {
        method: "DELETE",
        headers: {
          "x-CSRFToken": window.csrftoken,
        },
      })
        .then(async (resp) => {
          if (resp.ok) {
            window.location.href = redirectTo;
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
    createAnswer(e) {
      fetch(e.target.action, {
        method: "POST",
        body: new FormData(e.target),
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs.answer_form.insertAdjacentHTML(
              "beforebegin", // before answer form
              await resp.text()
            );
            e.target.reset();
            this.errors = {};
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
    updateAnswer(e) {
      fetch(e.target.action, {
        method: "POST",
        body: new FormData(e.target),
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs.cancel_edit_answer.click();
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
    deleteAnswer(id) {
      fetch(`/diskusi/api/answers/${id}`, {
        method: "DELETE",
        headers: {
          "x-CSRFToken": window.csrftoken,
        },
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs[`answer_${id}`].remove();
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
  };
}
