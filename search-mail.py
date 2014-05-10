import sys
import getpass
import imaplib
import os.path
import argh
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open('defaults.cfg'))
config.read([os.path.expanduser('~/.mailpy.cfg')])


def main(username=config.get('mailpy', 'username'),
         password=config.get('mailpy', 'password'),
         host=config.get('mailpy', 'host'),
         port=config.get('mailpy', 'port'),
         delete_messages=False,
         print_headers=True,
         from_addr=None,
         to_addr=None,
         subject=None):

    search_criteria = []
    if to_addr is not None:
        search_criteria.extend(['TO', to_addr])
    if from_addr is not None:
        search_criteria.extend(['FROM', from_addr])
    if subject is not None:
        search_criteria.extend(['SUBJECT', subject])

    if len(search_criteria) == 0:
        print >>sys.stderr, "No search criteria specified"
        sys.exit(1)

    if password == '-':
        password = getpass.getpass()

    imap = imaplib.IMAP4_SSL(host, port)
    imap.login(username, password)
    imap.select('INBOX')

    _, (uids, _) = imap.uid('SEARCH', *search_criteria)
    uids = uids.split()
    print >>sys.stderr, 'Matches %d messages' % len(uids)

    if not delete_messages and not print_headers:
        return

    for i, uid in enumerate(uids):
        if i % 10 == 0:
            print (i + 1), 'of', len(uids)
        if print_headers:
            print imap.uid('FETCH', uid, '(BODY.PEEK[HEADER])')[1][0][1].strip()
        if delete_messages:
            imap.uid('STORE', uid, '+FLAGS', '(\\Deleted)')

    if delete_messages and uids:
        imap.expunge()

if __name__ == '__main__':
    argh.dispatch_command(main)
