

def info():
    try:
        from django.conf import settings
        from fabsettings import PROJECT_NAME, PROJECT_SITES
        print "Running with PROJECT_ROOT {0}".format(settings.PROJECT_ROOT)
        print "Our PROJECT_NAME is {0}".format(PROJECT_NAME)
        print "We currently have the following instances:"
        for item in PROJECT_SITES:
            print " * %s \n" % item
    except:
        print "This is not a django project"
