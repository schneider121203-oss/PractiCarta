# Plan de producto y desarrollo en 5 sprints
## SaaS de carta digital + pedidos por WhatsApp para restaurantes
**Estado:** Documento de arranque para diseño de arquitectura y desarrollo con Codex  
**Mercado inicial:** Perú, con foco en restaurantes, cafeterías, pollerías, sangucherías, dark kitchens y otros negocios pequeños de comida  
**Nombre del producto:** Por definir  
**Modelo:** SaaS B2B de suscripción mensual  
**Objetivo inicial:** Conseguir 1–3 negocios piloto, validar uso real y convertir al menos uno en cliente de pago antes de ampliar el alcance.

---

# 1. Contexto y oportunidad

El producto toma como referencia la categoría de soluciones de carta digital para restaurantes, pero no pretende copiar código, textos, marca, diseño ni activos de ningún competidor.

La referencia competitiva inmediata es Karta Perú, que actualmente ofrece:

- Carta digital accesible por link y QR.
- Personalización de colores y logo.
- Multiidioma ES/EN/PT.
- Cambio de disponibilidad de platos.
- Fotos en planes superiores.
- Analítica.
- Varios menús y sucursales según plan.
- Precios publicados de S/ 9.90, S/ 19.90 y S/ 29.90 al mes.

Otra referencia es OlaClick, que amplía la propuesta hacia pedidos, WhatsApp, delivery, POS, inventario y otras funciones de gestión.

La oportunidad no es intentar reconstruir un ERP para restaurantes. La oportunidad es ocupar un espacio intermedio:

> Una carta digital extremadamente sencilla de configurar que no solo muestre productos, sino que permita al cliente elegirlos y enviar un pedido estructurado al WhatsApp del restaurante.

La ventaja inicial debe provenir de cuatro cosas:

1. Mejor experiencia de compra que una carta QR puramente informativa.
2. Configuración extremadamente sencilla.
3. Funciones útiles incluidas desde planes económicos.
4. Software reutilizable para todos los restaurantes, con costo marginal muy bajo por nuevo cliente.

---

# 2. Problema que resuelve

Un restaurante pequeño suele tener una combinación de estos problemas:

- Envía fotos o PDFs de su menú por WhatsApp.
- Tiene precios desactualizados en imágenes, redes o cartas impresas.
- Necesita volver a imprimir cuando cambia un precio.
- Los clientes preguntan constantemente por precios, disponibilidad, ubicación y delivery.
- Recibe pedidos escritos de manera desordenada.
- No sabe qué productos reciben más interés en su carta digital.
- No tiene página propia o su página es difícil de actualizar.
- Depende de marketplaces que controlan parte de la experiencia comercial.
- El propietario no quiere aprender WordPress, hosting, DNS, CMS ni herramientas complejas.

El producto debe reducir estas fricciones.

No se vende “una página web”.

Se vende:

> “Tu carta siempre actualizada, tus clientes eligen lo que quieren y te mandan el pedido ordenado por WhatsApp.”

---

# 3. Propuesta de valor

## Para el dueño del restaurante

Debe poder:

1. Crear una cuenta.
2. Registrar su negocio.
3. Cargar o importar su carta.
4. Cambiar precios desde celular.
5. Marcar productos como agotados.
6. Publicar inmediatamente.
7. Descargar un QR.
8. Recibir pedidos prearmados en WhatsApp.
9. Consultar métricas simples de interés y conversión.

Sin conocimientos técnicos.

## Para el cliente del restaurante

Debe poder:

1. Escanear un QR.
2. Abrir la carta sin instalar aplicaciones.
3. Navegar categorías.
4. Ver precios y fotos.
5. Añadir productos a un carrito.
6. Seleccionar cantidades y variantes.
7. Elegir consumo en local, recojo o delivery cuando corresponda.
8. Pulsar “Pedir por WhatsApp”.
9. Enviar un mensaje estructurado al negocio.

---

# 4. Diferenciación frente a una carta QR básica

El producto no debe competir únicamente por precio.

La diferencia principal será convertir la carta en un pequeño canal de venta.

Ejemplo:

```text
Cliente escanea QR
        ↓
Visualiza productos
        ↓
Añade 1 pollo + 2 gaseosas + 1 porción
        ↓
Ve total estimado
        ↓
Selecciona "Recojo"
        ↓
Pedir por WhatsApp
        ↓
WhatsApp abre con:

Hola, quisiera realizar este pedido:

1 × Pollo entero ........ S/ 52.00
2 × Inca Kola ........... S/ 10.00
1 × Yuca ................. S/ 9.00

Total estimado: S/ 71.00
Modalidad: Recojo
Origen: Carta web
```

Inicialmente el sistema NO debe procesar el pedido internamente.

WhatsApp continúa siendo el canal final de conversación entre negocio y cliente.

Esto reduce radicalmente la complejidad del MVP.

---

# 5. Principios de producto

## 5.1 Simplicidad sobre cantidad de funciones

Una feature nueva solo se debe construir si:

- Reduce trabajo al restaurante.
- Facilita una venta.
- Facilita actualizar la carta.
- Produce información accionable.
- Ayuda directamente a captar o retener clientes.

No añadir funciones solo porque otro SaaS las tenga.

## 5.2 Mobile first

El público final escaneará QR desde un teléfono.

La interfaz pública debe diseñarse primero para pantallas móviles.

El dashboard del dueño también debe ser completamente usable desde celular.

## 5.3 Un monolito antes que microservicios

Este proyecto no necesita microservicios.

La arquitectura inicial debe favorecer:

