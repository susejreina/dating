import json
from django import template
from dateSite.models.enum import GenderE
from dateSite.models.inbox import Inbox

register = template.Library()


@register.filter(name='remaining_pics')
def remaining_pics(length, sub):
    pics = int(length) - int(sub)
    if(pics > 99):
        return 99
    return pics


@register.filter(name='endswith')
def endswith(value, endswith):
    return value.endswith(endswith)


@register.filter(name='pronoun')
def pronoun(gender):
    if gender == GenderE['man'].value or gender == GenderE['gay'].value:
        return 'he'
    if gender == GenderE['woman'].value or gender == GenderE['lesbian'].value:
        return 'she'

@register.filter(name='concat_ids')
def concat_ids(obj):
    new_string = ''
    if obj:
        for client in obj:
            new_string += str(client.clicode) + ';'
        new_string=new_string[:-1]
    else:
        new_string="0"
    return new_string


@register.filter(name='apics_string')
def album_concat_list(obj):
    pics = []
    for pic in obj:
        temp = {
            'code': str(pic.piccode),
            'path': pic.picpath.url,
            'description': ('' if not pic.picdescription else pic.picdescription)
        }
        pics.append(temp)
    return json.dumps(pics)


@register.assignment_tag(takes_context=True)
def inbox_with(context, inbox_code):
    try:
        request = context['request']
        inbox = Inbox.objects.get(inbcode=inbox_code)
        if request.user.pk == inbox.clicodesent.clicode:
            return inbox.clicoderecieved
        else:
            return inbox.clicodesent
    except Exception as e:
        return ""
