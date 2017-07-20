import json
import socket, struct
import logging
from ipware.ip import get_ip
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from allauth.account.views import (SignupView, LoginView, LogoutView,
                                   EmailView, PasswordResetView)
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models.testimonial import Testimonial
from .models.purchase import Purchase
from .models.client import Client, Picture, PhotoAlbum
from .models.enum import ClientTypeE, SubServiceE
from .models.notification import Notification, NotificationType
from .models.inbox import Inbox
from .models.deniedip import DeniedIp
from .models.log_session import LogSession
from .base_helper import save_log, can_access, get_private_albums
from .forms import EditProfileForm, UploadAlbumForm, UploadFilesForm
from channels import Channel
from .ajax_request import *
from .statics import *


class LoginView(LoginView):
    def __init__(self, **kwargs):
        super(LoginView, self).__init__(*kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        client_testimonials = list(Testimonial.objects.filter(
                                testype='C',
                                tesactive=True).order_by(
                                '-tesname')[:6])
        context['client_testimonials'] = client_testimonials
        love_stories = list(Testimonial.objects.filter(
            testype='L',
            tesactive=True).order_by(
            '-tesname')[:6])
        context['love_stories'] = love_stories
        # Cantidad de miembros
        context['total_members'] = Client.total_members()
        context['total_women'] = Client.total_members_by_gender(2)
        context['total_men'] = Client.total_members_by_gender(1)
        context['total_online'] = Client.total_members_online()
        context['ip'] = get_ip(self.request)
        return context

    def form_invalid(self, form):
        return render(self.request, 'account/login.html', {'login_form': form})


class LogoutView(LogoutView):
    from .models.client import ManagerClient
    def __init__(self, **kwargs):
        super(LogoutView, self).__init__(*kwargs)

    def logout(self):
        if Client.objects.filter(clicode=self.request.user.pk).exists():
            client = Client.objects.get(clicode=self.request.user.pk)
            if (client.tclcode.tclcode == ClientTypeE['client'].value or
                    client.tclcode.tclcode == ClientTypeE['supervisor'].value):
                save_log(False, client)
            elif client.tclcode.tclcode == ClientTypeE['manager'].value:
                save_log(False, client, client)
            elif client.tclcode.tclcode == ClientTypeE['our_client'].value:
                previous_log = LogSession.objects.filter(
                        clicode=client, logsignout__isnull=True)
                if previous_log:
                    previous_log = previous_log.latest('logsignin')
                    managed_girls = ManagerClient.objects.filter(
                        clicodemanager=previous_log.clicodemanager).values_list(
                            'clicodegirl', flat=True)
                    online = LogSession.objects.filter(
                        clicode__in=managed_girls, logsignout__isnull=True,
                        clicodemanager=previous_log.clicodemanager).exclude(
                            clicode__in=[client,previous_log.clicodemanager])
                    if not online:
                        save_log(False, previous_log.clicodemanager)
                    save_log(False, client)


        super(LogoutView, self).logout()


class SignupView(SignupView):

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        return render(self.request,
                      'account/signup.html',
                      {'signup_form': form})


class EmailView(EmailView):

    def __init__(self, **kwargs):
        super(EmailView, self).__init__(*kwargs)


class PasswordResetView(PasswordResetView):
    from django.contrib.auth.models import User

    def __init__(self, **kwargs):
        super(PasswordResetView, self).__init__(*kwargs)

    def dispatch(self, request, *args, **kwargs):
        if Client.objects.filter(clicode=self.request.user.pk).exists():
            if not can_access(self.request.user):
                return redirect("dateSite:forbidden")
        return super(PasswordResetView, self).dispatch(
            self.request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            email = form.cleaned_data["email"]
            if not can_access(User.objects.get(email=email)):
                return redirect("dateSite:forbidden")
        return super(PasswordResetView, self).form_valid(form)


class Index(ListView):
    model = Client
    context_object_name = 'members'
    template_name = 'dateSite/main.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['seaminage'] = self.request.POST.get('seaminage', 0)
        context['seamaxage'] = self.request.POST.get('seamaxage', 0)
        context['country'] = self.request.POST.get('seacountry', 0)

        if Client.objects.filter(clicode=self.request.user.pk).exists():
            client = Client.objects.get(clicode=self.request.user.pk)
            context['show_promo_10'] = 1
            if client.tclcode.tclcode == ClientTypeE['client'].value:
                init_promo = datetime(2017, 6, 11, 23, 59, 59)
                if LogSession.objects.filter(
                        clicode=self.request.user.pk,
                        logsignin__gte=init_promo.date()).count() > 1:
                    context['show_promo_10'] = 0
        return context

    def get_queryset(self):
        user = self.request.user
        if Client.objects.filter(clicode=user.pk).exists():  # Es un cliente
            client = Client.objects.get(clicode=user.pk)
            gen_code = client.gencode.genpreference

            if (client.tclcode.tclcode == ClientTypeE['our_client'].value):
                tcl_code = [ClientTypeE['client'].value]
            else:
                tcl_code = [ClientTypeE['client'].value,
                            ClientTypeE['our_client'].value]

            min_age = self.request.POST.get('seaminage')
            max_age = self.request.POST.get('seamaxage')
            country = self.request.POST.get('seacountry')

            all_members = Client.list_client(tcl_code, gen_code, min_age,
                                             max_age, country)
            show_more = 1 if (len(all_members) > 18) else 0
            members = randomize(all_members, 18)
        else:  # Es un usuario
            json_gender = json.loads(user.last_name)
            gender = Gender.objects.get(gencode=json_gender['gen'])
            gen_code = gender.genpreference

            tcl_code = [ClientTypeE['client'].value]
            tcl_code = [ClientTypeE['our_client'].value]

            min_age = self.request.POST.get('seaminage')
            max_age = self.request.POST.get('seamaxage')
            country = self.request.POST.get('seacountry')

            all_members = Client.list_client(tcl_code, gen_code, min_age,
                                             max_age, country)
            show_more = 1 if (len(all_members) > 18) else 0
            members = randomize(all_members, 18)

        result = []
        result.append(members)  # Los miembros
        result.append(show_more)  # Si hay mas

        return result


    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                return redirect('manager:manager_index')
        return super(Index, self).dispatch(
            self.request, *args, **kwargs)


class AlertView(ListView):
    model = Notification
    context_object_name = 'all_notifications'
    template_name = 'dateSite/notifications.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        user = self.request.user
        Notification.objects.filter(
            clicoderecieved=user.pk,
            notread=False).update(
            notread=True)
        all_notifications = Notification.objects.filter(
            clicoderecieved=user.pk).order_by("-notcode")
        return all_notifications


class ProfileView(DetailView):
    from django.http import Http404
    from .models.client import ClientCollectionAlbum

    model = Client
    template_name = 'dateSite/profile.html'
    slug_field = 'cliusername'
    context_object_name = 'member'

    def get_context_data(self, **kwargs):
        current_client = kwargs.get('object')
        if not Client.objects.filter(
                clicode=current_client.pk).exists():
            raise Http404

        context = super(ProfileView, self).get_context_data(**kwargs)
        album = PhotoAlbum.objects.filter(clicode=current_client, phatype=1,
                                          phaactive=True).order_by(
                                                    'phacreationdate').first()
        context['album_list'] = get_client_albums(current_client)
        if album:
            public_pictures = Picture.objects.filter(
                picactive=True, phacode=album).exclude(
                    picprofile=True).order_by('piccode')
            context['public_album'] = public_pictures
            context['album_data'] = album

        if current_client.pk == self.request.user.pk:
            context['upload_profile'] = UploadFilesForm()

        context['private_albums'] = get_private_albums(current_client)
        context['private_collection'] = list(
            ClientCollectionAlbum.objects.filter(
                clicode=self.request.user.pk).values_list(
                'phacode', flat=True))
        context['photoalbum_form'] = UploadAlbumForm()
        costs = SubService.objects.filter(sercode=ServiceE['photos'].value)
        context['credit_cost'] = {
            'view_album': costs.get(
                suscode=SubServiceE['view_album'].value).susquantitycredit,
            'add_album': costs.get(
                suscode=SubServiceE['add_album'].value).susquantitycredit}
        context["chat_messages"] = reversed(get_chat_messages(Client.objects.get(clicode=self.request.user.pk), Client.objects.get(clicode=current_client.pk)))
        try:
            sender = self.model.objects.get(pk=self.request.user.pk)
            if(current_client.clicode != sender.clicode):
                alert = Notification.objects.filter(
                    clicodesent=sender.clicode,
                    clicoderecieved=current_client.clicode).last()
                if alert:
                    seg = timezone.now() - alert.notdate
                    save = False if seg.total_seconds() < 43200 else True
                    if save:
                        alert = Notification(
                            notdate=datetime.now(),
                            clicoderecieved=current_client,
                            clicodesent=sender,
                            ntycode=NotificationType.objects.get(ntycode=1)
                        )
                        alert.save()

                        j_alert = ExtJsonSerializer().serialize(
                            [alert],
                            default=convert_data_to_serielize,
                            fields=['notread', 'formatted_notdate', 'clicodesent',
                                    'clicoderecieved', 'ntycode'],
                            indent=2,
                            use_natural_foreign_keys=True,
                            use_natural_primary_keys=True)

                        if current_client.clireplychannel:
                            d = {"notification": j_alert, "error": {'type': '3'}}
                            Channel(current_client.clireplychannel).send({
                                "text": json.dumps(d)
                            })
        except Client.DoesNotExist:
            d = {"notification": 0}


        return context

    def dispatch(self, request, *args, **kwargs):
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                return redirect('manager:manager_index')
        return super(ProfileView, self).dispatch(
            self.request, *args, **kwargs)


class InboxView(ListView):
    model = Inbox
    template_name = 'dateSite/inbox.html'
    context_object_name = 'member'

    def get_suggestions(self,context):
        suggestions = list(Client.suggestions(self.request.user.pk,10))
        context["inbox_suggestions"]  = suggestions[0:4]
        context["chat_suggestions"]  = suggestions[4:]
        return context

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['upload_pictures_form'] = UploadFilesForm()
        client = Client.objects.filter(clicode=self.request.user.pk)
        if client.exists():
            list_inbox = Inbox.list_client_inbox(self.request.user.pk)
            # if list_inbox: # Hay correos
            context['list_inbox'] = list_inbox
            list_inbox_notread = Inbox.last_not_read(self.request.user.pk)
            if list_inbox_notread:
                context['inbox_not_read'] = list_inbox_notread
            context = self.get_suggestions(context)


        # Cuando van al inbox desde el home al hacer click en el sobre de un perfil
        try:
            if Client.objects.filter(cliusername=self.kwargs['slug']).exists():
                mail_to = Client.objects.get(cliusername=self.kwargs['slug'])
                context['id_to'] = mail_to.clicode
                context['user_to'] = mail_to.cliusername
        except:
            pass

        return context

    def get_queryset(self):
        user = self.request.user
        Notification.objects.filter(
            clicoderecieved=user.pk,
            notread=False).update(
            notread=True)
        all_notifications = Notification.objects.filter(
            clicoderecieved=user.pk).order_by("-notcode")
        return all_notifications

    def dispatch(self, request, *args, **kwargs):
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                return redirect('manager:manager_index')
        return super(InboxView, self).dispatch(
            self.request, *args, **kwargs)


class UpdateProfileView(UpdateView):
    model = Client
    form_class = EditProfileForm
    template_name = 'dateSite/edit_profile.html'
    success_url = "/"
    context_object_name = 'client'

    def form_valid(self, form):
        if self.request.method == 'POST':
            if form.is_valid():
                form_data = form.cleaned_data
                client = Client.objects.get(clicode=self.request.user.pk)
                client.cliname = form_data['cliname']
                client.clidescription = form_data['clidescription']
                client.clibirthdate = form_data['clibirthdate']
                client.inccode = form_data['inccode']
                client.gencode = form_data['gencode']
                client.citcode = form_data['citcode']
                client.marcode = form_data['marcode']
                client.educode = form_data['educode']
                client.lancodefirst = form_data['lancodefirst']
                client.lancodesecond = form_data['lancodesecond']
                client.heicode = form_data['heicode']
                client.weicode = form_data['weicode']
                client.ocucode = form_data['ocucode']
                client.ethcode = form_data['ethcode']
                client.langlevel = form_data['langlevel']
                client.bodycode = form_data['bodycode']
                client.chicode = form_data['chicode']
                client.eyecode = form_data['eyecode']
                client.haicode = form_data['haicode']
                client.hlecode = form_data['hlecode']
                client.relcode = form_data['relcode']
                client.zodcode = form_data['zodcode']
                client.frecodedrink = form_data['frecodedrink']
                client.frecodesmoke = form_data['frecodesmoke']
                client.feecode = form_data['feecode']
                client.save()
            else:
                print('error')

        return redirect('dateSite:profile', slug=self.request.user.username)

    def user_passes_test(self, request):
        if request.user.is_authenticated():
            self.object = self.get_object()
            return self.object.cliuser == request.user
        return False

    def get_object(self):
        return self.model.objects.get(pk=self.request.user.pk)

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object() or not self.user_passes_test(request):
            return redirect('/')
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                return redirect('manager:manager_index')
        return super(UpdateProfileView, self).dispatch(
            self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateProfileView, self).get_context_data(**kwargs)
        public_albums = PhotoAlbum.objects.filter(
            phaactive=True, phatype=1,
            clicode=self.request.user.pk)
        context['public_pictures'] = Picture.objects.filter(
            picactive=True, phacode__in=public_albums)
        context['upload_profile'] = UploadFilesForm()
        context['member'] = Client.objects.get(clicode=self.request.user.pk)
        return context


class OnlineMembers(ListView):
    model = Client
    context_object_name = 'members'
    template_name = 'dateSite/online_members.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super(OnlineMembers, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(OnlineMembers, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['modal'] = True
        context['seaminage']=self.request.POST.get('seaminage',18)
        context['seamaxage']=self.request.POST.get('seamaxage',30)
        context['gencode']=self.request.POST.get('gencode')
        return context

    def get_queryset(self):
        min_age = self.request.POST.get('seaminage',18)
        max_age = self.request.POST.get('seamaxage',99)
        tcl_code = [ClientTypeE['our_client'].value]

        if self.request.POST.get('gencode'):
            gen_code = self.request.POST.get('gencode')
            gender = Gender.objects.get(gencode=gen_code)
            gen_code = gender.genpreference
        else:
            gen_code = 2

        result=[]
        all_members = Client.list_client(tcl_code, gen_code, min_age, max_age)
        if (len(all_members)>18):
            show_more = 1
        else:
            show_more = 0
        members = randomize(all_members,18)
        result.append(members) #Los miembros
        result.append(show_more) #si hay mas

        return result

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class CreditsApproval(ListView):
    model = Purchase
    context_object_name = 'approval'
    template_name = 'dateSite/approval.html'

    def get_context_data(self, **kwargs):
        context = super(CreditsApproval, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['modal'] = True
        return context

    def register_purchase(self):
        objGET = self.request.GET
        approval = {}
        customer_fname = objGET.get('n')
        customer_lname = objGET.get('l')
        email = objGET.get('e')
        price = objGET.get('p')
        addres1 = objGET.get('a')
        cardType = objGET.get('c')
        referer = objGET.get('cb')
        if referer == '':
            referer=None
        city = objGET.get('cy')
        country = objGET.get('co')
        zipcode = objGET.get('z')
        idsuscription = objGET.get('id')
        approvalid = objGET.get('si')

        #Guardar el Purchase
        purchase = Purchase.objects.filter(puridsuscription=idsuscription).update(
                   purcredit = approval["credits"],
                   purdate = datetime.now().isoformat(),
                   purstatus = True,
                   purbalance = approval["credits"],
                   purfname = customer_fname,
                   purlname = customer_lname,
                   puremail = email,
                   puraddress1 = addres1,
                   purcity = city,
                   purcountry = country,
                   purzipcode = zipcode,
                   purprice = price,
                   purcardtype = cardType,
                   purccbillreferer = referer,
                   purapprovalid = approvalid)
        return approval

    def get_queryset(self):
        approval = {}
        ip = get_ip(self.request)
        if ip is not None:
            allowed_ranges = ["64.38.240", "64.38.241", "64.38.215", "64.38.212"]
            split_ip = ip.split(".")
            allowed = False
            for a in allowed_ranges:
                compare = '%s.%s.%s' % (split_ip[0], split_ip[1], split_ip[2])
                if compare == a:
                    allowed = True
                    """
                    if self.request.method == 'GET':
                        approval = self.register_purchase(self.request.GET)
                    """
                    break
            if allowed == False:
                approval["msg"] = "Ip is not allowed. Sorry, your payment has been processed with an untrust IP. Please get in contact with our staff for the solution. We will be glad to help you. Please Just send us and email to DatinglatinosStaff@datinglatinos.com"
            approval = self.register_purchase()
        else:
            approval["msg"] = "Ip is none. Sorry, your payment has been processed with an untrust IP. Please get in contact with our staff for the solution. We will be glad to help you. Please Just send us and email to DatinglatinosStaff@datinglatinos.com"
        approval["ip"] = ip

        return approval


class CreditsDenied(ListView):
    model = Purchase
    context_object_name = 'denied'
    template_name = 'dateSite/denied.html'

    def get_context_data(self, **kwargs):
        context = super(CreditsDenied, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['modal'] = True
        return context

    def get_queryset(self):
        denied = {}
        if self.request.method == 'GET':
            customer_fname = self.request.GET.get('n')
            customer_lname = self.request.GET.get('l')
            email = self.request.GET.get('e')
            price = self.request.GET.get('p')
            addres1 = self.request.GET.get('a')
            cardType = self.request.GET.get('c')
            referer = self.request.GET.get('cb')
            if referer == '':
                referer=None
            city = self.request.GET.get('cy')
            country = self.request.GET.get('co')
            zipcode = self.request.GET.get('z')
            idsuscription = self.request.GET.get('id')
            approvalid = self.request.GET.get('si')

            denialid = self.request.GET.get('d')
            reasondecline = self.request.GET.get('rfd')
            reasondeclinecode = self.request.GET.get('rdi')

            denied["reason"] = self.request.GET.get('rfd')

            #Guardar el Purchase
            purchase = Purchase.objects.filter(puridsuscription=idsuscription).update(
                       purcredit = denied["credits"],
                       purdate = datetime.now().isoformat(),
                       purstatus = False,
                       purbalance = denied["credits"],
                       purfname = customer_fname,
                       purlname = customer_lname,
                       puremail = email,
                       puraddress1 = addres1,
                       purcity = city,
                       purcountry = country,
                       purzipcode = zipcode,
                       purprice = price,
                       purcardtype = cardType,
                       purccbillreferer = referer,
                       purdenialid = denialid,
                       purreasondecline = reasondecline,
                       purreasondeclinecode = reasondeclinecode)

        return denied

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
