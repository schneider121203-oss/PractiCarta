from pathlib import Path
from pypdf import PdfReader
from django import forms
from app.core.uploads import validate_image_file

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
            try:
                reader = PdfReader(source, strict=False)
                if reader.is_encrypted:
                    raise forms.ValidationError("El PDF está protegido con contraseña. Sube una copia sin protección.")
                if len(reader.pages) > 50:
                    raise forms.ValidationError("El PDF no puede superar 50 páginas.")
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError("El PDF no es válido o está dañado.")
            finally:
                source.seek(0)
            source.validated_mime = "application/pdf"
            return source
        if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise forms.ValidationError("Usa un archivo PDF, JPEG, PNG o WebP.")
        try:
            validate_image_file(source, MAX_DOCUMENT_BYTES)
            source.validated_mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}[extension]
        except forms.ValidationError:
            raise
        finally:
            source.seek(0)
        return source
