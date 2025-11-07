from django import forms
from .models import Product
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name","description","price_cents","image"]
    def clean_image(self):
        img = self.cleaned_data.get("image")
        if not img: return img
        if getattr(img, "size", 0) > 2*1024*1024:
            raise ValidationError("Max file size is 2MB")
        ct = getattr(img, "content_type", "") or ""
        if not ct.startswith("image/"):
            raise ValidationError("Only image files are allowed")
        return img
