# 🧾 Sistema de Ventas y Facturación
### Proyecto Escolar · 4to Semestre · Programación Orientada a Objetos con Python + Django

> **Stack:** Python · Django 5+ · Bootstrap 5 · SQLite  
> **Patrón:** MVT (Model – View – Template)  
> **Asignatura:** Programación Orientada a Objetos (POO)

---

## Índice de Contenidos

1. [Descripción del Sistema](#1--descripción-del-sistema)
2. [Estructura de Directorios](#2--estructura-de-directorios)
3. [Instalación Paso a Paso](#3--instalación-paso-a-paso)
4. [Arquitectura de Datos y Relaciones](#4--arquitectura-de-datos-y-relaciones)
5. [La Carpeta `shared/` — Lógica Reutilizable (DRY)](#5--la-carpeta-shared--lógica-reutilizable-dry)
6. [Notas de Desarrollo Importantes](#6--notas-de-desarrollo-importantes)
7. [Rutas del Sistema (URL Map)](#7--rutas-del-sistema-url-map)

---

## 1. 📋 Descripción del Sistema

Este proyecto implementa un **Sistema de Ventas y Facturación** web completo, desarrollado con Django siguiendo el patrón arquitectónico **MVT**. Permite gestionar el ciclo de vida completo de una venta: desde el catálogo de productos hasta la emisión de facturas con múltiples líneas de detalle.

| Característica | Detalle |
|---|---|
| Gestión de catálogo | Marcas, Grupos, Proveedores y Productos |
| Gestión de clientes | Registro con perfil extendido y validación de cédula/RUC ecuatoriano |
| Facturación | Cabecera + líneas de detalle con cálculo automático de subtotales |
| Autenticación | Registro, Login y Logout seguros (compatible con Django 5+) |
| Control de acceso | Vistas protegidas por `@login_required` y `LoginRequiredMixin` |
| Panel admin | Registro completo de todos los modelos en `django.contrib.admin` |
| Dos estilos de vistas | FBV (Brand) y CBV genéricas (todos los demás módulos) |

---

## 2. 📁 Estructura de Directorios

```
sales_project/                    ← Raíz del repositorio
│
├── config/                       ← Configuración global del proyecto Django
│   ├── __init__.py
│   ├── settings.py               ← BASE_DIR, INSTALLED_APPS, LOGIN_URL, etc.
│   ├── urls.py                   ← Enrutador raíz (admin + accounts + billing)
│   ├── wsgi.py
│   └── asgi.py
│
├── billing/                      ← App principal del negocio
│   ├── migrations/               ← Historial de cambios en la base de datos
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py                  ← Registro de modelos en el panel /admin/
│   ├── apps.py
│   ├── forms.py                  ← SignUpForm, BrandForm, InvoiceForm, etc.
│   ├── models.py                 ← Brand, Product, Customer, Invoice…
│   ├── tests.py
│   ├── urls.py                   ← Rutas con namespace 'billing'
│   └── views.py                  ← FBV para Brand; CBV para el resto
│
├── shared/                       ← Paquete reutilizable (NO es app de Django)
│   ├── __init__.py
│   ├── mixins.py                 ← StaffRequiredMixin (protege DeleteViews)
│   ├── decorators.py             ← @audit_action (auditoría de FBV)
│   └── validators.py             ← validate_cedula_ec (Módulo 10 + RUC)
│
├── templates/                    ← Directorio raíz de plantillas HTML
│   ├── base.html                 ← Layout principal con Bootstrap 5 y navbar
│   ├── registration/
│   │   ├── login.html            ← Formulario de inicio de sesión
│   │   └── signup.html           ← Formulario de registro de usuario
│   └── billing/
│       ├── brand_list.html
│       ├── brand_form.html
│       ├── invoice_form.html     ← Usa InvoiceFormSet (productos + cantidades)
│       └── ...                   ← Un template por cada entidad / acción
│
├── venv/                         ← Entorno virtual (NO se sube a Git)
├── db.sqlite3                    ← Base de datos local (NO se sube a Git)
├── manage.py                     ← Punto de entrada de comandos Django
├── requirements.txt              ← Dependencias del proyecto
└── .gitignore
```

> **Regla de oro:** La carpeta `venv/` y el archivo `db.sqlite3` siempre deben estar en `.gitignore`. Nunca se suben al repositorio.

---

## 3. 🚀 Instalación Paso a Paso

Sigue estos pasos **en orden** para tener el proyecto corriendo en tu máquina local. No te saltes ninguno.

---

### Paso 1 — Clonar el repositorio o crear el directorio

**Opción A — Clonar desde Git (recomendado):**
```bash
git clone <URL_DEL_REPOSITORIO> sales_project
cd sales_project
```

**Opción B — Crear el directorio manualmente:**
```bash
mkdir sales_project
cd sales_project
```

---

### Paso 2 — Crear el entorno virtual

El entorno virtual aisla las dependencias de este proyecto del resto de tu sistema. Es una buena práctica **siempre** crearlo.

```bash
python -m venv venv
```

> Verás que se crea una carpeta llamada `venv/` en el directorio. Eso es correcto.

---

### Paso 3 — Activar el entorno virtual

Este paso **cambia según tu sistema operativo:**

| Sistema Operativo | Comando |
|---|---|
| **Windows** (CMD / PowerShell) | `venv\Scripts\activate` |
| **Linux / macOS** (Bash / Zsh) | `source venv/bin/activate` |

Sabrás que el entorno está activo porque tu terminal mostrará `(venv)` al inicio de la línea:
```
(venv) C:\Users\Tu_Usuario\sales_project>
```

---

### Paso 4 — Instalar las dependencias

**Si el proyecto tiene `requirements.txt`** (caso normal al clonar):
```bash
pip install -r requirements.txt
```

**Si estás configurando el proyecto desde cero:**
```bash
pip install django
# Congela las dependencias para que otros puedan reproducir el entorno exacto
pip freeze > requirements.txt
```

---

### Paso 5 — Crear la estructura del proyecto Django (solo si es desde cero)

> Si ya clonaste el repositorio, **omite este paso**. El proyecto ya existe.

```bash
# Crear el proyecto de configuración en el directorio actual (el punto '.' es importante)
django-admin startproject config .

# Crear la aplicación principal del negocio
python manage.py startapp billing
```

---

### Paso 6 — Configurar `settings.py`

Verifica que `billing` esté en `INSTALLED_APPS` y que la carpeta de templates esté correctamente apuntada:

```python
# config/settings.py

INSTALLED_APPS = [
    ...
    'billing',           # <-- la app del proyecto
    # 'shared' NO va aquí, es un paquete Python, no una app Django
]

TEMPLATES = [
    {
        ...
        'DIRS': [BASE_DIR / 'templates'],   # <-- directorio raíz de templates
        ...
    }
]

# Redirecciones de autenticación
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL           = '/accounts/login/'
```

---

### Paso 7 — Crear y aplicar las migraciones

Las migraciones son el mecanismo de Django para traducir tus modelos Python a tablas en la base de datos.

```bash
# 1. Detectar cambios en models.py y generar el archivo de migración
python manage.py makemigrations

# 2. Aplicar las migraciones (crear las tablas en db.sqlite3)
python manage.py migrate
```

Deberías ver una salida similar a:
```
Applying billing.0001_initial... OK
```

---

### Paso 8 — Crear el superusuario (Administrador)

```bash
python manage.py createsuperuser
```

El sistema te pedirá:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

> Con este usuario puedes acceder al panel administrativo en `http://127.0.0.1:8000/admin/`

---

### Paso 9 — Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

Verás este mensaje de éxito:
```
Django version 5.x, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Abre tu navegador y ve a: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

### Resumen rápido de comandos

```bash
# Clonar → entorno → dependencias → base de datos → servidor
git clone <URL> sales_project && cd sales_project
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 4. 🗄️ Arquitectura de Datos y Relaciones

El sistema implementa **8 modelos** organizados en torno al flujo de una venta: catálogo → cliente → factura.

### Diagrama de Relaciones (simplificado)

```
Brand ──────┐
            ├──► Product ◄──── ManyToMany ──── Supplier
ProductGroup┘        │
                     │ ForeignKey
                     ▼
Customer ──OneToOne──► CustomerProfile
    │
    │ ForeignKey
    ▼
Invoice
    │
    │ ForeignKey (CASCADE)
    ▼
InvoiceDetail ──ForeignKey──► Product
```

### Tabla de Modelos

| Modelo | Tabla DB | Relaciones | Descripción |
|---|---|---|---|
| `Brand` | `billing_brand` | — | Marcas de productos (ej: Samsung, Nike) |
| `ProductGroup` | `billing_productgroup` | — | Categorías de productos (ej: Electrónica, Ropa) |
| `Supplier` | `billing_supplier` | `ManyToMany` → `Product` | Empresas proveedoras. Un producto puede tener varios proveedores |
| `Product` | `billing_product` | `FK` → `Brand`, `FK` → `ProductGroup`, `M2M` → `Supplier` | Ítem del catálogo con precio y stock |
| `Customer` | `billing_customer` | `OneToOne` → `CustomerProfile` | Datos de identificación del cliente con validación de cédula/RUC |
| `CustomerProfile` | `billing_customerprofile` | `OneToOne` → `Customer` | Perfil financiero: tipo de contribuyente, plazo de pago, límite de crédito |
| `Invoice` | `billing_invoice` | `FK` → `Customer` | Cabecera de factura: cliente, fecha, subtotal, impuesto y total |
| `InvoiceDetail` | `billing_invoicedetail` | `FK` → `Invoice`, `FK` → `Product` | Línea de detalle: producto, cantidad, precio y subtotal calculado automáticamente |

### Comportamiento especial de `InvoiceDetail.save()`

El modelo `InvoiceDetail` sobreescribe el método `save()` heredado de `models.Model` para calcular el subtotal de forma automática **antes de persistir** el registro en la base de datos:

```python
# billing/models.py

class InvoiceDetail(models.Model):
    invoice    = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='details')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='invoice_details')
    quantity   = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal   = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price   # cálculo automático
        super().save(*args, **kwargs)                     # delegar al padre
```

> Este es un ejemplo clásico de **polimorfismo** en POO: redefinimos el comportamiento de un método heredado para adaptarlo a nuestra lógica de negocio.

### Tipos de relaciones implementadas

| Tipo | Dónde se usa | Significado práctico |
|---|---|---|
| `ForeignKey` (1:N) | `Product → Brand`, `Invoice → Customer`, `InvoiceDetail → Invoice` | Muchos productos pueden pertenecer a una marca; muchas facturas a un cliente |
| `ManyToManyField` (N:M) | `Product ↔ Supplier` | Un producto puede tener varios proveedores, y un proveedor puede abastecer varios productos |
| `OneToOneField` (1:1) | `CustomerProfile → Customer` | Cada cliente tiene exactamente un perfil extendido (patrón **Profile Extension**) |

---

## 5. 📦 La Carpeta `shared/` — Lógica Reutilizable (DRY)

### ¿Por qué existe `shared/`?

El principio **DRY** (*Don't Repeat Yourself*) nos dice que la lógica que se repite en varios lugares debe extraerse a un único lugar. La carpeta `shared/` es un **paquete Python estándar** (no una app de Django) que centraliza utilidades transversales a toda la aplicación.

**Diferencia clave:**

| | App Django | Paquete `shared/` |
|---|---|---|
| Tiene modelos | Sí (generalmente) | No |
| Se registra en `INSTALLED_APPS` | **Sí, obligatorio** | **No, no se registra** |
| Tiene migraciones | Sí | No |
| Se importa como | `from billing.forms import ...` | `from shared.mixins import ...` |

Basta con que `shared/` tenga un archivo `__init__.py` para que Python lo reconozca como un paquete importable.

---

### Componentes de `shared/`

| Archivo | Componente | Tipo | ¿Dónde se usa? |
|---|---|---|---|
| `mixins.py` | `StaffRequiredMixin` | Clase (Mixin para CBV) | En todas las `DeleteView` del proyecto |
| `decorators.py` | `@audit_action` | Decorador de función (para FBV) | En las vistas FBV de `Brand` |
| `validators.py` | `validate_cedula_ec` | Función validadora | En el campo `dni` del modelo `Customer` |

---

### `StaffRequiredMixin` — Protección de vistas de borrado

```python
# shared/mixins.py

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect

class StaffRequiredMixin(UserPassesTestMixin):
    """Permite ejecutar la vista únicamente a usuarios con is_staff=True."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, 'Acción restringida al personal autorizado.')
        return redirect('billing:brand_list')
```

**¿Cómo se usa?**

```python
# billing/views.py

from shared.mixins import StaffRequiredMixin

class ProductGroupDeleteView(StaffRequiredMixin, LoginRequiredMixin, DeleteView):
    model = ProductGroup
    ...
```

> El orden de los mixins importa: Django evalúa la cadena de herencia de izquierda a derecha, por lo que `StaffRequiredMixin` se verifica **primero**.

---

### `@audit_action` — Decorador de auditoría para FBV

```python
# shared/decorators.py

import functools
from datetime import datetime

def audit_action(func):
    """Registra en consola quién ejecutó qué acción y cuándo."""

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        print(
            f"[AUDIT] {datetime.now().isoformat()} | "
            f"User: {request.user} | "
            f"Method: {request.method} | "
            f"Path: {request.path} | "
            f"IP: {request.META.get('REMOTE_ADDR')}"
        )
        return func(request, *args, **kwargs)

    return wrapper
```

**¿Cómo se usa?**

```python
# billing/views.py

from shared.decorators import audit_action

@audit_action
@login_required
def brand_create(request):
    ...
```

> Los decoradores se apilan y se leen **de abajo hacia arriba**: primero se verifica el login, luego se registra la auditoría.

---

### `validate_cedula_ec` — Validador de cédula/RUC ecuatoriano

Este validador implementa el **algoritmo oficial del Módulo 10** exigido por el Servicio de Rentas Internas (SRI) del Ecuador para verificar la autenticidad de cédulas de identidad (10 dígitos) y RUC de personas naturales (13 dígitos).

```python
# shared/validators.py

from django.core.exceptions import ValidationError

def validate_cedula_ec(value: str):
    """Valida cédulas (10 dígitos) y RUC de personas naturales (13 dígitos)."""

    # --- Validaciones básicas ---
    if not value.isdigit():
        raise ValidationError('El DNI/RUC solo debe contener dígitos.')

    if len(value) not in (10, 13):
        raise ValidationError('Ingrese una cédula (10 dígitos) o un RUC (13 dígitos).')

    provincia = int(value[:2])
    if not (1 <= provincia <= 24):
        raise ValidationError('Los dos primeros dígitos deben corresponder a una provincia válida (01–24).')

    # --- Algoritmo Módulo 10 (aplicado sobre los primeros 9 dígitos) ---
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0

    for i, coef in enumerate(coeficientes):
        producto = int(value[i]) * coef
        suma += producto - 9 if producto > 9 else producto

    digito_verificador_calculado = (10 - (suma % 10)) % 10

    if digito_verificador_calculado != int(value[9]):
        raise ValidationError('El número de cédula o RUC no es válido.')
```

**¿Cómo se acopla al modelo?**

```python
# billing/models.py

from shared.validators import validate_cedula_ec

class Customer(models.Model):
    dni = models.CharField(
        max_length=13,
        unique=True,
        validators=[validate_cedula_ec],   # <-- acoplado aquí
        verbose_name='DNI/RUC'
    )
```

> Django ejecuta automáticamente todos los `validators` de un campo cuando se llama a `full_clean()`, lo que ocurre antes de cada operación de guardado desde formularios.

---

## 6. 🔧 Notas de Desarrollo Importantes

Esta sección documenta dos decisiones técnicas no obvias que resuelven limitaciones reales de Django 5+.

---

### 6.1 — Logout Seguro con Método POST

**El problema:** A partir de Django 5.0, la vista `LogoutView` del sistema de autenticación **ya no acepta peticiones HTTP GET**. Si tu botón de logout era un simple enlace `<a href="/accounts/logout/">`, el usuario verá un error `405 Method Not Allowed`.

**¿Por qué hizo esto Django?** Por seguridad. Un enlace `<a href>` realiza una petición GET, lo que significa que cualquier página externa podría cerrar la sesión del usuario incluyendo esa URL en una etiqueta `<img>` o similar (ataque CSRF). El método POST está protegido por el token CSRF.

**La solución:** Reemplazar el enlace por un formulario que envíe `POST` con el token CSRF, camuflado con clases de Bootstrap para que luzca como un botón normal de la navbar:

```html
<!-- templates/base.html -->

<!-- ❌ Forma antigua (no funciona en Django 5+) -->
<a href="/accounts/logout/">Salir</a>

<!-- ✅ Forma correcta para Django 5+ -->
<form method="POST" action="{% url 'logout' %}" class="d-inline">
    {% csrf_token %}
    <button type="submit" class="btn btn-link nav-link p-0 text-white">
        Cerrar Sesión
    </button>
</form>
```

> **`{% csrf_token %}`** inserta un campo oculto `<input type="hidden">` con un token único de seguridad que Django verifica en cada petición POST. Sin él, Django rechazará el formulario con un error `403 Forbidden`.

---

### 6.2 — Formsets para Facturación Compleja

**El problema:** Una factura real no solo tiene un cliente: tiene **múltiples líneas de detalle** (productos, cantidades, precios). Una `CreateView` estándar solo gestiona un formulario (`InvoiceForm`) y no tiene forma nativa de manejar los `InvoiceDetail` al mismo tiempo.

**La solución:** `inlineformset_factory`, una función de Django que genera una colección de formularios hijos (`InvoiceDetailFormSet`) vinculados a un formulario padre (`InvoiceForm`). Esto permite procesar la cabecera de la factura y todas sus líneas de producto en **una sola vista y un solo `POST`**.

```python
# billing/views.py (versión con formsets)

from django.forms import inlineformset_factory
from decimal import Decimal
from .models import Invoice, InvoiceDetail
from .forms import InvoiceForm

# Fábrica de formsets: "genera hasta 10 formularios InvoiceDetail para un Invoice"
InvoiceDetailFormSet = inlineformset_factory(
    Invoice,          # modelo padre
    InvoiceDetail,    # modelo hijo
    fields=['product', 'quantity', 'unit_price'],
    extra=3,          # cantidad de formularios vacíos iniciales
    can_delete=True,  # permite marcar líneas para borrar
)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form    = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)   # guardar cabecera sin persistir aún

            # Calcular totales con Decimal para evitar errores de punto flotante
            subtotal = Decimal('0.00')
            for detail_form in formset:
                if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE'):
                    qty   = Decimal(str(detail_form.cleaned_data['quantity']))
                    price = detail_form.cleaned_data['unit_price']
                    subtotal += qty * price

            invoice.subtotal = subtotal
            invoice.tax      = subtotal * Decimal('0.15')   # IVA 15%
            invoice.total    = invoice.subtotal + invoice.tax
            invoice.save()                                  # persistir cabecera

            formset.instance = invoice
            formset.save()                                  # persistir líneas de detalle
            return redirect('billing:invoice_list')
    else:
        form    = InvoiceForm()
        formset = InvoiceDetailFormSet()

    return render(request, 'billing/invoice_form.html', {'form': form, 'formset': formset})
```

**¿Por qué `Decimal` y no `float`?**

```python
# Problema con float (¡no hagas esto en dinero!)
>>> 0.1 + 0.2
0.30000000000000004   # ERROR de representación binaria

# Solución con Decimal
>>> from decimal import Decimal
>>> Decimal('0.1') + Decimal('0.2')
Decimal('0.3')        # EXACTO
```

> En sistemas financieros, usar `float` para dinero es un error grave. `Decimal` garantiza precisión matemática exacta en todos los cálculos monetarios.

---

## 7. 🗺️ Rutas del Sistema (URL Map)

| Método | URL | Vista | Nombre de URL | Descripción |
|---|---|---|---|---|
| GET/POST | `/accounts/login/` | `LoginView` | `login` | Inicio de sesión |
| POST | `/accounts/logout/` | `LogoutView` | `logout` | Cerrar sesión (solo POST) |
| GET/POST | `/signup/` | `SignUpView` | `billing:signup` | Registro de nuevo usuario |
| GET | `/brands/` | `brand_list` | `billing:brand_list` | Lista de marcas |
| GET/POST | `/brands/create/` | `brand_create` | `billing:brand_create` | Crear marca |
| GET/POST | `/brands/<pk>/edit/` | `brand_update` | `billing:brand_update` | Editar marca |
| GET/POST | `/brands/<pk>/delete/` | `brand_delete` | `billing:brand_delete` | Eliminar marca |
| GET | `/groups/` | `ProductGroupListView` | `billing:productgroup_list` | Lista de grupos |
| GET | `/suppliers/` | `SupplierListView` | `billing:supplier_list` | Lista de proveedores |
| GET | `/products/` | `ProductListView` | `billing:product_list` | Lista de productos |
| GET | `/customers/` | `CustomerListView` | `billing:customer_list` | Lista de clientes |
| GET | `/invoices/` | `InvoiceListView` | `billing:invoice_list` | Lista de facturas |
| GET/POST | `/invoices/create/` | `invoice_create` | `billing:invoice_create` | Nueva factura con formset |
| GET | `/admin/` | Panel Admin Django | — | Administración completa |

> Todas las rutas (excepto `/accounts/login/`, `/signup/` y `/admin/`) están protegidas con autenticación. Los usuarios no autenticados son redirigidos automáticamente a `/accounts/login/`.

---

## Contribución y Convenciones

Este es un proyecto académico. Para mantener el código ordenado:

- Cada módulo del negocio tiene su propio bloque de vistas en `views.py`, separado por comentarios.
- Los nombres de las URL siguen el patrón `<entidad>_<acción>` (ej: `brand_list`, `product_create`).
- Las CBV se prefieren para CRUD estándar; las FBV se usan cuando se necesita lógica más explícita o auditoría.
- Nunca hardcodear URLs en los templates: usar siempre `{% url 'billing:nombre_url' %}`.

---

<div align="center">

**Proyecto desarrollado como parte del plan académico de 4to Semestre**  
Programación Orientada a Objetos con Python · Django MVT

</div>