- Desarrollo rápido.
- Despliegue barato.
- Debug sencillo.
- Una sola base de código.
- Portabilidad fuera de AWS.
- Poca carga operativa.

## 5.4 Multi-tenant desde el inicio

Aunque existan solo dos clientes piloto, el sistema debe modelarse como SaaS multi-tenant.

Cada negocio debe quedar aislado lógicamente mediante claves de pertenencia y autorización.

Nunca asumir que habrá un solo restaurante.

## 5.5 AWS es una ventaja temporal, no una dependencia

Existe acceso temporal a aproximadamente USD 200 en créditos AWS durante un máximo de seis meses.

El software debe utilizar esos créditos para desarrollo, pruebas y primeras cargas reales, pero NO diseñarse de manera que migrar fuera de AWS requiera reescribir la aplicación.

---

# 6. Insumos disponibles

## Recursos técnicos

- Python.
- Django.
- PostgreSQL.
- Docker.
- HTML/CSS/JavaScript.
- Experiencia con despliegues y servicios cloud.
- AWS con aproximadamente USD 200 en créditos por hasta seis meses.
- Codex como apoyo de ingeniería y pair programming.

## Enfoque de stack recomendado

### Backend

- Python 3.13.
- Django 5.2 LTS.
- Django ORM.
- Django Admin para operaciones internas.
- API JSON únicamente donde aporte valor.

Se prefiere Django 5.2 LTS frente a perseguir la última versión por estabilidad y soporte prolongado.

### Frontend

Para el MVP:

- Django Templates.
- HTMX para interacciones parciales.
- Alpine.js solo cuando sea necesario.
- Tailwind CSS o CSS utilitario equivalente.

Evitar React/Next.js separado durante el MVP salvo que exista una razón técnica demostrable.

Separar frontend y backend duplicaría autenticación, despliegue, testing y superficie de errores sin generar suficiente valor en esta etapa.

### Base de datos

- PostgreSQL 17 o 18.
- UUID como identificadores públicos cuando convenga.
- Índices explícitos para slugs, relaciones multi-tenant y consultas de analítica.

### Archivos

Crear una interfaz abstracta de almacenamiento.

Producción inicial:

- Amazon S3 para imágenes.
- CloudFront opcional cuando exista tráfico suficiente.

Desarrollo:

- almacenamiento local o MinIO.

La aplicación nunca debe depender directamente de rutas específicas de S3.

### Procesamiento asíncrono

No introducir Celery/Redis en el Sprint 1.

Añadir una cola únicamente cuando aparezca trabajo que realmente necesite ejecución diferida, por ejemplo:

- procesamiento de imágenes;
- OCR/importación automática;
- traducciones;
- agregación de analítica;
- emails.

Para primeras versiones puede utilizarse Django-Q, Huey, Celery o un worker sencillo, pero la elección debe tomarse cuando exista el caso de uso.

### Infraestructura

La aplicación debe empaquetarse con Docker.

Debe ser desplegable como mínimo en:

- AWS;
- una VPS común;
- Render/Railway/Fly.io u otro PaaS compatible;
- Docker Compose.

No usar servicios propietarios de AWS dentro de la lógica central.

---

# 7. Modelo de precios inicial

No crear demasiados planes.

Se propone comenzar con:

## Prueba

**14 días gratis**

Sin tarjeta inicialmente.

Objetivo: reducir fricción para conseguir pilotos.

## Básico — S/ 8.90 / mes

- 1 negocio.
- 1 sucursal.
- 1 carta activa.
- Productos suficientes para un restaurante pequeño.
- Categorías.
- Fotos.
- QR.
- Colores/logo.
- Agotado.
- Carrito.
- Pedido por WhatsApp.
- Analítica básica.

## Pro — S/ 14.90 / mes

Todo lo anterior más:

- Productos ilimitados.
- Varios menús.
- Menú del día.
- Programación horaria.
- Promociones.
- QR por mesa.
- Analítica ampliada.
- Importación asistida de carta.
- Multiidioma.

## Futuro Business — ~S/ 24.90 / mes

NO construir durante el MVP salvo que un cliente real lo solicite.

Posibles funciones:

- varias sucursales;
- usuarios por negocio;
- roles;
- analítica consolidada;
- soporte prioritario.

El precio es una hipótesis y debe validarse con clientes reales.

No competir mediante una carrera permanente hacia el precio más bajo.

---

# 8. Modelo de dominio inicial

Entidades principales:

```text
User
 └── Membership
      └── Business
           ├── Branch
           ├── Menu
           │    └── Category
           │         └── Product
           │              └── ProductOptionGroup
           │                   └── ProductOption
           ├── QRCode
           ├── Promotion
           ├── Subscription
           └── AnalyticsEvent
```

## User

Usuario autenticado.

Campos sugeridos:

- id
- email
- password_hash
- first_name
- last_name
- is_active
- created_at
- updated_at

Usar email como identidad principal.

## Business

Representa la marca/restaurante.

Campos iniciales:

- id
- owner/membership
- name
- slug
- description
- logo
- cover_image
- primary_color
- secondary_color
- phone
- whatsapp_number
- instagram_url
- tiktok_url
- maps_url
- address
- timezone
- currency
- default_language
- is_published
- created_at
- updated_at

## Branch

Preparar el modelo desde el inicio aunque inicialmente se permita solo una sucursal.

Campos:

- business
- name
- address
- phone
- whatsapp_number
- latitude
- longitude
- opening_hours
- delivery_enabled
- pickup_enabled
- dine_in_enabled

## Menu

Campos:

