import jQuery from "jquery";

(($) => {
  let loading = false;
  const blockId = $("#codeblock-editor").data("block-id");
  const codeblockForm = $("#codeblock-form");
  const codeblockRun = $("#codeblock-run");
  const codeblockOutput = $("#codeblock-output");
  const codeblockSuccess = $("#codeblock-success");
  const codeblockSuccessAction = $("#codeblock-success-action");

  function setLoading(yes) {
    loading = yes;
    if (yes) {
      codeblockRun.text(codeblockRun.data("text-loading"));
    } else {
      codeblockRun.text(codeblockRun.data("text"));
    }
  }

  function renderOutput(output) {
    if (output.length > 0) {
      let text = "";
      output.forEach((o) => {
        text += text === "" ? `>> ${o.title}` : `\n\n>> ${o.title}`;
        if (o.text !== null) {
          text += `\n${o.text}`;
        }
      });
      codeblockOutput.text(text).removeClass("d-none");
    } else {
      codeblockOutput.text("").addClass("d-none");
    }
  }

  codeblockSuccessAction.on("click", () => {
    codeblockSuccess.modal("hide");
    window.location.reload();
  });

  codeblockForm.on("submit", (e) => {
    e.preventDefault();
    if (loading) return;

    setLoading(true);

    const form = new FormData();
    form.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
    form.append("action", "code_submission");
    form.append("code_block_id", blockId);
    form.append("code_block", editor.getValue());

    let output = [];

    fetch("", {
      method: "post",
      body: form,
    })
      .then(async (resp) => {
        const data = await resp.json();

        if (resp.ok) {
          const { completed, result } = data;
          const {
            compile_output,
            is_expecting_output,
            is_output_match,
            status,
            stderr,
            stdout,
          } = result;
          const { description } = status;

          // compile output
          if (compile_output !== null) {
            output.push({ title: "Compile output", text: compile_output });
          }

          // stderr
          if (stderr !== null) {
            output.push({ title: description, text: stderr });
          }

          // stdout
          if (stdout !== null) {
            output.push({ title: "Output", text: stdout });
          }

          if (completed) {
            codeblockSuccess.modal({ backdrop: "static" });
          } else {
            if (is_expecting_output && !is_output_match && stderr === null) {
              output.push({
                title: description,
                text: "Output program tidak sesuai dengan yang diharapkan!",
              });
            }
            renderOutput(output);
          }
        } else {
          // error
          let error = null;

          Object.entries(data).forEach((item) => {
            error = item[1][0].message;
          });

          output.push({ title: error, text: null });
          renderOutput(output);
        }
      })
      .finally((_) => {
        setLoading(false);
      });
  });
})(jQuery);
