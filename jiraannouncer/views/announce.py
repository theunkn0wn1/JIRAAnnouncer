from pyramid.response import Response
from pyramid.view import view_config

import sys
import pickle
import time
import os
import random
import re
import simplejson

from sqlalchemy.exc import DBAPIError
from xmlrpc.client import ServerProxy, Error

from ..models import MyModel


# minutes to ignore duplicate messages
OFFSET = 5


def logprint(string):
    """Convert input to string, and print to log, ignoring non-ascii characters."""
    logfile = open("webhook.log", "a")
    logfile.write(str(string).encode('ascii', 'ignore').decode() + "\n")
    logfile.flush()


def jsondump(string):
    """Convert input to string, and dump to jsondump file, ignoring non-ascii characters."""
    dumpfile = open("jsondump.log", "a")
    dumpfile.write(time.strftime("[%H:%M:%S]", time.gmtime()) + ":\n")
    dumpfile.write(str(string).encode('ascii', 'ignore').decode() + "\n")
    dumpfile.close()


def demarkdown(string):
    """Remove markdown features from and limit length of messages"""
    string = re.sub('>.*(\n|$)', '', string).replace('`', '').replace('#', '')
    string = re.sub('\n.*', '', string)
    return string[:300] + ('...' if len(string) > 300 else '')


