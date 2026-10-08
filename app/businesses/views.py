from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Count, Max, Q
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from .forms import BusinessForm, BusinessOperationsForm, CategoryForm, ProductForm, ProductOptionFormSet, ProductOptionGroupForm
from .models import Business
from app.analytics.models import AnalyticsEvent
from app.catalog.models import Category, Product, ProductOption, ProductOptionGroup
import qrcode

def owned_business(request):
    business = request.user.businesses.order_by("created_at").first()
    if not business: raise Http404
    return business

@login_required
def dashboard(request):
    business = request.user.businesses.order_by("created_at").first()
    if not business: return redirect("businesses:create")
    events = business.events
    categories = business.categories.prefetch_related("products")
    products = Product.objects.filter(category__business=business).select_related("category")
    last_30_days = timezone.now() - timedelta(days=30)
    last_7_days = timezone.now() - timedelta(days=7)
    return render(request, "businesses/dashboard.html", {
        "business": business, "categories": categories, "products": products,
        "metrics": {
            "views": events.filter(event_type="menu_view", created_at__gte=last_30_days).count(),
            "adds": events.filter(event_type="add_to_cart", created_at__gte=last_30_days).count(),
            "whatsapp": events.filter(event_type="whatsapp_click", created_at__gte=last_30_days).count(),
            "views_7": events.filter(event_type="menu_view", created_at__gte=last_7_days).count(),
            "whatsapp_7": events.filter(event_type="whatsapp_click", created_at__gte=last_7_days).count(),
        },
        "setup": {"brand": bool(business.logo or business.cover_image), "category": categories.exists(), "product": products.exists()},
    })


@staff_member_required(login_url="login")
def operations_dashboard(request):
    today = timezone.localdate()
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    selected_status = request.GET.get("status", "")
    businesses = Business.objects.select_related("owner").annotate(
        views_7=Count("events", filter=Q(events__event_type="menu_view", events__created_at__gte=seven_days_ago)),
        whatsapp_7=Count("events", filter=Q(events__event_type="whatsapp_click", events__created_at__gte=seven_days_ago)),
        views_30=Count("events", filter=Q(events__event_type="menu_view", events__created_at__gte=thirty_days_ago)),
        whatsapp_30=Count("events", filter=Q(events__event_type="whatsapp_click", events__created_at__gte=thirty_days_ago)),
        last_activity=Max("events__created_at"),
    ).order_by("-created_at")
    if selected_status:
        businesses = businesses.filter(subscription_status=selected_status)
    for business in businesses:
        business.conversion_30 = round((business.whatsapp_30 / business.views_30) * 100) if business.views_30 else 0
    overview = {
        "total": businesses.count(),
        "active": businesses.filter(subscription_status=Business.SubscriptionStatus.ACTIVE).count(),
        "pending": businesses.filter(subscription_status=Business.SubscriptionStatus.PAYMENT_DUE).count(),
        "expiring": businesses.filter(subscription_expires_at__isnull=False, subscription_expires_at__lte=today + timedelta(days=7)).exclude(subscription_status__in=[Business.SubscriptionStatus.SUSPENDED, Business.SubscriptionStatus.CANCELED]).count(),
    }
    return render(request, "businesses/operations_dashboard.html", {
        "businesses": businesses, "overview": overview, "selected_status": selected_status,
        "statuses": Business.SubscriptionStatus.choices,
    })


@staff_member_required(login_url="login")
def operations_business(request, business_id):
    business = get_object_or_404(Business.objects.select_related("owner"), id=business_id)
    form = BusinessOperationsForm(request.POST or None, instance=business)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"El estado de {business.name} fue actualizado.")
        return redirect("businesses:operations_business", business_id=business.id)
    now = timezone.now()
    events = business.events
    metrics = {
        "views_7": events.filter(event_type="menu_view", created_at__gte=now - timedelta(days=7)).count(),
        "whatsapp_7": events.filter(event_type="whatsapp_click", created_at__gte=now - timedelta(days=7)).count(),
        "views_30": events.filter(event_type="menu_view", created_at__gte=now - timedelta(days=30)).count(),
        "whatsapp_30": events.filter(event_type="whatsapp_click", created_at__gte=now - timedelta(days=30)).count(),
    }
    metrics["conversion_30"] = round((metrics["whatsapp_30"] / metrics["views_30"]) * 100) if metrics["views_30"] else 0
    return render(request, "businesses/operations_business.html", {"business": business, "form": form, "metrics": metrics})

@login_required
def create_business(request):
    if request.user.businesses.exists(): return redirect("businesses:dashboard")
    form = BusinessForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        business = form.save(commit=False); business.owner = request.user; business.save()
        messages.success(request, "Tu negocio está listo. Ahora crea la primera categoría de tu carta.")
        return redirect("businesses:dashboard")
    return render(request, "businesses/form.html", {"form": form, "title": "Crea tu negocio", "subtitle": "Configura lo esencial. Podrás cambiar todo después.", "form_kind": "business"})

