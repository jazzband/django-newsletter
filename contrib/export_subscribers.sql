-- Export a list of currently active subscribers and subscription dates
-- Tested to work with MySQL
SELECT
    IFNULL(newsletter_subscription.name, CONCAT_WS(' ', auth_user.first_name, auth_user.last_name)) AS name,
    IFNULL(newsletter_subscription.email, auth_user.email) AS email,
    subscribe_date
FROM newsletter_subscription
LEFT JOIN auth_user
  ON newsletter_subscription.user_id = auth_user.id
WHERE
    subscribed = 1 AND
    unsubscribed = 0

