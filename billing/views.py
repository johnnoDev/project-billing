from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import *
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet
from shared.mixins import StaffRequiredMixin, ExportMixin, export_response
from shared.decorators import audit_action
from decimal import Decimal


# === HOME (Página principal) ===
@login_required
def home(request):
    """Vista principal del sistema. Muestra resumen general."""
    context = {
        'total_brands': Brand.objects.count(),
        'total_products': Product.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_invoices': Invoice.objects.count(),
        'recent_invoices': Invoice.objects.all()[:5],
        'low_stock': Product.objects.filter(stock__lte=5, is_active=True),
    }
    return render(request, 'billing/home.html', context)


# === REGISTRO ===
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('billing:brand_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


# === BRAND (FBV) ===
_BRAND_EXPORT_FIELDS = [
    ('name',       'Nombre'),
    ('is_active',  'Activo'),
    ('created_at', 'Creado'),
]

@login_required
@audit_action('LIST_BRANDS')
def brand_list(request):
    brands = Brand.objects.all()
    exp = export_response(request, brands, _BRAND_EXPORT_FIELDS, 'Listado de Marcas', 'marcas')
    if exp:
        return exp
    return render(request, 'billing/brand_list.html', {'brands': brands})

@login_required
@audit_action('CREATE_BRAND')
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created!')
            return redirect('billing:brand_list')
    else: form = BrandForm()
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Create Brand'})

@login_required
@audit_action('UPDATE_BRAND')
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated!')
            return redirect('billing:brand_list')
    else: form = BrandForm(instance=brand)
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Edit Brand'})

@login_required
@audit_action('DELETE_BRAND')
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Brand deleted!')
        return redirect('billing:brand_list')
    return render(request, 'billing/brand_confirm_delete.html', {'object': brand})


# === PRODUCTGROUP (CBV) ===
class ProductGroupListView(LoginRequiredMixin, ExportMixin, ListView):
    model = ProductGroup; template_name = 'billing/productgroup_list.html'; context_object_name = 'items'
    export_fields = [('name', 'Nombre'), ('is_active', 'Activo')]
    export_filename = 'grupos'; export_title = 'Listado de Grupos de Producto'

class ProductGroupCreateView(LoginRequiredMixin, CreateView):
    model = ProductGroup; fields = ['name', 'is_active']; template_name = 'billing/productgroup_form.html'; success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductGroup; fields = ['name', 'is_active']; template_name = 'billing/productgroup_form.html'; success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProductGroup; template_name = 'billing/productgroup_confirm_delete.html'; success_url = reverse_lazy('billing:productgroup_list')


# === SUPPLIER (CBV) ===
class SupplierListView(LoginRequiredMixin, ExportMixin, ListView):
    model = Supplier; template_name = 'billing/supplier_list.html'; context_object_name = 'items'
    export_fields = [
        ('name',         'Proveedor'),
        ('contact_name', 'Contacto'),
        ('email',        'Email'),
        ('phone',        'Teléfono'),
        ('address',      'Dirección'),
        ('is_active',    'Activo'),
    ]
    export_filename = 'proveedores'; export_title = 'Listado de Proveedores'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier; fields = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']; template_name = 'billing/supplier_form.html'; success_url = reverse_lazy('billing:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier; fields = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']; template_name = 'billing/supplier_form.html'; success_url = reverse_lazy('billing:supplier_list')

class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Supplier; template_name = 'billing/supplier_confirm_delete.html'; success_url = reverse_lazy('billing:supplier_list')


# === PRODUCT (CBV) ===
class ProductListView(LoginRequiredMixin, ExportMixin, ListView):
    model = Product
    template_name = 'billing/product_list.html'
    context_object_name = 'items'
    paginate_by = 10
    export_filename = 'productos'
    export_title = 'Listado de Productos'
    export_fields = [
        ('name',                                      'Nombre'),
        ('brand.name',                                'Marca'),
        ('group.name',                                'Grupo'),
        (lambda o: f"${o.unit_price}",               'Precio'),
        ('stock',                                     'Stock'),
        (lambda o: 'Activo' if o.is_active else 'Inactivo', 'Estado'),
        (lambda o: ', '.join(s.name for s in o.suppliers.all()), 'Proveedores'),
    ]
    # Mapa clave→campo; las claves coinciden con data-col del template.
    # El cliente envía ?cols=name,brand,price para exportar solo lo visible.
    export_fields_map = {
        'name':      ('name',                                      'Nombre'),
        'brand':     ('brand.name',                                'Marca'),
        'group':     ('group.name',                                'Grupo'),
        'price':     (lambda o: f"${o.unit_price}",               'Precio'),
        'stock':     ('stock',                                     'Stock'),
        'status':    (lambda o: 'Activo' if o.is_active else 'Inactivo', 'Estado'),
        'suppliers': (lambda o: ', '.join(s.name for s in o.suppliers.all()), 'Proveedores'),
    }

    def get_queryset(self):
        qs = Product.objects.select_related('brand', 'group').prefetch_related('suppliers')
        g = self.request.GET
        if name := g.get('name', '').strip():
            qs = qs.filter(name__icontains=name)
        if brand := g.get('brand', ''):
            qs = qs.filter(brand_id=brand)
        if group := g.get('group', ''):
            qs = qs.filter(group_id=group)
        if supplier := g.get('supplier', ''):
            qs = qs.filter(suppliers__id=supplier)
        if price_min := g.get('price_min', '').strip():
            qs = qs.filter(unit_price__gte=price_min)
        if price_max := g.get('price_max', '').strip():
            qs = qs.filter(unit_price__lte=price_max)
        if stock_min := g.get('stock_min', '').strip():
            qs = qs.filter(stock__gte=stock_min)
        if stock_max := g.get('stock_max', '').strip():
            qs = qs.filter(stock__lte=stock_max)
        if (is_active := g.get('is_active', '')) in ('true', 'false'):
            qs = qs.filter(is_active=(is_active == 'true'))
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brands'] = Brand.objects.order_by('name')
        ctx['groups'] = ProductGroup.objects.order_by('name')
        ctx['suppliers_list'] = Supplier.objects.order_by('name')
        # q sin 'page' para armar URLs de paginación con filtros preservados
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['q'] = params
        return ctx

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'billing/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('brand', 'group').prefetch_related('suppliers')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product; fields = ['name', 'description', 'brand', 'group', 'suppliers', 'unit_price', 'stock', 'image', 'is_active']; template_name = 'billing/product_form.html'; success_url = reverse_lazy('billing:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product; fields = ['name', 'description', 'brand', 'group', 'suppliers', 'unit_price', 'stock', 'image', 'is_active']; template_name = 'billing/product_form.html'; success_url = reverse_lazy('billing:product_list')

class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product; template_name = 'billing/product_confirm_delete.html'; success_url = reverse_lazy('billing:product_list')


# === CUSTOMER (CBV) ===
class CustomerListView(LoginRequiredMixin, ExportMixin, ListView):
    model = Customer; template_name = 'billing/customer_list.html'; context_object_name = 'items'
    export_fields = [
        ('dni',        'DNI'),
        ('last_name',  'Apellido'),
        ('first_name', 'Nombre'),
        ('email',      'Email'),
        ('phone',      'Teléfono'),
        (lambda o: 'Activo' if o.is_active else 'Inactivo', 'Estado'),
    ]
    export_filename = 'clientes'; export_title = 'Listado de Clientes'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer; fields = ['dni', 'first_name', 'last_name', 'email', 'phone', 'address', 'is_active']; template_name = 'billing/customer_form.html'; success_url = reverse_lazy('billing:customer_list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer; fields = ['dni', 'first_name', 'last_name', 'email', 'phone', 'address', 'is_active']; template_name = 'billing/customer_form.html'; success_url = reverse_lazy('billing:customer_list')

class CustomerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Customer; template_name = 'billing/customer_confirm_delete.html'; success_url = reverse_lazy('billing:customer_list')


# =============================================
# CRUD DE INVOICE - VISTAS BASADAS EN FUNCIONES
# =============================================

_INVOICE_EXPORT_FIELDS = [
    ('id',                                           '#'),
    (lambda o: str(o.customer),                     'Cliente'),
    (lambda o: o.invoice_date.strftime('%d/%m/%Y'), 'Fecha'),
    (lambda o: f"${o.subtotal}",                    'Subtotal'),
    (lambda o: f"${o.tax}",                         'IVA'),
    (lambda o: f"${o.total}",                       'Total'),
]

@login_required
def invoice_list(request):
    """Lista todas las facturas con sus totales."""
    invoices = Invoice.objects.select_related('customer').all()
    exp = export_response(request, invoices, _INVOICE_EXPORT_FIELDS, 'Listado de Facturas', 'facturas')
    if exp:
        return exp
    return render(request, 'billing/invoice_list.html', {'items': invoices})

@login_required
def invoice_create(request):
    """Crea factura con sus líneas de detalle."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.save()
            formset.instance = invoice
            formset.save()
            subtotal = sum(d.subtotal for d in invoice.details.all())
            invoice.subtotal = subtotal
            invoice.tax = subtotal * Decimal('0.15')
            invoice.total = invoice.subtotal + invoice.tax
            invoice.save()
            messages.success(request, f'Invoice #{invoice.id} created! Total: ${invoice.total}')
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceDetailFormSet()
    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    })

@login_required
def invoice_detail(request, pk):
    """Muestra el detalle completo de una factura."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer').prefetch_related('details__product'),
        pk=pk
    )
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@login_required
def invoice_delete(request, pk):
    """Elimina una factura y todos sus detalles (CASCADE)."""
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice_id = invoice.id
        invoice.delete()
        messages.success(request, f'Invoice #{invoice_id} deleted!')
        return redirect('billing:invoice_list')
    return render(request, 'billing/invoice_confirm_delete.html', {'object': invoice})