def jira(request, LASTMESSAGE):
    """Handle JIRA events."""
    request_type = request['webhookEvent']
    PROXY = ServerProxy("https://irc.eu.fuelrats.com:6080/xmlrpc")
    print("In JIRA, set request type.")
    if 'issue' in request:
        issue_key = request['issue']['key']
    elif 'user' in request:
        issue_key = request['user']['key']
    elif 'project' in request:
        issue_key = request['project']['key']
    else:
        issue_key = "JIRA"

    if "OV-" in issue_key or "DRR-" in issue_key or "DOS-" in issue_key or "CID-" in issue_key:
        channels = ["#announcerdev"]
    elif "OPS-" in issue_key or "OVPR-" in issue_key:
        channels = ["#announcerdev"]
    elif "SPARK-" in issue_key or "MECHA-" in issue_key:
        channels = ["#announcerdev"]
    elif "SQUAD-" in issue_key:
        channels = ["#announcerdev"]
    else:
        channels = ["#announcerdev"]

    domessage = True

    if request_type == 'jira:issue_created':
        if "OV-" in issue_key or "DRR-" in issue_key:
            message = ("\x0307" + request['issue']['fields']['issuetype']['name'] +
                       "\x03 Created: \x02" + request['issue']['fields']['summary'] +
                       "\x02 in " + request['issue']['fields']['project']['name'] +
                       " by \x02\x0314" + request['issue']['fields']['reporter'][
                           'displayName'] +
                       "\x02\x03. (\x02\x0311https://jira.fuelrats.com/projects/" +
                       request['issue']['fields']['project']['key'] + "/issues/" + issue_key +
                       "/\x03\x02)")
        else:
            if 'priority' in request['issue']['fields']:
                message = ("Issue Created: \x02\x0307" + request['issue']['fields']['issuetype'][
                    'name'] + "\x02\x03 [\x02\x0306" + issue_key + "\x03\x02] Priority: " +
                           request['issue']['fields']['priority']['name'] + " in \x02" +
                           request['issue']['fields']['project']['name'] + "\x02(\x02" +
                           request['issue']['fields']['project']['key'] + "\x02) by \x02\x0314" +
                           request['issue']['fields']['reporter']['displayName'] + ".\x03\x02 \"" +
                           request['issue']['fields']['summary'] +
                           "\". (\x02\x0311https://jira.fuelrats.com/projects/" +
                           request['issue']['fields']['project']['key'] + "/issues/" + issue_key +
                           "/\x03\x02)")
            else:
                message = ("Issue Created: \x02\x0307" + request['issue']['fields']['issuetype'][
                    'name'] + "\x02\x03 [\x02\x0306" + issue_key + "\x03\x02] in \x02" +
                           request['issue']['fields']['project']['name'] + "\x02(\x02" +
                           request['issue']['fields']['project']['key'] + "\x02) by \x02\x0314" +
                           request['issue']['fields']['reporter']['displayName'] + ".\x03\x02 \"" +
                           request['issue']['fields']['summary'] +
                           "\". (\x02\x0311https://jira.fuelrats.com/projects/" +
                           request['issue']['fields']['project']['key'] + "/issues/" + issue_key +
                           "/\x03\x02)")
    elif request_type == 'jira:issue_updated':
        if "OV-" in issue_key or "DRR-" in issue_key:
            if request['user']['displayName'] == "Fuel Rats Automation":
                message = ("Fuel Rats Automation cleanup done.")
                domessage = False
                this_kennel = str(random.random())
                kfile = open("/tmp/kennel.p", "w")
                kfile.write(this_kennel)
                kfile.close()
                time.sleep(2)
                kfile2 = open("/tmp/kennel.p", "r")
                if kfile2.readline() == this_kennel:
                    domessage = True
                else:
                    logprint("JIRA Automation report suppressed")
            else:
                if (request['issue']['fields']['status']['id'] == "10400" or
                        request['issue']['fields']['status']['id'] == "10600"):
                    status_colour = "\x0304"
                else:
                    status_colour = "\x0303"
                message = ("\x0307" + request['issue']['fields']['issuetype']['name'] + "\x03 " +
                           status_colour + request['issue']['fields']['status']['name'] +
                           "\x03: \x02" + request['issue']['fields']['summary'] + "\x02 in " +
                           request['issue']['fields']['project']['name'] + " by \x02\x0314" +
                           request['user']['displayName'] +
                           "\x02\x03. (\x02\x0311https://jira.fuelrats.com/projects/" +
                           request['issue']['fields']['project']['key'] + "/issues/" + issue_key +
                           "/\x03\x02)")
        else:
            if 'changelog' in request:
                if len(request['changelog']['items']) == 1:
                    if request['changelog']['items'][0]['field'] == "Rank" or request[
                        'changelog']['items'][0]['field'] == "Sprint":
                        logprint("Rank or sprint change ignored")
                        domessage = False
                        return
            if "user" not in request:
                user = "Nep"
            else:
                user = request['user']['displayName']

            if request['issue_event_type_name'] == "issue_commented":
                update_type = "Commented:"
            elif request['issue_event_type_name'] == "issue_assigned":
                update_type = "Assigned to " + request['issue']['fields'][
                    'assignee']['displayName'] + ":"
            else:
                update_type = "Updated:"

            if "SQUAD-" in issue_key:
                if request['issue']['fields']['status']['id'] == "10100":
                    status_colour = "\x0304"
                else:
                    status_colour = "\x0303"
            else:
                status_colour = "\x0303"

            message = ("Issue " + update_type + " \x02\x0307" + request['issue']['fields'][
                'issuetype']['name'] + "\x02\x03 \"" + request['issue']['fields']['summary'] +
                       "\" [\x02\x0306" + request['issue']['key'] + "\x03\x02] in \x02" +
                       request['issue']['fields']['project']['name'] + "\x02(\x02" +
                       request['issue']['fields']['project']['key'] + "\x02) by \x0314\x02" +
                       user + ".\x03\x02 Status: \x02" + status_colour +
                       request['issue']['fields']['status']['name'] +
                       "\x03\x02. (\x0311\x02https://jira.fuelrats.com/projects/" +
                       request['issue']['fields']['project']['key'] + "/issues/" + issue_key +
                       "/\x03\x02)")
    elif request_type == 'jira:issue_deleted':
        message = ("Issue Deleted: \x02\x0307" + request['issue']['fields']['issuetype']['name'] +
                   "\x02\x03 \"" + request['issue']['fields']['summary'] + "\" [\x02\x0306" +
                   request['issue']['key'] + "\x03\x02] in \x02" +
                   request['issue']['fields']['project']['name'] + "\x02(\x02" +
                   request['issue']['fields']['project']['key'] + "\x02) by \x0314\x02" +
                   request['user']['displayName'] + ".\x03\x02")
    elif request_type == 'user_created':
        message = ("User created: \x02\x0307" + request['user']['key'] + "\x02\x03 (\x02\x0311" +
                   request['user']['emailAddress'] + "\x02\x03)")
        domessage = False
    elif request_type == 'user_deleted':
        message = ("User deleted: \x02\x0307" + request['user']['key'] + "\x02\x03 (\x02\x0311" +
                   request['user']['name'] + "\x02\x03)")
    elif request_type == 'jira:version_created':
        message = "Version created: \x02\x0307" + request['version']['name'] + "\x02\x03 of "
    elif request_type == 'project_created':
        message = ("Project created: \x02\x0307" + request['project']['name'] +
                   "\x02\x03 [\x02\x0306" + request['project']['key'] +
                   "\x03\x02] under \x02\x0314" + request['project']['projectLead']['key'] +
                   " (" + request['project']['projectLead']['displayName'] + ")")
    elif request_type == 'project_deleted':
        message = ("Project deleted: \x02\x0307" + request['project']['name'] +
                   "\x02\x03 [\x02x0308" + request['project']['key'] +
                   "\x03\x02] under \x02\x0314" + request['project']['projectLead']['key'] +
                   " (" + request['project']['projectLead']['displayName'] + ")")
    else:
        message = "JIRA unhandled event: " + request_type
        logprint(message)
        return

    msgshort = {"time": time.time(), "type": request_type, "key": issue_key, "full": message}

    squadstatuschange = False
    if "SQUAD-" in issue_key:
        if 'changelog' in request:
            for item in request['changelog']['items']:
                if item['field'] == "status":
                    squadstatuschange = True

    if (LASTMESSAGE['type'] == request_type and LASTMESSAGE['key'] == issue_key and
            LASTMESSAGE['time'] > time.time() - (OFFSET * 60) and
            request['issue_event_type_name'] != "issue_commented" and
            squadstatuschange is False):
        logprint("Duplicate message, skipping:")
        logprint(message)
    elif domessage is True:
        for channel in channels:
            send(channel, "[\x0315JIRA\x03] " + message, msgshort, PROXY)


