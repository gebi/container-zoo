#!/usr/bin/python3

import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader

DEBUG=False
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'debian')),
    trim_blocks=False)

# example context:
#    context = {
#        'IMAGE_BASE': 'debian:jessie',
#        'IMAGE_DIST_NAME': 'jessie',
#    }
def create(docker_template, context, output):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    html = TEMPLATE_ENVIRONMENT.get_template(docker_template).render(context)
    if DEBUG:
        sys.stdout.write(html)
        sys.stdout.write('\n')
        return
    with open(output, 'w') as f:
        f.write(html)
        f.write('\n')

def main():
    debian_release_list = [ "wheezy", "jessie", "stretch", "buster", "sid"]
    instances = [{'IMAGE_BASE': "debian:%s" %(i), 'dist_name': i} for i in debian_release_list]
    for context in instances:
        create("debian/Dockerfile.j2", context, os.path.join(PATH, "debian", c['dist_name'], "Dockerfile"))

def main2():
    tname = "build.j2"
    context = {}
    build_yaml = TEMPLATE_ENVIRONMENT.get_template(tname).render(context)
    build = yaml.safe_load(build_yaml)
    # create default vars
    for (k,v) in build.items():
        e = v.get('env', dict)
        e['IMAGE_BASE'] = v['base']
        e['IMAGE_NAME'] = k
    sys.stdout.write(yaml.dump(build, default_flow_style=False))
    for (k,v) in build.items():
        create(v['dockerfile'], v['env'], os.path.join(PATH, "debian", k, "Dockerfile"))


########################################

if __name__ == "__main__":
    #main()
    main2()
