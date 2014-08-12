__author__ = 'dominik'

from contacts.models import Contact
from campaigns.models import Event

# events with trainer field filled.
# to verify in production the ids (should be the same)
# events = Event.objects.exclude(trainer__isnull=True).exclude(trainer__exact='')
e21 = Event.objects.get(pk=21)
e23 = Event.objects.get(pk=23)
e40 = Event.objects.get(pk=40)
e41 = Event.objects.get(pk=41)
e43 = Event.objects.get(pk=43)
e44 = Event.objects.get(pk=44)

ciacci = Contact()
ciacci.type = 'C'
ciacci.status = 'I'
ciacci.name = 'MANILA'
ciacci.surname = 'CIACCI'
ciacci.email = ''
ciacci.code = 'CCCMNL00XX00E999V'
ciacci.save()

e21.consultant = ciacci
e44.consultant = ciacci
e21.save()
e44.save()

baccolini = Contact()
baccolini.type = 'C'
baccolini.status = 'I'
baccolini.name = 'FEDERICA'
baccolini.surname = 'BACCOLINI'
baccolini.email = ''
baccolini.code = 'BCCFDC00XX00E999Y'
baccolini.save()

e23.consultant = baccolini
e41.consultant = baccolini
e23.save()
e41.save()

iader = Contact()
iader.type = 'C'
iader.status = 'I'
iader.name = 'IADER'
iader.surname = 'FABBRI'
iader.email = ''
iader.code = 'FBRIDR00XX00E999Z'
iader.save()

e40.consultant = iader
e40.save()

carnevali = Contact()
carnevali.type = 'C'
carnevali.status = 'I'
carnevali.name = 'STEFANO'
carnevali.surname = 'CARNEVALI'
carnevali.email = ''
carnevali.code = 'CRVSTF00XX00E999A'
carnevali.save()

e43.consultant = carnevali
e43.save()