import os
import boto3
from django.template.loader import render_to_string


def send_mail(subject, template, send_to, send_from, context, bcc_addresses=[]):
    html_content = render_to_string(template, context)
    client = boto3.client(
             'ses', region_name='us-east-1',
             aws_access_key_id=os.environ.get('SES_ACCESS_KEY_ID', 'AKIAIGYKIBHKQT27J7XQ'),
             aws_secret_access_key=os.environ.get('SES_SECRET_ACCESS_KEY', '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'))

    response = client.send_email(
        Destination={
            'ToAddresses': send_to,
            'BccAddresses' : bcc_addresses,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': html_content,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=send_from,
    )
