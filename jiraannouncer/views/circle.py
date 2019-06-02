import time

from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast

OFFSET = 5


@view_config(route_name='circle', renderer="json")
def circle(request):
    """Handle CircleCI events"""
    lastmessage = getlast()

    if request['reponame'] == "pipsqueak3":
        if request['username'] == "FuelRats":
            channels = ['#mechadev']
        else:
            jsondump(request)
            return
    else:
        channels = ['#rattech']

    if request['compare'] is None:
        if len(request['all_commit_details']) > 0:
            compareurl = request['all_commit_details'][0]['commit_url']
        elif len(request['pull_requests']) > 0:
            compareurl = request['pull_requests'][0]['url']
        else:
            compareurl = "\x0302null\x03"
    else:
        compareurl = request['compare']

    message1 = ("[\x0315CircleCI\x03] \x0306" + request['reponame'] + "/" + request['reponame'] +
                "\x03#" + str(request['build_num']) + " (\x0306" + request['branch'] + "\x03 - " +
                request['vcs_revision'][:7] + " : \x0314" + request['user']['login'] +
                "\x03): " + request['outcome'])
    message2 = ("[\x0315CircleCI\x03] Change view: \x02\x0311" + compareurl +
                "\x02\x03 Build details: \x02\x0311" + request['build_url'] + "\x02\x03")
    msgshort1 = {"time": time.time(), "type": "Circle", "key": request['reponame'], "full": message1}
    msgshort2 = {"time": time.time(), "type": "Circle", "key": request['reponame'], "full": message2}
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
