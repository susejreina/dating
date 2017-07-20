from django.contrib import admin
from .models.client import Client, PetClient, HobbieClient, SportClient
from .models.testimonial import Testimonial
from .models.catalog import (Country, City, Gender, Marital, Frequency,
                             Children, BodyType, Religion, Zodiac, Occupation,
                             Income, Weight, Height, Ethnicity, Education,
                             Language)
from .models.notification import Notification, NotificationType
from .models.inbox import Inbox
from .models.chat import Room, Message


@admin.register(Testimonial)
class AdminTestimonial(admin.ModelAdmin):
    list_display = ('tesname', 'tescomment', 'tespicture',
                    'tesactive', 'testype', 'tesdate')
    list_filter = ('testype',)


@admin.register(Country)
class AdminCountry(admin.ModelAdmin):
    list_display = ('couname', 'couactive')
    search_fields = ('couname',)


@admin.register(City)
class AdminCity(admin.ModelAdmin):
    list_display = ('coucode',)


@admin.register(Gender)
class AdminGender(admin.ModelAdmin):
    list_display = ('gendescription',)


@admin.register(Client)
class AdminClient(admin.ModelAdmin):
    list_display = ('cliusername', 'cliemail', 'cliactive',)
    list_filter = ('gencode',)
    search_fields = ('cliusername', 'cliname', 'cliemail',)


@admin.register(Marital)
class AdminMaritalStatus(admin.ModelAdmin):
    list_display = ('marname', 'maractive',)
    list_filter = ('marcode',)


@admin.register(Notification)
class AdminNotification(admin.ModelAdmin):
    list_display = ('notdate', 'clicodesent', 'clicoderecieved',)
    list_filter = ('notdate', 'clicoderecieved')


@admin.register(NotificationType)
class AdminNotificationType(admin.ModelAdmin):
    list_display = ('ntyname', 'ntydescription', 'ntyactive',)
    list_filter = ('ntyname', )


@admin.register(Inbox)
class AdminInboxClient(admin.ModelAdmin):
    list_display = ('inbtitle', 'inbmessage', 'inbsenddate', 'inbreadate',
                    'clicodesent', 'clicoderecieved', 'lancode')
    search_fields = ('inbtitle', 'inbmessage', 'inbsenddate', 'inbreadate',
                    'clicodesent', 'clicoderecieved',)

@admin.register(BodyType)
class AdminBodyType(admin.ModelAdmin):
    list_display = ('bodname', 'bodactive',)
    list_filter = ('bodactive',)


@admin.register(Ethnicity)
class AdminEthnicity(admin.ModelAdmin):
    list_display = ('ethname', 'ethactive',)
    list_filter = ('ethactive',)


@admin.register(Education)
class AdminEducation(admin.ModelAdmin):
    list_display = ('edudescription', 'eduactive',)
    list_filter = ('eduactive',)


@admin.register(Children)
class AdminChildren(admin.ModelAdmin):
    list_display = ('chiname', 'chiactive',)
    list_filter = ('chiactive',)


@admin.register(Frequency)
class AdminFrequency(admin.ModelAdmin):
    list_display = ('frename', 'freactive',)
    list_filter = ('freactive',)


@admin.register(Height)
class AdminHeight(admin.ModelAdmin):
    list_display = ('heicode', 'heidescription',)
    search_fields = ('heidescription',)


@admin.register(Weight)
class AdminWeight(admin.ModelAdmin):
    list_display = ('weicode', 'weidescription',)
    search_fields = ('weidescription',)


@admin.register(Language)
class AdminLanguage(admin.ModelAdmin):
    list_display = ('lanname',)


@admin.register(Occupation)
class AdminOccupation(admin.ModelAdmin):
    list_display = ('ocudescription', 'ocuactive',)
    list_filter = ('ocuactive',)
    search_fields = ('ocudescription',)


@admin.register(Religion)
class AdminReligion(admin.ModelAdmin):
    list_display = ('relname', 'relactive',)
    list_filter = ('relactive',)


@admin.register(Zodiac)
class AdminZodiac(admin.ModelAdmin):
    list_display = ('zodname', 'zodactive',)
    list_filter = ('zodactive',)


@admin.register(Income)
class AdminIncome(admin.ModelAdmin):
    list_display = ('incmin', 'incmax',)


@admin.register(Room)
class AdminRoom(admin.ModelAdmin):
    list_display = ('roostartdatetime', 'clicode1', 'clicode2',)
    search_fields =  ('roostartdatetime', 'clicode1', 'clicode2',)


@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    list_display = ('mescontent', 'mescontentoriginal', 'mesdatetime',
                    'clicodesent', 'clicoderecieved', 'roocode')
    search_fields =  ('mescontent', 'mescontentoriginal', 'mesdatetime',
                    'clicodesent', 'clicoderecieved', 'roocode')
