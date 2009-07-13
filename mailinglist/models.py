import os, sha, random, logging

from datetime import datetime

from django.db import models
from django.db.models import permalink

from django.dispatch import dispatcher

from django.template.defaultfilters import slugify
from django.template import Template, Context

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives, SMTPConnection

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.conf import settings

def make_activation_code():
    return sha.new(sha.new(str(random.random())).hexdigest()[:5]+str(datetime.now().microsecond)).hexdigest()

def get_default_sites():
    return [site.id for site in Site.objects.all()]

class EmailTemplate(models.Model):
    ACTION_CHOICES = (
        ('subscribe', _('Subscribe')),
        ('unsubscribe', _('Unsubscribe')),
        ('update', _('Update')),
        ('message', _('Message')),
    )
    
    def __unicode__(self):
        return u"%s '%s'" % (self.get_action_display(), self.title)

    @classmethod
    def get_templates(cls, action, newsletter):
        assert action in ['subscribe', 'unsubscribe', 'update', 'message'], 'Unknown action %s' % action

        myemail =  eval('newsletter.%s_template' % action)
        
        if myemail.html:            
            return (Template(myemail.subject), Template(myemail.text), Template(myemail.html))
        else:
            return (Template(myemail.subject), Template(myemail.text), None)                            

    class Meta:
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')
        
        unique_together = ("title", "action")
    
    @classmethod
    def get_default_id(cls, action):
        try:
            ls = EmailTemplate.objects.filter(action__exact = action)
            if ls.count() == 1:
                return ls[0].id
            else:
                ls = ls.filter(title__exact = _('Default'))
                if ls.count():
                    #There can be only one of these
                    return ls[0].id
        except:
            pass
        
        return None

    title = models.CharField(max_length=200, verbose_name=_('name'), default=_('Default'))    
    action = models.CharField(max_length=16, choices=ACTION_CHOICES, db_index=True, verbose_name=_('action'))
    
    subject = models.CharField(max_length=255, verbose_name=_('subject'))
    
    text = models.TextField(verbose_name=_('Text'), help_text=_('Plain text e-mail message. Available objects: date, subscription, site, submission, newsletter and message.'))
    html = models.TextField(verbose_name=_('HTML'), help_text=_('HTML e-mail alternative.'), null=True, blank=True)


class Newsletter(models.Model):
    site = models.ManyToManyField(Site, default=get_default_sites)
    
    title = models.CharField(max_length=200, verbose_name=_('newsletter title'))
    slug = models.SlugField(db_index=True, unique=True)
    
    email = models.EmailField(verbose_name=_('e-mail'), help_text=_('Sender e-mail'))
    sender = models.CharField(max_length=200, verbose_name=_('sender'), help_text=_('Sender name'))
    
    visible = models.BooleanField(default=True, verbose_name=_('visible'), db_index=True)

    # Use this to automatically filter the current site
    on_site = CurrentSiteManager()
    objects = on_site # To make stuff consistent
    
    subscribe_template = models.ForeignKey('EmailTemplate', default=EmailTemplate.get_default_id('subscribe'), related_name='subcribe_template', verbose_name=_('subscribe template'), limit_choices_to={'action':'subscribe'})
    unsubscribe_template = models.ForeignKey('EmailTemplate', default=EmailTemplate.get_default_id('unsubscribe'), related_name='unsubcribe_template', verbose_name=_('unsubscribe template'), limit_choices_to={'action':'unsubscribe'})
    update_template = models.ForeignKey('EmailTemplate', default=EmailTemplate.get_default_id('update'), related_name='update_template', verbose_name=_('update template'), limit_choices_to={'action':'update'})
    message_template = models.ForeignKey('EmailTemplate', default=EmailTemplate.get_default_id('message'), related_name='message_template', verbose_name=_('message template'), limit_choices_to={'action':'message'})
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')
    
    @permalink
    def get_absolute_url(self):
        return ('mailinglist_newsletter_detail', (),
                {'newsletter_slug': self.newsletter.slug })
        
    @permalink
    def subscribe_url(self):
        return ('mailinglist_newsletter_subscribe_request', (),
                {'newsletter_slug': self.newsletter.slug })
                
    @permalink
    def unsubscribe_url(self):
        return ('mailinglist_newsletter_unsubscribe_request', (),
                {'newsletter_slug': self.newsletter.slug })
                
    @permalink
    def update_url(self):
        return ('mailinglist_newsletter_update_request', (),
                {'newsletter_slug': self.newsletter.slug })
                
    def get_sender(self):
        return u'%s <%s>' % (self.sender, self.email)
        
    def get_subscriptions(self):
        logging.debug(_(u'Looking up subscribers for %s') % self)
        logging.debug(Subscription.objects.filter(newsletter=self, activated=True, unsubscribed=False))

        return Subscription.objects.filter(newsletter=self, unsubscribed=False, activated=True)

    @classmethod
    def get_default_id(cls):
        try:
            objs = cls.objects.all()
            if objs.count() == 1:
                return objs[0].id
        except:
            pass
        return None

