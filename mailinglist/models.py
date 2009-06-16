import os, sha, random

from datetime import datetime

#import Image

from django.db import models
from django.db.models import permalink, signals

from django.dispatch import dispatcher

from django.template.defaultfilters import slugify
from django.template import Template, Context, loader #loader should be removed later on

from django.core.validators import ValidationError

#from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives, SMTPConnection

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from django.conf import settings

def make_activation_code():
    return sha.new(sha.new(str(random.random())).hexdigest()[:5]+str(datetime.now().microsecond)).hexdigest()

def TemplateValidator(new_data, all_data):
    try:
        Template(new_data)
    except Exception, e:
        raise ValidationError(_('There was an error parsing your template: %s') % e)

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

    class Admin:
        list_display = ('title','action')
        list_display_links = ('title',)
        list_filter = ('action',)
        
        save_as = True

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

    title = models.CharField(max_length=200, verbose_name=_('name'), core=True, default=_('Default'))
    
    action = models.CharField(max_length=16, choices=ACTION_CHOICES, db_index=True, radio_admin=True, verbose_name=_('action'))
    
    subject = models.CharField(max_length=255, verbose_name=_('subject'), validator_list=[TemplateValidator,])
    
    text = models.TextField(verbose_name=_('Text'), help_text=_('Plain text e-mail message. Available objects: date, subscription, site, submission, newsletter and message.'), validator_list=[TemplateValidator,])
    
    html = models.TextField(verbose_name=_('HTML'), help_text=_('HTML e-mail alternative.'), null=True, blank=True, validator_list=[TemplateValidator,])


class Newsletter(models.Model):
    site = models.ManyToManyField(Site)
    
    title = models.CharField(max_length=200, verbose_name=_('newsletter title'))
    slug = models.SlugField(db_index=True, prepopulate_from=('title',),unique=True)
    
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

    class Admin:
        list_display = ('title', 'admin_subscriptions', 'admin_messages', 'admin_submissions')

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    def admin_messages(self):
        return '<a href="../message/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Messages'))
    admin_messages.allow_tags = True
    admin_messages.short_description = ''

    def admin_subscriptions(self):
        return '<a href="../subscription/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Subscriptions'))
    admin_subscriptions.allow_tags = True
    admin_subscriptions.short_description = ''

    def admin_submissions(self):
        return '<a href="../submission/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Submissions'))
    admin_submissions.allow_tags = True
    admin_submissions.short_description = ''

    
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
            print _(u'Looking up subscribers for %s') % self
            print  Subscription.objects.filter(newsletter=self, activated=True, unsubscribed=False)

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

    class Admin:
        list_display = ('name', 'email', 'admin_newsletter', 'subscribe_date', 'admin_unsubscribe_date', 'admin_status_text', 'admin_status')
        list_display_links = ('name', 'email')
        list_filter = ('newsletter','activated', 'unsubscribed','subscribe_date')
        search_fields = ('name', 'email')
        date_hierarchy = 'subscribe_date'

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ('email','newsletter')

    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True       

    def admin_status(self):
        if self.unsubscribed:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', self.admin_status_text())
        
        if self.activated:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', self.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', self.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True

    def admin_status_text(self):
        if self.unsubscribed:
            return ugettext("Unsubscribed")
        
        if self.activated:
            return ugettext("Activated")
        else:
            return ugettext("Unactivated")
    admin_status_text.short_description = ugettext('Status')   
    
    def admin_unsubscribe_date(self):
        if self.unsubscribe_date:
            return self.unsubscribe_date
        else:
            return ''
    admin_unsubscribe_date.short_description = unsubscribe_date.verbose_name
    
    def get_recipient(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return u'%s' % (self.email)
        
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
    post = models.ForeignKey('Message', edit_inline=models.TABULAR, num_in_admin=2, verbose_name=_('message'), related_name='articles') #STACKED TABULAR    
    
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
        list_display = ('admin_newsletter', 'title', 'admin_preview', 'date_create', 'date_modify')
        list_display_links  = ('title',)
        list_filter = ('newsletter', )
        date_hierarchy = 'date_create'

        #save_on_top = True
        search_fields = ('title',)
        #fields = (('Artikelen', {'fields' : ('title',), 'classes' : 'wide extrapretty', }),)
        #Note: find some way to fix this bullcrap

    def admin_preview(self):
        return '<a href="%s/preview/">%s</a>' % (self.id, ugettext('Preview'))
    admin_preview.short_description = ''
    admin_preview.allow_tags = True
    
    
    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True

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
                
    class Admin:
        list_display = ('admin_newsletter', 'message', 'publish_date', 'publish', 'admin_status_text', 'admin_status')
        list_display_links = ['message',]
        date_hierarchy = 'publish_date'
        list_filter = ('newsletter', 'publish', 'sent')
        save_as = True

    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True

    
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
    admin_status_text.short_description = ugettext('Status')
 
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
        if settings.DEBUG:
            print ugettext('Submission of message %s') %  message
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
    
    subscriptions = models.ManyToManyField('Subscription', help_text=_('If you select none, the system will automatically find the subscribers for you.'), blank=True, db_index=True, verbose_name=_('recipients'), filter_interface=models.HORIZONTAL, limit_choices_to={ 'activated' :True, 'unsubscribed' : False})

    publish_date = models.DateTimeField(verbose_name=_('publication date'), blank=True, null=True, default=datetime.now(), db_index=True) 
    publish = models.BooleanField(default=True, verbose_name=_('publish'), help_text=_('Publish in archive.'), db_index=True)

    prepared = models.BooleanField(default=False, verbose_name=_('prepared'), db_index=True, editable=False)
    sent = models.BooleanField(default=False, verbose_name=_('sent'), db_index=True, editable=False)
    sending = models.BooleanField(default=False, verbose_name=_('sending'), db_index=True, editable=False)
