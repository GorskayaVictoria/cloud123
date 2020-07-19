from django.forms import forms


class UploadForm(forms.Form):
    profile_pic = forms.FileField(required=False)