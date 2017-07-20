import json
from .models import Manager
from .helper import register_login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.http import JsonResponse
from dateSite.models.client import Client, ManagerClient
from dateSite.models.inbox import Inbox
from dateSite.models.chat import Room, Message
from dateSite.models.purchase import Purchase
from dateSite.models.enum import ClientTypeE
from django.contrib.auth import authenticate, login as auth_login
from dateSite.forms import LoginForm
from dateSite.base_helper import save_log
from channels import Channel
from dating.settings import USERS_PASS
from django.db.models import Count
from django.contrib.auth.models import User



class LoginManager(View):
    template_name = 'manager/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'login_form': LoginForm()})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request.POST)

        if not login_form.is_valid():
            return render(request, 'manager:manager_login',
                          {'login_form': login_form})
        else:
            email = login_form.cleaned_data['login']
            password = login_form.cleaned_data['password']
            remember = login_form.cleaned_data['remember']
            user = authenticate(email=email, password=password,
                                remember=remember)
            if user is not None:
                client = Client.objects.get(clicode=user.pk)
                if client.tclcode.tclcode == ClientTypeE['supervisor'].value:
                    auth_login(request, user)
                    return redirect('manager:supervisor_panel')
                elif client.tclcode.tclcode == ClientTypeE['manager'].value:
                    auth_login(request, user)
                    return redirect('manager:manager_index')
                else:
                    return render(request, 'manager/login.html',
                                  {'login_form': login_form,
                                   'error': "You don't have permission to "
                                            "access to this content"})

        return render(request, 'manager:manager_login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return redirect('manager:manager_index')
        return super(LoginManager, self).dispatch(
            self.request, *args, **kwargs)


class IndexManager(ListView):
    model = ManagerClient
    context_object_name = 'members'
    template_name = 'manager/index.html'

    def get_queryset(self):
        manager = Manager()
        managed_clients = manager.get_clients_by_manager(
                            self.request.user.pk)
        manager.update_clients_state(self.request.user.pk)

        return managed_clients

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('manager:manager_login')
        else:
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode != ClientTypeE['manager'].value:
                return redirect('dateSite:forbidden')
        return super(IndexManager, self).dispatch(
            self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class CheckpointManager(ListView):
    model = ManagerClient
    context_object_name = 'managers'
    template_name = 'manager/checkpoint.html'

    def get_queryset(self):
        manager = ManagerClient.objects.filter(
                        clicodegirl=self.request.user.pk)

        return manager

    def post(self, request, *args, **kwargs):
        manager = request.POST.get("manager")
        clients = Client.objects.filter(clicode__in=[manager,
                                                     self.request.user.pk])

        register_login(clients.get(tclcode=ClientTypeE['our_client'].value),
                       clients.get(tclcode=ClientTypeE['manager'].value))

        return redirect('dateSite:main')

    def dispatch(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode != ClientTypeE['our_client'].value:
                return redirect('dateSite:main')
            else:
                manager = ManagerClient.objects.filter(
                                clicodegirl=self.request.user.pk)
                if manager.count() <= 1:
                    register_login(manager.first().clicodegirl,
                                   manager.first().clicodemanager)
                    return redirect('dateSite:main')
        except Client.DoesNotExist:
            return redirect('dateSite:main')

        return super(CheckpointManager, self).dispatch(
            self.request, *args, **kwargs)


class SupervisorView(View):
    template_name = 'supervisor/activity.html'

    def get(self, request, *args, **kwargs):
        context = {}
        #Get our clients clicode
        our_clients = Client.objects.filter(tclcode=ClientTypeE['our_client'].value).values('clicode')

        #Rooms without answer
        room = Room.objects.filter(roostartdatetime__isnull=True).values('roocode')
        msgs = Message.objects.filter(roocode__in=room,
                                      clicoderecieved__in=our_clients).order_by(
                                      'clicoderecieved','clicodesent').distinct(
                                      'clicoderecieved','clicodesent')
        context['chat'] = msgs

        context['inbox'] = Inbox.objects.filter(
            clicoderecieved__in=our_clients, inbread=False)

        return render(request, self.template_name, context)

    def dispatch(self, request, *args, **kwargs):
        if Client.objects.filter(clicode=request.user.pk).exists():
            client = Client.objects.get(clicode=request.user.pk)
            if client.tclcode.tclcode != ClientTypeE['supervisor'].value:
                return redirect('manager:manager_index')
        return super(SupervisorView, self).dispatch(
            self.request, *args, **kwargs)


class NewsFeedView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'supervisor/newsfeed.html'


    def get_context_data(self, **kwargs):
        context = super(NewsFeedView, self).get_context_data(**kwargs)
        context['clients'] = Client.objects.all().order_by(
            '-clidatesubscription')[:200]
        context['purchase'] = Purchase.objects.all().order_by(
            '-purdate')[:100]

        return context

    def query_set(self):
        return User.objects.all().order_by(
            '-date_joined')[:200]



def ajax_connect(request):
    data = request.POST.get('data')
    manager = Client.objects.get(clicode=request.user.pk)
    client = json.loads(data)
    client = Client.objects.get(cliusername=client['client'])
    email = client.cliemail
    password = client.clipassword

    user = authenticate(email=email, password=USERS_PASS)

    if user is not None:
        save_log(True, client, manager)
        auth_login(request, user)
        response = '/'

    return JsonResponse({ "data": response }, safe=False)


def ajax_replace_connection(request):
    data = json.loads(request.POST.get('data'))
    client = Client.objects.get(cliusername=data['client'])
    manager = Client.objects.get(cliusername=data['manager'])

    Channel(client.clireplychannel).send(
        {'message': 'Your connection has been replaced',
         'manager': manager})

    user = authenticate(email=email, password=USERS_PASS)

    if user is not None:
        # Guardar el registro del log
        save_log(True, client, manager)
        auth_login(request, user)
        response = '/'

    return JsonResponse({ "data": 'response' }, safe=False)
