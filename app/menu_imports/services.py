import json
import logging
import shutil
import tempfile
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

MENU_SCHEMA = {
    "type": "object",
    "properties": {
        "categories": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "products": {
                        "type": "array",
                        "items": {"type": "object", "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "price": {"type": "number"},
                        }, "required": ["name", "description", "price"]},
                    },
                },
                "required": ["name", "products"],
            },
        },
    },
    "required": ["categories"],
}

PROMPT = """Extrae esta carta de restaurante. Conserva los nombres tal como aparecen, agrupa cada producto en su categoría y devuelve el precio numérico en soles sin símbolo monetario. No inventes texto ni precios. Si no existe descripción usa una cadena vacía. Omite elementos cuyo precio no pueda leerse con seguridad. Devuelve únicamente el objeto definido por el esquema."""

class MenuImportError(Exception): pass

@lru_cache(maxsize=1)
def get_gemini_api_key():
    if settings.GEMINI_API_KEY:
        return settings.GEMINI_API_KEY
    if not settings.AWS_GEMINI_SECRET_ID:
        raise MenuImportError("Configura GEMINI_API_KEY o AWS_GEMINI_SECRET_ID.")
    try:
        import boto3
        session_options = {}
        if settings.AWS_SECRETS_PROFILE:
            session_options["profile_name"] = settings.AWS_SECRETS_PROFILE
        session = boto3.Session(**session_options)
        client = session.client("secretsmanager", region_name=settings.AWS_SECRETS_REGION)
        secret = client.get_secret_value(SecretId=settings.AWS_GEMINI_SECRET_ID).get("SecretString", "").strip()
        if settings.GEMINI_SECRET_JSON_KEY:
            secret = json.loads(secret)[settings.GEMINI_SECRET_JSON_KEY]
        if not secret:
            raise ValueError("empty secret")
        return secret
    except MenuImportError:
        raise
    except Exception as exc:
        raise MenuImportError("No se pudo leer la clave de Gemini desde AWS Secrets Manager.") from exc

def extract_menu(menu_import):
    api_key = get_gemini_api_key()
    try:
        from google import genai
        from google.genai import errors, types
        client = genai.Client(api_key=api_key)
        menu_import.source_file.open("rb")
        suffix = Path(menu_import.original_name).suffix[:10]
        with tempfile.NamedTemporaryFile(suffix=suffix) as temporary:
            shutil.copyfileobj(menu_import.source_file.file, temporary)
            temporary.flush()
            uploaded = client.files.upload(
                file=temporary.name,
                config={"mime_type": menu_import.mime_type, "display_name": menu_import.original_name},
            )
            models = list(dict.fromkeys(filter(None, [settings.GEMINI_MODEL, settings.GEMINI_FALLBACK_MODEL])))
            response = None
            last_api_code = None
            for index, model_name in enumerate(models):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[uploaded, PROMPT],
                        config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=MENU_SCHEMA),
                    )
                    break
                except errors.APIError as api_error:
                    last_api_code = getattr(api_error, "code", None)
                    can_fallback = last_api_code in {404, 429, 500, 502, 503, 504}
                    logger.warning("Gemini model %s failed with %s for import %s", model_name, last_api_code, menu_import.id)
                    if not can_fallback:
                        raise
                    if index == len(models) - 1:
                        if last_api_code == 404:
                            raise MenuImportError("Los modelos configurados ya no están disponibles. Actualiza GEMINI_MODEL.")
                        raise MenuImportError("Gemini está temporalmente saturado. Reintenta la importación en unos minutos.")
            if response is None:
                raise MenuImportError("Gemini no devolvió una respuesta para la carta.")
        payload = json.loads(response.text)
    except MenuImportError:
        raise
    except Exception as exc:
        logger.exception("Gemini menu extraction failed for import %s", menu_import.id)
        raise MenuImportError("No se pudo interpretar la carta. Intenta con un archivo más nítido.") from exc
    return normalize_draft(payload)

def normalize_draft(payload):
    normalized = {"categories": []}
    for category in payload.get("categories", [])[:30]:
        category_name = str(category.get("name", "")).strip()[:100]
        if not category_name: continue
        products = []
        for product in category.get("products", [])[:200]:
            name = str(product.get("name", "")).strip()[:120]
            try: price = Decimal(str(product.get("price"))).quantize(Decimal("0.01"))
            except (InvalidOperation, TypeError): continue
            if not name or price < 0 or price > Decimal("99999999.99"): continue
            products.append({"name": name, "description": str(product.get("description", "")).strip()[:1000], "price": str(price)})
        if products: normalized["categories"].append({"name": category_name, "products": products})
    if not normalized["categories"]:
        raise MenuImportError("No encontramos productos con precios legibles en el archivo.")
    return normalized
