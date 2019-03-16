from django import forms
from django.core.exceptions import ValidationError
from .models import EventSku, Event, Product, Vendor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import csv


def import_product_document_validator(document):
    # check file valid csv format
    headers = {
        'SKU': {'field': 'SKU', 'required': True},
        'Product Name': {'field': 'Product Name', 'required': True},
        'Current Inventory': {'field': 'Current Inventory', 'required': True},
        'Vendor': {'field': 'Vendor', 'required': True},
        'Price': {'field': 'Price', 'required': True},
    }
    try:
        dialect = csv.Sniffer().sniff(document.read(1024))
        document.seek(0, 0)
    except (csv.Error, TypeError):
        raise ValidationError('Not a valid CSV file')
    reader = csv.reader(document.read().splitlines(), dialect)
    csv_headers = []
    required_headers = [header_name for header_name, values in
                        headers.items() if values['required']]
    for y_index, row in enumerate(reader):
        # check that all headers are present
        if y_index == 0:
            # store header_names to sanity check required cells later
            csv_headers = [header_name.lower() for header_name in row if header_name]
            missing_headers = set(required_headers) - set([r.lower() for r in row])
            if missing_headers:
                missing_headers_str = ', '.join(missing_headers)
                raise ValidationError('Missing headers: %s' % missing_headers_str)
            continue
        # ignore blank rows
        if not ''.join(str(x) for x in row):
            continue
        # sanity check required cell values
        for x_index, cell_value in enumerate(row):
            # if indexerror, probably an empty cell past the headers col count
            try:
                csv_headers[x_index]
            except IndexError:
                continue
            if csv_headers[x_index] in required_headers:
                if not cell_value:
                    raise ValidationError('Missing required value %s for row %s' %
                                          (csv_headers[x_index], y_index + 1))


def import_sales_document_validator(document):
    # check file valid csv format
    headers = {
        'SKU': {'field': 'SKU', 'required': True},
        'Date': {'field': 'Date', 'required': True},
        'Quantity': {'field': 'Quantity', 'required': True},
    }
    try:
        dialect = csv.Sniffer().sniff(document.read(1024))
        document.seek(0, 0)
    except (csv.Error, TypeError):
        raise ValidationError('Not a valid CSV file')
    reader = csv.reader(document.read().splitlines(), dialect)
    csv_headers = []
    required_headers = [header_name for header_name, values in
                        headers.items() if values['required']]
    for y_index, row in enumerate(reader):
        # check that all headers are present
        if y_index == 0:
            # store header_names to sanity check required cells later
            csv_headers = [header_name.lower() for header_name in row if header_name]
            missing_headers = set(required_headers) - set([r.lower() for r in row])
            if missing_headers:
                missing_headers_str = ', '.join(missing_headers)
                raise ValidationError('Missing headers: %s' % missing_headers_str)
            continue
        # ignore blank rows
        if not ''.join(str(x) for x in row):
            continue
        # sanity check required cell values
        for x_index, cell_value in enumerate(row):
            # if indexerror, probably an empty cell past the headers col count
            try:
                csv_headers[x_index]
            except IndexError:
                continue
            if csv_headers[x_index] in required_headers:
                if not cell_value:
                    raise ValidationError(u'Missing required value %s for row %s' %
                                          (csv_headers[x_index], y_index + 1))


class CSVProductUploadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CSVProductUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload', css_class='btn btn-primary'))
        self.helper.form_method = 'POST'

    product_file = forms.FileField(
        required=True,
        label="Product CSV Upload",
        help_text="""
            CSV with headers: SKU, Product Name, Current Inventory, Vendor,
            Price. Note it is required to first add vendors in the system prior to this step.
        """,
        validators=[import_product_document_validator]
    )
    sales_file = forms.FileField(
        required=True,
        label="Sales CSV Upload",
        help_text="CSV with headers: SKU, Date, Quantity.  Note Dates should be in format MM/DD/YYYY",
        validators=[import_sales_document_validator]
    )


class CSVVendorUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="Vendor CSV Upload",
        help_text="""
        CSV with headers: Vendor Name, Channel (Air, Sea), Contact Person, Contact Email, Average Lead Time
        """
    )


class EventProductForm(forms.ModelForm):
    class Meta:
        model = EventSku
        fields = ['product', 'increase']


EventProductFormsetFactory = forms.formset_factory(EventProductForm)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date']
