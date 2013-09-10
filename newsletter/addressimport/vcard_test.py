import vobject

myfile = open("vcards.vcf", "rb")
myvcards = vobject.readComponents(myfile)

print
print 'Extracting data...'
for myvcard in myvcards:
    print '----'
    if hasattr(myvcard, 'fn') and hasattr(myvcard, 'email'):
        print 'Name:', myvcard.fn.value
        print 'Email:', myvcard.email.value
    else:
        print 'Entry skipped because no name or email was found.'