def github(event, data, LASTMESSAGE):
    """Handle GitHub events."""
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
            kfile = open("/tmp/kennel.p", "w")
            kfile.write(this_kennel)
            kfile.close()
            time.sleep(2)
            kfile2 = open("/tmp/kennel.p", "r")
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
    if LASTMESSAGE['full'] == message:
        logprint("Duplicate message, skipping:")
        logprint(message)
    else:
        if domessage:
            for channel in channels:
                send(channel, "[\x0315GitHub\x03] " + message, msgshort)


def travis(repo, data, LASTMESSAGE):
    """Handle TravisCI events"""
    if not data.startswith("payload="):
        logprint("Error in Travis input, expected \"payload=\"")
        return
    try:
        request = simplejson.loads(data[8:])
    except:
        logprint("Error loading Travis payload:")
        logprint(data)
        return

    if repo == "FuelRats/pipsqueak3":
        channels = ['#mechadev']
    else:
        channels = ['#rattech']
        message1 = ("[\x0315TravisCI\x03] \x0306" + repo + "\x03#" + request['number'] +
                    " (\x0306" + request['branch'] + "\x03 - " + request['commit'][:7] +
                    " : \x0314" + request['author_name'] + "\x03): " + request['result_message'])
        message2 = ("[\x0315TravisCI\x03] Change view: \x02\x0311" + request['compare_url'] +
                    "\x02\x03 Build details: \x02\x0311" + request['build_url'] + "\x02\x03")
        msgshort1 = {"time": time.time(), "type": "Travis", "key": repo, "full": message1}
        msgshort2 = {"time": time.time(), "type": "Travis", "key": repo, "full": message2}
        if LASTMESSAGE['full'] == message2:
            logprint("Duplicate message, skipping:")
            logprint(message1)
            logprint(message2)
        else:
            for channel in channels:
                send(channel, message1, msgshort1)
            time.sleep(0.5)
            for channel in channels:
                send(channel, message2, msgshort2)


def circle(inputstr, LASTMESSAGE):
    """Handle CircleCI events"""

    request = inputstr['payload']

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
    if LASTMESSAGE['full'] == message2:
        logprint("Duplicate message, skipping:")
        logprint(message1)
        logprint(message2)
    else:
        for channel in channels:
            send(channel, message1, msgshort1)
        time.sleep(0.5)
        for channel in channels:
            send(channel, message2, msgshort2)


def send(channel, message, msgshort, PROXY):
    """Send resulting message to IRC over XMLRPC."""
    message = message.replace('\n', ' ').replace('\r', '')
    try:
        messagesplit = [message[i:i + 475] for i in range(0, len(message), 475)]
        for msgpart in messagesplit:
            logprint(time.strftime("[%H:%M:%S]", time.gmtime()) + " Sending to " + channel + "...")
            logprint(PROXY.command("botserv", "ABish", "say " + channel + " " + msgpart))
            # logprint(msgpart)
            time.sleep(0.5)
        pickle.dump(msgshort, open("lastmessage.p", "wb"))
    except Error as err:
        logprint("ERROR" + str(err))
    except:
        logprint("Error sending message")
        logprint(sys.exc_info())
        return


