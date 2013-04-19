import urllib
import urllib2

from fabric.api import task, env, run
from fabric.context_managers import prefix
from fabric.operations import get
from fabric.colors import red, green

from fabric_colors.environment import set_target_env


@task(default=True)
@set_target_env
def newrelic():
    """
    Check if newrelic is sending data to rpm.newrelic.com's data collector
    """
    if env.newrelic:
        print(green("newrelic is expected to be running on this host"))
        with prefix(env.activate):
            run("newrelic-admin validate-config {0}/{1}".format(env.path_release_current, env.newrelic['INI_FILE']))
            get("/tmp/python-agent-test.log", "{0}_data/{1}/%(path)s".format(env.project_name, env.host, env))
    else:
        print(red("We are not deploying newrelic on this host"))


@task
@set_target_env
def record_deploy():
    """
    values is a dictionary containing key and value.
    Equivalent of this example (please use the correct API key of course)
    curl -H "x-api-key:f55da53a178959f9130381396b2172ac5e26cfa2383503c" \
            -d "deployment[application_id]=2142298" \
            -d "deployment[host]=localhost" \
            -d "deployment[description]=This deployment was sent using curl" \
            -d "deployment[revision]=1242" \
            -d "deployment[changelog]=many hands make light work" \
            -d "deployment[user]=Calvin Cheng"  \
            https://rpm.newrelic.com/deployments.xml
    """
    if env.newrelic:
        url = "https://rpm.newrelic.com/deployments.xml"
        data = urllib.urlencode(env.newrelic['VALUES'])

        # Send the HTTP Post, with custom header x-api-key
        req = urllib2.Request(url, data)
        req.add_header('x-api-key', env.newrelic['API_KEY'])
        urllib2.urlopen(req)
    else:
        print(red("We are not deploying newrelic on this host"))
