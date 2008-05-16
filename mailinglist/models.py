import os, sha, random

from datetime import datetime

#import Image

from django.db import models
from django.db.models import permalink, signals

from django.dispatch import dispatcher

from django.template.defaultfilters import slugify
from django.template import Template, Context, loader #loader should be removed later on

#from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives, SMTPConnection

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.conf import settings

def make_activation_code():
    return sha.new(sha.new(str(random.random())).hexdigest()[:5]+str(datetime.now().microsecond)).hexdigest()

class Newsletter(models.Model):
    site = models.ManyToManyField(Site)
    
    title = models.CharField(max_length=200, verbose_name=_('newsletter title'))
    slug = models.SlugField(db_index=True,prepopulate_from=('title',),unique=True)
    
    email = models.EmailField(verbose_name=_('e-mail'), help_text=_('Sender e-mail'))
    sender = models.CharField(max_length=200, verbose_name=_('sender'), help_text=_('Sender name'))
    
    visible = models.BooleanField(default=True, verbose_name=_('visible'), db_index=True)

    # Use this to automatically filter the current site
    on_site = CurrentSiteManager()
    objects = on_site # To make stuff consistent

    def __unicode__(self):
        return self.title

    class Admin:
        list_display = ('title',)

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    #@permalink
    #def get_absolute_url(self):
    #    return ('mailinglist.views.newsletter', (),
    #            {'newsletter_slug': self.newsletter.slug })
        
    @permalink
    def subscribe_url(self):
        return ('mailinglist.views.subscribe_request', (),
                {'newsletter_slug': self.newsletter.slug })
                
    @permalink
    def unsubscribe_url(self):
        return ('mailinglist.views.unsubscribe_request', (),
                {'newsletter_slug': self.newsletter.slug })
                
    def get_sender(self):
        return u'%s <%s>' % (self.sender, self.email)
        
    def get_subscriptions(self):
        if settings.DEBUG:
            print 'Looking up subscribers for %s' % self
            print  Subscription.objects.filter(newsletter=self, activated=True, unsubscribed=False)

        return Subscription.objects.filter(newsletter=self, unsubscribed=False, activated=True)

    @classmethod
    def get_default_id(cls):
        objs = cls.objects.all()
        if objs.count() == 1:
            return objs[0].id
        else:
            return None

class EmailTemplate(models.Model):
    ACTION_CHOICES = (
        ('subscribe', _('Subscribe')),
        ('unsubscribe', _('Unsubscribe')),
        ('update', _('Update')),
        ('message', _('Message')),
    )
    
    def __unicode__(self):
        return u"%s '%s'" % (self.admin_newsletter(), self.get_action_display())

    def admin_newsletter(self):
        if not self.newsletter:
            return _('Default')
        else:
            return self.newsletter
    admin_newsletter.short_description = _('newsletter')

    @classmethod
    def get_templates(cls, action, newsletter):
        assert action in ['subscribe', 'unsubscribe', 'update', 'message'], 'Unknown action %s' % action
        try:
            myemail = cls.objects.get(action__exact=action, newsletter__id=newsletter.id)
        except EmailTemplate.DoesNotExist:
            # If no specific template exists, use the default
            myemail = cls.objects.get(action__exact=action, newsletter__isnull=True)

        if myemail.html:            
            return (Template(myemail.subject), Template(myemail.text), Template(myemail.html))
        else:
            return (Template(myemail.subject), Template(myemail.text), None)                            

    class Admin:
        list_display = ('admin_newsletter','action')
        list_display_links = ('admin_newsletter','action')
        # newsletter belongs here but we have to fix a way to do 'defaults processing' ;)
        list_filter = ('action',)
        
        save_as = True

    class Meta:
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')
        
        unique_together = ("newsletter", "action")
            
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), blank=True, null=True, db_index=True)
    
    action = models.CharField(max_length=16, choices=ACTION_CHOICES, db_index=True, radio_admin=True, verbose_name=_('action'))
    
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    
    text = models.TextField(verbose_name=_('Text'), help_text=_('Plain text e-mail message. Available objects: date, subscription, site, submission, newsletter and message.'))
    
    html = models.TextField(verbose_name=_('HTML'), help_text=_('HTML e-mail alternative.'), null=True, blank=True)


