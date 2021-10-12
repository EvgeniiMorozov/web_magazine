from django import forms

from shop.models import Order


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_date"].label = "Дата получения заказа"

    order_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    # comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Order
        fields = ("first_name", "last_name", "phone", "address", "buying_type", "order_date", "comment")
