#!/usr/bin/env python

#
# Author:  Marcos Lin
# Date:    02 July 2014
#
# A fake SMTP server that will accept any authentication request but does not send any emails.
# It will simply log the user/password authentication and any output raw email message to stdout.
#

from pymta import PythonMTA
from pymta.api import IAuthenticator, IMessageDeliverer

# Authentication Class
class AuthLogger(IAuthenticator):
    def authenticate(self, username, password, peer):
        print "################################"
        print "# LOGIN: username: %s, password: %s, peer: %s" % (username, password, peer)
        print "#"
        return True

# Delivery Class
class DeliverLogger(IMessageDeliverer):
    def new_message_accepted(self, message):
        print "\n================================"
        print "| To: %s" % message.smtp_to
        print message.msg_data
        print "|"
        print "--------------------------------"


# Start the fake SMTP server
if __name__ == '__main__':
    # SMTP server will listen on localhost/port 8025
    server = PythonMTA('localhost', 8025, deliverer_class=DeliverLogger, authenticator_class=AuthLogger)

    try:
        server.serve_forever(use_multiprocessing=False)
    except KeyboardInterrupt:
        print "# Shutting down the server"
        server.shutdown_server()

