# PractiCarta

MVP de carta digital mobile-first con carrito y pedido estructurado por WhatsApp.

## Inicio local

```bash
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Abre `http://127.0.0.1:8000/registro/`, crea tu negocio, categorías y productos. La carta pública queda en `/m/<slug>/`.

Con PostgreSQL y Docker:

```bash
docker compose up --build
```

## Alcance actual

- Registro e identidad por email.
- Un negocio por usuario en la primera experiencia de dashboard.
- Productos, fotos, disponibilidad y personalización básica.
- Flujo guiado de categorías: antes de crear un producto se solicita su categoría.
- Previsualización local de logo, portada y foto de producto antes de guardar.
- Carta pública, carrito persistente y enlace WhatsApp validado en servidor.
- QR PNG y métricas first-party de visitas, añadidos y clics WhatsApp.
- Importación asistida desde PDF/JPEG/PNG/WebP con borrador editable antes de crear productos.
- Cuenta basada en email, recuperación/cambio de contraseña y perfil.
- Modalidades de recojo, delivery y consumo local.
- Variantes y extras genéricos, reutilizables entre productos y con precios verificados por el servidor.
- Indicaciones del pedido, dirección manual y ubicación temporal del cliente para delivery.
- Dirección y coordenadas configurables del local, sin APIs de mapas pagadas.
- Mensajes de WhatsApp estructurados con modalidad, modificadores, ubicación e indicaciones.
- Saludo, paletas, dos colores configurables y contraste automático en la carta pública.

Las imágenes aceptadas son JPEG, PNG o WebP de hasta 8 MB.

## Importación de cartas con Gemini

Configura estas variables en `.env` antes de usar **Importar carta**:

```bash
GEMINI_API_KEY=tu-clave
GEMINI_MODEL=gemini-3.5-flash
GEMINI_FALLBACK_MODEL=gemini-3.1-flash-lite
```

También puedes mantener la clave en AWS Secrets Manager y guardar localmente solo la referencia:

```bash
AWS_GEMINI_SECRET_ID=habitflow/dev/gemini-api-key
AWS_SECRETS_REGION=us-east-1
AWS_SECRETS_PROFILE=habitflow  # solo para desarrollo local
```

En producción se debe omitir `AWS_SECRETS_PROFILE` y conceder `secretsmanager:GetSecretValue` al rol IAM de la aplicación, limitado al secreto correspondiente.

El archivo se analiza mediante Gemini, pero el resultado se guarda primero como borrador. El dueño debe revisar categorías, nombres, descripciones y precios y confirmar expresamente la importación.

## Probar el QR desde un teléfono sin desplegar

Conecta el teléfono y la computadora a la misma red, configura la IP local y levanta Django escuchando en la red:

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.20
PUBLIC_BASE_URL=http://192.168.1.20:8000
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Reemplaza `192.168.1.20` por la IP local de la computadora. El QR descargado usará `PUBLIC_BASE_URL`.

## Entorno de prueba en AWS

El staging actual está publicado en:

- Panel: `https://practicarta.184.195.95.29.nip.io/ingresar/`
- Carta de demostración: `https://practicarta.184.195.95.29.nip.io/m/Terra/`
- Salud: `https://practicarta.184.195.95.29.nip.io/health/`

Se ejecuta en una única instancia Lightsail de 2 GB con PostgreSQL, Django/Gunicorn y Caddy. Caddy gestiona HTTPS automáticamente. Esta arquitectura mantiene un coste predecible para staging y evita añadir una base de datos administrada mientras se validan el producto y los créditos disponibles.

Para desplegar una nueva versión en la instancia:

```bash
cd /opt/practicarta/deploy
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

Las copias de PostgreSQL y de las imágenes se generan diariamente a las 03:15 (hora de Lima) en `/opt/practicarta-backups` y se conservan siete días. Para ejecutar y comprobar una copia manualmente:

```bash
/opt/practicarta/deploy/backup.sh
gzip -t /opt/practicarta-backups/practicarta-*.sql.gz
```

## Operación de clientes

Las cuentas con rol de administrador pueden abrir `/dashboard/operaciones/`. Ahí se gestiona manualmente el estado comercial de cada negocio (prueba, activo, pago pendiente, suspendido o cancelado), la fecha de vigencia y notas internas. También se muestran visitas y pedidos iniciados por WhatsApp de los últimos 7 y 30 días.

Cada dueño puede elegir su apariencia en **Mi cuenta** y una paleta de marca al personalizar la carta. El campo **Enlace de tu carta** acepta nombres normales con espacios y los convierte automáticamente a una dirección segura, por ejemplo `Pollería El Sol` pasa a `polleria-el-sol`.
