from django.db import models
from dateSite.models.catalog import Gender


class QuickSubscription(models.Model):
    gender = models.ForeignKey(Gender, models.DO_NOTHING,
                                db_column='gencode', blank=False,
                                null=False,
                                default=1,
                                related_name='quickSubs_gender')

    class Meta:
        managed = False
