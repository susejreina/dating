import json
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import email_confirmed, user_logged_in
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.shortcuts import render
from .models.client import Client
from .models.catalog import Gender, TypeClient, Language
from .models.enum import ClientTypeE
from .forms import GoodLuckSearchForm
from .base_helper import save_log
from .sending import send_mail
from landings.forms import QuickSubscription


class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        if self.request.method == "POST":
            form2 = GoodLuckSearchForm(request.POST)
            form3 = QuickSubscription(request.POST)
            if form.is_valid():
                user_data = form.cleaned_data
                search_data = None
                preferences = None

                if form2.is_valid():
                    search_data = form2.cleaned_data
                    preferences = '{"gen":%i, "min":%i, "max":%i}' % (
                        search_data['gencode'].gencode,
                        int(search_data['seaminage']),
                        int(search_data['seamaxage']))
                if form3.is_valid():
                    search_data = form3.cleaned_data
                    preferences = '{"gen":%i, "min":%i, "max":%i}' % (
                                      search_data['gender'].gencode, 18, 99)

                user.username = user_data['username']
                user.email = user_data['email']
                user.last_name = preferences

                if 'password1' in user_data:
                    user.set_password(user_data['password1'])
                else:
                    user.set_unusable_password()

                self.populate_username(request, user)

                if commit:
                    user.save()

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        json_gender = json.loads(
            emailconfirmation.email_address.user.last_name)
        gender_preference = Gender.objects.get(
            genpreference=json_gender['gen'])
        current_site = Site.objects.get_current()
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        context = {
            'user': emailconfirmation.email_address.user,
            'activate_url': activate_url,
            'current_site': current_site,
            'key': emailconfirmation.key,
            'email': emailconfirmation.email_address.user.email,
            'gender_preference': gender_preference.genname,
        }

        template = 'account/email/email_confirmation_message.html'
        send_mail("Welcome to datinglatinos.com!!! Please confirm your email.", template,
                  [emailconfirmation.email_address.email],
                  'Dating Latinos <noreply@datinglatinos.com>', context)
        return render(request, 'account/verification_sent.html')

    def get_login_redirect_url(self, request):
        path = "/"
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                path = "/manager/"
            if client.tclcode.tclcode == ClientTypeE['supervisor'].value:
                path = "/supervisor"
            # if client.tclcode.tclcode == ClientTypeE['our_client'].value:
                # path = "/manager/checkpoint"

        return path

    @receiver(email_confirmed)
    def email_confirmed_(request, email_address, **kwargs):
        user = User.objects.get(email=email_address.email)
        json_gender = json.loads(user.last_name)
        client_gender = Gender.objects.get(gencode=json_gender['gen'])
        type_client = TypeClient.objects.all()

        client = Client()
        client.clicode = client.cliuser_id = user.id
        client.cliusername = user.username
        client.cliemail = user.email
        client.clipassword = user.password
        client.clidatesubscription = user.date_joined
        client.gencode = client_gender
        # Default
        client.cliactive = True
        client.cliverified = False
        client.tclcode = type_client.get(tclcode=ClientTypeE['client'].value)
        client.lancodefirst = Language.objects.get(lanname='English')
        client.save()
        save_log(True, client)

    @receiver(user_logged_in)
    def user_logged_in_(request, user, **kwargs):
        if Client.objects.filter(clicode=user.pk).exists():
            client = Client.objects.get(clicode=user.pk)
            if (client.tclcode.tclcode == ClientTypeE['client'].value or
                    client.tclcode.tclcode == ClientTypeE['supervisor'].value or
                    client.tclcode.tclcode == ClientTypeE['our_client'].value):
                save_log(True, client)
            elif client.tclcode.tclcode == ClientTypeE['manager'].value:
                save_log(True, client, client)