class Subscription(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('name'), help_text=_('optional'))
    email = models.EmailField(verbose_name=_('e-mail'), db_index=True)

    ip = models.IPAddressField(_("IP address"), blank=True, null=True)

    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'))

    subscribe_date = models.DateTimeField(verbose_name=_("subscribe date"), auto_now=True)

    activation_code = models.CharField(verbose_name=_('activation code'), max_length=40, default=make_activation_code())
    activated = models.BooleanField(default=False, verbose_name=_('activated'),db_index=True)
    
    unsubscribed = models.BooleanField(default=False, verbose_name=_('unsubscribed'), db_index=True)
    unsubscribe_date = models.DateTimeField(verbose_name=_("unsubscribe date"), null=True, blank=True)
    
    def __unicode__(self):
        if self.name:
            return _(u"%(name)s <%(email)s> to %(newsletter)s") % {'name':self.name, 'email':self.email, 'newsletter':self.newsletter}
        else:
            return _(u"%(email)s to %(newsletter)s") % {'email':self.email, 'newsletter':self.newsletter}

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ('email','newsletter')
    
    def get_recipient(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return u'%s' % (self.email)
        
    def send_activation_email(self, action):
        assert action in ['subscribe', 'unsubscribe', 'update'], 'Unknown action'

        (subject_template, text_template, html_template) = EmailTemplate.get_templates(action, self.newsletter)

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
        logging.debug('Activation email sent for action \'%(action)s\' to %(subscriber)s with activation code "%(action_code)s".' % 
            {'action_code':self.activation_code,
             'action':action,
             'subscriber':self})
        
    @permalink
    def subscribe_activate_url(self):
        return ('mailinglist_newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'subscribe',
                 'activation_code' : self.activation_code})
    @permalink
    def unsubscribe_activate_url(self):
        return ('mailinglist_newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'unsubscribe',
                 'activation_code' : self.activation_code})
    
    @permalink
    def update_activate_url(self):
        return ('mailinglist_newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'update',
                 'activation_code' : self.activation_code})

class Article(models.Model):
    sortorder =  models.PositiveIntegerField(help_text=_('Sort order determines the order in which articles are concatenated in a post.'), verbose_name=_('sort order'), db_index=True)
    
    title = models.CharField(max_length=200, verbose_name=_('title'))
    text = models.TextField(verbose_name=_('text'))
    
    url = models.URLField(verbose_name=_('link'), blank=True, null=True, verify_exists=False)
    
    # Make this a foreign key for added elegance
    image = models.ImageField(upload_to='newsletter/images/%Y/%m/%d', blank=True, null=True, verbose_name=_('image'), help_text='xxx')
    thumb = models.CharField(max_length=600, verbose_name=_('thumbnail url'), editable=False, null=True, blank=True)

    # Post this article is associated with
    post = models.ForeignKey('Message', verbose_name=_('message'), related_name='articles') #STACKED TABULAR    
    
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

class Message(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), default=Newsletter.get_default_id())
    
    date_create = models.DateTimeField(verbose_name=_('created'), auto_now_add=True, editable=False) 
    date_modify = models.DateTimeField(verbose_name=_('modified'), auto_now=True, editable=False) 
    
    def __unicode__(self):
        return _(u"%(title)s in %(newsletter)s") % {'title':self.title, 'newsletter':self.newsletter}
        
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        
    @classmethod        
    def get_default_id(cls):
        try:
            objs = cls.objects.all().order_by('-date_create')
            if not objs.count() == 0:
                return objs[0].id
        except:
            pass
        
        return None

class Submission(models.Model):
    class Meta:
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')
 
    def __unicode__(self):
        return _(u"%(newsletter)s on %(publish_date)s") % {'newsletter':self.message, 'publish_date':self.publish_date}

    def submit(self):
        subscriptions = self.subscriptions.filter(activated=True, unsubscribed=False)
        print ugettext("Submitting %(submission)s to %(count)d people") % {'submission':self, 'count':subscriptions.count()}
        assert self.publish_date < datetime.now(), 'Something smells fishy; submission time in future.'

        self.sending = True
        self.save()

        try:
            (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', self.message.newsletter)
                                        
            conn = SMTPConnection()
    
            for subscription in subscriptions:
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
                
                try:
                    print ugettext('  - %s.' % subscription)
                    message.send()
                except Exception, e:
                    print ugettext('Message %s failed with error: %s' % (subscription, e[0]))
    
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
        logging.debug(ugettext('Submission of message %s') %  message)
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
    message = models.ForeignKey('Message', verbose_name=_('message'), editable=True, default=Message.get_default_id(), null=False)
    
    subscriptions = models.ManyToManyField('Subscription', help_text=_('If you select none, the system will automatically find the subscribers for you.'), blank=True, db_index=True, verbose_name=_('recipients'), limit_choices_to={ 'activated' :True, 'unsubscribed' : False})

    publish_date = models.DateTimeField(verbose_name=_('publication date'), blank=True, null=True, default=datetime.now(), db_index=True) 
    publish = models.BooleanField(default=True, verbose_name=_('publish'), help_text=_('Publish in archive.'), db_index=True)

    prepared = models.BooleanField(default=False, verbose_name=_('prepared'), db_index=True, editable=False)
    sent = models.BooleanField(default=False, verbose_name=_('sent'), db_index=True, editable=False)
    sending = models.BooleanField(default=False, verbose_name=_('sending'), db_index=True, editable=False)
