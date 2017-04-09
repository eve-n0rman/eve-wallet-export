import logging

from flask import redirect, url_for, render_template
from eve_wallet_export.frontend import frontend


log = logging.getLogger(__name__)


@frontend.route('/')
def front_page():
    return render_template('app.html')

