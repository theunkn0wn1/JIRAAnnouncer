from pyramid.view import view_config

from ..utils import logprint, jsondump, send, getlast, demarkdown
import subprocess


@view_config(route_name='updater', renderer="json")
def updater(request):
    """Handle updates to OS files through github pulls."""
    #subprocess.call()
