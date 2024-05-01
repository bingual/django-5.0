(function () {
    observeNodeInsertion("#default-modal", (modalEl) => {
        const submitButtonEl = modalEl.querySelector("button[type=submit]");
        if (submitButtonEl) {
            submitButtonEl.onclick = () => {
                const formEl = modalEl.querySelector("form");
                if (formEl) {
                    if (window.htmx) htmx.trigger(formEl, "submit");
                    else formEl.dispatchEvent(new CustomEvent("submit"));
                }
            };
        } else {
            console.warn("not found submit button.");
        }
    });

})();