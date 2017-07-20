import uuid
from django.db import models
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from .service import SubService
from .chat import Room
from .client import Client
from django.db.models import IntegerField, Sum

class Purchase(models.Model):
    CARD_TYPE = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
    )
    purcode = models.BigAutoField(primary_key=True)
    puridsuscription = models.CharField(max_length=100, unique=True)
    purcredit = models.SmallIntegerField(blank=True, null=True)
    purdate = models.DateTimeField(blank=True, null=True)
    purstatus = models.BooleanField('Active', default=False)
    purbalance = models.SmallIntegerField(blank=True, null=True)
    purobservation = models.CharField(max_length=40, blank=True, null=True)
    purfname = models.CharField(max_length=20, blank=True, null=True)
    purlname = models.CharField(max_length=30, blank=True, null=True)
    puremail = models.CharField(max_length=40, blank=True, null=True)
    puraddress1 = models.CharField(max_length=40, blank=True, null=True)
    purcity = models.CharField(max_length=30, blank=True, null=True)
    purcountry = models.CharField(max_length=30, blank=True, null=True)
    purzipcode = models.CharField(max_length=10, blank=True, null=True)
    purprice = models.FloatField('Unit price', blank=True, null=True)
    purcardtype = models.CharField(max_length=10, choices=CARD_TYPE, blank=True, null=True)
    purccbillreferer = models.CharField(max_length=30, blank=True, null=True)
    purapprovalid = models.BigIntegerField('Approval id',blank=True, null=True)
    purdenialid = models.BigIntegerField('Denial id',blank=True, null=True)
    purreasondecline = models.CharField(max_length=50, blank=True, null=True)
    purreasondeclinecode = models.CharField(max_length=16, blank=True, null=True)
    purdatestart = models.DateField(blank=True, null=True)
    purdateend = models.DateField(blank=True, null=True)
    clicode = models.ForeignKey(Client, models.DO_NOTHING, db_column='clicode',
                                related_name='purchase_client')

    def __str__(self):
        return self.puridsuscription

    def getIdSuscription(client):
        purchase = Purchase.objects.filter(clicode=client.clicode,
                   purstatus=False, purapprovalid__isnull=True,
                   purreasondeclinecode__isnull=True)
        if not purchase:
            idsuscription = '%s_%s' % (client.clicode, uuid.uuid4())
            finid=False
            while finid == False:
                existe = Purchase.objects.filter(puridsuscription=idsuscription
                         ).exists()
                if existe:
                    idsuscription = '%s_%s' % (client.clicode, uuid.uuid4())
                else:
                    finid = True
            Purchase.objects.create(clicode=client, purstatus=False,
                                    puridsuscription=idsuscription)
        else:
            idsuscription = purchase[0].puridsuscription
        return idsuscription

    class Meta:
        managed = True
        db_table = 'purchase'
