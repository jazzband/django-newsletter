import os
import Image
from django.template import Library
from django.conf import settings

register = Library()

def thumb(file, size='200x200'):
    # defining the size
    x, y = [int(x) for x in size.split('x')]
    # defining the filename and the miniature filename
    file = str(file).replace('\\', '/') # windows fix
    basename, format = file.rsplit('.', 1)
    miniature = basename + '_t_' + size + '.' +  format
    miniature_filename = os.path.join(settings.MEDIA_ROOT, miniature)
    miniature_url = os.path.join(settings.MEDIA_URL, miniature)
    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename):
        print 'resizing %s to %s' % (basename, size)
        filename = os.path.join(settings.MEDIA_ROOT, file)
        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS) # generate a thumbnail
        if format == "jpg" or "JPG" or "jpeg" or "JPEG":
            image.save(miniature_filename, image.format, quality=100)
        else:
            image.save(miniature_filename, image.format)
    return miniature_url

register.filter(thumb)
