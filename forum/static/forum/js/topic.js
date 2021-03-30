function topic() {
  return {
    errors: {},
    submit(e) {
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
          } else {
            this.errors = await resp.json();
          }
        })
        .finally(() => {});
    },
  };
}
