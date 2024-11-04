from django import forms

class ImageUploadForm(forms.Form):
    image1 = forms.ImageField(label='Upload Image 1')
    image2 = forms.ImageField(label='Upload Image 2')
