const featureImage = $("bookingFeaturePhoto");
const featureTitle = $("bookingFeatureTitle");
const featureDetail = $("bookingFeatureDetail");

function updateFeature() {
  const photo = PHOTO[selected.id === "quadDuo" ? "quad" : selected.id] || PHOTO.other;
  if (featureImage.getAttribute("src") !== photo) featureImage.src = photo;
  featureTitle.textContent = selected.name[lang];
  featureDetail.textContent = D[selected.detail]?.[["fr","en","es","ar"].indexOf(lang)] || "";
  const stay = ["night","personNight"].includes(selected.unit);
  $("endDate").required = stay;
  document.querySelector('label[for="endDate"]').textContent = stay ? EDITORIAL[lang][0] : txt().endDate;
  $("endDate").setCustomValidity("");
  $("people").min = selected.id === "rafting4" ? 4 : 1;
  $("people").max = selected.id === "camp" ? 14 : 50;
}

for (const id of ["date","endDate"]) {
  $(id).addEventListener("input", () => $("endDate").setCustomValidity(""));
}
