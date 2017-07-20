from dateSite.models.log_session import LogSession
from dateSite.base_helper import save_log

def register_login(client, manager):
    # If the manager has not active connections, save the manager log first
    previous_log = LogSession.objects.filter(clicode=client,
                                             logsignout__isnull=True)
    if not previous_log:
        save_log(True, manager, manager)
    save_log(True, client, manager)