class Subscription(models.Model):
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'))

    activated = models.BooleanField(default=False, verbose_name=_('activated'),db_index=True)
    activation_code = models.CharField(verbose_name=_('activation code'), max_length=40, default=make_activation_code())
    
    subscribe_date = models.DateTimeField(verbose_name=_("subscribe date"), auto_now=True)
    unsubscribe_date = models.DateTimeField(verbose_name=_("unsubscribe date"), null=True, blank=True)

    unsubscribed = models.BooleanField(default=False, verbose_name=_('unsubscribed'), db_index=True)
    
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('name'), help_text=_('optional'))
    email = models.EmailField(verbose_name=_('e-mail'), db_index=True)
    
    ip = models.IPAddressField(_("IP address"), blank=True, null=True)

    def __unicode__(self):
        return _(u"%(name)s <%(email)s> to %(newsletter)s") % {'name':self.name, 'email':self.email, 'newsletter':self.newsletter}

    class Admin:
        list_display = ('email', 'newsletter', 'subscribe_date', 'activated', 'unsubscribed')
        list_filter = ('newsletter','activated', 'unsubscribed')

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ('email','newsletter')
    
    def get_recipient(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return self.name
        
    def send_activation_email(self, action):
        assert action in ['subscribe', 'unsubscribe', 'update'], 'Unknown action'

        (subject_template, text_template, html_template) = EmailTemplate.get_templates(action, self.newsletter)
        # TODO: HTML mail alternative        
        c = Context({'subscription' : self, 
                     'site' : Site.objects.get_current(),
                     'date' : self.subscribe_date })
        
        message = EmailMultiAlternatives(subject_template.render(c), 
                                         text_template.render(c), 
                                         from_email=self.newsletter.get_sender(), 
                                         to=[self.email])
        if html_template:
            message.attach_alternative(html_template.render(c), "text/html")
        
        message.send()

#     @permalink
#     def update_url(self):
#         return ('mailinglist.views.activate_subscription', (), {
#                 'newsletter_slug': self.newsletter.slug,
#                 'email': self.email,
#                 'action' : 'subscribe',
#                 'activation_code' : self.activation_code})
    
    @permalink
    def subscribe_activate_url(self):
        return ('mailinglist.views.activate_subscription', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'subscribe',
                 'activation_code' : self.activation_code})
    @permalink
    def unsubscribe_activate_url(self):
        return ('mailinglist.views.activate_subscription', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'unsubscribe',
                 'activation_code' : self.activation_code})

    @permalink
    def update_activate_url(self):
        return ('mailinglist.views.activate_subscription', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'update',
                 'activation_code' : self.activation_code})


    
    # Oh so dry!
#     @permalink
#     def get_absolute_url(self):
#         return ('mailinglist.views.subscribe_update', (), {
#                 'newsletter_slug': self.newsletter.slug,
#                 'subscription_id': self.id})
        
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
    sortorder =  models.PositiveIntegerField(core=True, help_text=_('Sort order determines the order in which articles are concatenated in a post.'), verbose_name=_('sort order'), db_index=True)
    
    # Article's core
    title = models.CharField(max_length=200, verbose_name=_('title'), core=True)
    text = models.TextField(core=True, verbose_name=_('text'))
    
    url = models.URLField(verbose_name=_('link'), blank=True, null=True)
    
    # Make this a foreign key for added elegance
    image = models.ImageField(upload_to='newsletter/images/%Y/%m/%d', blank=True, null=True, verbose_name=_('image'), help_text='xxx')
    thumb = models.CharField(max_length=600, verbose_name=_('thumbnail url'), editable=False, null=True, blank=True)
    
    remove = models.BooleanField(default=False, verbose_name=_('remove'))

    # Post this article is associated with
    post = models.ForeignKey('Message', edit_inline=models.TABULAR, num_in_admin=1, verbose_name=_('message')) #STACKED TABULAR    
    
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

    thumbnail.short_description = _('thumbnail')
    thumbnail.allow_tags = True

    def save(self):
        if self.remove:
            self.delete()
        else:
            super(Article, self).save()

class Message(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))

    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), default=Newsletter.get_default_id())
    
    date_create = models.DateTimeField(verbose_name=_('created'), auto_now_add=True, editable=False) 
    date_modify = models.DateTimeField(verbose_name=_('modified'), auto_now=True, editable=False) 

    def __unicode__(self):
        return _(u"%(title)s in %(newsletter)s") % {'title':self.title, 'newsletter':self.newsletter}
        
    @permalink
    def text_preview_url(self):
        return ('mailinglist.admin_views.text_preview', (self.id, ), {})

    @permalink
    def html_preview_url(self):
        return ('mailinglist.admin_views.html_preview', (self.id, ), {})
  
    class Admin:
        js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
        save_as = True
        list_display = ('title', 'newsletter', 'date_create', 'date_modify')
        list_display_links  = ('title',)
        list_filter = ('newsletter', )
        date_hierarchy = 'date_create'

        #save_on_top = True
        search_fields = ('title',)
        #fields = (('Artikelen', {'fields' : ('title',), 'classes' : 'wide extrapretty', }),)
        #Note: find some way to fix this bullcrap

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    @classmethod        
    def get_default_id(cls):
        objs = cls.objects.all().order_by('-date_create')
        if objs.count() == 0:
            return None
        else:
            return objs[0].id

