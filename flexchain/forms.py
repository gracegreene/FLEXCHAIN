from django import forms
from .models import EventSku, Event, Product, Vendor
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Fieldset


class InitialCSVUploadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(InitialCSVUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload', css_class='btn btn-primary'))
        self.helper.form_method = 'POST'

    vendor_file = forms.FileField(
        required=True,
        label="Vendor CSV File",
        help_text="""
        CSV File with the following headers: Vendor Name,Channel,Contact Person,Contact Email,Average Lead Time,Vendor Type,Address<br>
        *Vendor Name: Name of vendor<br>
        *Channel: (Sea, Air, Ground)<br>
        *Contact Person: The name of the person to contact when speaking to this Vendor<br>
        *Contact Email: The email of the person to contact when speaking to this Vendor<br>
        *Vendor Type: The type of vendor (Trading,Manufacturer)<br>
        Address: The address of the business<br>
        (*) - Required
        """
    )

    product_file = forms.FileField(
        required=True,
        label="Product CSV File",
        help_text="""
        CSV File with the following headers: SKU,Product Name,Vendor,Price<br>
        *SKU: Product Identifier<br>
        *Product Name: Product Name<br>
        *Vendor: The name of the vendor<br>
        *Price: The price of the product just as a number ex:   4.32<br>
        *MOQ: Minimum Order Quantity, the minimum units that can be ordered from the given vendor<br>
        *Cost: The cost associated from purchasing from this vendor ex:  1.12<br>
        *Average Lead Time: The average time it takes this vendor to send products (In Weeks)<br>
        (*) - Required
        """
    )

    inventory_file = forms.FileField(
        required=True,
        label="Inventory CSV File",
        help_text="""
        CSV File with the following headers: SKU,Date,On Hand,Back Order,Pending Return<br>
        *SKU: Product Identifier<br>
        *Date: Date with format  Month/Day/Year<br>
        *On Hand: The amount of inventory currently in stock<br>
        *Back Order: The amount that is currently ordered<br>
        *Pending Return: The amount of product that will be returned<br>
        (*) - Required
        """
    )

    sales_file = forms.FileField(
        required=True,
        label="Sales History CSV File",
        help_text="""
        *CSV File with the following headers: SKU,Date,Amount<br>
        *SKU: Product Identifier<br>
        *Date: When this product was sold<br>
        *Amount: The amount of this product sold in this transaction<br>
        (*) - Required
        """
    )


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
    )
    sales_file = forms.FileField(
        required=True,
        label="Sales CSV Upload",
        help_text="CSV with headers: SKU, Date, Quantity.  Note Dates should be in format MM/DD/YYYY",
    )


class CSVVendorUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="Vendor CSV Upload",
        help_text="""
        CSV with headers: Vendor Name, Channel (Air, Sea), Contact Person, Contact Email, Average Lead Time
        """
    )


EventProductFormsetFactory = forms.inlineformset_factory(
    Event,
    EventSku,
    fields=('product', 'increase'),
    can_delete=True
)

class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.layout = Layout(
            Fieldset('Create a New Event', 'Name')
        )
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create', css_class='btn btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = Event
        fields = ['name', 'date']

