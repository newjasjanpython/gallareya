from django.forms import ModelForm
from main.models import *


class OnVerifyArtForm(ModelForm):
    class Meta:
        model = OnVerifyArt
        fields = '__all__'


class ArtForm(ModelForm):
    class Meta:
        model = Art
        fields = '__all__'


class UploadImageForm(ModelForm):
    class Meta:
        model = Art
        fields = ['image']
