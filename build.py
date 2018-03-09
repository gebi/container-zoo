#!/usr/bin/python3

import sys
import os
import subprocess
import click
import yaml
from jinja2 import Environment, FileSystemLoader
from concurrent.futures import ThreadPoolExecutor, as_completed

DEBUG=None

# container graph
#   container_name (from fs) -> [ base (from Dockerfile) ]
cg = {}
# container graph reverse
#   container_base_name -> [ container depending on this base ]
cgr = {}

PATH = os.path.dirname(os.path.abspath(__file__))

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

def buildfilter(dir):
    '''special filter to match a directory with a build.j2 file'''
    tmp = os.path.abspath(dir)
    if os.path.exists(os.path.join(tmp, 'build.j2')):
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
    global DEBUG
    DEBUG=debug

def build_docker(cmds):
    return [(i, subprocess.check_output(i)) for i in cmds]

@cli.command()
@click.option('-j', '--max_workers', default=0, help="Number of parallel build workers")
def build(max_workers): #{{{
    if max_workers == 0:
        max_workers = None
    executor = ThreadPoolExecutor(max_workers)
    futures = {}
    for i in walk('.', buildfilter):
        build_file = os.path.join(PATH, i, "build.j2")
        if DEBUG:
            print(i, build_file)
        build = gen_build(build_file)
        for k in sorted(build):
            v = build[k]
            first_docker_image_name = v['tags'][0]
            other_docker_image_names = v['tags'][1:]
            cmds = [["docker", "build", "--no-cache", "-t", first_docker_image_name, os.path.join(i, k)]]
            cmds.extend([["docker", "tag", first_docker_image_name, tag] for tag in other_docker_image_names])
            if DEBUG:
                cmds = [ ["echo"] + i for i in cmds ]
            futures[executor.submit(build_docker, cmds)] = v
    for future in as_completed(futures):
        try:
            cmds_output = future.result()
            build_spec = futures[future]
        except Exception as e:
            print('%r generated an exception: %s' %(build_spec, e))
        else:
            print('%r' %(build_spec))
            for (cmd, out) in cmds_output:
                print("#", " ".join(cmd))
                sys.stdout.buffer.write(out)
            sys.stdout.write("\n")
# }}}

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

def gen_docker(docker_template, context, output):
    tenv = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.dirname(docker_template)),
        trim_blocks=False)
    html = tenv.get_template(os.path.basename(docker_template)).render(context)
    if DEBUG:
        os.makedirs(os.path.dirname(output), exist_ok=True)
        sys.stdout.write("# %s (%s)\n" %(docker_template, output))
        sys.stdout.write(html)
        sys.stdout.write('\n\n')
        return
    with open(output, 'w') as f:
        f.write(html)
        f.write('\n')

def gen_build(build_file):
    context = {}
    tenv = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.dirname(build_file)),
        trim_blocks=False)
    build_yaml = tenv.get_template(os.path.basename(build_file)).render(context)
    build = yaml.safe_load(build_yaml)
    # create default vars
    for (k,v) in build.items():
        v['name'] = k
        e = v.get('env', dict)
        e['IMAGE_BASE'] = v['base']
        e['IMAGE_NAME'] = k
        #dir_base = os.path.relpath(os.path.dirname(build_file), start=PATH)
        #e['docker_context'] = os.path.join(dir_base, k)
    if DEBUG:
        sys.stdout.write("# %s (%s)\n" %(build_file, "build"))
        sys.stdout.write(yaml.dump(build, default_flow_style=False))
        sys.stdout.write("\n\n")
    return build

@cli.command()
def generate(): # {{{
    '''Generate Dockerfiles'''
    build = gen_build(os.path.join(PATH, "debian", "build.j2"))
    for (k,v) in build.items():
        gen_docker(os.path.join(PATH, "debian", v['dockerfile']), v['env'], os.path.join(PATH, "debian", k, "Dockerfile"))
#}}}


if __name__ == '__main__':
    cli()
