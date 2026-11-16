const journey = document.querySelector(".shell");
const panels = Array.from(document.querySelectorAll(".journey-panel"));
const milestones = Array.from(document.querySelectorAll("[data-booking-step]"));
const prev = $("journeyPrev");
const next = $("journeyNext");
const submitActions = $("journeySubmit");
let stage = 0;

function renderJourney() {
  const book = JOURNEY[lang];
  journey.dataset.stage = String(stage);
  panels.forEach((panel, i) => { panel.hidden = i !== stage; });
  milestones.forEach((item, i) => {
    item.textContent = book[i];
    item.classList.toggle("is-complete", i < stage);
    if (i === stage) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
  document.querySelector('label[for="endDate"]').textContent =
    ["night","personNight"].includes(selected.unit) ? book[8] : txt().endDate;
  prev.textContent = book[3];
  next.textContent = stage === 0 ? book[4] : book[5];
  $("journeyReviewTitle").textContent = book[2];
  $("journeyReviewHint").textContent = book[6];
  prev.hidden = stage === 0;
  next.hidden = stage === 2;
  submitActions.hidden = stage !== 2;
}

function goToStage(value) {
  stage = value;
  renderJourney();
  panels[stage].querySelector("h2").focus();
  journey.scrollIntoView({block:"start"});
}

function validateDetails() {
  const end = $("endDate");
  const start = $("date");
  const stay = ["night","personNight"].includes(selected.unit);
  end.required = stay;
  end.setCustomValidity("");
  if (start.value && end.value && (end.value < start.value || (stay && end.value === start.value))) {
    end.setCustomValidity(JOURNEY[lang][7]);
  }
  const people = $("people");
  const limit = selected.id === "camp" ? 14 : 50;
  people.min = selected.id === "rafting4" ? 4 : 1;
  people.max = limit;
  for (const field of panels[1].querySelectorAll("input, select, textarea")) {
    if (!field.reportValidity()) return false;
  }
  return true;
}

$("endDate").addEventListener("input", () => $("endDate").setCustomValidity(""));
$("date").addEventListener("input", () => $("endDate").setCustomValidity(""));
prev.addEventListener("click", () => goToStage(stage - 1));
next.addEventListener("click", () => {
  if (stage === 0 || (stage === 1 && validateDetails())) goToStage(stage + 1);
});
