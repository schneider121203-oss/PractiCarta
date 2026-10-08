from pathlib import Path
from PIL import Image, UnidentifiedImageError
from django import forms

MAX_DOCUMENT_BYTES = 15 * 1024 * 1024

class MenuImportForm(forms.Form):
    source_file = forms.FileField(
        label="Carta en PDF o imagen",
        help_text="PDF, JPEG, PNG o WebP de hasta 15 MB.",
        widget=forms.FileInput(attrs={"accept": ".pdf,image/jpeg,image/png,image/webp"}),
    )

    def clean_source_file(self):
        source = self.cleaned_data["source_file"]
        if source.size > MAX_DOCUMENT_BYTES:
            raise forms.ValidationError("El archivo no puede superar los 15 MB.")
        extension = Path(source.name).suffix.lower()
        signature = source.read(8); source.seek(0)
        if extension == ".pdf" and signature.startswith(b"%PDF-"):
            source.validated_mime = "application/pdf"
            return source
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise forms.ValidationError("Usa un archivo PDF, JPEG, PNG o WebP.")
        try:
            image = Image.open(source); image.verify(); source.seek(0)
        except (UnidentifiedImageError, OSError):
            raise forms.ValidationError("La imagen no es válida o está dañada.")
        source.validated_mime = Image.open(source).get_format_mimetype(); source.seek(0)
        return source
