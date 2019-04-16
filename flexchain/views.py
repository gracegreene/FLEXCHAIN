from django.shortcuts import render, redirect
from .models import Vendor, Product, Sales, Inventory, ProductVendor, EventSku, Event
from .forms import CSVProductUploadForm, CSVVendorUploadForm, EventProductFormsetFactory, EventForm, \
    InitialCSVUploadForm
from django_datatables.datatable import *
from django_datatables import column
from datetime import datetime
from django.contrib import messages
import dateutil.parser
import csv


def home(request):
    context = dict()
    form = InitialCSVUploadForm()
    if request.method == 'POST':
        # Handle if there are validation errors with the form.
        if not form.is_valid:
            context['vendor_count'] = Vendor.objects.exists()
            context['product_count'] = Product.objects.exists()
            context['sale_history_count'] = Sales.objects.exists()
            messages.error(request, form.errors)
            return render(request, 'flexchain/index.html')
        # Form has no errors currently on happy path , still need to read csv files
        vendor_file = request.FILES.get('vendor_file')
        vendor_file_contents = ""
        for chunk in vendor_file.chunks():
            vendor_file_contents = vendor_file_contents + chunk.decode('utf-8')

        current_line = 0
        vendor_csv_reader = csv.DictReader(vendor_file_contents.splitlines())
        for dictionary_csv_vendor_entry in vendor_csv_reader:
            current_line = current_line + 1
            vendor_name = dictionary_csv_vendor_entry.get('Vendor Name', None)
            channel = dictionary_csv_vendor_entry.get('Channel', None)
            contact_person = dictionary_csv_vendor_entry.get('Contact Person', None)
            contact_email = dictionary_csv_vendor_entry.get('Contact Email', None)
            vendor_type = dictionary_csv_vendor_entry.get('Vendor Type', None)
            address = dictionary_csv_vendor_entry.get('Address', None)
            if (
                vendor_name is None or
                channel is None or channel is not 'Land' or channel is not 'Sea' or channel is not 'Air' or
                contact_person is None or
                contact_email is None or
                vendor_type is None or
                address is None
            ):
                #TODO Handle error here
                error_message = "Invalid entry in csv, line: {current_line}".format(current_line=current_line)
            else:
                # Convert Vendor Freight Type to abbreviated version for database
                for freight_type in Vendor.VENDOR_FREIGHT_TYPE_CHOICES:
                    if freight_type[1] == channel:
                        channel = freight_type[0]

                # Convert Vendor Type Choice to abbreviated version for database
                for vendor_type_choice in Vendor.VENDOR_TYPE_CHOICES:
                    if vendor_type_choice[1] == vendor_type:
                        vendor_type = vendor_type_choice[0]

                Vendor.objects.update_or_create(
                    vendor_name = vendor_name,
                    contact_person = contact_person,
                    email = contact_email,
                    freight_type = channel,
                    vendor_type = vendor_type,
                    address = address
                )
        # Remove file contents for memory resources
        vendor_file_contents = None

        product_file = request.FILES.get('product_file')
        product_file_contents = ""
        for chunk in product_file.chunks():
            product_file_contents = product_file_contents + chunk.decode('utf-8')

        product_csv_reader = csv.DictReader(product_file_contents.splitlines())
        for dictionary_csv_product_entry in product_csv_reader:
            sku = dictionary_csv_product_entry.get('SKU', None)
            product_name = dictionary_csv_product_entry.get('Product Name', None)
            vendor_name = dictionary_csv_product_entry.get('Vendor', None)
            price = dictionary_csv_product_entry.get('Price', None)
            unit_weight = dictionary_csv_product_entry.get('Unit Weight', None)
            moq = dictionary_csv_product_entry.get('MOQ', None)
            cost = dictionary_csv_product_entry.get('Cost', None)
            average_lead_time = dictionary_csv_vendor_entry.get('Average Lead Time', None)

            if (
                sku is None or
                product_name is None or
                    vendor_name is None or
                price is None or
                moq is None or
                cost is None or
                    average_lead_time is None or
                    unit_weight is None
            ):
                #TODO handle error here.
                pass
            vendor_exists = Vendor.objects.filter(vendor_name=vendor_name).exists()
            if not vendor_exists:
                #TODO Throw error here
                pass
            print(dictionary_csv_product_entry)
            print(price)
            vendor_obj = Vendor.objects.filter(vendor_name=vendor_name).first()
            Product.objects.update_or_create(
                sku=sku,
                name=product_name,
                price=price,
                unit_weight=unit_weight
            )
            ProductVendor.objects.update_or_create(
                product__sku=sku,
                vendor=vendor_obj,
                cost=cost,
                moq=moq,
                lead_time=average_lead_time
            )
        # Clear file contents to remove memory resources
        product_file_contents = None

        inventory_file = request.FILES.get('inventory_file')
        inventory_file_contents = ""

        for chunk in inventory_file.chunks():
            inventory_file_contents = inventory_file_contents + chunk.decode('utf-8')

        inventory_csv_reader = csv.DictReader(inventory_file_contents.splitlines())
        for dictionary_csv_inventory_entry in inventory_csv_reader:
            sku = dictionary_csv_product_entry.get('SKU', None)
            date = dictionary_csv_product_entry.get('Date', None)
            on_hand = dictionary_csv_product_entry.get('On Hand', None)
            back_order = dictionary_csv_product_entry.get('Back Order', None)
            pending_return = dictionary_csv_product_entry.get('Pending Return', None)
            if (
                sku is None or
                date is None or
                on_hand is None or
                back_order is None or
                pending_return is None
            ):
                #TODO add validation error
                pass

            date_time_object = dateutil.parser.parse(date)

            Inventory.objects.get_or_create(
                product_sku=sku,
                recorded_date=date_time_object,
                amount_on_hand=on_hand,
                amount_back_order=back_order,
                amount_pending_return=pending_return
            )

        # Clear file contents to remove memory resources
        inventory_file_contents = None


        sales_file = request.FILES.get('sales_file')

        sales_file_contents = ""
        for chunk in sales_file.chunks():
            sales_file_contents = sales_file_contents + chunk.decode('utf-8')

        sales_csv_reader = csv.DictReader(sales_file_contents.splitlines())

        for dictionary_csv_sales_entry in sales_csv_reader:
            sku = dictionary_csv_sales_entry.get('SKU', None)
            date = dictionary_csv_sales_entry.get('Date', None)
            amount = dictionary_csv_sales_entry.get('Amount', None)

            if (
                sku is None or
                date is None or
                amount is None
            ):
                # TODO create validation error here
                pass

            date_time_object = dateutil.parser.parse(date)

            Sales.objects.create(
                product_sku=sku,
                sales_date=date_time_object,
                quantity_sold=amount
            )

        #Clear file contents to remove memory resources
        sales_file_contents = None

        return render(request, 'flexchain/index.html', context=context)

    # Case that the request method is NOT POST
    context = dict()
    context['vendor_count'] = Vendor.objects.exists()
    context['product_count'] = Product.objects.exists()
    context['inventory_count'] = Inventory.objects.exists()
    context['sale_history_count'] = Sales.objects.exists()
    context['csv_upload_form'] = InitialCSVUploadForm
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


