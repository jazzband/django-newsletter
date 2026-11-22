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

Calling the Subscription Endpoint via JavaScript / AJAX (React, Axios, Fetch)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The action views support JSON requests and responses. You can submit either JSON or ``FormData`` from frontend frameworks (such as React, Vue, Axios, or Fetch)::

    // Using Axios with JSON payload:
    axios.post('/newsletter/[SLUG-OF-NEWSLETTER]/subscribe/', {
        email: 'subscriber@example.com',
        name: 'Optional Name'
    }, {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // if CSRF middleware is active
        }
    })
    .then(response => {
        console.log(response.data);
        // { success: true, action: 'subscribe', message: 'Activation email sent.', redirect_url: '...' }
    })
    .catch(error => {
        console.error(error.response.data);
        // { success: false, errors: { email_field: ['...'] } }
    });

Both ``email`` and ``email_field`` (as well as ``name`` and ``name_field``) are accepted as field names.
When an invalid submission is made with JSON or ``Accept: application/json``, the endpoint returns HTTP 400 Bad Request with a JSON object containing the validation errors.

Dynamically generate subscriptions
^^^^^^^^^^^^^^^^^
If you want to dynamically generate the recipients of your newsletter at the time of submitting, you can configure the ``subscription_generator_class`` in the newsletter admin.

This must be a full class name with package. It should inherit ``newsletter.models.SubscriptionGenerator`` and implement two methods:

* ``generate_subscriptions``, which takes a newsletter and returns a list of ``(name, email)``.
* ``find_subscription``, which takes a newsletter and an email and returns the ``(name, email)`` that ``generate_subscriptions`` would include for that address (compared case-insensitively), or ``None``. It is used when a visitor unsubscribes, so it should look the address up directly instead of generating the whole list.

A class that does not implement both is rejected when the newsletter is saved or used.

The generated subscriptions will be joined to existing ``Subscription`` objects (both subscribed and unsubscribed) to generate the list of recipients.
