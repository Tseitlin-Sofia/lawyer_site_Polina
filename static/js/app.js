/* Модальное окно заявки: подставляет выбранный вопрос и отправляет форму без перезагрузки. */
(function () {
  "use strict";

  const modal = document.getElementById("lead-modal");
  if (!modal) return;

  const form = modal.querySelector("form");
  const body = modal.querySelector(".modal__body");
  const done = modal.querySelector(".modal__done");
  const questionLabel = modal.querySelector("[data-question-text]");
  const templateInput = form.querySelector('[name="question_template"]');
  const customField = modal.querySelector("[data-custom-field]");
  const submitBtn = form.querySelector('[type="submit"]');
  let lastFocused = null;

  function openModal(questionId, questionText, needsCustom) {
    lastFocused = document.activeElement;
    templateInput.value = questionId || "";
    questionLabel.textContent = questionText;
    customField.hidden = !needsCustom;
    customField.querySelector("textarea").required = Boolean(needsCustom);
    clearErrors();
    body.hidden = false;
    done.classList.remove("is-visible");
    modal.classList.add("is-open");
    document.body.style.overflow = "hidden";
    const firstInput = form.querySelector('[name="name"]');
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
  }

  function closeModal() {
    modal.classList.remove("is-open");
    document.body.style.overflow = "";
    form.reset();
    if (lastFocused) lastFocused.focus();
  }

  function clearErrors() {
    modal.querySelectorAll(".field__error").forEach((el) => el.remove());
  }

  function showErrors(errors) {
    clearErrors();
    Object.keys(errors).forEach((name) => {
      const message = errors[name].join(" ");
      const input = form.querySelector('[name="' + name + '"]');
      const holder = input ? input.closest(".field") : form;
      const div = document.createElement("div");
      div.className = "field__error";
      div.textContent = message;
      holder.appendChild(div);
    });
  }

  document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => {
      openModal(
        button.dataset.question,
        button.dataset.questionText,
        button.dataset.custom === "1"
      );
    });
  });

  modal.querySelectorAll("[data-close]").forEach((el) =>
    el.addEventListener("click", closeModal)
  );

  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("is-open")) closeModal();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    submitBtn.disabled = true;
    const original = submitBtn.textContent;
    submitBtn.textContent = "Отправляю…";
    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const data = await response.json();
      if (data.ok) {
        body.hidden = true;
        done.classList.add("is-visible");
      } else {
        showErrors(data.errors || { __all__: ["Не получилось отправить. Попробуйте ещё раз."] });
      }
    } catch (err) {
      showErrors({ __all__: ["Нет связи с сервером. Проверьте интернет и попробуйте снова."] });
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = original;
    }
  });
})();
