from django import forms
from django.db.models import Q
from django.utils.text import slugify
from .models import Business
from django.forms import inlineformset_factory
from app.catalog.models import Category, Product, ProductOption, ProductOptionGroup
from app.core.uploads import validate_image_file

MAX_IMAGE_BYTES = 8 * 1024 * 1024

def validate_image_upload(image):
    return validate_image_file(image, MAX_IMAGE_BYTES)

class BusinessForm(forms.ModelForm):
    PALETTE_COLORS = {
        "sunset": ("#ea580c", "#3c2417"), "ocean": ("#1677c8", "#16344d"),
        "forest": ("#16834c", "#183c2b"), "grape": ("#7048c8", "#38255e"),
        "rose": ("#d9486b", "#562232"),
    }
    slug = forms.CharField(
        required=False,
        label="Enlace de tu carta",
        help_text="Es la parte final de tu enlace. Puedes escribir con espacios: los convertiremos automáticamente. Ejemplo: Pollería El Sol.",
        widget=forms.TextInput(attrs={"placeholder": "Ej.: Pollería El Sol", "autocomplete": "off", "data-menu-link": "true"}),
    )

    class Meta:
        model = Business
        fields = ("name", "slug", "description", "greeting_message", "whatsapp_number", "brand_palette", "menu_theme", "primary_color", "secondary_color", "logo", "cover_image", "pickup_enabled", "delivery_enabled", "dine_in_enabled", "address", "latitude", "longitude", "is_published")
        labels = {
            "name": "Nombre del negocio", "slug": "Enlace de tu carta",
            "description": "Descripción", "greeting_message": "Saludo de la carta", "whatsapp_number": "WhatsApp",
            "brand_palette": "Paleta de colores", "menu_theme": "Apariencia de la carta", "primary_color": "Color principal", "secondary_color": "Color secundario", "logo": "Logo",
            "cover_image": "Imagen de portada", "is_published": "Carta publicada",
            "pickup_enabled": "Permitir recojo", "delivery_enabled": "Permitir delivery",
            "dine_in_enabled": "Permitir consumo en local",
            "address": "Dirección del local", "latitude": "Latitud del local", "longitude": "Longitud del local",
        }
        help_texts = {
            "slug": "Es la parte final de tu enlace. Puedes escribir con espacios: los convertiremos automáticamente. Ejemplo: Pollería El Sol.",
            "whatsapp_number": "Incluye el código de país, sin espacios. Ejemplo: 51999999999",
            "greeting_message": "Un mensaje breve para tus clientes. Máximo 160 caracteres.",
            "menu_theme": "Define cómo verán la carta tus clientes. “Según el dispositivo” respeta la preferencia de cada teléfono.",
            "address": "Se mostrará como referencia para los pedidos con recojo.",
            "latitude": "Opcional. Usa ambos campos para generar el enlace de ubicación del local.",
            "longitude": "Opcional. Usa ambos campos para generar el enlace de ubicación del local.",
        }
        widgets = {
            "slug": forms.TextInput(attrs={"placeholder": "Ej.: Pollería El Sol", "autocomplete": "off", "data-menu-link": "true"}),
            "brand_palette": forms.Select(attrs={"data-palette-select": "true"}),
            "menu_theme": forms.Select(),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Cuéntales a tus clientes qué hace especial a tu negocio"}),
            "greeting_message": forms.TextInput(attrs={"placeholder": "Ej.: Hoy provoca un cevichito 🐟", "maxlength": 160}),
            "address": forms.TextInput(attrs={"placeholder": "Ej.: Av. Arequipa 1234, Miraflores"}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "Ej.: -12.119142"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "Ej.: -77.034904"}),
            "logo": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-preview": "logo-preview"}),
            "cover_image": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-preview": "cover-preview"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keeps older clients and partial integrations compatible with this new preference.
        self.fields["menu_theme"].required = False


    def clean_slug(self):
        value = slugify(self.cleaned_data.get("slug", ""))
        if value and Business.objects.exclude(pk=self.instance.pk).filter(slug=value).exists():
            raise forms.ValidationError("Ese enlace ya está en uso. Prueba con otra variante.")
        return value

    def clean_logo(self): return validate_image_upload(self.cleaned_data.get("logo"))
    def clean_cover_image(self): return validate_image_upload(self.cleaned_data.get("cover_image"))

    def clean_whatsapp_number(self):
        number = "".join(filter(str.isdigit, self.cleaned_data["whatsapp_number"]))
        if not 9 <= len(number) <= 15:
            raise forms.ValidationError("Ingresa un número válido con código de país. Ejemplo: 51999999999.")
        return number

    def clean(self):
        cleaned = super().clean()
        cleaned["menu_theme"] = cleaned.get("menu_theme") or Business.MenuTheme.SYSTEM
        if not cleaned.get("slug"):
            generated = slugify(cleaned.get("name", ""))
            if not generated:
                self.add_error("slug", "Escribe el nombre del negocio para crear su enlace.")
            elif Business.objects.exclude(pk=self.instance.pk).filter(slug=generated).exists():
                self.add_error("slug", "Ese enlace ya está en uso. Prueba con otra variante.")
            else:
                cleaned["slug"] = generated
        palette = cleaned.get("brand_palette")
        if palette in self.PALETTE_COLORS:
            cleaned["primary_color"], cleaned["secondary_color"] = self.PALETTE_COLORS[palette]
        if (cleaned.get("latitude") is None) != (cleaned.get("longitude") is None):
            raise forms.ValidationError("Completa latitud y longitud del local, o deja ambos campos vacíos.")
        if not any(cleaned.get(field) for field in ("pickup_enabled", "delivery_enabled", "dine_in_enabled")):
            raise forms.ValidationError("Habilita al menos una modalidad de pedido.")
        return cleaned

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "sort_order", "active")
        labels = {"name": "Nombre", "sort_order": "Orden", "active": "Visible en la carta"}
        help_texts = {"sort_order": "Las categorías con menor número aparecen primero."}
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Ej.: Platos principales, Bebidas, Postres"})}

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("category", "name", "description", "price", "image", "active", "available", "sort_order")
        labels = {
            "category": "Categoría", "name": "Nombre del producto", "description": "Descripción",
            "price": "Precio", "image": "Foto", "active": "Visible en la carta",
            "available": "Disponible", "sort_order": "Orden",
        }
        help_texts = {"active": "Desactívalo para ocultarlo sin borrarlo.", "available": "Desmárcalo para mostrarlo como agotado."}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ej.: Pollo a la brasa"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Ingredientes, tamaño o una descripción breve"}),
            "price": forms.NumberInput(attrs={"step": "0.01", "min": "0", "inputmode": "decimal"}),
            "image": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-preview": "product-preview"}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            allowed = Q(active=True)
            if self.instance and self.instance.pk:
                allowed |= Q(pk=self.instance.category_id)
            self.fields["category"].queryset = Category.objects.filter(Q(business=business) & allowed)

    def clean_image(self): return validate_image_upload(self.cleaned_data.get("image"))