- business
- branch nullable
- name
- slug
- description
- menu_type
- starts_at nullable
- ends_at nullable
- days_of_week
- active
- sort_order

Tipos previstos:

- regular
- breakfast
- lunch
- dinner
- daily
- promotion

## Category

Campos:

- menu
- name
- description
- sort_order
- active

## Product

Campos:

- category
- name
- description
- price
- promotional_price nullable
- image
- active
- available
- featured
- sort_order

Nunca borrar automáticamente un producto solo porque el dueño lo quite de la carta.

Preferir soft delete o estado inactivo donde tenga sentido.

## ProductOptionGroup

Ejemplos:

- tamaño;
- punto de cocción;
- acompañamiento;
- sabor;
- extras.

Campos:

- product
- name
- required
- min_choices
- max_choices

## ProductOption

Campos:

- option_group
- name
- price_delta
- available

## QRCode

Debe permitir identificar contexto.

Ejemplos:

```text
/cevicheria-pepito
/cevicheria-pepito?table=7
/cevicheria-pepito?source=instagram
```

Guardar:

- business
- branch
- code
- table_number nullable
- campaign/source nullable
- created_at

## AnalyticsEvent

Eventos iniciales:

```text
menu_view
category_view
product_view
add_to_cart
remove_from_cart
begin_checkout
whatsapp_click
google_maps_click
instagram_click
review_click
```

Campos:

- business_id
- branch_id nullable
- menu_id nullable
- product_id nullable
- session_id
- event_type
- metadata JSONB
- referrer
- device_type
- created_at

No almacenar información personal innecesaria.

---

# 9. Seguridad mínima obligatoria

Aunque sea un micro-SaaS, la seguridad no debe dejarse para el final.

## Autorización multi-tenant

Toda query del dashboard debe comprobar pertenencia al negocio.

Nunca:

```python
Product.objects.get(id=product_id)
```

sin verificar tenant.

Preferir patrones similares a:

```python
Product.objects.get(
    id=product_id,
    category__menu__business=current_business
)
```

o servicios/repositories que encapsulen esta regla.

## Autenticación

- sesiones seguras de Django;
- CSRF habilitado;
- cookies Secure en producción;
- HttpOnly;
- SameSite;
- rate limiting en login;
- política razonable de contraseña;
- recuperación de contraseña segura.

## Archivos

- validar MIME real;
- limitar tamaño;
- generar nombres aleatorios;
- no confiar en extensiones;
- re-encodear imágenes si es viable;
- impedir archivos ejecutables;
- no servir uploads desde el proceso principal de la aplicación.

## Inputs

- validación server-side;
- escape por defecto;
- evitar HTML arbitrario en descripciones;
- sanitización cuando se permita rich text.

## Secretos

Nunca guardar credenciales AWS/API en repositorio.

Usar variables de entorno o secret manager.

## Pagos

Nunca almacenar datos de tarjetas.

La tokenización y procesamiento debe delegarse al proveedor de pagos.

---

# 10. Analítica mínima útil

Evitar dashboards gigantes.

El propietario inicialmente necesita responder cinco preguntas:

1. ¿Cuántas personas vieron mi carta?
2. ¿Qué productos reciben más interés?
3. ¿Cuántas personas agregaron algo al carrito?
4. ¿Cuántas terminaron pulsando WhatsApp?
5. ¿Qué QR/canal genera más actividad?

Embudo:

```text
Menu views
   ↓
Product views
   ↓
Add to cart
   ↓
Begin checkout
   ↓
WhatsApp click
```

Métrica aproximada:

```text
WhatsApp conversion =
whatsapp_click / unique_menu_sessions
```

No afirmar que cada click es una venta.

Debe mostrarse como:

> “Personas que iniciaron pedido por WhatsApp”

y no como:

> “Ventas”.

---

# 11. SPRINT 1 — Fundamentos, arquitectura y publicación de una carta

## Objetivo

Terminar el sprint con una aplicación desplegable donde un usuario pueda crear un negocio, registrar categorías/productos y publicar una carta pública funcional.

Este sprint establece la arquitectura definitiva del MVP.

## Historias de usuario

### US-1 Registro

Como propietario quiero crear una cuenta para administrar mi restaurante.

### US-2 Crear negocio

Como usuario quiero registrar nombre, descripción, WhatsApp y datos básicos de mi restaurante.

### US-3 Crear categorías

Como propietario quiero ordenar productos por categorías.

### US-4 Crear productos

Como propietario quiero registrar nombre, descripción y precio.

### US-5 Publicar carta

Como propietario quiero obtener una URL pública de mi carta.

## Tareas técnicas

### Repositorio

Crear:

```text
/
├── app/
├── config/
├── docker/
├── docs/
├── tests/
├── static/
├── templates/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── pyproject.toml
├── README.md
└── Makefile
```

La estructura exacta puede variar, pero debe quedar documentada.

### Aplicaciones Django sugeridas

```text
accounts
businesses
menus
catalog
analytics
billing
core
```

No crear dependencias circulares.

### Docker

Docker Compose para desarrollo:

- web;
- postgres.

No añadir Redis todavía.

### Autenticación

- Custom User desde el primer migration.
- Login.
- Logout.
- Registro.
- Password reset preparado.

### Multi-tenancy

Implementar aislamiento por `Business`.

Crear helper/service central para determinar `current_business`.

Agregar pruebas automáticas que intenten acceder a objetos de otro negocio.

### CRUD

Implementar CRUD de:

- Business;
- Menu;
- Category;
- Product.

### Carta pública

Ruta sugerida:

```text
/m/<business_slug>/
```

