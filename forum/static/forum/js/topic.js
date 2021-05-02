function topic() {
  return {
    errors: {},
    showForm: false,
    creatingThread: false,
    createThread(e) {
      if (this.loding) return;
      this.creatingThread = true;
      this.errors = {};

      fetch(e.target.action, {
        method: "POST",
        body: new FormData(e.target),
      })
        .then(async (resp) => {
          if (resp.ok) {
            this.$refs.threads.insertAdjacentHTML(
              "afterbegin",
              await resp.text()
            );
            this.errors = {};
            e.target.reset();
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {
          this.creatingThread = false;
        });
    },
  };
}
