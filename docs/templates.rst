=========
Templates
=========
To get started, we recommend copying the existing 'stub'-templates from
the module directory to your project's `templates` dir::

    cp -rv `python -c 'import newsletter; from os import path; print path.dirname(newsletter.__file__)'`/templates/newsletter <project_dir>/templates/

Web view templates
^^^^^^^^^^^^^^^^^^
`newsletter_list.html`
    Newsletter list view, showing all newsletters marked as public and allowing
    authenticated Django users to (un)subscribe directly.
`newsletter_detail.html`
    Newsletter detail view, linking to subscribe, update,
    unsubscribe and archive views for a particular newsletter.
`submission_archive.html`
    Archive; list of public submissions for a particular newsletter.
`subscription_subscribe.html`
    Subscribe form for unauthenticated users.
`subscription_subscribe_email_sent.html`
    Confirmation of subscription request.
`subscription_activate.html`
    Activation form for (un)subscriptions or updates of unauthenticated users.
`subscription_subscribe_activated.html`
    Confirmation of activation of subscription.
`subscription_unsubscribe_activated.html`
    Confirmation of activation of unsubscription.
`subscription_update_activated.html`
    Confirmation of activation of update.
`subscription_subscribe_user.html`
    Subcribe form for authenticated users.
`subscription_unsubscribe.html`
    Unsubscribe form for unauthenticated users.
`subscription_unsubscribe_email_sent.html`
    Confirmation of unsubscription request.
`subscription_unsubscribe_user.html`
    Unsubscribe form for authenticated users.
`subscription_update.html`
    Update form for unauthenticated users.
`subscription_update_email_sent.html`
    Confirmation of update request.

Email templates
^^^^^^^^^^^^^^^^^
Email templates can be specified per newsletter in `message/<newsletter_slug>`.
If no newsletter-specific templates are found, the defaults in the `message`
folder are used.

When a newsletter is configured to send HTML-messages, the HTML and txt are
both used to create a multipart message. When the use of HTML is not configured
only the text templates are used.

The following templates can be defined:

`message.(html|txt)`
    Template for rendering a messages with the following context available:
        * `subscription`: Subscription containing name and email of recipient.
        * `site`: Current `site` object.
        * `submission`: Current submission.
        * `message`: Current message.
        * `newsletter`: Current newsletter.
        * `date`: Publication date of submission.
        * `STATIC_URL`: Django's `STATIC_URL` setting.
        * `MEDIA_URL`: Django's `MEDIA_URL` setting.
`message_subject.txt`
    Template for the subject of an email newsletter. Context is the same as
    with messages.
`subscribe.(html|txt)`
    Template with confirmation link for subscription.
`subscribe_subject.txt`
    Subject template with confirmation link for subscription.
`unsubscribe.(html|txt)`
    Template with confirmation link for unsubscription.
`unsubscribe_subject.txt`
    Subject template with confirmation link for unsubscription.
`update.(html|txt)`
    Template with confirmation link for updating subscriptions.unsubscription.
`update_subject.txt`
    Subject template with confirmation link for updating subscriptions.

