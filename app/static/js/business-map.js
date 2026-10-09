(() => {
  const element = document.getElementById("business-map");
  if (!element || !window.L) return;
  const latitude = Number(element.dataset.latitude);
  const longitude = Number(element.dataset.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

  const map = L.map(element, {
    attributionControl: false,
    zoomControl: false,
    scrollWheelZoom: false,
  }).setView([latitude, longitude], 16);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
  }).addTo(map);
  L.circleMarker([latitude, longitude], {
    radius: 10,
    color: "#ffffff",
    weight: 3,
    fillColor: getComputedStyle(document.body).getPropertyValue("--brand").trim() || "#ea580c",
    fillOpacity: 1,
  }).addTo(map);
})();
