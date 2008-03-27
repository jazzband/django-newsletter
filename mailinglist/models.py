from django.db import models
from django import newforms as forms
from random import sample
from django.template.defaultfilters import slugify

import os
import Image
from django.template import Library
from django.conf import settings

## ALGEMENE GEGEVENS
class GeneralSettings(models.Model):
    domain = models.CharField(max_length=200, verbose_name='Domein')
    title = models.CharField(max_length=200, verbose_name='Nieuwsbrief titel')
    email = models.EmailField(verbose_name='E-mail', help_text='from / sender: ...@...')
    sender = models.TextField(verbose_name='Post-adres')
    edition = models.PositiveIntegerField(default=1, verbose_name='Editie')
    def __unicode__(self):
        return self.title

    class Admin:
        list_display = ('title',)

    class Meta:
        verbose_name = "Instellingen"
        verbose_name_plural = "Instellingen"


class ExSubscriber(models.Model):
    email = models.EmailField(verbose_name='E-mail')
    def __unicode__(self):
        return self.email

    class Admin:
        list_display = ('email', )
        search_fields = ['email',]

    class Meta:
        verbose_name = "Ex-abonnee"
        verbose_name_plural = "Ex-abonnees"
        
        
## ABONNEES
class Subscriber(models.Model):
    active = models.BooleanField(default=False, verbose_name='Actief')
    email = models.EmailField(verbose_name='E-mail', unique=True)
    verification_code = models.CharField(max_length=8, verbose_name="Verificatie-code", editable=False)
    def __unicode__(self):
        return self.email

    class Admin:
        list_display = ('email', 'active')
        search_fields = ['email',]

    class Meta:
        verbose_name = "Abonnee"
        verbose_name_plural = "Abonnees"

    def save(self):
        self.verification_code = ''.join(sample("abcdefghijklmnopqrstuvw0123456789", 8))
        super(Subscriber, self).save()
        # Hier moet eigenlijk nog een bevestiging, maar weet niet hoe ik http responses kan renderen vanuit models. (lijkt me niet de bedoeling)
#       Dit werkt, user wordt niet opgeslagen. Maar 'messagelist' geeft wel de melding
#           try: ExSubscriber.objects.get(email=self.email): 
#             print "User excists in ex"
#             pass
#         except ExSubscriberDoesNotExcist: 
#             print "User doesn't excist in excist"
#             super(Subscriber, self).save()
        
    def delete(self):
        ExSubscriber(email=self.email).save()
        super(Subscriber, self).delete()


