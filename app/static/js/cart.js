(() => {
  const carta = JSON.parse(document.querySelector('#menu-config').textContent || '{}');
  const storageKey = `practicarta:${carta.slug}`;
  const optionCatalog = JSON.parse(document.querySelector('#product-options').textContent || '{}');
  const $ = selector => document.querySelector(selector);
  const escapeHtml = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
  const money = amount => `S/ ${(Number.isFinite(Number(amount)) ? Number(amount) : 0).toFixed(2)}`;
  const headers = () => ({'Content-Type':'application/json','X-CSRFToken':carta.csrf});
  let cart;
  let configuring = null;
  let customerLocation = null;
  try { cart = JSON.parse(localStorage.getItem(storageKey) || '[]'); } catch (_) { cart = []; }
  if (!Array.isArray(cart)) cart = [];

  const currentCatalog = new Map([...document.querySelectorAll('.add')].map(button => {
    const groups = optionCatalog[button.dataset.id]?.groups || [];
    return [button.dataset.id, {name:button.dataset.name, basePrice:Number(button.dataset.price), groups}];
  }));

  function selectedOptionData(product, optionIds) {
    const all = product.groups.flatMap(group => group.options.map(option => ({...option, groupId:group.id, groupName:group.name})));
    const selected = optionIds.map(id => all.find(option => option.id === id)).filter(Boolean);
    if (selected.length !== optionIds.length) return null;
    for (const group of product.groups) {
      const count = selected.filter(option => option.groupId === group.id).length;
      if ((group.required && count === 0) || (group.type === 'single' && count > 1)) return null;
    }
    return selected;
  }

  cart = cart.flatMap(item => {
    const id = String(item?.id || ''); const product = currentCatalog.get(id);
    const optionIds = Array.isArray(item?.options) ? item.options.map(option => typeof option === 'string' ? option : String(option.id || '')) : [];
    const selected = product && selectedOptionData(product, optionIds);
    if (!product || !Number.isFinite(product.basePrice) || selected === null) return [];
    const price = product.basePrice + selected.reduce((sum, option) => sum + Number(option.price), 0);
    const quantity = Math.min(99, Math.max(1, Number.parseInt(item.quantity, 10) || 1));
    return [{lineId:`${id}:${optionIds.slice().sort().join(',')}`, id, name:product.name, price, quantity, options:optionIds, optionNames:selected.map(option => `${option.groupName}: ${option.name}`)}];
  });

  const total = () => cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  function save() { localStorage.setItem(storageKey, JSON.stringify(cart)); render(); }
  function render() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    $('#cart-count').textContent = count; $('#trigger-total').textContent = money(total()); $('#cart-total').textContent = money(total()); $('#cart-trigger').hidden = count === 0;
    $('#cart-items').innerHTML = cart.map(item => `<div class="cart-item"><span><strong>${escapeHtml(item.name)}</strong>${item.optionNames.length ? `<em>${item.optionNames.map(escapeHtml).join(' · ')}</em>` : ''}<small>${money(item.price)} c/u</small></span><div class="quantity"><button data-change="${item.lineId}" data-delta="-1" aria-label="Quitar uno">−</button><b>${item.quantity}</b><button data-change="${item.lineId}" data-delta="1" aria-label="Añadir uno">+</button></div></div>`).join('') || '<div class="cart-empty"><span>♨</span><p>Tu pedido todavía está vacío.</p></div>';
  }
  function showToast() { const toast=$('#cart-toast'); toast.hidden=false; clearTimeout(showToast.timer); showToast.timer=setTimeout(()=>{toast.hidden=true;},1800); }
  function recordAdd(productId) { fetch(`/m/${carta.slug}/event/`,{method:'POST',headers:headers(),body:JSON.stringify({event_type:'add_to_cart',product_id:productId})}).catch(()=>{}); }
  function addLine(button, selected=[]) {
    const id=button.dataset.id; const optionIds=selected.map(option=>option.id).sort(); const lineId=`${id}:${optionIds.join(',')}`; const existing=cart.find(item=>item.lineId===lineId);
    const price=Number(button.dataset.price)+selected.reduce((sum,option)=>sum+Number(option.price),0);
    if (existing) existing.quantity+=1; else cart.push({lineId,id,name:button.dataset.name,price,quantity:1,options:optionIds,optionNames:selected.map(option=>`${option.groupName}: ${option.name}`)});
    save(); showToast(); recordAdd(id);
  }

  function closeOptions() { $('#options-panel').hidden=true; $('#options-overlay').hidden=true; configuring=null; document.body.classList.remove('cart-open'); }
  function updateConfiguredPrice() {
    if (!configuring) return;
    const chosen=[...$('#options-form').querySelectorAll('input[data-price]:checked')];
    const price=Number(configuring.dataset.price)+chosen.reduce((sum,input)=>sum+Number(input.dataset.price),0);
    $('#configured-price').textContent=money(price);
  }
  function openOptions(button, groups) {
    configuring=button; $('#options-product-name').textContent=button.dataset.name;
    $('#options-groups').innerHTML=groups.map(group=>`<fieldset class="option-group" data-required="${group.required}" data-group="${group.id}"><legend>${escapeHtml(group.name)}${group.required?'<b>Obligatorio</b>':'<span>Opcional</span>'}</legend>${group.options.map(option=>`<label><input type="${group.type==='single'?'radio':'checkbox'}" name="group-${group.id}" value="${option.id}" data-name="${escapeHtml(option.name)}" data-group-name="${escapeHtml(group.name)}" data-price="${option.price}"><span><i>${escapeHtml(option.name)}</i><small>${Number(option.price)>0?`+ ${money(option.price)}`:'Incluido'}</small></span></label>`).join('')}</fieldset>`).join('');
    $('#options-panel').hidden=false; $('#options-overlay').hidden=false; document.body.classList.add('cart-open'); updateConfiguredPrice();
  }

  document.querySelectorAll('.add').forEach(button=>button.addEventListener('click',()=>{
    const groups=optionCatalog[button.dataset.id]?.groups || [];
    if (groups.length) openOptions(button,groups); else addLine(button);
  }));
  $('#options-form').addEventListener('change',updateConfiguredPrice);
  $('#options-form').addEventListener('submit',event=>{
    event.preventDefault(); const selected=[]; let valid=true;
    document.querySelectorAll('.option-group').forEach(group=>{ const checked=[...group.querySelectorAll('input:checked')]; if(group.dataset.required==='true'&&!checked.length){valid=false;group.classList.add('invalid');}else group.classList.remove('invalid'); checked.forEach(input=>selected.push({id:input.value,name:input.dataset.name,groupName:input.dataset.groupName,price:Number(input.dataset.price)})); });
    if (!valid) return;
    addLine(configuring,selected); closeOptions();
  });
  $('#close-options').addEventListener('click',closeOptions); $('#options-overlay').addEventListener('click',closeOptions);

  function openCart(){ $('#cart').hidden=false;$('#cart-overlay').hidden=false;document.body.classList.add('cart-open'); }
  function closeCart(){ $('#cart').hidden=true;$('#cart-overlay').hidden=true;document.body.classList.remove('cart-open'); }
  $('#cart-items').addEventListener('click',event=>{const button=event.target.closest('[data-change]');if(!button)return;const item=cart.find(candidate=>candidate.lineId===button.dataset.change);if(!item)return;item.quantity+=Number(button.dataset.delta);cart=cart.filter(candidate=>candidate.quantity>0);save();});
  $('#cart-trigger').addEventListener('click',openCart); $('#close-cart').addEventListener('click',closeCart); $('#cart-overlay').addEventListener('click',closeCart);
  const deliveryDetails=$('#delivery-details'); const deliveryAddress=$('#delivery-address'); const note=$('#customer-note'); const noteCount=$('#note-count'); const locationButton=$('#use-location'); const locationStatus=$('#location-status');
  const findLocationButton=$('#find-my-location'); const clearLocationButton=$('#clear-my-location'); const customerMapLink=$('#customer-map-link'); const customerLocationTitle=$('#customer-location-title'); const customerLocationCopy=$('#customer-location-copy');
  const distanceInKm=(from,to)=>{const radians=value=>value*Math.PI/180;const earthRadius=6371;const latitudeDelta=radians(to.latitude-from.latitude);const longitudeDelta=radians(to.longitude-from.longitude);const value=Math.sin(latitudeDelta/2)**2+Math.cos(radians(from.latitude))*Math.cos(radians(to.latitude))*Math.sin(longitudeDelta/2)**2;return earthRadius*2*Math.atan2(Math.sqrt(value),Math.sqrt(1-value));};
  function updateLocationUI(){
    const hasLocation=Boolean(customerLocation); const mapUrl=hasLocation?`https://www.google.com/maps?q=${customerLocation.latitude.toFixed(6)},${customerLocation.longitude.toFixed(6)}`:'';
    if(locationStatus){locationStatus.textContent=hasLocation?'✓ Ubicación añadida voluntariamente al pedido':'Opcional si escribes una dirección. No la guardaremos.';locationStatus.className=hasLocation?'success':'';}
    if(customerLocationTitle)customerLocationTitle.textContent=hasLocation?'Ubicación lista para compartir':'Compártela solo si quieres';
    if(customerLocationCopy){const distance=hasLocation&&carta.businessLocation?distanceInKm(customerLocation,carta.businessLocation):null;customerLocationCopy.textContent=distance===null?'Puede agilizar el delivery y calcular una distancia aproximada.':`Estás aproximadamente a ${distance<1?`${Math.round(distance*1000)} m`:`${distance.toFixed(1)} km`} del negocio.`;}
    if(customerMapLink){customerMapLink.hidden=!hasLocation;if(hasLocation)customerMapLink.href=mapUrl;}
    if(clearLocationButton)clearLocationButton.hidden=!hasLocation;
    [locationButton,findLocationButton].filter(Boolean).forEach(button=>{button.textContent=hasLocation?'✓ Ubicación lista':'⌖ Compartir mi ubicación';});
  }
  function requestCustomerLocation(){
    if(!navigator.geolocation){if(locationStatus){locationStatus.textContent='Tu navegador no permite obtener la ubicación. Escribe una referencia.';locationStatus.className='error';}if(customerLocationCopy)customerLocationCopy.textContent='Tu navegador no permite obtener la ubicación.';return;}
    [locationButton,findLocationButton].filter(Boolean).forEach(button=>button.disabled=true);if(locationStatus){locationStatus.textContent='Solicitando permiso…';locationStatus.className='';}if(customerLocationCopy)customerLocationCopy.textContent='Esperando tu autorización…';
    navigator.geolocation.getCurrentPosition(position=>{customerLocation={latitude:position.coords.latitude,longitude:position.coords.longitude};[locationButton,findLocationButton].filter(Boolean).forEach(button=>button.disabled=false);updateLocationUI();},error=>{customerLocation=null;[locationButton,findLocationButton].filter(Boolean).forEach(button=>button.disabled=false);const denied=error.code===error.PERMISSION_DENIED;const message=denied?'No compartiste tu ubicación. Puedes continuar sin hacerlo.':'No pudimos obtenerla. Inténtalo otra vez o escribe una referencia.';if(locationStatus){locationStatus.textContent=message;locationStatus.className='error';}if(customerLocationCopy)customerLocationCopy.textContent=message;},{enableHighAccuracy:true,timeout:15000,maximumAge:300000});
  }
  function syncDeliveryDetails(){ const delivery=document.querySelector('input[name="order_type"]:checked')?.value==='delivery'; if(deliveryDetails)deliveryDetails.hidden=!delivery; }
  document.querySelectorAll('input[name="order_type"]').forEach(input=>input.addEventListener('change',syncDeliveryDetails));
  if(note&&noteCount)note.addEventListener('input',()=>{noteCount.textContent=note.value.length;});
  locationButton?.addEventListener('click',requestCustomerLocation);findLocationButton?.addEventListener('click',requestCustomerLocation);clearLocationButton?.addEventListener('click',()=>{customerLocation=null;updateLocationUI();});updateLocationUI();
  syncDeliveryDetails();
  $('#whatsapp').addEventListener('click',async()=>{
    const button=$('#whatsapp'); const orderType=document.querySelector('input[name="order_type"]:checked')?.value;
    if(!orderType)return alert('Selecciona cómo quieres recibir el pedido.');
    const address=deliveryAddress?.value.trim()||''; const customerNote=note?.value.trim()||'';
    if(orderType==='delivery'&&!address&&!customerLocation){alert('Escribe una dirección o usa tu ubicación actual para el delivery.');deliveryAddress?.focus();return;}
    button.disabled=true;button.querySelector('span').textContent='Preparando pedido…';
    try{const response=await fetch(`/m/${carta.slug}/checkout/`,{method:'POST',headers:headers(),body:JSON.stringify({items:cart,order_type:orderType,delivery_address:address,customer_note:customerNote,location:customerLocation})});if(!response.ok)throw new Error('invalid cart');const {phone,text}=await response.json();window.location.href=`https://wa.me/${phone}?text=${encodeURIComponent(text)}`;}catch(_){alert('No pudimos preparar el pedido. Revisa los datos e inténtalo nuevamente.');button.disabled=false;button.querySelector('span').textContent='Continuar por WhatsApp';}
  });
  const search=$('#menu-search');if(search)search.addEventListener('input',()=>{const query=search.value.trim().toLocaleLowerCase('es');let matches=0;document.querySelectorAll('.menu-product').forEach(product=>{const visible=product.dataset.search.includes(query);product.hidden=!visible;if(visible)matches+=1;});document.querySelectorAll('.menu-category').forEach(section=>{section.hidden=!section.querySelector('.menu-product:not([hidden])');});$('#no-results').hidden=matches>0;});
  save();
})();
