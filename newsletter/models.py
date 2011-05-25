import os, random, logging

logger = logging.getLogger(__name__)

from datetime import datetime

from django.db import models
from django.db.models import permalink

from django.dispatch import dispatcher

from django.template.defaultfilters import slugify
from django.template import Template, Context

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.utils.hashcompat import sha_constructor

from django.core.mail import EmailMultiAlternatives

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.contrib.auth.models import User

from django.conf import settings

def make_activation_code():
    return sha_constructor(sha_constructor(str(random.random())).hexdigest()[:5]+str(datetime.now().microsecond)).hexdigest()

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
    
    text = models.TextField(verbose_name=_('Text'), help_text=_('Plain text e-mail message. Available objects: date, subscription, site, submission, newsletter, STATIC_URL, MEDIA_URL and message.'))
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
    
    subscribe_template = models.ForeignKey('EmailTemplate', default=lambda: EmailTemplate.get_default_id('subscribe'), related_name='subcribe_template', verbose_name=_('subscribe template'), limit_choices_to={'action':'subscribe'})
    unsubscribe_template = models.ForeignKey('EmailTemplate', default=lambda: EmailTemplate.get_default_id('unsubscribe'), related_name='unsubcribe_template', verbose_name=_('unsubscribe template'), limit_choices_to={'action':'unsubscribe'})
    update_template = models.ForeignKey('EmailTemplate', default=lambda: EmailTemplate.get_default_id('update'), related_name='update_template', verbose_name=_('update template'), limit_choices_to={'action':'update'})
    message_template = models.ForeignKey('EmailTemplate', default=lambda: EmailTemplate.get_default_id('message'), related_name='message_template', verbose_name=_('message template'), limit_choices_to={'action':'message'})
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')
    
    @permalink
    def get_absolute_url(self):
        return ('newsletter_detail', (),
                {'newsletter_slug': self.slug })
        
    @permalink
    def subscribe_url(self):
        return ('newsletter_subscribe_request', (),
                {'newsletter_slug': self.slug })
                
    @permalink
    def unsubscribe_url(self):
        return ('newsletter_unsubscribe_request', (),
                {'newsletter_slug': self.slug })
                
    @permalink
    def update_url(self):
        return ('newsletter_update_request', (),
                {'newsletter_slug': self.slug })
                
    def get_sender(self):
        return u'%s <%s>' % (self.sender, self.email)
        
    def get_subscriptions(self):
        logger.debug(_(u'Looking up subscribers for %s') % self)
        logger.debug(Subscription.objects.filter(newsletter=self, subscribed=True))

        return Subscription.objects.filter(newsletter=self, subscribed=True)

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
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_('user'))
    
    name_field = models.CharField(db_column='name', max_length=30, blank=True, null=True, verbose_name=_('name'), help_text=_('optional'))
    def get_name(self):
        if self.user:
            return self.user.get_full_name()
        return self.name_field
    def set_name(self, name):
        if not self.user:
            self.name_field = name
    name = property(get_name, set_name)
    
    email_field = models.EmailField(db_column='email', verbose_name=_('e-mail'), db_index=True, blank=True, null=True)
    def get_email(self):
        if self.user:
            return self.user.email
        return self.email_field
    def set_email(self, email):
        if not self.user:
            self.email_field = email
    email = property(get_email, set_email)
    
    def subscribe(self):
        logger.debug('Subscribing subscription %s.' % self)
        
        self.subscribe_date = datetime.now()
        self.subscribed = True
        self.unsubscribed = False
    
    def unsubscribe(self):
        logger.debug('Unsubscribing subscription %s.' % self)
        
        self.subscribed = False
        self.unsubscribed = True
        self.unsubscribe_date = datetime.now()
        
    def save(self, *args, **kwargs):
        assert self.user or self.email_field, _('Neither an email nor a username is set. This asks for inconsistency!')
        assert (self.user and not self.email_field) or (self.email_field and not self.user), _('If user is set, email must be null and vice versa.')
        
        # This is a lame way to find out if we have changed but using Django API internals is bad practice.
        # This is necessary to discriminate from a state where we have never been subscribed but is mostly 
        # for backward compatibility. It might be very useful to make this just one attribute 'subscribe' later.
        # In this case unsubscribed can be replaced by a method property.
        
        if self.pk:
            assert(Subscription.objects.filter(pk=self.pk).count() == 1)
            old_subscribed = Subscription.objects.get(pk=self.pk).subscribed
            old_unsubscribed = Subscription.objects.get(pk=self.pk).unsubscribed
            
            # If we are subscribed now and we used not to be so, subscribe.
            # If we user to be unsubscribed but are not so anymore, subscribe.
            if (self.subscribed and not old_subscribed) or (old_unsubscribed and not self.unsubscribed):                
                self.subscribe()
                
                assert not self.unsubscribed
                assert self.subscribed
            
            # If we are unsubcribed now and we used not to be so, unsubscribe.
            # If we used to be subscribed but are not subscribed anymore, unsubscribe.
            elif (self.unsubscribed and not old_unsubscribed) or (old_subscribed and not self.subscribed):
               self.unsubscribe()
               
               assert not self.subscribed 
               assert self.unsubscribed
        else:
            if self.subscribed:
                self.subscribe()
            elif self.unsubscribed:
                self.unsubscribe()
            
        super(Subscription, self).save(*args, **kwargs)
    
    ip = models.IPAddressField(_("IP address"), blank=True, null=True)
    
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'))
    
    create_date = models.DateTimeField(editable=False, default=datetime.now)
    
    activation_code = models.CharField(verbose_name=_('activation code'), max_length=40, default=make_activation_code)
    
    subscribed = models.BooleanField(default=False, verbose_name=_('subscribed'), db_index=True)
    subscribe_date = models.DateTimeField(verbose_name=_("subscribe date"), null=True, blank=True)
    
    # This should be a pseudo-field, I reckon.
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
        unique_together = ('user', 'email_field', 'newsletter')
    
    def get_recipient(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return u'%s' % (self.email)
        
    def send_activation_email(self, action):
        assert action in ['subscribe', 'unsubscribe', 'update'], 'Unknown action'

        (subject_template, text_template, html_template) = EmailTemplate.get_templates(action, self.newsletter)

        c = Context({'subscription' : self, 
                     'site' : Site.objects.get_current(),
                     'date' : self.subscribe_date,
                     'STATIC_URL': settings.STATIC_URL,
                     'MEDIA_URL': settings.MEDIA_URL})
        
        message = EmailMultiAlternatives(subject_template.render(c), 
                                         text_template.render(c), 
                                         from_email=self.newsletter.get_sender(), 
                                         to=[self.email])
        if html_template:
            message.attach_alternative(html_template.render(c), "text/html")
            
        message.send()
        logger.debug('Activation email sent for action \'%(action)s\' to %(subscriber)s with activation code "%(action_code)s".' % 
            {'action_code':self.activation_code,
             'action':action,
             'subscriber':self})
        
    @permalink
    def subscribe_activate_url(self):
        return ('newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'subscribe',
                 'activation_code' : self.activation_code})
    @permalink
    def unsubscribe_activate_url(self):
        return ('newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'unsubscribe',
                 'activation_code' : self.activation_code})
    
    @permalink
    def update_activate_url(self):
        return ('newsletter_update_activate', (),
                {'newsletter_slug': self.newsletter.slug,
                 'email': self.email,
                 'action' : 'update',
                 'activation_code' : self.activation_code})

