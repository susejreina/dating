from django.db import models
from dateSite.models.client import Client, ManagerClient
from dateSite.models.log_session import LogSession
from dateSite.models.enum import ClientTypeE
from datetime import datetime

class Manager(models.Model):

    def __str__(self):
        return self.username

    def get_clients_by_manager(self, id):
        # Get all client manager
        managed_clients = ManagerClient.objects.filter(
                        clicodemanager=id).order_by('clicodegirl')
        client_list = managed_clients.values_list('clicodegirl', flat=True)
        log_session = LogSession.objects.filter(
                        clicode__in=client_list).order_by(
                            'clicode', '-logsignout').distinct('clicode')

        my_client_list = []
        for client in managed_clients:
            client_dict = {}
            client_dict['client'] = client
            client_dict['log'] = None if not log_session.filter(
                clicode=client.clicodegirl).exists() else log_session.get(
                    clicode=client.clicodegirl)
            my_client_list.append(client_dict)

        return my_client_list

    def update_clients_state(self, id):
        managed_clients = ManagerClient.objects.filter(
                                clicodemanager=id)
        # Get unused clients
        clients = Client.objects.filter(clicode__in=managed_clients,
                                        clireplychannel__isnull=True)
        # Search the last time when my unused clients were active
        last_seen = LogSession.objects.filter(
                        clicode__in=clients).order_by(
                            'clicode', '-logsignin').distinct('clicode')
        # Update clients with reply channel and logout null
        last_seen.filter(logsignout__isnull=True,
                         clicode__in=clients).update(
                            logsignout=datetime.now().isoformat())

        # inactive client and ready to taken
        inactive_clients = last_seen.filter(logsignout__isnull=False)

        # client whos probably taken because has a reply channel
        active_clients = Client.objects.filter(clicode__in=managed_clients,
                                        clireplychannel__isnull=False)
        # Update reply channel if has logout date
        last_seen = LogSession.objects.filter(clicode__in=active_clients,
                        logsignout__isnull=False).order_by(
                            'clicode', '-logsignin').distinct('clicode')
        active_clients.exclude(clicode__in=last_seen.values_list(
                        'clicode', flat=True)).update(clireplychannel=None)

    class Meta:
        managed = False
