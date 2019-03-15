import urllib

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
from ..utils import logprint, jsondump, demarkdown, send


# minutes to ignore duplicate messages
OFFSET = 5









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


@view_config(route_name='announce', renderer="json")
def my_view(request):
    PROXY = ServerProxy("https://irc.eu.fuelrats.com:6080/xmlrpc")
    SHORTMSG = "The Quick Brown Fox..."
    try:
        LASTMESSAGE = pickle.load(open("lastmessage.p", "rb"))
        logprint("Pickle loaded")
        if not all(KEY in LASTMESSAGE for KEY in ('type', 'key', 'time', 'full')):
            logprint("Error loading pickle")
            LASTMESSAGE = {'type': " ", 'key': " ", 'time': 0, 'full': " "}
    except:
        logprint("Error loading pickle")
        LASTMESSAGE = {'type': " ", 'key': " ", 'time': 0, 'full': " "}
    try:
        send("#announcerdev", "Pyramid Announcer got a hit!", SHORTMSG, PROXY)
        if request.params == "":
            return {'content': 'Input was empty!'}
        inputstr = simplejson.loads(request.body)
        if "X-GitHub-Event" in request.headers:
            try:
                github(request.headers['X-GitHub-Event'], request.body, LASTMESSAGE)
            except:
                print("Github event parsing failed!")
                return {'content': 'Failed to parse Github event!'}
            return {'content': 'Got a Github event!'}
        elif "Travis-Repo-Slug" in request.headers:
            travis(request.headers['Travis-Repo-Slug'], urllib.parse.unquote(request.body), LASTMESSAGE)
            return {'content': 'Got a Travis event!'}
        try:
            inputstr = simplejson.loads(request.body)
        except:
            return {'content': 'Couldn\'t parse any JSON from request'}
        print("Loaded a possible JIRA request.")
        if 'webhookEvent' in request.body:
            try:
                print("Sent to JIRA function.")
                jira(inputstr, LASTMESSAGE)
                return {'content': 'Probably got a JIRA event.'}
            except:
                logprint("Error sending JIRA message")
                logprint(sys.exc_info())
                jsondump(inputstr)
                if LASTMESSAGE['key'] == "ERR" and LASTMESSAGE['time'] < time.time() + 3600:
                    logprint("IRC error notice suppressed.")
                else:
                    SHORTMSG = {"time": time.time(), "type": "Error", "key": "ERR", "full": "JIRA Error"}
                    send("#rattech", "ABish: Something done nepped up in JIRA", SHORTMSG, PROXY)
        else:
            try:
                circle(inputstr)
                return {'content': 'Probably got a CircleCI event.'}
            except:
                return {'content': 'Failed to send CircleCI event.'}
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
