from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from app.catalog.models import Category, Product
from .forms import MenuImportForm
from .models import MenuImport
from .services import MenuImportError, extract_menu

def current_business(request):
    business = request.user.businesses.order_by("created_at").first()
    if not business: raise Http404
    return business

def process_import(job):
    job.status = MenuImport.Status.PROCESSING
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])
    try:
        job.draft = extract_menu(job); job.status = MenuImport.Status.READY
        job.save(update_fields=["draft", "status", "updated_at"])
        return None
    except MenuImportError as exc:
        job.status = MenuImport.Status.FAILED; job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        return str(exc)

@login_required
def upload(request):
    business = current_business(request)
    form = MenuImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        source = form.cleaned_data["source_file"]
        job = MenuImport.objects.create(
            business=business, created_by=request.user, source_file=source,
            original_name=source.name[:255], mime_type=source.validated_mime,
            status=MenuImport.Status.UPLOADED,
        )
        error = process_import(job)
        if not error:
            messages.success(request, "La carta fue interpretada. Revisa los datos antes de importarlos.")
            return redirect("menu_imports:review", import_id=job.id)
        messages.error(request, error)
    history = business.menu_imports.only("id", "original_name", "status", "created_at")[:5]
    return render(request, "menu_imports/upload.html", {"form": form, "history": history})

@login_required
@require_POST
def retry(request, import_id):
    job = get_object_or_404(MenuImport, id=import_id, business=current_business(request))
    if job.status != MenuImport.Status.FAILED:
        messages.info(request, "Esta importación no necesita reintentarse.")
        return redirect("menu_imports:upload")
    error = process_import(job)
    if error:
        messages.error(request, error)
        return redirect("menu_imports:upload")
    messages.success(request, "La carta fue interpretada. Revisa el borrador antes de importar.")
    return redirect("menu_imports:review", import_id=job.id)

@login_required
def review(request, import_id):
    business = current_business(request)
    job = get_object_or_404(MenuImport, id=import_id, business=business)
    if job.status not in {MenuImport.Status.READY, MenuImport.Status.IMPORTED}:
        messages.info(request, "Este borrador todavía no está disponible para revisión.")
        return redirect("menu_imports:upload")
    if request.method == "POST": return confirm_import(request, job)
    return render(request, "menu_imports/review.html", {"job": job, "draft": job.draft})

def confirm_import(request, job):
    if job.status == MenuImport.Status.IMPORTED:
        messages.info(request, "Este borrador ya fue importado.")
        return redirect("businesses:dashboard")
    rows, errors = [], []
    for category_index, category in enumerate(job.draft.get("categories", [])):
        category_name = request.POST.get(f"category_{category_index}_name", "").strip()[:100]
        if not category_name: errors.append(f"La categoría {category_index + 1} necesita un nombre.")
        for product_index, _product in enumerate(category.get("products", [])):
            if request.POST.get(f"product_{category_index}_{product_index}_include") != "on": continue
            name = request.POST.get(f"product_{category_index}_{product_index}_name", "").strip()[:120]
            description = request.POST.get(f"product_{category_index}_{product_index}_description", "").strip()[:1000]
            try: price = Decimal(request.POST.get(f"product_{category_index}_{product_index}_price", "")).quantize(Decimal("0.01"))
            except InvalidOperation: price = Decimal("-1")
            if not name or price < 0 or price > Decimal("99999999.99"):
                errors.append(f"Revisa el nombre y precio del producto {product_index + 1} en {category_name or 'la categoría'}.")
            else: rows.append((category_index, category_name, name, description, price))
    if not rows: errors.append("Selecciona al menos un producto para importar.")
    if errors:
        for error in errors[:5]: messages.error(request, error)
        return render(request, "menu_imports/review.html", {"job": job, "draft": job.draft})
    with transaction.atomic():
        categories = {}
        for category_index, category_name, name, description, price in rows:
            if category_index not in categories:
                categories[category_index], _ = Category.objects.get_or_create(business=job.business, name=category_name, defaults={"sort_order": category_index})
            Product.objects.create(category=categories[category_index], name=name, description=description, price=price)
        job.status = MenuImport.Status.IMPORTED; job.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Importamos {len(rows)} productos. Ya puedes revisarlos en tu panel.")
    return redirect("businesses:dashboard")
