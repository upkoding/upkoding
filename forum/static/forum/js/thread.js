function thread() {
  return {
    errors: {},
    replyErrors: {},
    reply: null,
    updatingThread: false,
    deletingThread: false,
    updateThread(e) {
      if (this.updatingThread) return;

      this.updatingThread = true;
      this.errors = {};

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
        .finally(() => {
          this.updatingThread = false;
        });
    },
    deleteThread(e) {
      const threadId = e.target.getAttribute("data-id");
      const redirectTo = e.target.getAttribute("data-redirect");
      fetch(`/forum/api/threads/${threadId}`, {
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
    __createAnswer(e, cb) {
      fetch(e.target.action, {
        method: "POST",
        body: new FormData(e.target),
      })
        .then(cb)
        .finally(() => {});
    },
    createAnswer(e) {
      this.__createAnswer(e, async (resp) => {
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
      });
    },
    createReply(e) {
      const answerId = e.target.getAttribute("data-id");
      this.__createAnswer(e, async (resp) => {
        if (resp.ok) {
          this.$refs[`reply_form_${answerId}`].insertAdjacentHTML(
            "beforebegin", // before reply form
            await resp.text()
          );
          e.target.reset();
          this.replyErrors = {};
        } else {
          this.replyErrors = await resp.json();
        }
      });
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
    deleteAnswer(e) {
      const answerId = e.target.getAttribute("data-id");
      const parentId = e.target.getAttribute("data-parent");
      fetch(`/forum/api/answers/${answerId}`, {
        method: "DELETE",
        headers: {
          "x-CSRFToken": window.csrftoken,
        },
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs[`answer_${answerId}`].remove();

            // show reply form for parent answer
            if (parentId) {
              this.reply = parseInt(parentId);
            }
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
    showReply(id) {
      this.reply = id;
    },
  };
}