class Submission(models.Model):
    class Meta:
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')
                
    class Admin:
        list_display = ('newsletter', 'message', 'publish_date', 'publish', 'admin_status_text', 'admin_status')
        list_display_links = ['message',]
        date_hierarchy = 'publish_date'
        list_filter = ('newsletter', 'publish', 'sent')
        save_as = True
    
    def admin_status(self):
        if self.prepared:
            if self.sent:
                return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', self.admin_status_text())
            else:
                if self.publish_date > datetime.now():
                    return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', self.admin_status_text())
                else:
                    return u'<img src="%s" width="12" height="12" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/submitting.gif', self.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', self.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True

    def admin_status_text(self):
        if self.prepared:
            if self.sent:
                return ugettext("Sent.")
            else:
                if self.publish_date > datetime.now():
                    return ugettext("Delayed submission.")
                else:
                    return ugettext("Submitting.")
        else:
            return ugettext("Not sent.")
    admin_status_text.short_description = 'Status'
 
    def __unicode__(self):
        print 'Newsletter', self.id, self.message.id
        return _(u"%(newsletter)s on %(publish_date)s") % {'newsletter':self.message, 'publish_date':self.publish_date}

    def submit(self):
        print _(u"Submitting %(submission)s") % {'submission':self}
        assert self.publish_date < datetime.now(), 'Something smells fishy; submission time in future.'

        self.sending = True
        self.save()

        try:
            (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', self.message.newsletter)
                                        
            conn = SMTPConnection()
    
            for subscription in self.subscriptions.filter(activated=True, unsubscribed=False):
                c = Context({'subscription' : subscription, 
                             'site' : Site.objects.get_current(),
                             'submission' : self,
                             'message' : self.message,
                             'newsletter' : self.newsletter,
                             'date' : self.publish_date })
    
                message = EmailMultiAlternatives(subject_template.render(c), 
                                                 text_template.render(c), 
                                                 from_email=self.newsletter.get_sender(), 
                                                 to=[subscription.get_recipient()], 
                                                 connection=conn)
                if html_template:
                    message.attach_alternative(html_template.render(c), "text/html")
                    
                message.send()
    
            # For some reason this is not working. Bug!?        
            #conn.close()

        except Exception, inst:
            self.sending = False
            self.save()
            raise inst
        
        self.sending = False
        self.sent = True
        self.save()

    @classmethod
    def submit_queue(cls):
        todo = cls.objects.filter(prepared=True, sent=False, sending=False, publish_date__lt=datetime.now())
        for submission in todo:
            submission.submit()
    
    @classmethod
    def from_message(cls, message):
        if settings.DEBUG:
            print 'Submission from message %s' %  message
        submission = cls()
        submission.message = message
        submission.newsletter = message.newsletter
        submission.save()
        submission.subscriptions = message.newsletter.get_subscriptions()
        return submission
   
    def save(self):
        self.newsletter = self.message.newsletter
        return super(Submission, self).save()

    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), editable=False)
    message = models.ForeignKey('Message', verbose_name=_('message'), editable=False, default=Message.get_default_id(), null=False)
    
    subscriptions = models.ManyToManyField('Subscription', help_text=_('If you select none, the system will automatically find the subscribers for you.'), blank=True, db_index=True, verbose_name=_('recipients'), filter_interface=models.HORIZONTAL)

    publish_date = models.DateTimeField(verbose_name=_('publication date'), blank=True, null=True, default=datetime.now(), db_index=True) 
    publish = models.BooleanField(default=True, verbose_name=_('publish'), help_text=_('Publish in archive.'), db_index=True)

    prepared = models.BooleanField(default=False, verbose_name=_('prepared'), db_index=True, editable=False)
    sent = models.BooleanField(default=False, verbose_name=_('sent'), db_index=True, editable=False)
    sending = models.BooleanField(default=False, verbose_name=_('sending'), db_index=True, editable=False)
