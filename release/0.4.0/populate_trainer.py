__author__ = 'dominik'
import sys
sys.path.append('/var/www/test')
from contacts.models import Contact
from campaigns.models import Event

# events with trainer field filled.
# to verify in production the ids (should be the same)
# events = Event.objects.exclude(trainer__isnull=True).exclude(trainer__exact='')

'''
under test
21 44
CIACCI MANILA

22
TRAINO

23 41
BACCOLINI FEDERICA

40
Iader Fabbri

43
CARNEVALI STEFANO

60
BARRY SEARS
'''
e21 = Event.objects.get(pk=21)
e22 = Event.objects.get(pk=22)
e23 = Event.objects.get(pk=23)
e40 = Event.objects.get(pk=40)
e41 = Event.objects.get(pk=41)
e43 = Event.objects.get(pk=43)
e44 = Event.objects.get(pk=44)
e60 = Event.objects.get(pk=60)

ciacci = Contact()
ciacci.type = 'C'
ciacci.status = 'I'
ciacci.name = 'MANILA'
ciacci.surname = 'CIACCI'
ciacci.email = ''
ciacci.code = 'CCCMNL00XX00E999'
ciacci.save()
print 'created '+str(ciacci)
e21.consultant = ciacci
e44.consultant = ciacci
e21.save()
e44.save()
print 'associated '+str(ciacci) + ' to ' + str(e21)
print 'associated '+str(ciacci) + ' to ' + str(e44)
traino = Contact()
traino.type = 'C'
traino.status = 'I'
traino.name = 'TRAINO'
traino.surname = 'TRAINO'
traino.email = ''
traino.code = 'TQRNXL00ZX00E999'
traino.save()
print 'created '+str(traino)
e22.consultant = traino
e22.save()
print 'associated '+str(traino) + ' to ' + str(e22)

baccolini = Contact()
baccolini.type = 'C'
baccolini.status = 'I'
baccolini.name = 'FEDERICA'
baccolini.surname = 'BACCOLINI'
baccolini.email = ''
baccolini.code = 'BCCFDC00XX00E999'
baccolini.save()
print 'created '+str(baccolini)
e23.consultant = baccolini
e41.consultant = baccolini
e23.save()
e41.save()
print 'associated '+str(baccolini) + ' to ' + str(e23)
print 'associated '+str(baccolini) + ' to ' + str(e41)
iader = Contact()
iader.type = 'C'
iader.status = 'I'
iader.name = 'IADER'
iader.surname = 'FABBRI'
iader.email = ''
iader.code = 'FBRIDR00XX00E999'
iader.save()
print 'created '+str(iader)
e40.consultant = iader
e40.save()
print 'associated '+str(iader) + ' to ' + str(e40)

carnevali = Contact()
carnevali.type = 'C'
carnevali.status = 'I'
carnevali.name = 'STEFANO'
carnevali.surname = 'CARNEVALI'
carnevali.email = ''
carnevali.code = 'CRVSTF00XX00E999'
carnevali.save()
print 'created '+str(carnevali)
e43.consultant = carnevali
e43.save()
print 'associated '+str(carnevali) + ' to ' + str(e43)
barry = Contact()
barry.type = 'C'
barry.status = 'I'
barry.name = 'BARRY'
barry.surname = 'SEARS'
barry.email = ''
barry.code = 'SRSBRR00XW00E001'
barry.save()
print 'created '+str(barry)
e60.consultant = barry
e60.save()
print 'associated '+str(barry) + ' to ' + str(e60)
