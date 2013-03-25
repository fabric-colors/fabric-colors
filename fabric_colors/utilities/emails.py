from fabric.api import env


def email_on_success(target, trigger):
    if trigger:
        # dynamic import for the right target's settings
        import_string = "from {0}.settings.{1} import *".\
                format(env.project_name, target)
        exec import_string

        # Execute email
        from django.core.mail import EmailMessage, BadHeaderError
        from django.core import mail
        from django.conf import settings
        subject = 'Deployed to {0}'.format(target)
        message = 'Deployed to {0}'.format(target)
        from_address = settings.DEFAULT_FROM_EMAIL
        admin_emails = [a[1] for a in settings.ADMINS]
        em = EmailMessage(subject, message, from_address, admin_emails)

        try:
            mail_connection = mail.get_connection()
            mail_connection.send_messages([em])
            print("Deployment notification sent to {0}".format(str(admin_emails)[1:-1]))
        except BadHeaderError, e:
            print e
            print("Invalid header found.")
    else:
        print("No email triggered")
