import json
import uuid
from PIL import ImageFilter
from datetime import datetime, date
from .models.log_session import LogSession
from .models.client import Client, Picture, PhotoAlbum
from .models.enum import ClientTypeE
from django.core.serializers.base import Serializer as BaseSerializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.json import Serializer as JsonSerializer


def get_current_client(request):
    try:
        client = Client.objects.get(clicode=request.user.pk)
        return client
    except (KeyError, Client.DoesNotExist):
        return


class ExtBaseSerializer(BaseSerializer):

    def serialize_property(self, obj):
        model = type(obj)
        for field in self.selected_fields:
            if (hasattr(model, field) and
                    type(getattr(model, field)) == property):
                self.handle_prop(obj, field)

    def handle_prop(self, obj, field):
        self._current[field] = getattr(obj, field)

    def end_object(self, obj):
        self.serialize_property(obj)

        super(ExtBaseSerializer, self).end_object(obj)


class ExtPythonSerializer(ExtBaseSerializer, PythonSerializer):
    pass


class ExtJsonSerializer(ExtPythonSerializer, JsonSerializer):
    pass


def convert_data_to_serielize(o):
    if isinstance(o, datetime) or isinstance(o, date):
        return o.__str__()
    if isinstance(o, Picture):
        return o.__str__()


# Save user log in DB. Login false is a Logout
def save_log(login, client, manager=None):
    if login:
        previous_log = LogSession.objects.filter(
            clicode=client, logsignout__isnull=True)
        if previous_log:
            previous_log = LogSession.objects.filter(
                clicode=client).latest(
                'logsignin')
            previous_log.logsignout = datetime.now().isoformat()
            previous_log.save()
        client_log = LogSession()
        client_log.clicode = client
        client_log.logsignin = datetime.now().isoformat()
        if manager:
            client_log.clicodemanager = manager
        client_log.save()
    else:
        try:
            previous_log = LogSession.objects.filter(
                clicode=client,
                logsignout__isnull=True).latest(
                'logsignin')
            previous_log.logsignout = datetime.now().isoformat()
            previous_log.save()
            client.clireplychannel = None
            client.save()
        except Exception as e:
            print(e)


def get_client_albums(current_client, album=None):
    if not album:
        albums = PhotoAlbum.objects.filter(
            phaactive=True,
            clicode=current_client.pk).order_by('phatype',
            '-phacreationdate')
    else:
        albums = PhotoAlbum.objects.filter(phacode=album)

    album_list = []
    for album in albums:
        pictures = Picture.objects.filter(picactive=True, picprofile=False,
                                          phacode=album)
        if not pictures:
            album.phaactive = False
            album.save()
        else:
            temp_album = {
                'code': album.phacode,
                'name': album.phaname,
                'type': album.phatype,
            }
            pic_array= []
            for pic in pictures:
                pics = {
                    'code': pic.piccode,
                    'thumb': None if not pic.picthumb else pic.picthumb.url,
                    'path': pic.picpath.url,
                    'description': pic.picdescription,
                }
                pic_array.append(pics)
            temp_album['pictures'] = pic_array
            album_list.append(temp_album)

    return json.dumps(album_list, default=convert_data_to_serielize)


def get_private_albums(current_client):
    priv_albums = PhotoAlbum.objects.filter(
        phaactive=True, phatype=2,
        clicode=current_client.pk).order_by('phatype',
        '-phacreationdate')

    album_list = []
    for album in priv_albums:
        pictures = Picture.objects.filter(
            picactive=True, picprofile=False,
            phacode=album)
        temp_album = {}
        temp_album['album'] = album
        temp_album['pictures'] = list(pictures)
        album_list.append(temp_album)

    return album_list


def get_user_folder(client):
    folder = "clients_pictures/%s_%s/albums/" % (
        client.clicode, client.cliusername)
    return folder


def new_picture_name(prefix, filename):
    ext = filename.split('.')[-1]
    picname = '%s_%s.%s' % (prefix, uuid.uuid4(), ext)

    return picname


def can_access(user):
    if not user.is_anonymous:
        if Client.objects.filter(clicode=user.pk).exists():
            client = Client.objects.get(clicode=user.pk)
            if client.tclcode.tclcode != ClientTypeE['client'].value:
                return False
        else:
            return True
    return True


class MyGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"

    def __init__(self, radius=2):
        self.radius = radius

    def filter(self, image):
        return image.gaussian_blur(self.radius)
