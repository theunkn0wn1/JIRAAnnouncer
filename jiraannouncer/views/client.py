import random
import time
import simplejson

from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast, demarkdown


@view_config(route_name='client', renderer="json")
def client(request):
    """Handle Client arrival announcements."""
    referer = request.headers['Referer']
    if referer != "https://clients.fuelrats.com:7778/":
        logprint("Client announcer called with invalid referer" + referer)
        return
    cmdrname = request.params['cmdrname']
    system = request.params['system']
    platform = request.params['platform']
    o2status = request.params['EO2']
    if request.params['extradata'] is not None:
        message = f"Incoming Client: {cmdrname} - System: {system} - Platform: {platform} - O2: {o2status} - {extradata}"
    else:
        message = f"Incoming Client: {cmdrname} - System: {system} - Platform: {platform} - O2: {o2status}"
    send("#announcerdev", message, "No Short for you!")
    return