Posteriormente puede migrarse a:

```text
/<business_slug>/
```

si no genera conflictos de routing.

### Diseño inicial

Mobile first.

No perseguir diseño definitivo.

Priorizar:

- lectura;
- velocidad;
- categorías visibles;
- precio;
- CTA.

## Entregables

- repositorio inicial;
- arquitectura documentada;
- Docker Compose;
- PostgreSQL;
- autenticación;
- CRUD funcional;
- primera carta pública;
- seed/demo restaurant;
- pruebas básicas;
- CI mínima.

## Criterios de aceptación

- Dos usuarios diferentes pueden crear negocios.
- Ninguno puede modificar productos del otro.
- Un dueño puede crear al menos 30 productos sin problemas.
- La carta es usable desde móvil.
- Un cambio de precio aparece en la carta pública inmediatamente.
- El proyecto puede levantarse desde cero con instrucciones del README.
- `docker compose up` debe ser suficiente para entorno local después de configurar `.env`.

## Pruebas obligatorias

- creación de usuario;
- creación de negocio;
- aislamiento tenant;
- CRUD producto;
- slug único;
- autorización;
- render público;
- producto inactivo no visible.

## Fuera de alcance

- pagos;
- OCR;
- traducciones;
- analítica avanzada;
- múltiples sucursales operativas;
- pedidos persistidos.

---

# 12. SPRINT 2 — Experiencia pública, imágenes, QR y personalización

## Objetivo

Convertir la carta funcional del Sprint 1 en un producto que pueda enseñarse a un restaurante real.

## Historias

### US-6 Subir logo

El dueño puede subir su logo.

### US-7 Fotos

El dueño puede subir imágenes de platos.

### US-8 Personalización

El dueño puede elegir colores y estilo visual.

### US-9 Disponibilidad

El dueño puede marcar un producto como agotado sin eliminarlo.

### US-10 QR

El dueño puede descargar un QR que abre su carta.

## Diseño público

Crear tres temas como máximo:

1. Minimal.
2. Gourmet.
3. Casual/Fast Food.

No construir editor drag-and-drop.

Variables permitidas:

- logo;
- portada;
- color principal;
- color secundario;
- tema;
- fuente entre opciones predefinidas.

## Gestión de imágenes

Al subir:

1. validar;
2. re-encodear;
3. redimensionar;
4. generar thumbnail;
5. almacenar versión optimizada.

Preferir WebP/AVIF cuando el navegador lo soporte.

Establecer límites.

Ejemplo:

```text
imagen original <= 8 MB
render final <= ~300–500 KB idealmente
thumbnail <= ~100 KB
```

Los números son objetivos, no contratos estrictos.

## QR

Generar QR como SVG o PNG.

Debe apuntar a URL del negocio.

Soportar parámetros opcionales:

```text
?table=4
?source=flyer
?source=instagram
```

No crear todavía dashboard complejo por mesa.

## Performance

Objetivo práctico para la carta:

- HTML inicial pequeño;
- lazy-loading de imágenes;
- compresión;
- cache headers;
- cero JS pesado;
- sin trackers externos innecesarios.

## Dashboard responsive

El propietario debe poder desde su teléfono:

- cambiar precio;
- marcar agotado;
- cambiar foto;
- editar descripción.

Esta experiencia tiene prioridad sobre un dashboard de escritorio sofisticado.

## Entregables

- imágenes;
- logos;
- portada;
- tres temas;
- personalización;
- modo agotado;
- QR descargable;
- responsive dashboard;
- primera versión visual apta para demo comercial.

## Criterios de aceptación

- Escanear QR abre la carta correcta.
- El QR sigue funcionando tras modificar productos.
- Marcar “agotado” actualiza inmediatamente la UI.
- Un restaurante puede actualizar un precio en menos de 30 segundos desde celular.
- Las imágenes no deforman el layout.
- Si falla una imagen existe fallback.
- Lighthouse/mobile performance razonable en una carta demo.

## Fuera de alcance

- editor visual libre;
- dominio personalizado;
- vídeos;
- almacenamiento de fotos originales indefinidamente;
- generación de imágenes con IA.

---

# 13. SPRINT 3 — Carrito y pedidos por WhatsApp

## Objetivo

Transformar la carta de un catálogo informativo en un canal de intención de compra.

Este es el sprint que crea la diferenciación central.

## Historias

### US-11 Añadir al carrito

El cliente puede añadir productos y cantidades.

### US-12 Variantes

El cliente puede elegir variantes como tamaño o acompañamiento.

### US-13 Total

El cliente ve total estimado.

### US-14 Modalidad

El cliente elige:

- local;
- recojo;
- delivery;

según lo habilitado por el negocio.

### US-15 WhatsApp

El cliente puede enviar el pedido preformateado por WhatsApp.

## Importante

El MVP NO debe:

- confirmar pagos;
- reservar stock;
- crear orden transaccional;
- asignar repartidor;
- confirmar que el restaurante aceptó;
- afirmar que el pedido fue completado.

El restaurante y cliente confirman todo por WhatsApp.

## Carrito

Preferir estado local del navegador.

Puede utilizar:

- LocalStorage;
- sessionStorage;

según decisión técnica.

No requiere login del cliente.

Ejemplo de estructura:

```json
{
  "items": [
    {
      "product_id": "uuid",
      "name": "Pollo entero",
      "quantity": 1,
      "unit_price": 52,
      "options": []
    }
  ],
  "source": {
    "table": 7,
    "campaign": null
  }
}
```

El servidor debe seguir siendo fuente de verdad de precios al generar checkout cuando sea relevante.

