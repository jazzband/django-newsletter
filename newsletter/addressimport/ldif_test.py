import ldif


class myparser(ldif.LDIFParser):
    def handle(self, dn, entry):
        print '----'
        if 'cn' in entry and 'mail' in entry:
            print 'Name:', entry['cn'][0]
            print 'Email:', entry['mail'][0]
        else:
            print 'Entry skipped because no name or email was found.'


try:
    myfile = open("ldif.ldif", "rb")

    myparser(myfile).parse()
except ValueError:
    pass
