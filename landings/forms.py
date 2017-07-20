from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from allauth.account.forms import SignupForm
from .models import QuickSubscription


class QuickSubscription(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuickSubscription, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('gender', css_class='input-xs'),
            Submit('submit', 'Create Account', css_class='btn-login')
        )

    class Meta:
        model = QuickSubscription
        fields = '__all__'
