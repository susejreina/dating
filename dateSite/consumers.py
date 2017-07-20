import io
import os
import json
import logging
from django.db.models import Q
from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http, channel_session_user
from .models.chat import Room, Message
from .models.client import Client

log = logging.getLogger(__name__)

@channel_session_user_from_http
def ws_connect(message):
    client = Client.objects.filter(clicode=message.user.pk)
    if client:
        update = client.update(clireplychannel=message.reply_channel)
    else:
        log.debug("Don't found the user with id %s", message.user.pk)
    return


@channel_session_user
def ws_receive(message):
    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return

    if set(data.keys()) != set(
            ('clicodesent', 'clicoderecieved', 'mescontent', 'type')):
        log.debug("ws message unexpected format data=%s", data)
        return
    # Verificamos si el cliente tiene creditos para enviar mensajes
    cli_sen = Client.objects.get(clicode=data['clicodesent'])
    cli_rec = Client.objects.get(clicode=data['clicoderecieved'])
    tipo = data["type"]
    del data["type"]
    data['clicodesent'], data['clicoderecieved'] = cli_sen, cli_rec

    if tipo == "mensaje":
        room = Room.get_room(clicode1=cli_sen, clicode2=cli_rec,
                             clicodesent=cli_sen)
        if room.roostartdatetime is None:
            startconversation = Message.objects.filter(
                                roocode=room.roocode,
                                clicoderecieved=cli_sen.clicode)
            if startconversation:
                room.set_startdatetime()
                room.set_enddatetime(both=True, clicode=1)
        else:  # Si ya comenzó la conversación
            room.set_enddatetime(False, clicode=cli_sen.clicode)
        content = Message.set_message(data["mescontent"])
        if content != data["mescontent"]:
            data["mescontentoriginal"] = data["mescontent"]
            data["mescontent"] = content
        m = room.messages_room.create(**data).as_dict()
        # Obtenemos el cliente que recibe como diccionario
        r, s = cli_rec.as_dict(), cli_sen.as_dict()
        d = {}
        d["clienterec"], d["clientesen"], d["mensaje"] = r, s, m
        room.send_message_room(d)
    elif tipo == "sticker":
        room = Room.get_room(clicode1=cli_sen, clicode2=cli_rec,
                             clicodesent=cli_sen)
        m = room.messages_room.create(**data).as_dict()
        # Obtenemos el cliente que recibe como diccionario
        # Obtenemos el cliente que recibe como diccionario
        r, s = cli_rec.as_dict(), cli_sen.as_dict()
        d = {}
        d["clienterec"], d["clientesen"], d["mensaje"] = r, s, m
        room.send_message_room(d)

@channel_session
def ws_disconnect(message):
    pass


def send_message(room, client_rec, client_sen, data, message):
    pass


@channel_session_user_from_http
def alerts(message):
    pass