def get_next_order():
    sib_order__max = Article.objects.aggregate(models.Max('sortorder'))['sortorder__max']
    if sib_order__max:
        return sib_order__max + 10
    else:
        return 10

class Article(models.Model):
    sortorder =  models.PositiveIntegerField(help_text=_('Sort order determines the order in which articles are concatenated in a post.'), verbose_name=_('sort order'), db_index=True, default=get_next_order)
    
    title = models.CharField(max_length=200, verbose_name=_('title'))
    text = models.TextField(verbose_name=_('text'))
    
    url = models.URLField(verbose_name=_('link'), blank=True, null=True, verify_exists=False)
    
    # Make this a foreign key for added elegance
    image = models.ImageField(upload_to='newsletter/images/%Y/%m/%d', blank=True, null=True, verbose_name=_('image'))
    thumb = models.CharField(max_length=600, verbose_name=_('thumbnail url'), editable=False, null=True, blank=True)

    # Post this article is associated with
    post = models.ForeignKey('Message', verbose_name=_('message'), related_name='articles') #STACKED TABULAR    
    
    class Meta:
        ordering = ('sortorder',)
        verbose_name = _('article')
        verbose_name_plural = _('articles')
            
    def __unicode__(self):
        return self.title

    def get_prev(self):
        try:
            a = Article.objects.all().order_by('-sortorder').filter(sortorder__lt=self.sortorder)[0]
            logger.debug('Found prev %d of %d.' % (a.sortorder, self.sortorder))
            return a
        except IndexError:
            logger.debug('No previous found.')
    
    def get_next(self):
        try:
            a = Article.objects.all().order_by('sortorder').filter(sortorder__gt=self.sortorder)[0]
            logger.debug('Found next %d of %d.' % (a.sortorder, self.sortorder))
            return a
        except IndexError:
            logger.debug('No previous found.')
    
    def move_up(self):
        sibling = self.get_prev()
        if sibling:
            logger.debug('Moving up. Switching %d and %d.' % (sibling.sortorder, self.sortorder))
        
            sibling.sortorder += 10
            self.sortorder -= 10
        
            sibling.save()
            self.save()
        else:
            logger.debug('Not moving up, already on top.')
        
    def move_down(self):
        sibling = self.get_next()

        if sibling:
            logger.debug('Moving down. Switching %d and %d.' % (sibling.sortorder, self.sortorder))

            sibling.sortorder -= 10
            self.sortorder += 10
        
            sibling.save()
            self.save()
        else:
            logger.debug('Not moving down, already at bottom.')
    
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
    slug = models.SlugField(verbose_name=_('slug'))
    
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), default=Newsletter.get_default_id)
    
    date_create = models.DateTimeField(verbose_name=_('created'), auto_now_add=True, editable=False) 
    date_modify = models.DateTimeField(verbose_name=_('modified'), auto_now=True, editable=False) 
    
    def __unicode__(self):
        try:
            return _(u"%(title)s in %(newsletter)s") % {'title':self.title, 'newsletter':self.newsletter}
        except Newsletter.DoesNotExist:
            logger.warn('Database inconsistency, related newsletter not found for message with id %d' % self.id)

            return "%s" % self.title

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        unique_together = ("slug", "newsletter")
        
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
        subscriptions = self.subscriptions.filter(subscribed=True)
        logger.info(ugettext(u"Submitting %(submission)s to %(count)d people") % {'submission':self, 'count':subscriptions.count()})
        assert self.publish_date < datetime.now(), 'Something smells fishy; submission time in future.'

        self.sending = True
        self.save()

        try:
            (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', self.message.newsletter)
                                        
            for subscription in subscriptions:
                c = Context({'subscription' : subscription, 
                             'site' : Site.objects.get_current(),
                             'submission' : self,
                             'message' : self.message,
                             'newsletter' : self.newsletter,
                             'date' : self.publish_date,
                             'STATIC_URL': settings.STATIC_URL,
                             'MEDIA_URL': settings.MEDIA_URL})

                message = EmailMultiAlternatives(subject_template.render(c), 
                                                 text_template.render(c), 
                                                 from_email=self.newsletter.get_sender(), 
                                                 to=[subscription.get_recipient()])
                if html_template:
                    message.attach_alternative(html_template.render(c), "text/html")
                
                try:
                    logger.debug(ugettext(u'Submitting message to: %s.' % subscription))
                    message.send()
                except Exception, e:
                    logger.error(ugettext(u'Message %(subscription)s failed with error: %(e)s') % {"subscription":subscription, "e":e})
            
            self.sent = True

        finally:
            self.sending = False
            self.save()
        
    @classmethod
    def submit_queue(cls):
        todo = cls.objects.filter(prepared=True, sent=False, sending=False, publish_date__lt=datetime.now())
        for submission in todo:
            submission.submit()
    
    @classmethod
    def from_message(cls, message):
        logger.debug(ugettext('Submission of message %s') %  message)
        submission = cls()
        submission.message = message
        submission.newsletter = message.newsletter
        submission.save()
        submission.subscriptions = message.newsletter.get_subscriptions()
        return submission
   
    def save(self):
        self.newsletter = self.message.newsletter
        return super(Submission, self).save()

    @permalink
    def get_absolute_url(self):
        return ('newsletter_archive_detail', (),
                {'newsletter_slug': self.newsletter.slug,
                 'year': self.publish_date.year,
                 'month':self.publish_date.month,
                 'day':self.publish_date.day,
                 'slug':self.message.slug })

    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), editable=False)
    message = models.ForeignKey('Message', verbose_name=_('message'), editable=True, default=Message.get_default_id, null=False)
    
    subscriptions = models.ManyToManyField('Subscription', help_text=_('If you select none, the system will automatically find the subscribers for you.'), blank=True, db_index=True, verbose_name=_('recipients'), limit_choices_to={ 'subscribed' :True })

    publish_date = models.DateTimeField(verbose_name=_('publication date'), blank=True, null=True, default=datetime.now(), db_index=True) 
    publish = models.BooleanField(default=True, verbose_name=_('publish'), help_text=_('Publish in archive.'), db_index=True)

    prepared = models.BooleanField(default=False, verbose_name=_('prepared'), db_index=True, editable=False)
    sent = models.BooleanField(default=False, verbose_name=_('sent'), db_index=True, editable=False)
    sending = models.BooleanField(default=False, verbose_name=_('sending'), db_index=True, editable=False)