class EventProductDatatable(Datatable):
    sku = column.TextColumn(title="SKU")
    name = column.TextColumn(title="Name")
    price = column.Column(title="Price")
    amount = column.StringColumn(title="Amount")

    class Meta:
        model = Product
        searching = True
        search_fields = ['name']
        search_min_length = 3
        title = 'Products'

    def render_amount(self, row):
        return """<input name="{}" type="number"></>""".format(row['sku'])


class EventDatatable(Datatable):
    name = column.StringColumn(title='Name', value='name', link='eventproduct', link_args=['id'])
    date = column.DateColumn(title='Date')

    class Meta:
        model = Event
        searching = True
        search_fields = ['name']
        search_min_length = 3
        title = 'Events'
        extra_fields = ('id',)

    # def render_name(self, row):
    #     return """<a href="{}">{}</a>""".format(reverse('eventproduct', row['id']), row['name'])


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
    if request.method == 'POST':
        form = EventForm(request.POST)
        if not form.is_valid():
            context['event_form'] = form
            return render(request, 'flexchain/event.html', context=context)
        event = form.save(commit=False)
        event.save()
        return redirect('eventproduct', event.id)
    context['event_datatable'] = EventDatatable()
    context['event_form'] = EventForm()
    return render(request, 'flexchain/event.html', context=context)


def eventproduct(request, event_id):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if Product.objects.filter(sku=key).exists():
                if value[0] == 0:
                    continue
                EventSku.objects.update_or_create(event_id=event_id, product_id=key, increase=value[0])
        return redirect('event')
    context = dict()
    context['product_data_table'] = EventProductDatatable()
    return render(request, 'flexchain/eventproduct.html', context=context)
