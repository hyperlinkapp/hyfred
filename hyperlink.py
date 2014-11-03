#!/usr/bin/env python2
from __future__ import print_function

import argparse
import sys
import json
import urllib2

from workflow import Workflow, ICON_WEB, ICON_WARNING, web, PasswordNotFound

def main(wf):

    parser = argparse.ArgumentParser() 
    # add an optional (nargs='?') --apikey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--token', dest='token', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    # decide what to do based on arguments
    if args.token:  # Script was passed an API key
        # save the key
        wf.save_password('hyperlink_token', args.token)
        return 0  # 0 means script exited cleanly

    # get token or exit
    try:
        token = wf.get_password('hyperlink_token')
    except PasswordNotFound:  # API key has not yet been set
        wf.add_item('No Hyperlink token is set.', 
                    'Please use hitoken to set your Hyperlink token.',
                    valid=False, 
                    icon=ICON_WARNING) 
        wf.send_feedback() 
        return 0

    query = wf.args[0]

    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'session=%s' % token))
    try:
        content = opener.open("https://hyperlinkapp.com/api/search/?types=file&query=%s" % query).read()
    except urllib2.HTTPError:
        wf.add_item('Your Hyperlink token is not valid.', 
                    'Please use hitoken to reset your Hyperlink token.',
                    valid=False, 
                    icon=ICON_WARNING) 
        wf.send_feedback() 
        return 0
        

    data = json.loads(content)

    # default suggestion
    wf.add_item(title=query, 
                subtitle="search on Hyperlink website",
                arg='https://hyperlinkapp.com/search/?q=%s' % query,
                valid=True,
                icon=ICON_WEB)

    nodes = []
    for node in data['nodes']:
        wf.add_item(title=node['filename'],
                    subtitle=node['path'],
                    arg=node['provider_link'],
                    valid=True,
                    icon=ICON_WEB)

    # Send the results to Alfred as XML
    wf.send_feedback()


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
