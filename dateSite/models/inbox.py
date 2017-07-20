from django.db import models
import datetime
from django.utils import timezone
from .catalog import Language
from .client import Client, get_user_image_folder
from django.db.models import Q
from dateSite.base_helper import ExtJsonSerializer, convert_data_to_serielize


class Inbox(models.Model):
    inbcode = models.BigAutoField(primary_key=True)
    inbtitle = models.CharField(max_length=250)
    inbmessage = models.TextField()
    inbmessageoriginal = models.TextField(null=True, blank=True)
    inbsenddate = models.DateTimeField('Datetime to send inbox',
                                       default=timezone.now, db_index=True)
    inbread = models.BooleanField(default=False)
    inbreadate = models.DateTimeField('Datetime to send inbox',
                                      null=True, blank=True, db_index=True)
    inbcodeorigin = models.IntegerField(null=True, blank=True, db_index=True)
    inbactive = models.BooleanField('Active', blank=True, null=False, default=True)
    clicodesent = models.ForeignKey(Client, models.DO_NOTHING,
                                    db_column='clicodesent',
                                    related_name='inbox_clientsent')
    clicoderecieved = models.ForeignKey(Client, models.DO_NOTHING,
                                        db_column='clicoderecieved',
                                        related_name='inbox_clientrecieved')
    lancode = models.ForeignKey(Language, models.DO_NOTHING,
                                db_column='lancode', related_name='inbox_lang',
                                default=1)
    clicodemanager = models.ForeignKey(Client, models.DO_NOTHING,
                                db_column='clicodemanager', blank=True, null=True,
                                related_name='inbox_clientmanager')

    def __str__(self):
        return self.inbtitle

    def quantityNotRead(clicode):
        total = Inbox.objects.filter(
            clicoderecieved=clicode, inbread=False, inbactive=True).count()
        return total

    def set_read_inbox(inbcode):
        update = False
        inbox = Inbox.objects.get(inbcode=inbcode)
        if inbox.inbread is False:
            update = Inbox.objects.filter(
                inbcode=inbcode).update(
                inbread=True,
                inbreadate=timezone.now())
        return update

    def last_title(inbcodeorigin):
        title = None
        inbox = Inbox.objects.filter(inbcodeorigin=inbcodeorigin).last()
        if inbox:
            title = inbox.inbtitle
        else:
            inbox = Inbox.objects.get(inbcode=inbcodeorigin)
            title = inbox.inbtitle
        return title

    def last_not_read(code, qty=None):
        query_filter = Q(clicoderecieved=code) & Q(inbactive=True) & Q(inbread=False)
        # Listado de todos los correos iniciales, por eso el codeorigin en true
        if qty:
            inbox = Inbox.objects.filter(query_filter).order_by("-inbcode")[:qty]
        else:
            inbox = Inbox.objects.filter(query_filter).order_by("-inbcode")
        return inbox

    def list_client_inbox(code):
        query_filter = (Q(clicoderecieved=code) | Q(clicodesent=code)) & Q(
                       inbactive=True) & Q(inbcodeorigin__isnull=True)
        # Listado de todos los correos iniciales, por eso el codeorigin en true
        inbox = Inbox.objects.filter(query_filter).order_by("-inbcode")
        return inbox

    def get_history_inbox(inbox_code):
        query_filter = (Q(inbcode=inbox_code) | Q(inbcodeorigin=inbox_code)) & Q(
                       inbactive=True)
        inbox = Inbox.objects.filter(query_filter).order_by("inbcode")

        return inbox

    @property
    def formatted_inbsenddate(self):
        return self.inbsenddate.strftime('%b %d,%Y %I:%M %p')

    @property
    def formatted_short_inbsenddate(self):
        return self.inbsenddate.strftime('%m %d,%Y')

    @property
    def short_title(self):
        title = self.inbtitle
        if len(self.inbtitle) > 22:
            title = "%s..." % self.inbtitle[0:20]
        return title

    @property
    def from_client(self):
        return self.clicodesent

    @property
    def to_client(self):
        return self.clicoderecieved.as_dict()

    @property
    def inbox_pictures(self):
        pictures = InboxPicture.objects.filter(
                        inbcode=self.inbcode)
        picture_list = []
        for pic in pictures:
            picture_list.append(pic.ipipath.url)
        return picture_list

    class Meta:
        managed = True
        db_table = 'inbox'


class InboxPicture(models.Model):
    ipicode = models.BigAutoField(primary_key=True)
    ipipath = models.ImageField(upload_to=get_user_image_folder,
                                blank=True, null=True)
    inbcode = models.ForeignKey(Inbox, models.DO_NOTHING, db_column='inbcode',
                                related_name='inboxpicture_inbox')

    def __str__(self):
        return self.ipipath.url

    @property
    def from_client(self):
        inbox = Inbox.objects.get(inbcode=self.inbcode_id)
        client = Client.objects.get(clicode=inbox.clicodesent_id)
        return client

    def natural_key(self):
        return self.ipipath.url

    class Meta:
        managed = True
        db_table = 'inboxpicture'
