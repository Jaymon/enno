# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from captain import exit, echo
from captain.decorators import arg
from captain.client import Captain
from evernote.api.client import EvernoteClient

from enno.server import AuthServer
from enno import environ


@arg(
    "--consumer-key", "--key", "-k",
    default=environ.CONSUMER_KEY,
    help="The Evernote app consumer key"
)
@arg(
    "--consumer-secret", "--secret", "-s",
    default=environ.CONSUMER_SECRET,
    help="The Evernote app consumer secret"
)
@arg("--sandbox", "-S", action="store_true", help="True if you want a sandbox token")
def main_oauth(consumer_key, consumer_secret, sandbox):

    if not consumer_key:
        raise ValueError("No consumer_key set")

    if not consumer_secret:
        raise ValueError("No consumer_secret set")


    request_token = {}
    def callback(res):
        access_token = client.get_access_token(
            request_token['oauth_token'],
            request_token['oauth_token_secret'],
            res.query.get('oauth_verifier', '')
        )

        echo.hr()
        echo.out("Your access token is:")
        echo.out()
        echo.indent(access_token)
        echo.out()
        echo.hr()
        return access_token

    s = AuthServer(callback)

    # https://github.com/evernote/evernote-sdk-python/#oauth
    client = EvernoteClient(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        sandbox=sandbox
    )

    request_token = client.get_request_token(s.netloc)
    auth_url = client.get_authorize_url(request_token)
    c = Captain('open "{}"'.format(auth_url))
    c.cmd_prefix = ""
    c.run()

    s.handle_request()


exit(__name__)

