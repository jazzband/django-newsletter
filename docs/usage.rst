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
