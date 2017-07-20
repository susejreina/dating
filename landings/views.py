from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .forms import QuickSubscription
from dateSite.forms import SignupForm


# Create your views here.
def landing_page(request, slug):
    template = "%s.html" % slug
    return render(request, template, context)


def landing_page_form(request, slug):
    template = "%s.html" % slug
    context = {
        'quick_form': QuickSubscription(),
        'landing_name': slug,
    }
    return render(request, template, context)


def validate_form(request):
    signup_form = SignupForm(request.POST)

    if not signup_form.is_valid():
        return JsonResponse({'success': False,
                             'error_messages': signup_form.errors },
                            safe=False)

    return JsonResponse({'success': True}, safe=False)