No confiar ciegamente en precios manipulables desde JS.

## Deep link de WhatsApp

Generar mensaje URL-encoded.

Ejemplo:

```text
https://wa.me/51999999999?text=...
```

Formato:

```text
Hola 👋 Quisiera realizar este pedido:

1 × Pollo entero — S/ 52.00
  - Papas fritas

2 × Inca Kola — S/ 10.00

Total estimado: S/ 62.00

Modalidad: Recojo
Origen: Carta digital
```

Para mesa:

```text
Mesa: 7
```

## Productos con opciones

Permitir grupos simples.

Ejemplo:

```text
Hamburguesa

Tamaño
○ Simple
○ Doble (+S/5)

Extras
□ Queso (+S/2)
□ Tocino (+S/3)
```

No intentar construir un motor de reglas complejo.

## CTA

El botón debe ser claramente visible:

```text
Ver pedido — S/ 43.00
```

y posteriormente:

```text
Pedir por WhatsApp
```

## Métricas básicas

Registrar desde este sprint:

- menu_view;
- product_view;
- add_to_cart;
- begin_checkout;
- whatsapp_click.

## Entregables

- carrito;
- cantidades;
- opciones;
- total;
- modalidades;
- QR por mesa básico;
- WhatsApp deep link;
- eventos de conversión.

## Criterios de aceptación

- Carrito funciona sin autenticación.
- Actualizar página no destruye carrito dentro de la sesión prevista.
- Producto agotado no puede añadirse.
- Total coincide con productos/opciones actuales.
- WhatsApp recibe un mensaje legible.
- Mesa/origen se conserva.
- Eventos no bloquean la UX si falla analítica.
- No se almacenan números de teléfono del consumidor final innecesariamente.

## Métrica principal del producto a partir de este sprint

```text
WhatsApp Intent Rate =
sesiones con whatsapp_click /
sesiones únicas de carta
```

---

# 14. SPRINT 4 — Menú inteligente, programación, importación y analítica

## Objetivo

Eliminar trabajo manual al dueño y crear razones claras para pagar una suscripción Pro.

## 14.1 Menú del día

Permitir:

```text
Menú ejecutivo
Disponible:
Lunes–Viernes
11:30–16:00
```

El sistema decide automáticamente si mostrarlo.

La lógica debe respetar timezone del negocio.

## 14.2 Productos y promociones programadas

Ejemplos:

```text
Happy hour:
Viernes 18:00–22:00

Desayuno:
07:00–11:00
```

No crear un motor promocional complejo.

Basta con ventanas temporales y precios promocionales simples.

## 14.3 Importación asistida

Objetivo:

El dueño carga:

- foto;
- PDF;
- captura de pantalla;

y el sistema intenta producir:

```text
Categoría
Producto
Descripción
Precio
```

Flujo:

```text
Upload
  ↓
Extracción
  ↓
Parser
  ↓
Borrador
  ↓
Pantalla de revisión
  ↓
Usuario corrige
  ↓
Importar
```

Nunca publicar automáticamente contenido extraído sin revisión humana.

## Arquitectura para importación

Crear interfaz:

```python
class MenuImporter:
    def extract(self, file) -> ImportDraft:
        ...
```

La implementación puede cambiar sin afectar el dominio.

Posibles backends:

- OCR tradicional;
- Amazon Textract;
- modelo multimodal externo;
- procesamiento local;
- combinación.

El MVP puede empezar con la opción más simple/costo-efectiva.

## 14.4 Multiidioma

El modelo de datos debe soportar traducciones.

Ejemplo conceptual:

```text
Product
ProductTranslation
    language
    name
    description
```

Idiomas iniciales:

- es;
- en;
- pt.

La traducción automática es asistencia.

El dueño puede editar el resultado.

No traducir precios, marcas ni nombres propios indiscriminadamente.

## 14.5 Analytics Dashboard

Mostrar:

### Resumen

- visitas a carta;
- sesiones únicas aproximadas;
- productos vistos;
- add-to-cart;
- inicios de pedido WhatsApp;
- tasa de intención.

### Productos

Tabla:

```text
Producto            Vistas   Añadidos   WhatsApp*
Pollo entero          240       71        -
Ceviche clásico       182       42        -
```

No atribuir una venta a un producto si el producto no puede rastrearse hasta una compra confirmada.

### Fuentes

```text
QR mesa
Instagram
Link WhatsApp
Flyer
Directo
```

## Privacidad

Preferir analítica first-party.

No depender inicialmente de Google Analytics.

Evitar cookies de marketing.

Generar session ID pseudónimo.

Definir política de retención.

Ejemplo:

- eventos crudos: 90 días;
- agregados: más tiempo.

La política final debe documentarse antes de producción comercial.

## Entregables

- programación horaria;
- menú del día;
- promociones simples;
- importador asistido beta;
- traducciones;
- analytics dashboard;
- embudo.

## Criterios de aceptación

- Un producto programado aparece/desaparece correctamente.
- Timezone se respeta.
- Un menú fotografiado puede convertirse en borrador editable.
- Nada extraído se publica sin confirmación.
- Analytics coincide razonablemente con eventos de prueba.
- Un evento duplicado no debe inflar métricas de forma absurda.
- El dueño entiende las métricas sin documentación técnica.

---

# 15. SPRINT 5 — Suscripciones, producción, piloto y lanzamiento

## Objetivo

Pasar de “proyecto bonito” a producto cobrable.

## 15.1 Billing

Crear abstracción:

```python
class BillingProvider:
    def create_subscription(...)
    def cancel_subscription(...)
    def get_status(...)
    def handle_webhook(...)
```

