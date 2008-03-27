import os, sha, random

from datetime import datetime

#import Image

from django.db import models
from django.template.defaultfilters import slugify
from django.template import Library
from django.utils.translation import ugettext_lazy as _

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.conf import settings

def make_activation_code():
    return sha.new(sha.new(str(random.random())).hexdigest()[:5]+str(datetime.now().microsecond)).hexdigest()

class Newsletter(models.Model):
    site = models.ManyToManyField('sites.Site')
    
    title = models.CharField(max_length=200, verbose_name=_('newsletter title'))
    slug = models.SlugField(db_index=True,prepopulate_from=('title',),unique=True)
    
    email = models.EmailField(verbose_name=_('e-mail'), help_text=_('Sender e-mail'))
    sender = models.CharField(max_length=200, verbose_name=_('sender'), help_text=_('Sender name'))
    
    visible = models.BooleanField(default=True, verbose_name=_('visible'))

    # Use this to automatically filter the current site
    on_site = CurrentSiteManager()

    def __unicode__(self):
        return self.title

    class Admin:
        list_display = ('title',)

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

class Subscription(models.Model):
    newsletter = models.ForeignKey('Newsletter')

    activated = models.BooleanField(default=False, verbose_name=_('activated'))
    activation_code = models.CharField(verbose_name=_('activation code'), max_length=40, default=make_activation_code())
    
    subscribe_date = models.DateTimeField(verbose_name=_("subscribe date"), auto_now_add=True)
    unsubscribe_date = models.DateTimeField(verbose_name=_("unsubscribe date"), null=True, blank=True)

    unsubscribed = models.BooleanField(default=False, verbose_name=_('unsubscribed'))
    
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('name'), help_text=_('optional'))
    email = models.EmailField(verbose_name=_('e-mail'), db_index=True)

    def __unicode__(self):
        return "%s, %s" % (self.email, self.newsletter)

    class Admin:
        list_display = ('email', 'newsletter', 'subscribe_date')

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        
## - Bestand
# class File(models.Model):
#     title = models.CharField(max_length=200, verbose_name=_('title'))
#     file = models.FileField(upload_to='files', help_text=_('Maximal size is 3 Megabytes (MB).'))
#     url = models.CharField(max_length=600, verbose_name=_('url'), editable=False, null=True, blank=True)
# 
#     def __unicode__(self):
#         return self.title
# 
#     class Admin:
#         list_display = ('title', 'url')
#         search_fields = ['title', 'file', 'url']
#         
#     def get_absolute_url(self):
#         return "/static/%s" %self.file
# 
#     class Meta:
#         verbose_name = _('file')
#         verbose_name_plural = _('files')
# 
#     def save(self):
#         settings = Newsletter.objects.all()[0] ## .title .sender .edition .email .domain
#         self.url = "%s/static/%s" %(general.site, self.file)
#         super(File,self).save()


class Article(models.Model):
    sortorder =  models.PositiveIntegerField(core=True, help_text=_('Sort order determines the order in which articles are concatenated in a post.'), verbose_name=_('sort order'))
    
    # Article's core
    title = models.CharField(max_length=200, verbose_name=_('title'), core=True)
    text = models.TextField(core=True, verbose_name=_('text'))
    
    url = models.URLField(verbose_name=_('link'), blank=True, null=True)
    
    # Make this a foreign key for added elegance
    image = models.ImageField(upload_to='newsletter/images/%Y/%m/%d', blank=True, null=True, verbose_name='afbeelding', help_text='xxx')
    thumb = models.CharField(max_length=600, verbose_name='Thumbnail url', editable=False, null=True, blank=True)
    
    # Post this article is associated with
    post = models.ForeignKey('Publication', edit_inline=models.TABULAR, num_in_admin=1, verbose_name='Nieuwsbrief') #STACKED TABULAR    
    
    class Meta:
        ordering = ('sortorder',)
        verbose_name = _('article')
        verbose_name_plural = _('articles')

    def __unicode__(self):
        return self.title
    
    # This belongs elsewhere
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

class Publication(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))

    newsletter = models.ForeignKey('Newsletter')

    def __unicode__(self):
        return self.title

    class Admin:
        js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
        #search_fields = ['work_title',]
        #fields = ((None, {'fields': ('work_title'), 'classes': 'wide extrapretty'}),)

    class Meta:
        verbose_name = _('publication')
        verbose_name_plural = _('publications')

class Mailing(models.Model):
    class Meta:
        verbose_name = _('mailing')
        verbose_name_plural = _('mailings')
        
    class Admin:
        list_display = ('newsletter', 'publication', 'publish_date', 'publish', 'sent')
        
    newsletter = models.ForeignKey('Newsletter')
    
    publication = models.ForeignKey('Publication')
    
    subscriptions = models.ManyToManyField('Subscription')

    publish_date = models.DateField(verbose_name=_('publication date'), blank=True, null=True) 
    publish = models.BooleanField(default=True, verbose_name=_('publish'), help_text=_('Publish in archive.'))

    sent = models.BooleanField(default=False, verbose_name=_('sent'))

    def save(self):
        self.newsletter = self.publication.newsletter
        super(Mailing, self).save()
        
