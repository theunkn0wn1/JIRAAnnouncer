import random
import time

from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast

OFFSET = 5


@view_config(route_name='jira', renderer="json")
def jira(request):
    """Handle JIRA events."""
    lastmessage = getlast()
    request_type = request['webhookEvent']
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
                message = "Fuel Rats Automation cleanup done."
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

    if (lastmessage['type'] == request_type and lastmessage['key'] == issue_key and
            lastmessage['time'] > time.time() - (OFFSET * 60) and
            request['issue_event_type_name'] != "issue_commented" and
            squadstatuschange is False):
        logprint("Duplicate message, skipping:")
        logprint(message)
    elif domessage is True:
        for channel in channels:
            send(channel, "[\x0315JIRA\x03] " + message, msgshort)