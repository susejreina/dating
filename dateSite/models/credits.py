import json
import os.path
from django.db import models
from .client import Client, PhotoAlbum, ClientCollectionAlbum
from .purchase import Purchase
from .service import SubService

def purch_album(request, album_added):
    client = Client.objects.get(clicode=request.user.pk)
    album = PhotoAlbum.objects.get(phacode=album_added)
    member_album = Client.objects.get(clicode=album.clicode_id)

    collection = ClientCollectionAlbum.objects.filter(
        clicode=client,
        phacode=album)

    if not collection.exists():
        collection = ClientCollectionAlbum()
        collection.clicode = client
        collection.phacode = album
        collection.save()

    clisender = client.as_dict()
    clireciever = member_album.as_dict()
    data = {}
    data["clisender"] = clisender
    data["clireciever"] = clireciever
    return json.dumps(data)
