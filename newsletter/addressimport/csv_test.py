import csv
myfile = open("contacts_google.csv", "rb")
myreader = csv.reader(myfile)
firstrow = myreader.next()

# Find name column
colnum = 0
for column in firstrow:
    if 'naam' in column.lower() or 'name' in column.lower():
        namecol = colnum

        if 'display' in column.lower() or 'weergave' in column.lower():
            break

    colnum += 1
assert namecol is not None, 'Name column not found.'
print 'Name column found \'%s\'' % firstrow[namecol]

# Find email column
colnum = 0
for column in firstrow:
    if 'email' in column.lower() or 'e-mail' in column.lower():
        mailcol = colnum

        break

    colnum += 1
assert mailcol is not None, 'E-mail column not found.'
print 'E-mail column found \'%s\'' % firstrow[mailcol]

assert namecol != mailcol, 'Name and e-mail column should not be the same.'

print
print 'Extracting data...'
for row in myreader:
    print '----'
    print 'Name:', row[namecol]
    print 'Email:', row[mailcol]
