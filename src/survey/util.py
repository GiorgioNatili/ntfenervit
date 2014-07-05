from email.mime.text import MIMEText
import itertools
import smtplib

import re
from django.conf import settings


def get_function(path):
    """ This used to use import_module, but certain Django-isms such as object
    models appeared to not be available with that approach. """
    parts = path.split(".")
    to_exec = "from %s import %s as got" % (".".join(parts[:-1]), parts[-1])
    try:
        exec(to_exec)
    except ImportError, error:
        raise ImportError(error.msg, to_exec)
    # return got


class ChoiceEnum(object):
    def __init__(self, choices):
        if isinstance(choices, basestring):
            choices = choices.split()
        if all([isinstance(choices, (list,tuple)),
                all(isinstance(x, tuple) and len(x) == 2 for x in choices)]):
            values = choices
        else:
            values = zip(itertools.count(1), choices)
        for v, n in values:
            name = re.sub('[- ]', '_', n.upper())
            setattr(self, name, v)
            if isinstance(v, str):
                setattr(self, v.upper(), v)
        self._choices = values

    def __getitem__(self, idx):
        return self._choices[idx]

    def getdisplay(self, key):
        return [v[1] for v in self._choices if v[0] == key][0]



def _get_remote_ip(request):
    forwarded=request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[-1].strip()
    return request.META['REMOTE_ADDR']


def send_single_email(email_to_notify, subject, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = settings.EMAIL_FROM
    # print settings.EMAIL_HOST+settings.EMAIL_FROM
    s = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, 'enervit.com')
    s.set_debuglevel(1)
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(settings.EMAIL_FROM, email_to_notify, msg.as_string())