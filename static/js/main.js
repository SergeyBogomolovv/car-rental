// Год в подвале и счетчик символов в отзыве.
const year = document.getElementById("current-year");
if (year) year.textContent = new Date().getFullYear();

const review = document.getElementById("id_text");
if (review) {
  const counter = document.createElement("div");
  counter.className = "form-text";
  counter.setAttribute("aria-live", "polite");
  review.after(counter);

  function updateCounter() {
    counter.textContent = `Символов: ${review.value.length}`;
  }
  review.addEventListener("input", updateCounter);
  updateCounter();
}
