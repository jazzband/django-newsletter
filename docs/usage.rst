=====
Usage
=====
#) Start the development server::

       ./manage.py runserver

#) Navigate to ``/admin/`` and: behold!
#) Setup a newsletter and create an initial message.
#) Preview the message and create submission.
#) Queue the submission for submission.
#) Process the submission queue::

       ./manage.py submit_newsletter

#) For a proper understanding, please take a look at the :ref:`reference`.


Embed A Sign-up Form Within Any Page
^^^^^^^^^^^^^^^^^
If you want to include a sign-up form on any page of your site, similar to the code that MailChimp or other email services may provide, you simply paste the following code snippet where you want the form to appear::

  <form enctype="multipart/form-data" method="post" action="/newsletter/[SLUG-OF-NEWSLETTER]/subscribe/">
  {% csrf_token %}
  <label for="id_email_field">E-mail:</label> <input type="email" name="email_field" required="" id="id_email_field">
  <button id="id_submit" name="submit" value="Subscribe" type="submit">Subscribe</button>
  </form>
        
Replace [SLUG-OF-NEWSLETTER] with the slug of your newsletter. You do not need to add anything to views, urls, or any other file. This snippet alone should simply work. Take note that the name field is removed from this, since most people only want the user to have to enter an email address to sign up for a newsletter. If you want to include the name field, you'd add this line before the <button> line::

  <label for="id_name_field">Name:</label> <input type="text" name="name_field" maxlength="30" id="id_name_field"><span class="helptext">optional</span>

Manage subscriptions while logged in
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The newsletter list shows visible newsletters for the current site, including
those the logged-in user has not subscribed to. Select or clear their
checkboxes and submit "Update subscriptions" to save changes. Viewing the
list or leaving a choice unchanged does not create a subscription.

The individual subscribe and unsubscribe pages also wait for the user to
submit their confirmation form before changing a subscription. Confirmation
requests must use POST; opening a confirmation URL with GET only displays
the page. Anonymous subscription requests still retain a pending row when
needed for an emailed activation link.

When adding a recipient in the admin, selecting "Unsubscribed" records an
opt-out, which also prevents the generator from including that address.

Dynamically generate subscriptions
^^^^^^^^^^^^^^^^^
If you want to dynamically generate the recipients of your newsletter at the time of submitting, you can configure the ``subscription_generator_class`` in the newsletter admin.

This must be a full class name with package. It should inherit ``newsletter.models.SubscriptionGenerator`` and implement the method ``generate_subscriptions``, which takes a newsletter and returns a list of ``(name, email)``.

The generated subscriptions will be joined to existing ``Subscription`` objects (both subscribed and unsubscribed) to generate the list of recipients.

Code preparing a generated recipient can call
``newsletter.create_subscription_from_generator(email, commit=False)`` to
obtain an unsaved ``Subscription``. Without ``commit=False``, the helper keeps
its existing behavior of saving the object. Request validation uses unsaved
instances; the view saves only when a confirmation code must persist or a
subscription decision is applied. Generated recipients used for sending remain
unsaved.