@login_required
def edit_business(request):
    business = owned_business(request)
    form = BusinessForm(request.POST or None, request.FILES or None, instance=business)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Los cambios de tu carta ya están publicados."); return redirect("businesses:dashboard")
    return render(request, "businesses/form.html", {"form": form, "title": "Personaliza tu carta", "subtitle": "Así reconocerán tu marca cuando escaneen el QR.", "business": business, "form_kind": "business"})

@login_required
def add_category(request):
    business = owned_business(request); form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False); category.business = business; category.save()
        messages.success(request, f"Categoría «{category.name}» creada.")
        return redirect("businesses:product_add" if request.GET.get("next") == "product" else "businesses:dashboard")
    return render(request, "businesses/entity_form.html", {"form": form, "title": "Nueva categoría", "subtitle": "Agrupa productos para que tus clientes encuentren rápido lo que buscan.", "form_kind": "category"})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, business=owned_business(request))
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Categoría actualizada."); return redirect("businesses:dashboard")
    return render(request, "businesses/entity_form.html", {"form": form, "title": "Editar categoría", "subtitle": "Cambia su nombre, orden o visibilidad.", "form_kind": "category"})

@login_required
def add_product(request):
    business = owned_business(request)
    if not business.categories.filter(active=True).exists():
        messages.info(request, "Primero crea una categoría; después podrás agregar el producto.")
        return redirect(f'{reverse("businesses:category_add")}?next=product')
    return product_form(request)
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, category__business=owned_business(request))
    return product_form(request, product)

def product_form(request, product=None):
    business = owned_business(request)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product, business=business)
    if request.method == "POST" and form.is_valid():
        saved = form.save(); messages.success(request, f"«{saved.name}» se guardó correctamente."); return redirect("businesses:dashboard")
    reusable_groups = ProductOptionGroup.objects.filter(product__category__business=business).select_related("product").exclude(product=product) if product else ProductOptionGroup.objects.none()
    return render(request, "businesses/entity_form.html", {"form": form, "title": "Editar producto" if product else "Nuevo producto", "subtitle": "Una foto clara y una descripción breve ayudan a vender más.", "form_kind": "product", "product": product, "reusable_groups": reusable_groups})

@login_required
def toggle_availability(request, product_id):
    if request.method != "POST": return redirect("businesses:dashboard")
    product = get_object_or_404(Product, id=product_id, category__business=owned_business(request))
    product.available = not product.available; product.save(update_fields=["available", "updated_at"])
    return redirect("businesses:dashboard")

@login_required
def product_options(request, product_id, group_id=None):
    business = owned_business(request)
    product = get_object_or_404(Product, id=product_id, category__business=business)
    if group_id:
        group = get_object_or_404(ProductOptionGroup, id=group_id, product=product)
    else:
        group = ProductOptionGroup(product=product)
    group_form = ProductOptionGroupForm(request.POST or None, instance=group)
    option_formset = ProductOptionFormSet(request.POST or None, instance=group)
    if request.method == "POST" and group_form.is_valid() and option_formset.is_valid():
        saved_group = group_form.save(commit=False); saved_group.product = product; saved_group.save()
        option_formset.instance = saved_group; option_formset.save()
        messages.success(request, "Las opciones del producto fueron actualizadas.")
        return redirect("businesses:product_edit", product_id=product.id)
    return render(request, "businesses/options_form.html", {"product": product, "group": group if group.pk else None, "group_form": group_form, "option_formset": option_formset})


@login_required
@require_POST
def copy_product_options(request, product_id):
    business = owned_business(request)
    product = get_object_or_404(Product, id=product_id, category__business=business)
    source = get_object_or_404(ProductOptionGroup.objects.prefetch_related("options"), id=request.POST.get("group_id"), product__category__business=business)
    with transaction.atomic():
        copied = ProductOptionGroup.objects.create(product=product, name=source.name, selection_type=source.selection_type, required=source.required, sort_order=source.sort_order)
        ProductOption.objects.bulk_create([ProductOption(group=copied, name=option.name, price_delta=option.price_delta, available=option.available, sort_order=option.sort_order) for option in source.options.all()])
    messages.success(request, f"El grupo «{source.name}» fue copiado a {product.name}.")
    return redirect("businesses:product_edit", product_id=product.id)

@login_required
def download_qr(request):
    business = owned_business(request)
    menu_path = business.get_absolute_url()
    public_url = f"{settings.PUBLIC_BASE_URL}{menu_path}" if settings.PUBLIC_BASE_URL else request.build_absolute_uri(menu_path)
    qr = qrcode.make(public_url)
    response = HttpResponse(content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="qr-{business.slug}.png"'
    qr.save(response, "PNG")
    return response
