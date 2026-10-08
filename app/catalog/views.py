import json
import re
from decimal import Decimal, InvalidOperation
from django.http import HttpResponseBadRequest, JsonResponse
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from app.analytics.models import AnalyticsEvent
from app.businesses.models import Business
from .models import Product, ProductOption, ProductOptionGroup

MAX_NOTE_LENGTH = 400
MAX_ADDRESS_LENGTH = 300


def clean_checkout_text(value, max_length):
    if value in (None, ""):
        return ""
    if not isinstance(value, str):
        raise ValueError
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) > max_length:
        raise ValueError
    return cleaned


def clean_customer_location(value):
    if value in (None, ""):
        return None
    if not isinstance(value, dict):
        raise ValueError
    try:
        latitude = Decimal(str(value.get("latitude")))
        longitude = Decimal(str(value.get("longitude")))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError
    if not latitude.is_finite() or not longitude.is_finite():
        raise ValueError
    if not Decimal("-90") <= latitude <= Decimal("90") or not Decimal("-180") <= longitude <= Decimal("180"):
        raise ValueError
    return latitude, longitude

def menu(request, slug):
    business = get_object_or_404(Business, slug=slug, is_published=True)
    option_groups = ProductOptionGroup.objects.prefetch_related(Prefetch("options", queryset=ProductOption.objects.filter(available=True)))
    products = Product.objects.filter(active=True).order_by("sort_order", "name").prefetch_related(Prefetch("option_groups", queryset=option_groups))
    categories = business.categories.filter(active=True).prefetch_related(
        Prefetch("products", queryset=products)
    )
    option_catalog = {}
    for category in categories:
        for product in category.products.all():
            option_catalog[str(product.id)] = {"groups": [{
                "id": str(group.id), "name": group.name, "type": group.selection_type, "required": group.required,
                "options": [{"id": str(option.id), "name": option.name, "price": str(option.price_delta)} for option in group.options.all()],
            } for group in product.option_groups.all()]}
    AnalyticsEvent.objects.create(business=business, event_type="menu_view", session_id=request.session.session_key or "")
    return render(request, "public/menu.html", {"business": business, "categories": categories, "option_catalog": option_catalog})

@require_POST
def checkout(request, slug):
    business = get_object_or_404(Business, slug=slug, is_published=True)
    try: payload = json.loads(request.body); items = payload["items"]
    except (json.JSONDecodeError, KeyError, TypeError): return HttpResponseBadRequest("Carrito inválido")
    if not isinstance(items, list) or len(items) > 100:
        return HttpResponseBadRequest("Carrito inválido")
    try:
        customer_note = clean_checkout_text(payload.get("customer_note"), MAX_NOTE_LENGTH)
        delivery_address = clean_checkout_text(payload.get("delivery_address"), MAX_ADDRESS_LENGTH)
        customer_location = clean_customer_location(payload.get("location"))
    except ValueError:
        return HttpResponseBadRequest("Datos de entrega inválidos")
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    products = {str(p.id): p for p in Product.objects.filter(id__in=ids, category__business=business, active=True, available=True).prefetch_related("option_groups__options")}
    modality = payload.get("order_type", "pickup")
    modality_config = {"pickup": (business.pickup_enabled, "Recojo"), "delivery": (business.delivery_enabled, "Delivery"), "dine_in": (business.dine_in_enabled, "Consumo en local")}
    if modality not in modality_config or not modality_config[modality][0]:
        return HttpResponseBadRequest("Modalidad no disponible")
    if modality == "delivery" and not (delivery_address or customer_location):
        return HttpResponseBadRequest("Ingresa una dirección o comparte tu ubicación")
    lines, total = [], Decimal("0")
    for item in items:
        if not isinstance(item, dict): continue
        product = products.get(str(item.get("id"))); quantity = item.get("quantity", 0)
        if not product or not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1 or quantity > 99: continue
        raw_option_ids = item.get("options", [])
        if not isinstance(raw_option_ids, list): continue
        option_ids = list(dict.fromkeys(str(option_id) for option_id in raw_option_ids))
        available_options = {str(option.id): option for group in product.option_groups.all() for option in group.options.all() if option.available}
        selected = [available_options[option_id] for option_id in option_ids if option_id in available_options]
        if len(selected) != len(option_ids): continue
        invalid_selection = False
        for group in product.option_groups.all():
            group_selected = [option for option in selected if option.group_id == group.id]
            if group.required and not group_selected: invalid_selection = True
            if group.selection_type == ProductOptionGroup.SelectionType.SINGLE and len(group_selected) > 1: invalid_selection = True
        if invalid_selection: continue
        unit_price = product.price + sum((option.price_delta for option in selected), Decimal("0"))
        subtotal = unit_price * quantity; total += subtotal
        line = f"{quantity}x {product.name} — S/ {subtotal:.2f}"
        for group in product.option_groups.all():
            group_selected = [option for option in selected if option.group_id == group.id]
            if not group_selected: continue
            option_names = ", ".join(option.name + (f" (+S/ {option.price_delta:.2f})" if option.price_delta else "") for option in group_selected)
            line += f"\n   • {group.name}: {option_names}"
        lines.append(line)
    if not lines: return HttpResponseBadRequest("No hay productos disponibles")
    details = [f"🚚 Modalidad: {modality_config[modality][1]}"]
    if customer_location:
        latitude, longitude = customer_location
        details.append(f"📍 Ubicación compartida por el cliente: https://www.google.com/maps?q={latitude:.6f},{longitude:.6f}")
    if modality == "delivery":
        if delivery_address:
            details.append(f"🏠 Dirección/referencia: {delivery_address}")
    elif modality == "pickup" and business.address:
        details.append(f"📍 Recojo en: {business.address}")
    if customer_note:
        details.append(f"📝 Indicaciones: {customer_note}")
    text = "🛒 Pedido\n\n" + "\n\n".join(lines) + "\n\n" + "\n".join(details) + f"\n\n💰 Total: S/ {total:.2f}"
    AnalyticsEvent.objects.create(business=business, event_type="whatsapp_click", session_id=request.session.session_key or "")
    return JsonResponse({"phone": "".join(filter(str.isdigit, business.whatsapp_number)), "text": text})

@require_POST
def event(request, slug):
    business = get_object_or_404(Business, slug=slug, is_published=True)
    try: event_type = json.loads(request.body).get("event_type")
    except json.JSONDecodeError: return HttpResponseBadRequest()
    if event_type not in {"add_to_cart"}: return HttpResponseBadRequest()
    AnalyticsEvent.objects.create(business=business, event_type=event_type, session_id=request.session.session_key or "")
    return JsonResponse({"ok": True})
