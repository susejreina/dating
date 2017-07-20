from enum import Enum


class GenderE(Enum):
    man = 1
    woman = 2
    gay = 3
    lesbian = 4


class ClientTypeE(Enum):
    superuser = 1
    supervisor = 2
    manager = 3
    client = 4
    our_client = 5
    franquicia = 6



class ServiceE(Enum):
    chat = 1        # Chat
    mail = 2        # Inbox
    videocam = 3    #
    photos = 4      # Albums


class SubServiceE(Enum):
    chat_message = 1        # Send/recieve chat messages
    sticker = 2             # Send sticker
    view_file = 3           # View file
    add_album = 4           # Create private album
    email = 5               # Send inbox
    mail_photo = 6          # Send inbox photos
    extra_photo = 7         # each aditional photo in email
    email_recieve = 8       # Recieve inbox
    mail_photo_recieve = 9  # Recieve photos
    view_album = 10         # View private album