@view_config(route_name='announce', renderer="json")
def my_view(request):
    PROXY = ServerProxy("https://irc.eu.fuelrats.com:6080/xmlrpc")
    LASTMESSAGE = {'type': " ", 'key': " ", 'time': 0, 'full': " "}
    SHORTMSG = "The Quick Brown Fox..."
    try:
        send("#announcerdev", "Pyramid Announcer got a hit!", SHORTMSG, PROXY)
        if request.params == "":
            return {'content': 'Input was empty!'}
        inputstr = simplejson.loads(request.body)
        if "HTTP_X_GITHUB_EVENT" in request.headers:
            try:
                github(os.environ['HTTP_X_GITHUB_EVENT'], request.body, LASTMESSAGE)
            except:
                print("Github event parsing failed!")
                return {'content': 'Failed to parse Github event!'}
            return {'content': 'Got a Github event!'}
        elif "HTTP_TRAVIS_REPO_SLUG" in request.headers:
            return {'content': 'Got a Travis event!'}
        try:
            inputstr = simplejson.loads(request.body)
        except:
            return {'content': 'Couldn\'t parse any JSON from request'}
        print("Loaded a possible JIRA request.")
        jira(inputstr, LASTMESSAGE)
        print("Sent to JIRA function.")
        return {'content': 'Probably got a JIRA event.'}

    except Error as v:
        return Response("ERROR", content_type='text/plain', status=500)

#        try:
#            INSTREAM = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
#            INPUTSTRING = INSTREAM.read()
#        except:
#            logprint("Error reading input:")
#            logprint(sys.exc_info())
#             sys.exit()
#
#         if INPUTSTRING == "":
#             logprint("Empty input.")
#             sys.exit()
#
#         try:
#             LASTMESSAGE = pickle.load(open("lastmessage.p", "rb"))
#             logprint("Pickle loaded")
#             if not all(KEY in LASTMESSAGE for KEY in ('type', 'key', 'time', 'full')):
#                 logprint("Error loading pickle")
#                 LASTMESSAGE = {'type': " ", 'key': " ", 'time': 0, 'full': " "}
#         except:
#             logprint("Error loading pickle")
#             LASTMESSAGE = {'type': " ", 'key': " ", 'time': 0, 'full': " "}
#
#         if "HTTP_X_GITHUB_EVENT" in os.environ:
#             try:
#                 github(os.environ['HTTP_X_GITHUB_EVENT'], INPUTSTRING, LASTMESSAGE)
#             except:
#                 logprint("Error sending GitHub message")
#                 logprint(sys.exc_info())
#                 jsondump(INPUTSTRING)
#                 if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
#                     logprint("IRC error notice suppressed.")
#                 else:
#                     SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "GitHub Error"}
#                     send("#rattech", "ABish: Something done nepped up in GitHub", SHORTMSG, PROXY)
#         elif "HTTP_TRAVIS_REPO_SLUG" in os.environ:
#             try:
#                 travis(os.environ['HTTP_TRAVIS_REPO_SLUG'], urllib.parse.unquote(INPUTSTRING), LASTMESSAGE)
#             except:
#                 logprint("Error sending Travis message")
#                 logprint(sys.exc_info())
#                 jsondump(INPUTSTRING)
#                 if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
#                     logprint("IRC error notice suppressed.")
#                 else:
#                     SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "Travis Error"}
#                     send("#rattech", "ABish: Something done nepped up in Travis", SHORTMSG, PROXY)
#         else:
#             try:
#                 INPUTSTR = simplejson.loads(INPUTSTRING)
#             except:
#                 logprint("Error sending JIRA/CircleCI message")
#                 logprint(sys.exc_info())
#                 jsondump(INPUTSTRING)
#                 if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
#                     logprint("IRC error notice suppressed.")
#                 else:
#                     SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "JIRA/Circle Error"}
#                     send("#rattech", "ABish: Something done nepped up in JIRA or CircleCI", SHORTMSG)
#             if 'webhookEvent' in INPUTSTR:
#                 try:
#                     jira(INPUTSTR, LASTMESSAGE)
#                 except:
#                     logprint("Error sending JIRA message")
#                     logprint(sys.exc_info())
#                     jsondump(INPUTSTRING)
#                     if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
#                         logprint("IRC error notice suppressed.")
#                     else:
#                         SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "JIRA Error"}
#                         send("#rattech", "ABish: Something done nepped up in JIRA", SHORTMSG, PROXY)
#             else:
#                 try:
#                     circle(INPUTSTR)
#                 except:
#                     logprint("Error sending CircleCI message")
#                     logprint(sys.exc_info())
#                     jsondump(INPUTSTRING, LASTMESSAGE)
#                     if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
#                         logprint("IRC error notice suppressed.")
#                     else:
#                         SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "Circle Error"}
#                         send("#rattech", "ABish: Something done nepped up in CircleCI", SHORTMSG, PROXY)
