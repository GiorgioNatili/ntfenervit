from django.core.management.base import NoArgsCommand
from campaigns.models import NewsletterSchedulation, NewsletterTarget, NewsletterAttachment, SCHEDULATION_STATUS
from contacts.models import Contact
import datetime
from django.utils import timezone
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
import time


def send_plain_email(receiver, txt, subject):
    from django.conf import settings

    header = 'To:' + receiver + '\n' + 'From: ' + settings.EMAIL_FROM + '\n' + 'Subject: ' + subject + '\n'
    msg = header + smart_str(txt)
    s = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, 'enervit.com')
    s.set_debuglevel(1)
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(settings.EMAIL_FROM, receiver, msg)


def sendmassive(newsletter):
    counter = 0
    targets = NewsletterTarget.objects.all().filter(newsletter=newsletter)
    for target in targets:
        to = (target.contact.email,)
        subject = newsletter.subject
        email_obj = """
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
                <html>
                <head>
                  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                  <title>Enervit</title>

                  <style>
                    @media only screen and (min-device-width: 541px) {
                      .content {
                        width: 540px !important;
                      }
                    }
                  </style>
                </head>
                <body style="background-color: #dcdcdc;">
                <!--[if (gte mso 9)|(IE)]>
                      <table width="540" align="center" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td>
                <![endif]-->

                <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 540px;">
                  <tr>
                    <td>
                """
        email_obj += smart_str(newsletter.content)
        email_obj += """
                         </td>
                      </tr>
                    </table>

            <!--[if (gte mso 9)|(IE)]>
                  </td>
                </tr>
            </table>
            <![endif]-->

            </body>
            </html>
            """

        contact = None
        if target.contact.email.find("@") != -1:
            contact = Contact.objects.all().filter(email=target.contact.email)[0]
        if contact:
            counter += 1
            email_obj = smart_str(email_obj).replace("[[NOME]]", smart_str(contact.name.capitalize()))
            email_obj = smart_str(email_obj).replace("[[COGNOME]]", smart_str(contact.surname.capitalize()))
            email_obj = smart_str(email_obj).replace("[[EMAIL]]", smart_str(contact.email.lower()))
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_FROM
            part1 = MIMEText(email_obj, 'html')
            msg.attach(part1)
            attachments = NewsletterAttachment.objects.all().filter(newsletter=newsletter)
            if attachments:
                i = 0
                while i < len(attachments):
                    path = "/var/www/yellowpage/media/" + str(attachments[i].file)
                    ctype, encoding = mimetypes.guess_type(path)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    if maintype == 'text':
                        fp = open(path)
                        attach = MIMEText(fp.read(), _subtype=subtype)
                        fp.close()
                    elif maintype == 'image':
                        fp = open(path, 'rb')
                        attach = MIMEImage(fp.read(), _subtype=subtype)
                        fp.close()
                    elif maintype == 'audio':
                        fp = open(path, 'rb')
                        attach = MIMEAudio(fp.read(), _subtype=subtype)
                        fp.close()
                    else:
                        fp = open(path, 'rb')
                        attach = MIMEBase(maintype, subtype)
                        attach.set_payload(fp.read())
                        fp.close()
                        encoders.encode_base64(attach)
                    attach.add_header('Content-Disposition', 'attachment',
                                      filename=str(path).replace("/var/www/yellowpage/media/attachments/", ""))
                    msg.attach(attach)
                    i += 1
            s = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, 'enervit.com')  # SMTP_SSL
            s.set_debuglevel(0)
            s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            s.sendmail(settings.EMAIL_FROM, to, msg.as_string())
    print counter


class Command(NoArgsCommand):
    help = "Invio massivo newsletter"

    NEXT_NEWSLETTER = """
    La newsletter \"XXXX\" verra' inviata tra 5 minuti.\n\n
    """
    NEXT_NEWSLETTER_SUBJECT = "[NTF] Newsletter in partenza"

    START_NEWSLETTER = """
     Invio in corso della Newsletter \"XXXX\" \n\n
    """
    START_NEWSLETTER_SUBJECT = "[NTF] Invio in corso newsletter"

    END_NEWSLETTER = """
         Invio terminato della Newsletter \"XXXX\" \n\n
    """
    END_NEWSLETTER_SUBJECT = "[NTF] Invio terminato newsletter"

    def handle_noargs(self, **options):
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        schedulations = NewsletterSchedulation.objects.all().filter(status="W", send_date__lte=now)
        print schedulations
        italy = pytz.timezone("Europe/Rome")
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        for task in schedulations:
            task_time = task.send_date.astimezone(italy)
            diff = now - task_time
            if diff > datetime.timedelta(0):
                send_plain_email(task.report_email, self.START_NEWSLETTER.replace("XXXX", task.newsletter.name), self.START_NEWSLETTER_SUBJECT)
                task.status = 'S'
                task.newsletter.status = 'S'
                task.newsletter.save()
                task.save()
                sendmassive(task.newsletter)
                send_plain_email(task.report_email, self.END_NEWSLETTER.replace("XXXX", task.newsletter.name), self.END_NEWSLETTER_SUBJECT)
                task.status = 'F'
                task.newsletter.status = 'F'
                task.newsletter.save()
                task.save()