Primera implementación recomendada:

- Mercado Pago Suscripciones;

Alternativa:

- Culqi Suscripciones.

Ambos soportan cobros recurrentes en Perú.

La aplicación no debe almacenar datos de tarjeta.

## Planes

Modelo:

```text
Plan
Subscription
BillingEvent
```

Estados internos sugeridos:

```text
trialing
active
past_due
canceled
expired
```

No asumir que los estados del proveedor son idénticos a los internos.

Mapearlos.

## Webhooks

Requisitos:

- verificar autenticidad;
- idempotencia;
- almacenar provider_event_id;
- procesar eventos una sola vez;
- logs;
- posibilidad de replay manual;
- pruebas.

## Política inicial ante fallo de pago

No borrar datos.

Ejemplo:

```text
Día 0: pago falla
Día 1–5: gracia
Día 5+: carta permanece visible, dashboard restringe funciones premium
```

La política puede variar, pero debe ser explícita.

## 15.2 Trial

14 días.

Durante trial:

- producto completo o casi completo;
- banner indicando días restantes;
- CTA para activar suscripción.

No pedir tarjeta al registrarse durante piloto inicial.

## 15.3 Página comercial

Landing mínima:

```text
Hero
Problema
Demo interactiva
Cómo funciona
Características
Comparación de planes
FAQ
CTA
```

Mensaje principal tentativo:

> Tu carta digital que convierte visitas en pedidos por WhatsApp.

Secundario:

> Actualiza precios en segundos, comparte tu QR y deja que tus clientes armen el pedido antes de escribirte.

## 15.4 Demo pública

Crear restaurante ficticio de calidad:

```text
Cevichería / Pollería / Cafetería
```

La demo debe mostrar:

- fotografías;
- categorías;
- promoción;
- carrito;
- opciones;
- pedido WhatsApp simulado.

## 15.5 Onboarding

Wizard:

```text
1. Tu negocio
2. WhatsApp
3. Logo/colores
4. Carta
5. Publicar
6. Descargar QR
```

Objetivo:

Un usuario debe poder publicar sin tutorial externo.

## 15.6 Observabilidad

Mínimo:

- logs estructurados;
- health endpoint;
- error tracking;
- uptime monitor;
- métricas de aplicación;
- backups;
- alertas de facturación AWS.

## 15.7 Backups

PostgreSQL:

- backup diario;
- retención definida;
- prueba documentada de restore.

Un backup nunca se considera válido hasta haber probado una restauración.

## 15.8 Control de costos AWS

Configurar desde el primer despliegue:

- AWS Budget;
- alertas;
- límite razonable;
- revisión semanal durante piloto.

Los créditos deben verse como presupuesto de experimentación, no como justificación para usar servicios caros.

## 15.9 Piloto real

Conseguir 1–3 restaurantes.

No esperar a terminar absolutamente todo antes de enseñar el sistema.

Idealmente:

- piloto 1 durante Sprint 3;
- piloto 2 durante Sprint 4;
- piloto 3 durante Sprint 5.

Registrar:

- tiempo para crear carta;
- cantidad de ayuda requerida;
- preguntas frecuentes;
- errores;
- funciones que realmente utilizan;
- frecuencia de cambios de precio;
- número de sesiones;
- clicks a WhatsApp;
- disposición a pagar.

## Entregables

- billing;
- planes;
- trial;
- webhooks;
- landing;
- onboarding;
- producción endurecida;
- backup;
- monitoring;
- 1–3 pilotos;
- checklist de lanzamiento.

## Criterios de aceptación

- Usuario puede iniciar trial.
- Suscripción activa desbloquea plan correcto.
- Cancelación no elimina datos.
- Webhook repetido no duplica efectos.
- Pago fallido se maneja sin corrupción.
- Aplicación restaura desde backup probado.
- Carta sigue funcionando aunque falle temporalmente billing.
- Existe al menos un negocio real utilizando la aplicación.
- Existe feedback escrito de pilotos.

---

# 16. Arquitectura lógica objetivo

```text
                     ┌─────────────────────────┐
                     │        Browser          │
                     │ Owner / Customer Mobile │
                     └───────────┬─────────────┘
                                 │ HTTPS
                                 ▼
                     ┌─────────────────────────┐
                     │ Reverse proxy / CDN     │
                     └───────────┬─────────────┘
                                 │
                                 ▼
                     ┌─────────────────────────┐
                     │ Django Monolith         │
                     │                         │
                     │ accounts                │
                     │ businesses              │
                     │ menus/catalog           │
                     │ cart helpers            │
                     │ analytics               │
                     │ billing                 │
                     │ imports                 │
                     └───────┬────────┬────────┘
                             │        │
                 ┌───────────┘        └──────────────┐
                 ▼                                   ▼
        ┌─────────────────┐                 ┌────────────────┐
        │ PostgreSQL      │                 │ Object Storage │
        │ transactional   │                 │ product images │
        └─────────────────┘                 └────────────────┘

                 External integrations
                 ─────────────────────
                 WhatsApp deep links
                 Mercado Pago / Culqi
                 OCR/AI provider optional
```

No meter Redis, Kafka, Kubernetes, ECS cluster, event buses ni servicios separados hasta que un requisito real lo exija.

---

# 17. Arquitectura AWS inicial sugerida

Hay dos objetivos contradictorios:

1. aprovechar créditos;
2. mantener costo bajo después.

Por eso la infraestructura debe mantenerse intercambiable.

## Opción MVP

