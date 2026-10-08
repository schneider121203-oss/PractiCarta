(() => {
  const linkInput = document.querySelector('[data-menu-link]');
  const nameInput = document.querySelector('#id_name');
  const preview = document.querySelector('[data-menu-link-preview]');
  const previewValue = preview?.querySelector('strong');
  const warning = preview?.querySelector('[data-link-warning]');
  const palette = document.querySelector('[data-palette-select]');
  const color = document.querySelector('#id_primary_color');
  const secondaryColor = document.querySelector('#id_secondary_color');
  const colors = {sunset:['#ea580c','#3c2417'], ocean:['#1677c8','#16344d'], forest:['#16834c','#183c2b'], grape:['#7048c8','#38255e'], rose:['#d9486b','#562232']};
  if (linkInput && preview && previewValue) {
    const initial = linkInput.value;
    const normalize = value => value.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    const update = () => { const value = normalize(linkInput.value || nameInput?.value || ''); preview.hidden = !value; previewValue.textContent = `${window.location.origin}/m/${value || 'tu-negocio'}/`; warning.hidden = !initial || value === initial; };
    linkInput.addEventListener('input', update); nameInput?.addEventListener('input', () => { if (!linkInput.value) update(); }); update();
  }
  palette?.addEventListener('change', () => { if (colors[palette.value]) { if (color) color.value = colors[palette.value][0]; if (secondaryColor) secondaryColor.value = colors[palette.value][1]; } });
  color?.addEventListener('input', () => { if (palette) palette.value = 'custom'; });
  secondaryColor?.addEventListener('input', () => { if (palette) palette.value = 'custom'; });
  const captureLocation = document.querySelector('#capture-business-location');
  const clearLocation = document.querySelector('#clear-business-location');
  const latitude = document.querySelector('#id_latitude');
  const longitude = document.querySelector('#id_longitude');
  const locationStatus = document.querySelector('#business-location-status');
  const setStatus = (message, state = '') => { if (locationStatus) { locationStatus.textContent = message; locationStatus.className = `location-picker-status ${state}`.trim(); } };
  captureLocation?.addEventListener('click', () => {
    if (!navigator.geolocation) { setStatus('Este navegador no permite obtener la ubicación. Puedes ingresar las coordenadas manualmente.', 'error'); return; }
    captureLocation.disabled = true; setStatus('Solicitando permiso de ubicación…');
    navigator.geolocation.getCurrentPosition(position => {
      latitude.value = position.coords.latitude.toFixed(6); longitude.value = position.coords.longitude.toFixed(6);
      const accuracy = Math.round(position.coords.accuracy);
      setStatus(`✓ Ubicación capturada (precisión aproximada: ${accuracy} m). Guarda los cambios para publicarla.`, 'success');
      captureLocation.disabled = false;
    }, error => {
      const denied = error.code === error.PERMISSION_DENIED;
      setStatus(denied ? 'No diste permiso para usar la ubicación. Puedes intentarlo otra vez o ingresar las coordenadas manualmente.' : 'No pudimos obtener una ubicación precisa. Inténtalo al aire libre o completa las coordenadas manualmente.', 'error');
      captureLocation.disabled = false;
    }, {enableHighAccuracy:true,timeout:15000,maximumAge:0});
  });
  clearLocation?.addEventListener('click', () => { if (latitude) latitude.value = ''; if (longitude) longitude.value = ''; setStatus('Ubicación retirada. Guarda los cambios para actualizar la carta.'); });
})();
