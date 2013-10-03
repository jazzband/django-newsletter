from .test_web import (
    AnonymousNewsletterListTestCase, UserNewsletterListTestCase,
    SubscribeTestCase, UserSubscribeTestCase,
    InvisibleAnonymousSubscribeTestCase, InvisibleUserSubscribeTestCase,
    AnonymousSubscribeTestCase, ArchiveTestcase,
    ActivationEmailSentUrlTestCase, ActionActivatedUrlTestCase
)

from .test_mailing import (
    MailingTestCase, ArticleTestCase, CreateSubmissionTestCase,
    SubmitSubmissionTestCase, SubscriptionTestCase, HtmlEmailsTestCase,
    TextOnlyEmailsTestCase, TemplateOverridesTestCase
)

from .test_settings import SettingsTestCase