```text
Route 53 / DNS
        ↓
CloudFront opcional
        ↓
EC2 pequeño o Lightsail equivalente
        ↓
Docker
 ├── Django/Gunicorn
 └── reverse proxy

PostgreSQL:
- inicialmente servicio gestionado si el crédito lo permite;
- o PostgreSQL en infraestructura pequeña durante desarrollo;
- migrable sin cambios de dominio.

S3:
- imágenes de productos;
- logos;
- assets generados.
```

Para producción real es preferible separar base de datos y aplicación cuando el presupuesto lo permita.

## No casarse con AWS

Usar:

```text
DATABASE_URL
STORAGE_BACKEND
MEDIA_BUCKET
EMAIL_BACKEND
BILLING_PROVIDER
```

como configuración.

Toda integración externa debe estar detrás de adapters/services.

Objetivo:

Mover aplicación a otra VPS/PaaS debe ser operación de despliegue, no reescritura.

---

# 18. Estrategia de testing

## Pirámide aproximada

### Unit

- cálculo de total;
- disponibilidad horaria;
- promociones;
- formateo WhatsApp;
- pricing;
- permisos.

### Integration

- modelos;
- views;
- tenant isolation;
- billing webhooks;
- upload;
- analytics.

### End-to-end

Flujos críticos:

```text
Register
→ Create business
→ Add product
→ Publish
→ Scan/open menu
→ Add to cart
→ WhatsApp
```

y:

```text
Trial
→ Subscribe
→ webhook
→ Plan active
```

## Regla

No perseguir 100 % de cobertura.

Priorizar rutas que puedan:

- exponer datos entre tenants;
- cobrar incorrectamente;
- romper un pedido;
- publicar precios incorrectos;
- impedir acceso a la carta.

---

# 19. Definition of Done global

Una tarea no está terminada solo porque “funciona en mi máquina”.

Debe cumplir según corresponda:

- código revisable;
- tests;
- lint/format;
- autorización;
- responsive;
- estado vacío;
- mensajes de error;
- logging razonable;
- migraciones;
- documentación;
- variables en `.env.example`;
- sin secretos;
- deploy reproducible;
- aceptación manual.

---

# 20. Métricas de éxito del MVP

No medir éxito por cantidad de código.

## Producto

- tiempo medio para publicar primera carta;
- % de registros que publican;
- tiempo para cambiar un precio;
- visitas por restaurante;
- add-to-cart rate;
- WhatsApp Intent Rate.

## Negocio

Objetivo inicial:

```text
3 pilotos
↓
1 cliente pagando
↓
5 clientes pagando
↓
10 clientes pagando
```

Con S/ 8.90:

```text
10 clientes = S/ 89 MRR
20 clientes = S/ 178 MRR
30 clientes = S/ 267 MRR
```

Con mezcla de Básico/Pro, alcanzar S/ 100–300 mensuales requiere relativamente pocos clientes.

La prioridad inicial no es “escalar”.

La prioridad es probar que restaurantes reales:

1. lo usan;
2. vuelven al dashboard;
3. reciben interacciones;
4. pagan por mantenerlo.

---

# 21. Hipótesis que deben validarse

Antes de construir features avanzadas preguntar a clientes reales:

1. ¿Actualmente cómo comparten su carta?
2. ¿Con qué frecuencia cambian precios?
3. ¿Usan QR?
4. ¿Reciben pedidos por WhatsApp?
5. ¿Cuál es la parte más molesta del proceso?
6. ¿Necesitan delivery/recojo/local?
7. ¿Usan menú del día?
8. ¿Necesitan varias cartas?
9. ¿Qué tan difícil sería para ellos cargar 50 productos?
10. ¿Pagarían S/ 9–15 al mes?
11. ¿Prefieren pagar mensualmente por tarjeta o manualmente?
12. ¿Quién actualizaría el menú?
13. ¿Necesitan varias personas administrándolo?
14. ¿Qué función haría que dejaran de usar una foto/PDF?

No explicar el producto primero.

Escuchar su proceso actual primero.

---

# 22. Funciones deliberadamente fuera del MVP

No construir durante estos cinco sprints salvo evidencia fuerte:

- POS.
- Inventario.
- Facturación electrónica.
- Cocina/KDS.
- Repartidores.
- Optimización de rutas.
- Marketplace.
- Aplicación Android/iOS nativa.
- Programa completo de fidelización.
- CRM complejo.
- Chatbot IA.
- Reservas de mesa.
- Integración con Rappi/PedidosYa.
- Motor de descuentos complejo.
- Multiempresa contable.
- IA que genere fotos de platos.
- Kubernetes.
- Microservicios.

Cada una puede convertirse posteriormente en producto propio, pero ahora diluiría el objetivo.

---

# 23. Backlog post-MVP

Solo después de validar clientes.

Prioridad candidata:

1. dominio personalizado;
2. reseñas Google;
3. botón Instagram/TikTok;
4. integración Google Maps;
5. sucursales;
6. usuarios/roles;
7. QR analytics avanzado;
8. cupones;
9. pedido persistente opcional;
10. integración WhatsApp Business API;
11. notificaciones;
12. exportación CSV;
13. panel reseller;
14. branding white-label.

---

# 24. Posicionamiento recomendado

Evitar:

> “Software SaaS omnicanal para digitalización gastronómica.”

Preferir:

> “Tu carta digital con pedidos por WhatsApp.”

o:

> “Tus clientes escanean, eligen y te mandan el pedido listo por WhatsApp.”

Submensaje:

> “Cambia precios y productos desde tu celular sin volver a imprimir tu carta.”

Esto explica el valor en segundos.

---

