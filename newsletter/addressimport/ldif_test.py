import ldif

myfile = open("ldif.ldif", "rb")

class myparser(ldif.LDIFParser):
	def handle(self, dn, entry):
		print '----'
		if entry.has_key('cn') and entry.has_key('mail'):
			print 'Name:',entry['cn'][0]
			print 'Email:',entry['mail'][0]
		else:
			print 'Entry skipped because no name or email was found.'

try:
	myparser(myfile).parse()
except ValueError:
	pass