class ProductOptionGroupForm(forms.ModelForm):
    class Meta:
        model = ProductOptionGroup
        fields = ("name", "selection_type", "required", "sort_order")
        labels = {"name": "Nombre del grupo", "selection_type": "Tipo de selección", "required": "Selección obligatoria", "sort_order": "Orden"}
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Ej.: Tamaño, acompañamiento o extras"})}

ProductOptionFormSet = inlineformset_factory(
    ProductOptionGroup, ProductOption,
    fields=("name", "price_delta", "available", "sort_order"),
    labels={"name": "Opción", "price_delta": "Precio adicional", "available": "Disponible", "sort_order": "Orden"},
    widgets={"name": forms.TextInput(attrs={"placeholder": "Ej.: Grande"}), "price_delta": forms.NumberInput(attrs={"step": "0.01", "min": "0"})},
    extra=3, can_delete=True,
)


class BusinessOperationsForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ("subscription_status", "subscription_expires_at", "is_published", "internal_notes")
        labels = {
            "subscription_status": "Estado del cliente",
            "subscription_expires_at": "Vigencia hasta",
            "is_published": "Mantener carta publicada",
            "internal_notes": "Notas internas",
        }
        help_texts = {
            "subscription_expires_at": "Déjalo vacío si no tiene una fecha de vencimiento definida.",
            "internal_notes": "Solo lo ve el equipo de PractiCarta.",
        }
        widgets = {
            "subscription_expires_at": forms.DateInput(attrs={"type": "date"}),
            "internal_notes": forms.Textarea(attrs={"rows": 5, "placeholder": "Ej.: Pagó por Yape el 6 de octubre. Renovar el próximo mes."}),
        }
