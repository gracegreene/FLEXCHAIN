from django.shortcuts import render
from .models import Vendor, Product, Sales, Inventory
from .forms import CSVProductUploadForm, CSVVendorUploadForm, EventProductFormsetFactory, EventForm
from django_datatables.datatable import *
from django_datatables import column
from datetime import datetime
import csv


def home(request):
    context = dict()
    context['vendor_count'] = Vendor.objects.exists()
    context['product_count'] = Product.objects.exists()
    context['sale_history_count'] = Sales.objects.exists()
    return render(request, 'flexchain/index.html', context=context)


class ProductDatatable(Datatable):
    sku = column.TextColumn(title="SKU")
    name = column.TextColumn(title="Name")
    price = column.Column(title="Price")

    class Meta:
        model = Product
        searching = True
        search_fields = ['name']
        search_min_length = 3
        title = 'Products'


def product(request):
    if request.method == 'POST':
        form = CSVProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product_file = request.FILES.get('product_file')
            reader = csv.DictReader(product_file)
            total_products_created = 0
            total_products_updated = 0
            current_time = datetime.now()
            for row in reader:
                product, created = Product.objects.update_or_create(
                    sku=row['SKU'],
                    name=row['Product Name'],
                    price=row['Price'],
                )
                if created:
                    total_products_created = total_products_created + 1
                else:
                    total_products_updated = total_products_updated + 1

                inventory, created = Inventory.objects.update_or_create(
                    product_id=row['SKU'],
                    recorded_date=current_time,
                    amount_on_hand=row['Current Inventory'],
                )
                # Still have Current Inventory and Vendor
            sales_file = request.FILES.get('sales_file')
            reader = csv.DictReader(sales_file)
            total_sales_created = 0
            total_sales_updated = 0
            for row in reader:
                sales, created = Sales.objects.update_or_create(
                    product_id=row['SKU'],
                    sales_date=row['Date'],
                    quantity_sold=row['Quantity'],
                )
                if created:
                    total_sales_created = total_sales_created + 1
                else:
                    total_sales_updated = total_sales_updated + 1

            # Redirect?
            context = dict()
            context['has_product'] = Product.objects.exists()
            context['has_product_sales'] = Sales.objects.exists()
            if context['has_product'] and context['has_product_sales']:
                context['product_table'] = ProductDatatable()
            context['product_csv_upload_form'] = form
            return render(request, 'flexchain/product.html', context=context)
        else:
            context = dict()
            context['has_product'] = Product.objects.exists()
            context['has_product_sales'] = Sales.objects.exists()
            if context['has_product'] and context['has_product_sales']:
                context['product_table'] = ProductDatatable()
            context['product_csv_upload_form'] = form
            return render(request, 'flexchain/product.html', context=context, status=400)
    else:
        context = dict()
        context['has_product'] = Product.objects.exists()
        context['has_product_sales'] = Sales.objects.exists()
        if context['has_product'] and context['has_product_sales']:
            context['product_table'] = ProductDatatable()
        context['product_csv_upload_form'] = CSVProductUploadForm()
        return render(request, 'flexchain/product.html', context=context)


class VendorDatatable(Datatable):
    vendor_name = column.TextColumn(title="Name")
    contact_person = column.TextColumn(title="Contact")
    email = column.TextColumn(title="Email")
    vendor_joined = column.DateColumn(title="Added")
    vendor_type = column.TextColumn(title="Type")
    freight_type = column.TextColumn(title="Shipping Method")

    class Meta:
        model = Vendor
        search_fields = ['vendor_name']
        title = 'Vendors'

    @staticmethod
    def render_vendor_type(row):
        v_type = "unrecognized"
        for vendor_type in Vendor.VENDOR_TYPE_CHOICES:
            if vendor_type[0] == row:
                v_type = vendor_type[1]
        return "{}".format(v_type)

    #

    @staticmethod
    def render_freight_type(row):
        freight_type = "unrecognized"
        for shipment_type in Vendor.VENDOR_FREIGHT_TYPE_CHOICES:
            if shipment_type[0] == row:
                freight_type = shipment_type[1]
        return "{}".format(freight_type)


def vendor(request):
    context = dict()
    context['has_vendors'] = Vendor.objects.exists()
    context['vendor_upload_form'] = CSVVendorUploadForm()
    if context['has_vendors']:
        context['vendor_table'] = VendorDatatable()
    return render(request, 'flexchain/vendor.html', context=context)


def task(request):
    context = dict()
    return render(request, 'flexchain/task.html', context=context)


def event(request):
    context = dict()
    context['event_form'] = EventForm()
    context['event_product_formset'] = EventProductFormsetFactory
    return render(request, 'flexchain/event.html', context=context)


def create_event(request):
    context = dict()
    context['event_form'] = EventForm()
    context['event_product_formset'] = EventProductFormsetFactory
    return render(request, 'flexchain/add_event.html', context=context)