# 25. Riesgos

## Riesgo 1 — El desarrollo es fácil, vender no

Mitigación:

Conseguir pilotos antes de terminar todas las features.

## Riesgo 2 — Guerra de precios

Mitigación:

Competir en flujo de compra y facilidad, no solo en S/1 menos.

## Riesgo 3 — Demasiado soporte

Mitigación:

Onboarding excelente, UX móvil y límites claros.

## Riesgo 4 — Scope creep

Mitigación:

Cada feature debe responder a feedback o métrica.

## Riesgo 5 — AWS se vuelve caro

Mitigación:

Docker + PostgreSQL estándar + storage abstraction + budgets.

## Riesgo 6 — Datos cruzados entre negocios

Mitigación:

Multi-tenancy probado automáticamente desde Sprint 1.

## Riesgo 7 — La analítica se interpreta como ventas

Mitigación:

Nombrar eventos correctamente. WhatsApp click significa intención, no venta.

---

# 26. Indicaciones específicas para Codex

Este documento describe producto y restricciones.

Codex NO debe empezar generando todo el SaaS de una sola vez.

Para cada sprint:

1. Revisar requisitos.
2. Proponer arquitectura concreta del sprint.
3. Identificar decisiones irreversibles o costosas.
4. Crear/actualizar ADR cuando corresponda.
5. Definir modelos y contratos.
6. Implementar vertical slices pequeños.
7. Añadir tests.
8. Ejecutar linters/tests.
9. Actualizar documentación.
10. Entregar resumen de cambios y deuda técnica.

## Antes de comenzar Sprint 1

Codex debe producir:

```text
docs/
├── architecture.md
├── domain-model.md
├── security.md
├── deployment.md
├── decisions/
│   ├── ADR-001-monolith.md
│   ├── ADR-002-multitenancy.md
│   ├── ADR-003-storage.md
│   └── ADR-004-frontend.md
└── sprints/
    ├── sprint-1.md
    ├── sprint-2.md
    ├── sprint-3.md
    ├── sprint-4.md
    └── sprint-5.md
```

## Restricciones para Codex

- No introducir microservicios sin justificarlo.
- No introducir dependencias innecesarias.
- No implementar una feature fuera del sprint actual sin pedir justificación arquitectónica.
- No almacenar secretos.
- No desactivar CSRF para “hacerlo funcionar”.
- No utilizar `*` en CORS en producción.
- No confiar en IDs proporcionados por el cliente para autorización.
- No almacenar tarjetas.
- No confundir WhatsApp click con compra.
- No diseñar solo para escritorio.
- No optimizar prematuramente.
- No acoplar dominio a AWS.
- No hacer migraciones destructivas sin estrategia.
- No borrar datos del cliente al cancelar suscripción.

## Preferencias de código

- código simple;
- funciones pequeñas;
- typing cuando aporte claridad;
- nombres descriptivos;
- servicios para lógica de negocio;
- views delgadas;
- modelos sin convertirse en “god objects”;
- tests de autorización;
- idempotencia donde exista integración externa;
- logs sin datos sensibles.

---

# 27. Primer prompt recomendado para Codex

Copiar este documento completo y luego pedir:

```text
Quiero empezar el Sprint 1 de este producto.

No escribas todavía toda la aplicación.

Primero:

1. Analiza críticamente los requisitos del documento.
2. Propón la arquitectura concreta del monolito Django.
3. Define los módulos/apps y sus responsabilidades.
4. Define el modelo de datos mínimo del Sprint 1.
5. Identifica riesgos de multi-tenancy y autorización.
6. Propón la estructura del repositorio.
7. Define estrategia de configuración por entornos.
8. Define Docker Compose local.
9. Define testing y CI inicial.
10. Crea los ADR necesarios.

Prioriza simplicidad, seguridad y portabilidad.

El sistema debe poder desplegarse inicialmente en AWS usando créditos disponibles, pero no debe quedar acoplado a AWS.

Después de presentar la propuesta arquitectónica, divide la implementación del Sprint 1 en tareas pequeñas y ordenadas. No avances al Sprint 2.
```

---

# 28. Referencias de mercado y técnicas

Consultadas como contexto al diseñar este plan:

- Karta Perú: https://kartape.com/
- OlaClick: https://olaclick.com/es/carta-para-restaurantes/
- AWS Free Tier: https://aws.amazon.com/free/
- Mercado Pago Suscripciones Perú: https://www.mercadopago.com.pe/developers/es/reference/online-payments/subscriptions/overview
- Culqi Suscripciones: https://docs.culqi.com/es/documentacion/pagos-online/recurrencia/suscripciones/
- Django: https://www.djangoproject.com/download/
- PostgreSQL: https://www.postgresql.org/support/versioning/

---

# 29. Resumen ejecutivo de los cinco sprints

| Sprint | Objetivo | Resultado visible |
|---|---|---|
| 1 | Arquitectura + catálogo | Restaurante crea y publica carta |
| 2 | Producto presentable | Fotos + diseño + QR + móvil |
| 3 | Diferenciador | Carrito + pedido estructurado a WhatsApp |
| 4 | Inteligencia operativa | Horarios + importación + traducciones + analytics |
| 5 | Monetización | Suscripciones + onboarding + producción + pilotos |

Resultado esperado al terminar:

> Un SaaS pequeño pero comercialmente utilizable, capaz de registrar restaurantes, publicar cartas QR, permitir selección de productos, enviar pedidos estructurados por WhatsApp, medir intención de compra y cobrar una suscripción mensual, sin haber construido innecesariamente un POS o sistema integral de restaurantes.
