from django.db import models

class DeniedIp(models.Model):
    dipcode = models.AutoField(primary_key=True)
    diprange = models.CharField(max_length=25)
    dipactive = models.BooleanField('Active', default=True, null=False, blank=False) 

    def __str__(self):
        return self.diprange

    class Meta:
        managed = True
        db_table = 'deniedip'
