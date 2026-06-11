=====
Usage
=====
#) Start the development server:

       ./manage.py runserver

#) Navigate to ``/admin/newsletter/``:

#) Create a newsletter by clicking the ``Add`` link in the ``Newsletters`` row:
       #) Fill in the form fields
       #) Click the ``SAVE`` button

#) Create an initial message:
       #) Navigate back to ``/admin/newsletter/``
       #) Click the ``Add`` link in the ``Messages`` row
       #) Fill in the form fields
       #) To preview the message:
              #) Click the ``Save and continue editing`` button at the bottom of the form
              #) Click the ``PREVIEW`` button at the top right of the page
              #) To return to editing the message click the ``CHANGE`` button at the top right of the page
       #) When you have finished editing the message click the ``SAVE`` button

#) Create a submission::
       #) Navigate back to ``/admin/newsletter/``
       #) Click the ``Add`` link in the ``Submissions`` row
       #) Fill in the form fields
       #) Click the ``SAVE``` button when you have finished editing the submission
       #) On the ``Select submission to change`` page you will see that your new submission has ``Not sent.`` in the ``STATUS`` column

#) Queue the submission:
       #) In the ``SUBMISSION`` column click the name of the submission you wish to queue
       #) Click the ``SUBMIT`` button at the top right of the ``Change submission`` page
       #) On the ``Select submission to change`` page you will see that ``STATUS`` column has changed to ``Submitting.``

#) Process the submission queue:
       #) Use the Django ``mange.py`` command:

              ./manage.py submit_newsletter

       #) To automate this process set up a recurring task/cron job:

              https://github.com/jazzband/django-newsletter/issues/361#issuecomment-1133546779

#) Submission status:
       #) Navigate to ``/admin/newsletter/submission/``
       #) You will see that ``STATUS`` column has changed to ``Sent.`` 

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

Dynamically generate subscriptions
^^^^^^^^^^^^^^^^^
If you want to dynamically generate the recipients of your newsletter at the time of submitting, you can configure the ``subscription_generator_class`` in the newsletter admin.

This must be a full class name with package. It should inherit ``newsletter.models.SubscriptionGenerator`` and implement the method ``generate_subscriptions``, which takes a newsletter and returns a list of ``(name, email)``.

The generated subscriptions will be joined to existing ``Subscription`` objects (both subscribed and unsubscribed) to generate the list of recipients.
