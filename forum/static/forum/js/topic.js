function topic() {
  return {
    errors: {},
    createThread(e) {
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
        .finally(() => {});
    },
  };
}
