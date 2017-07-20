import os
import json
import random
from datetime import datetime, time
from django.utils import timezone
from .context_processor import *
from django.http import JsonResponse, HttpResponse
from django.core.files import File
from django.db.models import Q
from .models.client import (Client, Picture, PhotoAlbum, ManagerClient,
                            ClientCollectionAlbum)
from .models.catalog import Gender, Feeling, Country, Language
from .models.notification import Notification, NotificationType
from .models.purchase import Purchase
from .models.chat import Room
from .models.inbox import Inbox, InboxPicture
from .models.enum import ClientTypeE, ServiceE, SubServiceE
from .base_helper import (ExtJsonSerializer, convert_data_to_serielize,
                          get_client_albums, new_picture_name, get_user_folder)
from channels import Channel
from django_file_form.models import UploadedFile
from django.core.files import File
from .sending import send_mail
from dating.settings import MEDIA_URL


def ajax_feeling(request):
    if Client.objects.filter(clicode=request.user.pk).exists():
        client = Client.objects.get(clicode=request.user.pk)
        feecode = request.POST.get('feeling');
        client.feecode = Feeling.objects.get(feecode=feecode)
        client.save()
        return JsonResponse(str(client.feecode.feeiconfile), safe=False)

    return JsonResponse({'error': True}, safe=False)


