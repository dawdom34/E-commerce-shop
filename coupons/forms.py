from django import forms
from .models import Coupon


class CouponForm(forms.ModelForm):
    coupon = forms.CharField(max_length=150)
    discount = forms.IntegerField()

    class Meta:
        model = Coupon
        fields = ('coupon', 'discount')

    def clean(self):
        """
        Check if coupon already exist
        """
        if self.is_valid():
            coupon = self.cleaned_data['coupon']
            try:
                c = Coupon.objects.get(coupon=coupon)
            except Coupon.DoesNotExist:
                return self.cleaned_data
            raise forms.ValidationError('Coupon name already in use')
