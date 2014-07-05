from django.core.management.base import BaseCommand, CommandError,NoArgsCommand
from campaigns.models import Newsletter, NewsletterSchedulation, NewsletterTarget, NewsletterAttachment
from contacts.models import  Contact
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

    def convert_timedelta2(duration):
        print duration
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds


    def send_plain_email(self,receiver,txt,subject):
        from django.conf import settings
        print settings.EMAIL_HOST_PASSWORD
        header = 'To:' + receiver + '\n' + 'From: ' +settings.EMAIL_FROM + '\n' + 'Subject: '+subject+'\n'
        msg = header + smart_str(txt)
        s = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT,'enervit.com')
        s.set_debuglevel(1)
        s.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
        s.sendmail(settings.EMAIL_FROM,receiver,msg)

    def sendmassive(self,newsletter):
	counter = 0 
        targets = NewsletterTarget.objects.all().filter(newsletter=newsletter)
	print "TARGETS: "+str(len(targets))
        for target in targets:
            to = (target.contact.email,)
            subject = newsletter.subject
            object = """
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
            object += smart_str(newsletter.content)
            object += """
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
            if target.contact.email.find("@")!=-1:
                contact = Contact.objects.all().filter(email=target.contact.email)[0]
            if contact:
		print "Sending to: "+contact.email
		counter = counter +1
                object = smart_str(object).replace("[[NOME]]", smart_str(contact.name.capitalize()))
                object = smart_str(object).replace("[[COGNOME]]",smart_str(contact.surname.capitalize()))
                object = smart_str(object).replace("[[EMAIL]]",smart_str(contact.email.lower()))
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = settings.EMAIL_FROM
                part1 = MIMEText(object,'html')
                msg.attach(part1)
                attachments = NewsletterAttachment.objects.all().filter(newsletter=newsletter)
                if attachments:
                    i = 0
                    while i < len(attachments):
                        path = "/var/www/yellowpage/media/"+str(attachments[i].file)
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
                        attach.add_header('Content-Disposition', 'attachment', filename=str(path).replace("/var/www/yellowpage/media/attachments/", ""))
                        msg.attach(attach)
                        i += 1
                s = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT,'enervit.com') #SMTP_SSL
                s.set_debuglevel(0)
                s.login(settings.EMAIL_HOST_USER,settings.EMAIL_HOST_PASSWORD)
                s.sendmail(settings.EMAIL_FROM,to,msg.as_string())
	print counter


    def handle_noargs(self, **options):
        schedulations = NewsletterSchedulation.objects.all().filter(status = "W")
        print schedulations
        italy = pytz.timezone("Europe/Rome")
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
        for task in schedulations:
             self.sendmassive(task.newsletter)
	     task_time = task.send_date.astimezone(italy)
             self.stdout.write("%s" % now.strftime("%d-%m-%Y %H:%M"))
             self.stdout.write("%s" % task_time.strftime("%d-%m-%Y %H:%M"))
             '''
	     if now > task_time:
                self.stdout.write('Task futuro')
                duration = now - task_time
                if duration.seconds == 3000:
                    self.send_plain_email(task.report_email,self.NEXT_NEWSLETTER.replace("XXXX",task.newsletter.name),self.NEXT_NEWSLETTER_SUBJECT)
                elif duration.seconds < 60:
                    task.newsletter.status = "S"
                    task.newsletter.save()
                    self.send_plain_email(task.report_email,self.START_NEWSLETTER.replace("XXXX",task.newsletter.name),self.START_NEWSLETTER_SUBJECT)
                    self.sendmassive(task.newsletter)
                    self.send_plain_email(task.report_email,self.END_NEWSLETTER.replace("XXXX",task.newsletter.name),self.END_NEWSLETTER_SUBJECT)
                    task.newsletter.status = "F"
                    task.newsletter.save()
                task.newsletter.status = "S"
                task.newsletter.save()
                task.status = "S"
                task.save()
                time.sleep(10)
                self.send_plain_email(task.report_email,self.START_NEWSLETTER.replace("XXXX",task.newsletter.name),self.START_NEWSLETTER_SUBJECT)
                self.sendmassive(task.newsletter)
                self.send_plain_email(task.report_email,self.END_NEWSLETTER.replace("XXXX",task.newsletter.name),self.END_NEWSLETTER_SUBJECT)
                time.sleep(10)
                task.newsletter.status = "F"
                task.newsletter.save()
                task.status = "F"
                task.save()
             
             elif now < task_time:
                self.stdout.write('Task scaduto')
             else:
                self.stdout.write('Da spedire adesso!!!')
	     '''
        self.stdout.write('Invio massivo terminato')