def ajax_info_complete_client(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to send message "
                              "with girl %s", (user.pk, girl))
                    error = ("You don't have permission to get this kind of "
                             "information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = 'Not results to show'

    if error != "":
        return JsonResponse({'error': error}, safe=False)
    else:
        data = client.client_complete()
        return JsonResponse(data, safe=False)


def ajax_qtyinbox(request):
    clicode = request.POST.get('clicode')
    inbox = Inbox.quantityNotRead(clicode=clicode)
    data = {'qty': inbox}
    return JsonResponse(data)


def ajax_qtynoti(request):
    clicode = request.POST.get('clicode')
    notis = Notification.quantityNotRead(clicode=clicode)
    data = {'qty': notis}
    return JsonResponse(data)


def ajax_readnoti(request):
    user = request.user
    q = int(request.POST.get('quantity'))
    error = ""
    code = request.user.pk

    # "girl" significa que es un manager
    if 'girl' in request.POST:
        girl = request.POST.get('girl')
        code = int(girl)
        exits = Client.objects.filter(clicode=user.pk).exists()
        if exits:
            client = Client.objects.get(clicode=user.pk)
            if client.cliactive:
                if client.tclcode.tclcode == ClientTypeE['manager'].value:
                    act_for_manager = ManagerClient.objects.filter(
                        clicodemanager=user.pk,
                        clicodegirl=int(girl)).exists()
                    if act_for_manager is False:
                        log.debug("Manager with code %s is trying to update "
                                  "notifications from girl %s",
                                  (user.pk, girl))
                        error = ("You don't have permission to get this kind "
                                 "of information")
                    else:
                        client = Client.objects.get(clicode=int(girl))
                        if client.cliactive is False:
                            error = ("Client that you want to get information "
                                     "isn't active")
                else:
                    log.debug("Trying to update notification and not is a "
                              "manager %s.", user.pk)
                    error = "You can't get information"
            else:
                log.debug("Trying to update notification with inactive user "
                          "code %s.", user.pk)
                error = "You aren't active"
        else:
            log.debug("Trying to update notification with user code %s.",
                      user.pk)
            error = 'You are not a user'

    if error:
        data = {'error': 'yes', 'description': error}
    else:
        notis = Notification.objects.filter(
            clicoderecieved=code,
            notread=False).order_by(
            '-notcode')
        if notis:
            i = q
            for n in notis:
                n.notread = True
                n.save()
                i = i - 1
                if i <= 0:
                    break
        qty = Notification.quantityNotRead(clicode=code)
        data = {'error': 'no', 'qty': qty}
    return JsonResponse(data)


def ajax_check_readmessage(request):
    code = request.POST.get('code')
    if code:
        up = Message.objects.filter(mescode=code).update(mesread=True)
    return JsonResponse({'transaccion': 'ok'})


def ajax_list_chat(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to get "
                              "notification with girl %s",
                              (user.pk, girl))
                    error = ("You don't have permission to get this kind "
                             "of information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = "Not results to show"

    if error == "":
        result = Room.getChatsRequest(girl)
        context = {}
        context['mychats'], context['myrequest'] = [], []
        if len(result) > 0:
            if "mychats" in result:
                if len(result["mychats"]) > 0:
                    context['mychats'].append(result["mychats"])
            if "myrequest" in result:
                if len(result["myrequest"]) > 0:
                    context['myrequest'].append(result["myrequest"])
        return JsonResponse(context, safe=False)
    else:
        return JsonResponse({'error': error}, safe=False)


def ajax_profile_picture(request):
    picture = request.POST.get('picture_id')
    client_albums = PhotoAlbum.objects.filter(
        clicode=request.user.pk)
    pictures = Picture.objects.filter(
        phacode__in=client_albums)

    try:
        old_picture = pictures.get(picprofile=True)
        oldpicname = new_picture_name('photo', str(old_picture.picpath))
        filename = "%s/%s" % (old_picture.phacode.phacode, oldpicname)
        back_to_album = Picture(
            picpath=File(old_picture.picpath, filename),
            picthumb=old_picture.picthumb,
            picprofile=False,
            picdescription=old_picture.picdescription,
            phacode=old_picture.phacode,
            picactive=True
        )
        back_to_album.save()
        old_picture.picpath.close()
        old_picture.picpath.delete()
        old_picture.delete()
    except Picture.DoesNotExist:
        pass

    new_picture = pictures.get(piccode=picture)
    pictures = pictures.update(picprofile=False)
    picname = new_picture_name('prof', str(new_picture.picpath))

    new_picture.picpath = File(new_picture.picpath, picname)
    new_picture.picprofile = True
    new_picture.save()

    json_pic = {
        'picpath': new_picture.picpath.url,
        'picdescription': new_picture.picdescription,
        'phacode': new_picture.phacode_id,
        'albums': get_client_albums(client_albums.first().clicode)
    }

    return JsonResponse(json_pic, safe=False)


def ajax_get_album(request):
    albumid = request.POST.get('albumid')

    album = PhotoAlbum.objects.filter(phacode=albumid)
    albums = get_client_albums(Client.objects.get(
                               clicode=request.user.pk),
                               album)

    return JsonResponse(albums, safe=False)


def ajax_get_albums(request):
    albums = get_client_albums(Client.objects.get(
                               clicode=request.user.pk))
    return JsonResponse(albums, safe=False)


def ajax_add_private_album(request):
    album_added = request.POST.get('album_id')
    response = purch_album(request, album_added)

    return JsonResponse(response, safe=False)


def ajax_add_picture_description(request):
    picture_id = request.POST.get('picture_id')
    description = request.POST.get('description')

    picture = Picture.objects.get(piccode=picture_id)
    picture.picdescription = description
    picture.save()

    album_id = picture.phacode.phaname

    return JsonResponse({'album_id': album_id,
                         'picture_id': picture_id,
                         'description': picture.picdescription}, safe=False)


def ajax_set_read_inbox(request):
    update = False
    if 'inbcode' in request.POST:
        code = request.POST.get("inbcode")
        update = Inbox.set_read_inbox(code)
    return JsonResponse({'transaccion': update})


def ajax_not_read_inbox(request):
    if Client.objects.filter(clicode=self.request.user.pk).exists():
        list_inbox_notread = Inbox.last_not_read(self.request.user.pk)
        if list_inbox_notread:
            context['inbox_not_read'] = list_inbox_notread
        else:
            suggestions = list(Client.suggestions(self.request.user.pk,10))
            context["inbox_suggestions"]  = suggestions[0:4]
            context["chat_suggestions"]  = suggestions[4:]
    return JsonResponse({'data': context},safe=False)


def ajax_get_inbox(request):
    if 'inbcode' in request.POST:
        inbcode = request.POST.get("inbcode")
        clicode = request.user.pk;
        if Inbox.objects.filter(inbcode=inbcode,inbactive=True).exists():
            inbox = Inbox.objects.get(inbcode=inbcode,inbactive=True)
            #Correo recibido por el cliente y aun no se ha leido
            if not inbox.inbread  and inbox.clicoderecieved.clicode == clicode:
                Inbox.set_read_inbox(inbox.inbcode)

            result = {'code': inbox.inbcode,
                     'message': inbox.inbmessage,
                     'title': inbox.inbtitle,
                     'pictures': inbox.inbox_pictures,
                     'codeorigin': inbox.inbcodeorigin,
                     'sentdate': inbox.formatted_inbsenddate,
                     'codesent': inbox.clicodesent.clicode,
                     'coderecieve': inbox.clicoderecieved.clicode,
                     'usersent': inbox.clicodesent.cliusername,
                     'userrecieve': inbox.clicoderecieved.cliusername,
                     'agesent': inbox.clicodesent.age,
                     'agerecieve': inbox.clicoderecieved.age,
                     'picturesent':inbox.clicodesent.profile_picture_media,
                     'picturerecieve':inbox.clicoderecieved.profile_picture_media,
                     }
        else:
            result= {'error': 'Inbox not found'}
        return JsonResponse(result, safe=False)


def ajax_delete_album(request):
    albumid = request.POST.get('album_id')
    album = PhotoAlbum.objects.get(phacode=albumid)
    pictures = Picture.objects.filter(phacode=album.phacode)
    for picture in pictures:
        picture.picpath.delete()
        picture.picthumb.delete()
    pictures.delete()
    album.delete()

    return JsonResponse({'message': 'Album deleted'}, safe=False)


def ajax_delete_picture(request):
    picture_id = request.POST.get('picture_id')
    picture = Picture.objects.get(piccode=picture_id)
    default = None

    if picture.picprofile is True:
        default = '/static/dateSite/img/default_profile.png'

    picture.picpath.delete()
    picture.picthumb.delete()
    picture.delete()

    album = PhotoAlbum.objects.get(phacode=picture.phacode_id)

    return JsonResponse({'message': 'picture deleted',
                         'album_id': album.phacode,
                         'default': default,
                         'albums': get_client_albums(album.clicode)},
                        safe=False)


def ajax_list_inbox(request):
    list_inbox = Inbox.list_client_inbox(request.user.pk)
    result = []
    for l in list_inbox:
        dic_inbox = {}
        dic_inbox["inbcode"] = l.inbcode
        dic_inbox["short_title"] = l.short_title
        dic_inbox["formatted_short_inbsenddate"] = l.formatted_short_inbsenddate
        dic_inbox["inbread"] = l.inbread
        if request.user.pk == l.clicoderecieved.clicode:
            dic_inbox["clicode"] = l.clicodesent.clicode
            dic_inbox["profile_picture"] = l.clicodesent.profile_picture_media
            dic_inbox["cliusername"] = l.clicodesent.cliusername
            dic_inbox["age"] = l.clicodesent.age
            dic_inbox["cliname"] = l.clicodesent.cliname
            dic_inbox["status"] = 'Recieved'
        else:
            dic_inbox["clicode"] = l.clicoderecieved.clicode
            dic_inbox["profile_picture"] = l.clicoderecieved.profile_picture_media
            dic_inbox["cliusername"] = l.clicoderecieved.cliusername
            dic_inbox["age"] = l.clicoderecieved.age
            dic_inbox["cliname"] = l.clicoderecieved.cliname
            dic_inbox["status"] = 'Sent'

        result.append(dic_inbox)

    return JsonResponse(result, safe=False)


def ajax_send_inbox(request):
    from django.contrib.sites.models import Site
    user_id = request.user.pk

    if 'girl' in request.POST:  # Es un manager
        send_inbox_manager(request)
    else:
        # Info recived
        msg = request.POST.get('msg')
        origin = request.POST.get('origin')
        form_id = request.POST.get('form_id')
        recieved = request.POST.get('recieved')
        recieved_arr = recieved.split(",")
        title = request.POST.get('title')
        # init vars
        client_sender = Client.objects.get(clicode=user_id)
        pictures = None

        if form_id:
            pictures = UploadedFile.objects.filter(form_id=form_id)

        response = []
        clients_recieved = Client.objects.filter(clicode__in=recieved_arr)
        for client in recieved_arr:
            client_recieved = clients_recieved.get(clicode=client)

            # origin = 0 es un correo nuevo
            title = title if origin == "0" else "Re: %s" % Inbox.last_title(origin)
            root = None if origin == "0" else origin

            inbox = Inbox(
                inbtitle=title,
                inbmessage=msg,
                clicoderecieved=client_recieved,
                clicodesent=client_sender,
                inbcodeorigin=root,
                inbsenddate=datetime.now().isoformat(),
                lancode=Language.objects.get(
                    lancode=client_sender.lancodefirst.lancode)
            )
            inbox.save()

            if pictures:
                for pic in pictures:
                    picname = new_picture_name(
                              'inbox', pic.original_filename)
                    picture = InboxPicture(
                        inbcode=inbox,
                        ipipath=File(pic.uploaded_file, picname)
                    )
                    picture.save()

            json_inbox = ExtJsonSerializer().serialize(
                    Inbox.objects.filter(inbcode=inbox.inbcode),
                    default=convert_data_to_serielize,
                    fields=['inbcode', 'inbtitle', 'short_title', 'to_client',
                            'inbcodeorigin', 'clicodesent', 'clicoderecieved',
                            'formatted_short_inbsenddate', 'inbox_pictures',
                            'formatted_inbsenddate', 'inbmessage', 'inbread'],
                    indent=2, use_natural_foreign_keys=True,
                    use_natural_primary_keys=True)

            response.append(json_inbox)

        for pic in pictures:
            pic.uploaded_file.close()
            pic.delete()

        context = {
            'client_recieved': client_recieved,
            'client_sender': client_sender,
            'client_img': client_sender.profile_picture,
            'inbox_title': title,
            'current_site': Site.objects.get_current(),
        }
        template = 'dateSite/email/inbox_notification.html'
        send_mail("@%s sent you a message" % client_sender, template, [],
                'Dating Latinos <noreply@datinglatinos.com>', context,
                bcc_addresses=list(
                    clients_recieved.values_list('cliemail', flat=True)))

        if inbox.clicoderecieved.clireplychannel:
            d = {
                'inbox': json_inbox,
                'error': {'type': '4'}
            }
            Channel(inbox.clicoderecieved.clireplychannel).send(
                                            {"text": json.dumps(d)})

        data = {'success': True, 'inbox': response}
        return JsonResponse(data, safe=False)


def send_inbox_manager(request):
    girl = request.POST.get('girl')
    code = int(girl)
    exits = Client.objects.filter(clicode=user_id).exists()
    if exits:
        client = Client.objects.get(clicode=user_id)
        if client.cliactive:
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user_id,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug(
                        "Manager with code %s is trying toget"
                        "inbox from girl %s", (user_id, girl))
                    error = ("You don't have permission to get this"
                             "kind of information")
                    return JsonResponse({
                            'error': True, 'description': error},
                            safe=False)
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information"
                                 "isn't active")
                        return JsonResponse({
                                'error': True, 'description': error},
                                safe=False)
            else:
                log.debug(
                    "Trying to get inbox and not is a"
                    "manager %s.", user_id)
                error = "You can't get information"
                return JsonResponse({
                        'error': True, 'description': error}, safe=False)
        else:
            log.debug(
                "Trying to get inbox with inactive user code %s.", user_id)
            error = "You aren't active"
            return JsonResponse({
                    'error': True, 'description': error}, safe=False)
    else:
        log.debug("Trying to get inbox with user code %s.", user_id)
        error = 'You are not a user'
        return JsonResponse({'error': True, 'description': error},
                            safe=False)


def ajax_clients(request):
    user = request.user
    min_age = request.POST.get('min_age',None)
    max_age = request.POST.get('max_age',None)
    ids = request.POST.get('ids',None)
    if not user.is_authenticated: #viene de la pagina publica
        tcl_code = [ClientTypeE['our_client'].value]

        if request.POST.get('gencode'):
            gen_code = request.POST.get('gencode')
            gender = Gender.objects.get(gencode=gen_code)
            gen_code = gender.genpreference
        else:
            gen_code = 2

        result=[]
        all_members = Client.list_client(tcl_code, gen_code, min_age,
                      max_age, ids=ids)
        if (len(all_members)>18):
            show_more = 1
        else:
            show_more = 0
        members = randomize(all_members,18)
    elif Client.objects.filter(clicode=user.pk).exists(): #es un cliente
        country = request.POST.get('country',None)

        client = Client.objects.get(clicode=user.pk)
        gen_code = client.gencode.genpreference

        if (client.tclcode.tclcode == ClientTypeE['our_client'].value):
            tcl_code = [ClientTypeE['client'].value]
        else:
            tcl_code = [ClientTypeE['client'].value,
                        ClientTypeE['our_client'].value]

        all_members = Client.list_client(tcl_code, gen_code, min_age,
                      max_age, country, ids=ids)
        if (len(all_members)>18):
            show_more = 1
        else:
            show_more = 0
        members = randomize(all_members,18)
    else: #es un usuario
        country = request.POST.get('country')

        json_gender = json.loads(user.last_name)
        gender = Gender.objects.get(gencode=json_gender['gen'])
        gen_code = gender.genpreference

        tcl_code = [ClientTypeE['client'].value,
                    ClientTypeE['our_client'].value]

        all_members = Client.list_client(tcl_code, gen_code, min_age, max_age,
                      country, ids=ids)
        if (len(all_members)>18):
            show_more = 1
        else:
            show_more = 0
        members = randomize(all_members,18)

    result=[members]
    result=[show_more]
    json_members = ExtJsonSerializer().serialize(members,
                    default=convert_data_to_serielize,
                    fields=['pk', 'cliusername', 'cliname', 'age',
                    'clidescription', 'cliverified', 'clibirthdate', 'citcode',
                    'marcode', 'educode', 'feecode', 'heicode',
                    'weicode', 'ocucode', 'ethcode', 'profile_picture',
                    'client_gallery'],
                    indent=2,
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True)

    return JsonResponse({'members':json_members,'show_more': show_more}, safe=False)


def randomize(all_members, qty = 18):
    new_members = []
    if all_members:
        members = []
        for m in all_members:
            members.append(m.clicode)

        while(len(new_members)<qty and len(members)>0):
            ran = random.choice(members)
            new_members.append(Client.objects.get(clicode=ran))
            members.remove(ran)

    return new_members

"""
def ajax_room(request):
    # Look up the room from the channel session, bailing if it doesn't exist
    reciever = int(request.POST.get("reciever"))
    sender = request.user.pk

    if request.user.pk != int(request.POST.get("sender")):
        # Verificamos que entonces sea un manager
        sender = int(request.POST.get("sender"))
        cli_sen = Client.objects.get(clicode=request.user.pk)
        if cli_sen.tclcode.tclcode == ClientTypeE['manager'].value:
            act_for_manager = ManagerClient.objects.filter(
                clicodemanager=request.user.pk,
                clicodegirl=sender).exists()
            if act_for_manager is False:
                log.debug("Manager with code %s is trying to get conversation "
                          "of girl %s", (message.user.pk, data['clicodesent']))
                return

    if sender < reciever:
        client1 = sender
        client2 = reciever
    else:
        client1 = reciever
        client2 = sender

    data = {}
    rooms = Room.objects.filter(
        clicode1=client1,
        clicode2=client2).order_by(
        "-roocode")
    if rooms:
        canti = 0
        i = 0
        newMessages = {}
        for room in rooms:
            # Marcamos que todos los mensajes fueron leidos
            upt = room.messages_room.filter(
                clicoderecieved=sender,
                mesread=False).update(
                mesread=True)
            messages = room.messages_room.order_by('-mescode')[:50]
            canti = canti + len(messages)
            for msg in messages:
                newMessages[i] = msg.as_dict()
                i = i + 1
            if canti >= 50:
                break

        resultMessage = {}
        for i in range(len(newMessages)):
            j = len(newMessages) - (i + 1)
            resultMessage[i] = newMessages[j]

        data["mensajes"] = resultMessage

    clientFilter = Client.objects.get(clicode=reciever).as_dict()
    data["cliente"] = clientFilter

    return HttpResponse(json.dumps(data), content_type='application/json')
"""

def ajax_room(request):
    # Look up the room from the channel session, bailing if it doesn't exist
    sender = int(request.POST.get("sender"))
    reciever = int(request.POST.get("reciever"))

    data = {}
    messages = get_chat_messages(sender, reciever)
    newMessages = []
    for msg in messages:
        newMessages.append(msg.as_dict())
    print(newMessages)

    data["mensajes"] = newMessages
    data["success"] = True
    return JsonResponse(data, safe=False)



def get_chat_messages(client1, client2):
    rooms = Room.objects.filter(clicode1__in=[client1, client2],
                                clicode2__in=[client1, client2]).order_by(
                                    "-roocode")
    # Marcamos que todos los mensajes fueron leidos
    messages = Message.objects.filter(roocode__in=rooms)
    upt = messages.update(mesread=True)
    messages = messages.order_by('-mescode')[:50]

    return messages



def leave_conversation(request):
    if request.user.pk == int(request.POST.get("sender")):
        # Look up the room from the channel session,biling if it doesn't exist
        if request.user.pk < int(request.POST.get("reciever")):
            client1 = request.user.pk
            client2 = request.POST.get("reciever")
        else:
            client1 = request.POST.get("reciever")
            client2 = request.user.pk

        data = {}
        rooms = Room.objects.filter(
            clicode1=client1,
            clicode2=client2).order_by(
            'roocode').last()
        cli_sen = Client.objects.get(clicode=request.POST.get("sender"))
        if rooms:
            if rooms.roostartdatetime:
                if client1 == request.user.pk:
                    endclient = rooms.rooendclient1
                    enddatetime = rooms.rooendc1datetime
                    rooms.rooendclient1 = True
                else:
                    endclient = rooms.rooendclient2
                    enddatetime = rooms.rooendc2datetime
                    rooms.rooendclient2 = True
                    rooms.save()
            data["error"] = "ok"
        else:
            data["error"] = "Conversation not found"
    else:
        data["error"] = "Problems with your log"
    return HttpResponse(json.dumps(data), content_type='application/json')


def ajax_notifications(request):
    user = request.user
    girl = request.POST.get('girl')
    error = ""
    notifications = []

    exits = Client.objects.filter(clicode=user.pk).exists()
    if exits:
        client = Client.objects.get(clicode=user.pk)
        if client.cliactive:
            if client.tclcode.tclcode == ClientTypeE['manager'].value:
                act_for_manager = ManagerClient.objects.filter(
                    clicodemanager=user.pk,
                    clicodegirl=int(girl)).exists()
                if act_for_manager is False:
                    log.debug("Manager with code %s is trying to get "
                              "notification with girl %s",
                              (user.pk, girl))
                    error = ("You don't have permission to get this kind "
                             "of information")
                else:
                    client = Client.objects.get(clicode=int(girl))
                    if client.cliactive is False:
                        error = ("Client that you want to get information "
                                 "isn't active")
        else:
            error = "You aren't active"
    else:
        log.debug("Trying to get complet info of cliente code %s.", user.pk)
        error = 'Not results to show'

    if error == "":
        i = 0
        exists = Notification.objects.filter(
            clicoderecieved=int(girl),
            notread=False).exists()
        if exists:
            noti = Notification.objects.filter(
                clicoderecieved=int(girl),
                notread=False)
            for n in noti:
                noti_detail = {}
                if n.ntycode.ntyactive:
                    noti_detail['notdescription'] = "@%s %s" % (
                        n.clicodesent.cliusername,
                        n.ntycode.ntydescription
                    )
                    noti_detail['notpicture'] = n.clicodesent.profile_picture
                    noti_detail['notdate'] = n.notdate
                    notifications.append(noti_detail)
                    i = i + 1
                    if i > 4:
                        break
        return JsonResponse(notifications, safe=False)
    else:
        return JsonResponse({'error': error}, safe=False)


def ajax_create_album(request):
    album_type = request.POST.get('album_type')

    client = Client.objects.get(clicode=request.user.pk)
    if (PhotoAlbum.objects.filter(clicode=client, phatype=1, phaactive=True).count()
            and album_type == "1"):
        return JsonResponse({
            'error': True,
            'message': "You can't create more than 1 public album."},
                            safe=False)
    else:
        response = add_new_album(request, album_type)
        return JsonResponse(response, safe=False)


def ajax_change_album_name(request):
    album_id = request.POST.get('album_id')
    new_name = request.POST.get('new_name')

    try:
        album = PhotoAlbum.objects.filter(
            phacode=album_id).update(phaname=new_name)
    except Exception as e:
        return JsonResponse({'success': False,
                             'error_message': 'The new album name is too long.'
                                              'Please, enter a short name'},
                            safe=False)

    return JsonResponse({'success': True}, safe=False)


def ajax_save_uploadedpicture(request):
    picture = request.POST.get('picture')
    pic = UploadedFile.objects.get(uploaded_file__icontains=picture)
    client = Client.objects.get(clicode=request.user.pk)

    client_albums = PhotoAlbum.objects.filter(clicode=client)
    client_pictures = Picture.objects.filter(phacode__in=client_albums)
    public_album = client_albums.filter(phaactive=True, phatype=1)
    json_pic = None

    if public_album:
        album_pics = client_pictures.filter(phacode=public_album,
                                            picactive=True)
        if album_pics.count() >= 10:
            json_pic = {
                'success': False,
                'error_message': 'Your public album exceeded the images allowed.',
            }
            return JsonResponse(json_pic, safe=False)
        else:
            client_pictures.update(picprofile=False)
            filename = "%s/%s" % (
                public_album.first().phacode,
                new_picture_name('photo', pic.original_filename))
            picture_obj = Picture(
                picactive=True,
                picprofile=True,
                picpath=File(pic.uploaded_file, filename),
                phacode=public_album.first()
            )
            picture_obj.save()
    else:
        album = PhotoAlbum()
        album.phaname = 'My album'
        album.phaactive = True
        album.phacreationdate = datetime.now().isoformat()
        album.phatype = 1
        album.clicode = client
        album.save()

        try:
            old_profile = client_pictures.get(picprofile=True)
            old_profile.phacode = album
            old_profile.picactive = True
            old_profile.picprofile = False
            old_profile.save()
        except:
            pass
        picname = new_picture_name('photo', pic.original_filename)
        album_folder = '%s%s/' % (get_user_folder(client), album.phacode)
        if not os.path.exists(album_folder):
            os.makedirs(album_folder)
        filename = "%s/%s" % (album.phacode, picname)
        picture_obj = Picture(
            picactive=True,
            picprofile=True,
            picpath=File(pic.uploaded_file, filename),
            phacode=album
        )
        picture_obj.save()

    pic.uploaded_file.close()
    pic.delete()

    json_pic = {
        'success': True,
        'piccode': picture_obj.piccode,
        'picpath': picture_obj.picpath.url,
        'picdescription': picture_obj.picdescription,
        'phacode': picture_obj.phacode.phacode,
        'albums': get_client_albums(client)
    }

    return JsonResponse(json_pic, safe=False)


def ajax_delete_uploadedpicture(request):
    picture = request.POST.get('picture')
    pic = UploadedFile.objects.get(uploaded_file__icontains=picture)
    pic.uploaded_file.close()
    pic.delete()

    return JsonResponse({'success': True}, safe=False)


def purch_album(request, album_added):
    from django.db.models import Q
    from datetime import date
    client = None
    try:
        client = Client.objects.get(clicode=request.user.pk)
    except Client.DoesNotExist:
        error_message = {'success': False,
                         'message': 'Please, Confirm your e-mail address to '
                         'activate your account.'}
        return json.dumps(error_message)

    premium_member = Purchase.objects.filter(
                        clicode=request.user.pk,
                        purdateend__gte=date.today().isoformat()).order_by(
                        '-purcode')

    print(premium_member)
    if premium_member:
        album = PhotoAlbum.objects.get(phacode=album_added)
        member_album = Client.objects.get(clicode=album.clicode_id)
        collection = ClientCollectionAlbum(clicode=client, phacode=album)
        collection.save()

        data = {
            "success": True,
            "album_added": get_client_albums(client, album_added)
        }
        return json.dumps(data)

    return json.dumps({'success': False})


def add_new_album(request, album_type):
    client = Client.objects.get(clicode=request.user.pk)
    album_name = request.POST.get('album_name')
    album_type = request.POST.get('album_type')
    form_id = request.POST.get('form_id')

    album = PhotoAlbum()
    album_names = PhotoAlbum.objects.filter(clicode=client.clicode,
        phaactive=True).values_list('phaname', flat=True)

    if not album_name:
        album_name = datetime.now().date().isoformat()

    # Don't repeat album name
    if album_name.lower() in album_names:
        count = 0
        while count < len(album_names):
            new_name = "%s %s" % (album_name, (count + 2))
            if new_name.lower() not in album_names:
                album_name = new_name
                break
            count = count + 1

    album.phaname = album_name
    album.phaactive = True
    album.phacreationdate = datetime.now().isoformat()
    album.phatype = album_type
    album.clicode = client
    album.save()

    temp_files = UploadedFile.objects.filter(form_id=form_id)

    from .base_helper import MyGaussianBlur
    from PIL import Image, ImageOps
    import io
    from django.core.files.uploadedfile import InMemoryUploadedFile
    for pic in temp_files:
        picname = new_picture_name('photo', pic.original_filename)
        filename = "%s/%s" % (album.phacode, picname)

        # Crear los thumbs y guadar la img con menor resolucion
        image = Image.open(pic.uploaded_file)
        image_io = io.BytesIO()
        try:
            image.save(image_io, format='JPEG', quality=60, optimize=True)
            image_file = InMemoryUploadedFile(
                                    image_io, None, picname, 'image/jpeg',
                                    image_io.getbuffer().nbytes, None)
            picture = Picture(picpath=File(image_file, filename),
                              picactive=True, picprofile=False, phacode=album)
            picture.save()

            if album.phatype == "2":
                size = (150, 150)
                thumb_io = io.BytesIO()
                thumb = ImageOps.fit(image, size, Image.ANTIALIAS)
                thumb.convert("L") # Change image mode
                thumb = thumb.filter(MyGaussianBlur(radius=15))
                thumb.save(thumb_io, format='JPEG')
                thumb_file = InMemoryUploadedFile(
                                thumb_io, None, picname, 'image/jpeg',
                                 thumb_io.getbuffer().nbytes, None)
                picture.picthumb = File(thumb_file, filename)
                picture.save()
            pic.uploaded_file.close()
            pic.delete()
        except:
            error_message = {
                'error': True,
                'message': 'Error to upload "%s". The Image is not in '
                         'the correct format' % pic.original_filename }
            album.phaactive = False
            pic.uploaded_file.close()
            pic.delete()
            return error_message

        data = {
            'message': 'success',
            'created_album': album.phacode,
            'albums': get_client_albums(client)
        }

        return json.dumps(data)
