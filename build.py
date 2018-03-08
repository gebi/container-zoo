#!/usr/bin/python3

import sys
import os
import subprocess
import click
import yaml
from jinja2 import Environment, FileSystemLoader

DEBUG=None

# container graph
#   container_name (from fs) -> [ base (from Dockerfile) ]
cg = {}
# container graph reverse
#   container_base_name -> [ container depending on this base ]
cgr = {}

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'debian')),
    trim_blocks=False)


# walk {{{
def walk(path, filter):
    '''yield every directory matched from filter(x) under path, recursively.'''
    def errhandler(err):
        if err.filename == path:
            raise err

    for root, dirs, files in os.walk(path, onerror=errhandler):
        if filter(root):
            yield root
        for d in dirs:
            dir = os.path.join(root, d)
            if filter(dir):
                yield dir
                dirs.remove(d)

def dockerfilter(dir):
    '''special filter to match a directory with a Dockerfile'''
    tmp = os.path.abspath(dir)
    if os.path.exists(os.path.join(tmp, 'Dockerfile')):
        return True
    return False
# }}}

def getbase(dir):
    from_ = set()
    for i in open(os.path.join(dir, 'Dockerfile'), 'r').readlines():
        i = i.lower()
        if i.startswith('from'):
            # fromcmd, baseimage, remainder
            tmp = i.split(' ', 2)
            from_.add(tmp[1].rstrip().lstrip())
    return from_

def get_container_name(dir):
    i = dir.lstrip('./').split('/')
    if len(i) == 1:
        return "local/%s" %(i[0])
    elif len(i) == 2:
        return "local/%s:%s" %(i[0], i[1])
    else:
        raise RuntimeError("Incompatible directory for Dockerfile: %s" %(dir))

def get_base_images():
    for i in cgr:
        if i not in cg:
            yield i

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    #click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    global DEBUG
    DEBUG=debug

@cli.command()
@click.option('--update/--no-update', default=False)
def upgrade_base(update): # {{{
    '''Upgrade base docker images'''
    for i in walk('.', dockerfilter):
        #print(i)
        container_base = getbase(i)
        container_name = get_container_name(i)
        cg[container_name] = container_base

    # create reverse mapping
    print("Local Container:")
    for container_name,base_set in cg.items():
        print("\t%s -> %s" %(container_name, base_set))
        for base in base_set:
            i = cgr.get(base, set())
            i.add(container_name)
            cgr[base] = i

    print("\nPrint dependencies:")
    for k in sorted(cgr):
        v = cgr[k]
        print("\t%s <- %s" %(k,sorted(v)))

    print("\nBase images:")
    for i in sorted(get_base_images()):
        print('\t%s'% i)

    print("\nUpdating base images:")
    to_update = sorted(filter(lambda x: x.find('/') == -1, get_base_images()))
    cmd = ["parallel", "docker", "pull", "--"] + to_update
    print("\t%s" % cmd)
    if update:
        subprocess.check_call(cmd)
    #print(cg)
# }}}

def create(docker_template, context, output):
    html = TEMPLATE_ENVIRONMENT.get_template(docker_template).render(context)
    if DEBUG:
        os.makedirs(os.path.dirname(output), exist_ok=True)
        sys.stdout.write("# %s (%s)\n" %(docker_template, output))
        sys.stdout.write(html)
        sys.stdout.write('\n\n')
        return
    with open(output, 'w') as f:
        f.write(html)
        f.write('\n')

@cli.command()
def build(): # {{{
    '''Build all images'''
    tname = "build.j2"
    context = {}
    build_yaml = TEMPLATE_ENVIRONMENT.get_template(tname).render(context)
    build = yaml.safe_load(build_yaml)
    # create default vars
    for (k,v) in build.items():
        e = v.get('env', dict)
        e['IMAGE_BASE'] = v['base']
        e['IMAGE_NAME'] = k
    sys.stdout.write("# %s (%s)\n" %(tname, "build"))
    sys.stdout.write(yaml.dump(build, default_flow_style=False))
    sys.stdout.write("\n\n")
    for (k,v) in build.items():
        create(v['dockerfile'], v['env'], os.path.join(PATH, "debian", k, "Dockerfile"))
# }}}

if __name__ == '__main__':
    cli()
