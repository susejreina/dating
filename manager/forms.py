from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='', required=True,
                             widget=forms.EmailInput(
                                attrs={'class' : 'form-control',
                                       'id' : 'email',
                                       'tabindex' : 1,
                                       'placeholder' : 'email'}))
    password = forms.CharField(label='',required=True,
                               widget=forms.PasswordInput(
                                   attrs={'class' : 'form-control',
                                          'id' : 'password',
                                          'tabindex' : 2,
                                          'placeholder' : 'password'}))
    remember = forms.BooleanField(label='Remember Me', required=False,
                                 widget=forms.CheckboxInput(
                                     attrs={'class' : 'control',
                                            'id' : 'remember',
                                            'tabindex' : 3,}))

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(LoginForm, self).__init__(*args, **kwargs)