## - Bestand
class File(models.Model):
    title = models.CharField(max_length=200, verbose_name='titel')
    file = models.FileField(upload_to='files', help_text="Maximaal 3 Megabyte (MB).")
    url = models.CharField(max_length=600, verbose_name='url', editable=False, null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Admin:
        list_display = ('title', 'url')
        search_fields = ['title', 'file', 'url']
        
    def get_absolute_url(self):
        return "/static/%s" %self.file

    class Meta:
        verbose_name = "Bestand"
        verbose_name_plural = "Bestanden"

    def save(self):
        general = GeneralSettings.objects.all()[0] ## .title .sender .edition .email .domain
        self.url = "%s/static/%s" %(general.domain, self.file)
        super(File,self).save()


## - Article
class Article(models.Model):
    sortorder =  models.PositiveIntegerField(core=True, help_text='Sortering bepaalt de volgorde van de artikelen.', verbose_name='Sortering')
    title = models.CharField(max_length=200, verbose_name='titel', core=True)
    text = models.TextField(core=True, verbose_name='Tekst')
    image = models.ImageField(upload_to='newsletter/images/%Y/%m/%d', blank=True, null=True, verbose_name='afbeelding', help_text='xxx')
    thumb = models.CharField(max_length=600, verbose_name='Thumbnail url', editable=False, null=True, blank=True)
    newsletter = models.ForeignKey('NewsLetter', edit_inline=models.TABULAR, num_in_admin=1, verbose_name='Nieuwsbrief') #STACKED TABULAR    
    class Meta:
        ordering = ('sortorder',)
        verbose_name = "Artiekel"
        verbose_name_plural = "Artikelen"

    def __unicode__(self):
        return self.title
        
    def thumbnail(self):
        """
        Display thumbnail-size image of ImageField named src
        Assumes images are not very large (i.e. no manipulation of the image is done on backend)
        Requires constant named MAX_THUMB_LENGTH to limit longest axis
        """
        MAX_THUMB_LENGTH = 200
        max_img_length = max(self.get_image_width(), self.get_image_height())
        ratio = max_img_length > MAX_THUMB_LENGTH and float(max_img_length) / MAX_THUMB_LENGTH or 1
        thumb_width = self.get_image_width() / ratio
        thumb_height = self.get_image_height() / ratio
        return '<img src="%s" width="%s" height="%s"/>' % (self.image, thumb_width, thumb_height)

    thumbnail.short_description = 'thumbnail'
    thumbnail.allow_tags = True


## - Nieuwsbrief - Maken
class NewsLetter(models.Model):
    work_title = models.CharField(max_length=200, verbose_name='Werktitel', help_text='Alleen als referentie, bijvoorbeeld: "Nieuwsbrief, januari 2008".', unique=True)

    def __unicode__(self):
        return self.work_title

    class Admin:
        js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
        pass
        #search_fields = ['work_title',]
        #fields = ((None, {'fields': ('work_title'), 'classes': 'wide extrapretty'}),)

    class Meta:
        verbose_name = "Nieuwsbrief - Maken"
        verbose_name_plural = "Nieuwsbrief - Maken"


## - Nieuwsbrief - Verzenden
class Send_NewsLetter(models.Model):
    class Admin:
        pass
    class Meta:
        verbose_name = "Nieuwsbrief - Verzenden"
        verbose_name_plural = "Nieuwsbrief - Verzenden"
        

## - Nieuwsbrief - Archief
class NewsLetter_Archive(models.Model):
    title =  models.CharField(max_length=200, verbose_name='Titel')
    slug =  models.SlugField(max_length=300, verbose_name='Slug', blank=True, null=True) #editable=False,
    publish = models.BooleanField(default=True, verbose_name='Publiseer in archief')
    print_run = models.PositiveIntegerField(verbose_name='Oplage', blank=True, null=True) #editable=False, 
    edition = models.PositiveIntegerField(verbose_name='Editie', blank=True, null=True) #editable=False, 
    send_date = models.DateField(verbose_name='Datum verstuurd', blank=True, null=True) #editable=False, 
    html =  models.TextField(verbose_name='HTML') #editable=False, 
    txt =  models.TextField(verbose_name='Tekst') #editable=False, 
    class Admin:
        list_display = ('title', 'publish', 'send_date', 'print_run')
        search_fields = ['html']
        #fields = ((None, {'fields': ('edition'), 'classes': 'wide extrapretty'}),)

    class Meta:
        verbose_name = "Nieuwsbrief - Archief"
        verbose_name_plural = "Nieuwsbrief - Archief"
    
    def get_absolute_url(self):
        return "/archive/%s/%s/%s/%s" % (self.send_date.year, self.send_date.month, self.send_date.day, self.slug)

    def save(self):
        self.slug = slugify(self.title)
        super(NewsLetter_Archive,self).save()
        
        
## FORMULIER, AAN- EN AFMELDEN
class SubsriberForm(forms.Form):
    subscriber_email = forms.EmailField(label='e-mail', required=True) #help_text="Wilt u onze nieuwsbrief ontvangen? Vul dan hier uw e-mailadres in!"


## FORMULIER, BEVESTIGEN
class ConfirmForm(forms.Form):
    mail = forms.EmailField(required=True)
    code = forms.CharField(required=True)


## Nieuwsbrief Preview Formulier
class NewsLetter_Preview_Form(forms.Form):
    newsletter = forms.ModelChoiceField(queryset=NewsLetter.objects.all(), label='')


## Nieuwsbrief Verzend Formulier    
class NewsLetter_Send_Form(forms.Form):
    newsletter_id = forms.CharField(required=True)