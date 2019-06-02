import time

from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast

OFFSET = 5


@view_config(route_name='circle', renderer="json")
def circle(request):
    """Handle CircleCI events"""
    lastmessage = getlast()

    if 'reponame' not in request.params:
        logprint("No repository name in request!")
    else:
        if request.params['reponame'] == "pipsqueak3":
            if request.params['username'] == "FuelRats":
                channels = ['#mechadev']
            else:
                jsondump(request)
                return
        else:
            channels = ['#rattech']

    if request.params['compare'] is None:
        if len(request.params['all_commit_details']) > 0:
            compareurl = request.params['all_commit_details'][0]['commit_url']
        elif len(request.params['pull_requests']) > 0:
            compareurl = request.params['pull_requests'][0]['url']
        else:
            compareurl = "\x0302null\x03"
    else:
        compareurl = request.params['compare']

    message1 = ("[\x0315CircleCI\x03] \x0306" + request.params['reponame'] + "/" + request.params['reponame'] +
                "\x03#" + str(request.params['build_num']) + " (\x0306" + request.params['branch'] + "\x03 - " +
                request.params['vcs_revision'][:7] + " : \x0314" + request.params['user']['login'] +
                "\x03): " + request.params['outcome'])
    message2 = ("[\x0315CircleCI\x03] Change view: \x02\x0311" + compareurl +
                "\x02\x03 Build details: \x02\x0311" + request.params['build_url'] + "\x02\x03")
    msgshort1 = {"time": time.time(), "type": "Circle", "key": request.params['reponame'], "full": message1}
    msgshort2 = {"time": time.time(), "type": "Circle", "key": request.params['reponame'], "full": message2}
    if lastmessage['full'] == message2:
        logprint("Duplicate message, skipping:")
        logprint(message1)
        logprint(message2)
    else:
        for channel in channels:
            send(channel, message1, msgshort1)
        time.sleep(0.5)
        for channel in channels:
            send(channel, message2, msgshort2)
