import random
import time
import simplejson

from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast, demarkdown

OFFSET = 5


@view_config(route_name='github', renderer="json")
def github(request):
    """Handle GitHub events."""
    lastmessage = getlast()
    data = request.body
    if 'X-GitHub-Event' not in request.headers:
        send("#announcerdev", "[\x0315GitHub\x03] " +
             "Malformed request to GitHub webhook handler (Missing X-GitHub-Event header)", "Fail!")
        return
    event = request.headers['X-GitHub-Event']
    try:
        request = simplejson.loads(data)
    except:
        logprint("Error loading GitHub payload:")
        logprint(data)
        return
    domessage = True
    if 'repository' in request and request['repository']['name'] in ["pipsqueak3", "limpet", "MechaChainsaw"]:
        channels = ['#mechadev']
    else:
        channels = ['#rattech']

    if event == 'issues':
        message = ("\x0314" + request['sender']['login'] + "\x03 " + request['action'] +
                   " issue #" + str(request['issue']['number']) + ": \"" + request['issue'][
                       'title'] + "\" in \x0306" + request['repository']['name'] +
                   "\x03. \x02\x0311" + request['issue']['html_url'] + "\x02\x03")
    elif event == 'issue_comment':
        message = ("\x0314" + request['sender']['login'] + "\x03 " + request['action'] +
                   " comment on issue #" + str(request['issue']['number']) + ": \"" +
                   demarkdown(request['comment']['body']) + "\" in \x0306" + request['repository'][
                       'name'] + "\x03. \x02\x0311" + request['comment']['html_url'] + "\x02\x03")
    elif event == 'pull_request':
        if 'id' in request['pull_request']['head']['repo'] and request['pull_request']['head'][
                'repo']['id'] == request['repository']['id']:
            headref = request['pull_request']['head']['ref']
        else:
            headref = request['pull_request']['head']['label']
        if request['action'] == 'review_requested':
            message = ("\x0314" + request['sender']['login'] +
                       "\x03 requested a review from \x0314" +
                       ", ".join([x['login'] for x in request['pull_request'][
                           'requested_reviewers']]) + "\x03 of pull request #" +
                       str(request['number']) + ": \"" + request['pull_request']['title'] +
                       "\" from \x0306" + headref +
                       "\x03 to \x0306" + request['pull_request']['base']['ref'] +
                       "\x03 in \x0306" + request['repository']['name'] + "\x03. \x02\x0311" +
                       request['pull_request']['html_url'] + "\x02\x03")
        else:
            message = ("\x0314" + request['sender']['login'] + "\x03 " + ("merged" if request[
                'pull_request']['merged'] else request['action']) + " pull request #" +
                       str(request['number']) + ": \"" + request['pull_request']['title'] +
                       "\" from \x0306" + headref +
                       "\x03 to \x0306" + request['pull_request']['base']['ref'] +
                       "\x03 in \x0306" + request['repository']['name'] +
                       "\x03. \x02\x0311" + request['pull_request']['html_url'] + "\x02\x03")
    elif event == 'pull_request_review':
        logprint("pull request review event:")
        if request['action'] == "commented":
            logprint("Probable duplicate review comment event ignored.")
            domessage = False
            return

        if request['action'] == "submitted":
            action = request['review']['state']
        else:
            action = request['action']

            message = ("\x0314" + request['sender']['login'] + "\x03 " + action +
                       "\x03 review of \x0314" + request['pull_request']['user']['login'] +
                       "\x03's pull request #" + str(request['pull_request']['number']) +
                       (": \"" + demarkdown(request['review']['body'] + "\"") if request['review'][
                           'body'] else "") + " in \x0306" + request['repository']['name'] +
                       "\x03. \x02\x0311" + request['review']['html_url'] + "\x02\x03")
            logprint(message)
    elif event == 'pull_request_review_comment':
        if request['comment']['user']['login'] == "houndci-bot":
            message = ("Style errors found on pull request #" + str(request['pull_request'][
                                                                        'number']) + ": \"" + request['pull_request'][
                           'title'] + "\" in \x0306" +
                       request['repository']['name'])
            domessage = False
            this_kennel = str(random.random())
            kfile = open("kennel.p", "w")
            kfile.write(this_kennel)
            kfile.close()
            time.sleep(2)
            kfile2 = open("kennel.p", "r")
            if kfile2.readline() == this_kennel:
                domessage = True
            else:
                logprint("Hound comment suppressed")
        else:
            message = ("\x0314" + request['sender']['login'] + "\x03 " + request['action'] +
                       " comment on pull request #" + str(request['pull_request']['number']) +
                       ": \"" + demarkdown(request['comment']['body']) + "\" in \x0306" + request[
                           'repository']['name'] + "\x03. \x02\x0311" + request['comment'][
                           'html_url'] + "\x02\x03")
    elif event == 'push':
        if not request['commits']:
            domessage = False
            message = "Empty commit event ignored"
        elif len(request['commits']) == 1:
            message = ("\x0314" + request['sender']['login'] + "\x03 pushed " + request[
                                                                                    'commits'][0]['id'][:7] + ": \"" +
                       request['commits'][0]['message'] +
                       "\" to \x0306" + request['repository']['name'] + "/" +
                       request['ref'].split('/')[-1] + "\x03. \x02\x0311" +
                       request['compare'] + "\x02\x03")
        else:
            message = ("\x0314" + request['sender']['login'] + "\x03 pushed " +
                       str(len(request['commits'])) + " commits to \x0306" + request['repository'][
                           'name'] + "/" + request['ref'].split('/')[-1] + "\x03. \x02\x0311" +
                       request['compare'] + "\x02\x03")
    elif event == 'commit_comment':
        message = ("\x0314" + request['sender']['login'] + "\x03 commented on commit \"" +
                   request['comment']['commit_id'][:7] + "\" to \x0306" + request['repository'][
                       'name'] + "\x03. \x02\x0311" + request['comment']['html_url'] + "\x02\x03")
    elif event == 'create':
        if request['ref_type'] == 'tag':
            message = ("\x0314" + request['sender']['login'] + "\x03 created " +
                       request['ref_type'] + " \"" + request['ref'] + "\" in \x0306" + request[
                           'repository']['name'] + "\x03.")
        else:
            logprint("Unhandled create ref:" + request['ref_type'])
            return
    elif event == 'status':
        logprint("Ignored github status event")
        return
    else:
        logprint("GitHub unhandled event: " + event)
        jsondump(request)
        return
    msgshort = {"time": time.time(), "type": event, "key": "GitHub", "full": message}
    if lastmessage['full'] == message:
        logprint("Duplicate message, skipping:")
        logprint(message)
    else:
        if domessage:
            for channel in channels:
                send(channel, "[\x0315GitHub\x03] " + message, msgshort)