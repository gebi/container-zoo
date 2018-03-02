#!/usr/bin/python3

import os
import sys
from jinja2 import Environment, FileSystemLoader

DEBUG=False
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, './')),
    trim_blocks=False)

# example context:
#    context = {
#        'IMAGE_BASE': 'debian:jessie',
#        'IMAGE_DIST_NAME': 'jessie',
#    }
def create(context, output):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    tname = "debian/Dockerfile.j2"
    html = TEMPLATE_ENVIRONMENT.get_template(tname).render(context)
    if DEBUG:
        sys.stdout.write(html)
        sys.stdout.write('\n')
        return
    with open(output, 'w') as f:
        f.write(html)
        f.write('\n')

def main():
    full_debian_release_list = [ \
            "wheezy",
            "wheezy-backports",
            "jessie",
            "jessie-backports",
            "stretch",
            "stretch-backports",
            "buster",
            "buster-backports",
            "sid",
            ]
    debian_release_list = [ \
            "wheezy",
            "jessie",
            "stretch",
            "buster",
            "sid",
            ]
    instances = [{'IMAGE_BASE': "debian:%s" %(i), 'IMAGE_DIST_NAME': i} for i in debian_release_list]
    for c in instances:
        create(c, os.path.join(PATH, "debian", c['IMAGE_DIST_NAME'], "Dockerfile"))

########################################

if __name__ == "__main__":
    main()
