#!/usr/bin/python3
# A small container image build script to mass create similar container images with different base images
#
# Idea should be:
#   ./build.py upgrade_base ... parses all build.j2 files and updates all depended on base container images
#   ./build.py build ... parses all build.j2 files and build all container  images
#                        from generated Dockerfiles (without persisting them to disk)
#
# Currently the workflow is:
#   ./build.py generate ... creates directory hierarchy and generates all Dockerfiles
#                           specified in build.j2 files
#                           actually currently hardcoded to only ./debian/build.j2
#   ./build.py upgrade_base ... parses all Dockerfile it finds with name-schema policy and
#                               update all base container images
#   ./build.py build ... parses build.j2 files, find all containers to build and execute
#                        commands to build container images (does NOT generate Dockerfiles)

import sys
import os
import subprocess
import multiprocessing
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
def walk(list_of_paths, filter):
    try:
        iterator = iter(list_of_paths)
        for i in list_of_paths:
            return walk_(i, filter)
    except exception.TypeError:
        return walk_(i, filter)

def walk_(path, filter):
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
    '''Parse all base images used inside Dockerfile in dir'''
    from_ = set()
    for i in open(os.path.join(dir, 'Dockerfile'), 'r').readlines():
        i = i.lower()
        if i.startswith('from'):
            # fromcmd, baseimage, remainder
            tmp = i.split(' ', 2)
            from_.add(tmp[1].rstrip().lstrip())
    return from_

def get_container_name(dir):
    '''Generate container name BY POLICY from directory name which contains a Dockerfile
         ./signal         => local/signal
         ./debian/stretch => local/debian:stretch
    '''
    i = dir.lstrip('./').split('/')
    if len(i) == 1:
        return "local/%s" %(i[0])
    elif len(i) == 2:
        return "local/%s:%s" %(i[0], i[1])
    else:
        raise RuntimeError("Incompatible directory for Dockerfile: %s" %(dir))

def get_base_images():
    '''Walk container dependency graph in global state cg/cgr and yield all roots'''
    for i in cgr:
        if i not in cg:
            yield i

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    global DEBUG
    DEBUG=debug

def build_docker(cmds):
    '''Function to actually execute a list of cmdlines to build a container and store their output'''
    return [(i, subprocess.check_output(i)) for i in cmds]

@cli.command()
@click.option('-j', '--max_workers', default=multiprocessing.cpu_count(), help="Number of parallel build workers (default = %d)" %(multiprocessing.cpu_count()))
@click.option('--cache/--no-cache', default=True, help="Per default docker cache is used")
def build(max_workers, cache): #{{{
    '''Build docker images'''
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
            base_cmd = ["docker", "build"]
            if not cache:
                base_cmd.append("--no-cache")
            cmds = [base_cmd + ["-t", first_docker_image_name, os.path.join(i, k)]]
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
            sys.exit(1)
        else:
            print('%r' %(build_spec))
            for (cmd, out) in cmds_output:
                print("#", " ".join(cmd))
                sys.stdout.buffer.write(out)
            sys.stdout.write("\n")
# }}}

# Format a dependency graph for printing
def format_dependencies(name_to_deps):
    msg = []
    for name, deps in name_to_deps.items():
        for parent in deps:
            msg.append("%s -> %s" % (name, parent))
    return "\n".join(msg)

# "Batches" are sets of tasks that can be run together
def get_batches(nodes):

    # Build a map of node names to node instances
    name_to_instance = dict( (n.name, n) for n in nodes )
    print("name_to_instace", name_to_instance)

    # Build a map of node names to dependency names
    #name_to_deps = dict( (n.name, set(n.base)) for n in nodes )
    for n in nodes:
        print(n.name, " -> ", n.base)
    name_to_deps = dict( (n.name, set(n.base)) for n in nodes )
    print("name_to_deps: ", name_to_deps)
    #print("name_to_deps: ")
    #for (name,dep_set) in name_to_deps:
    #    print("%s -> %s" %(name, ",".join(dep_set)))

    # This is where we'll store the batches
    batches = []

    # While there are dependencies to solve...
    while name_to_deps:
        print("batches: ", batches)

        # Get all nodes with no dependencies
        ready = {name for name, deps in name_to_deps.items() if not deps}
        print("ready: ", ready)

        # If there aren't any, we have a loop in the graph
        if not ready:
            #msg  = "Circular dependencies found!\n"
            #msg += format_dependencies(name_to_deps)
            #raise ValueError(msg)
            print("last batch found: ", name_to_deps)
            batches.append({name_to_instance[name] for name in name_to_deps})
            break

        # Remove them from the dependency graph
        for name in ready:
            del name_to_deps[name]
        for deps in name_to_deps.values():
            deps.difference_update(ready)

        print("name_to_deps left: ", name_to_deps)
        # Add the batch to the list
        batches.append( {name_to_instance[name] for name in ready} )
    return batches

def expand_remote_nodes(nodes):
    name_to_instance = dict( (n.spec['tags'][0], n) for n in nodes )
    remote_nodes = {}
    for name, instance in name_to_instance.items():
        for i in instance.base:
            if i not in name_to_instance:
                if i not in remote_nodes:
                    remote_nodes[i] = create_remote_build(i)
    nodes.extend(remote_nodes.values())
    return nodes

@cli.command()
@click.option('-j', '--max_workers', default=multiprocessing.cpu_count(), help="Number of parallel build workers (default = %d)" %(multiprocessing.cpu_count()))
@click.option('--cache/--no-cache', default=True, help="Per default docker cache is used")
def build1(max_workers, cache): #{{{
    '''Build docker images'''
    executor = ThreadPoolExecutor(max_workers)
    # generate build specs
    local_builds = []
    for i in walk('.', buildfilter):
        build_file = os.path.join(PATH, i, "build.j2")
        if DEBUG:
            print(i, build_file)
        build = gen_build(build_file)
        local_builds.extend(build)
    # add remote edge nodes (container that are not build in this step as stub Build objects
    for i in local_builds:
        print(i.name)
    builds = expand_remote_nodes(local_builds)
    print("Fooo")
    for i in builds:
        print(i.name)
    #FIXME: gether all build files
    # dep resolution
    build_batches = get_batches(builds)
    print(build_batches)
    for i in build_batches:
        print(",".join([j.name for j in i]))

    futures = {}
    for batch in build_batches:
        for b in sorted(batch):
            if b.remote:
                # later support pull of remote images
                continue
            k = b.name
            v = b.spec
            first_docker_image_name = v['tags'][0]
            other_docker_image_names = v['tags'][1:]
            base_cmd = ["docker", "build"]
            if not cache:
                base_cmd.append("--no-cache")
            i = 'debian/'  # FIXME
            cmds = [base_cmd + ["-t", first_docker_image_name, os.path.join(i, k)]]
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
            sys.exit(1)
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
    for i in walk(['debian', 'ubuntu'], dockerfilter):
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
    cmd = ["parallel", "docker", "pull", "--disable-content-trust=false", "--"] + to_update
    print("\t%s" % cmd)
    if update:
        subprocess.check_call(cmd)
    #print(cg)
# }}}

def gen_docker(docker_template, context, output):
    '''Core routine to parse templates specified in build.j2 to generate Dockerfiles from'''
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
    '''Core routine to parse build.j2 file, expand jinja2 templates and parse the result as yaml

    Later on Dockerfile.j2 is expanded using the generated `env', all uppercase variables are
    internal and set from build file metadata, but you can freely add additional variables.

    Internal Variables generated in `env':
    IMAGE_BASE ... Name of base docker image
    IMAGE_NAME ... Name of image

    :Example:
    stretch:
      base: debian:stretch
      dockerfile: Dockerfile.j2
      env:
        dist_name: stretch
      tags:
      - local/debian:stretch
      - local/debian:9
      - local/debian:stable
    '''
    context = {}
    tenv = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.dirname(build_file)),
        trim_blocks=False)
    build_yaml = tenv.get_template(os.path.basename(build_file)).render(context)
    build = yaml.safe_load(build_yaml)
    for (k,v) in build.items():
        print("FOOO")
        print(k, v)
    build_specs = []
    # create default vars
    for (k,v) in build.items():
        v['name'] = k
        e = v.get('env', dict)
        e['IMAGE_BASE'] = v['base']
        e['IMAGE_NAME'] = k
        b = Build(k, v['base'], v)
        build_specs.append(b)
        #dir_base = os.path.relpath(os.path.dirname(build_file), start=PATH)
        #e['docker_context'] = os.path.join(dir_base, k)
    # add vars needed for internal stuff
    #build.name = 
    #build.depends = set(v['base'])  # currently not needed to be a set, but needed later on for multi stage dockerfiles
    if DEBUG:
        sys.stdout.write("# %s (%s)\n" %(build_file, "build"))
        sys.stdout.write(yaml.dump(build, default_flow_style=False))
        sys.stdout.write("\n\n")
    return build_specs

def create_remote_build(name):
    return Build(name, None, None, remote=True)

class Build(object):
    def __init__(self, name, base, spec, remote=False):
        self.spec = spec
        self.name = name
        if base is None:
            self.base = set()
        else:
            self.base = set([base])
        self.remote = remote
    def __lt__(self, other):
        return self.name < other.name


@cli.command()
def generate(): # {{{
    '''Generate Dockerfiles'''
    build = gen_build(os.path.join(PATH, "debian", "build.j2"))
    for (k,v) in build.items():
        gen_docker(os.path.join(PATH, "debian", v['dockerfile']), v['env'], os.path.join(PATH, "debian", k, "Dockerfile"))
#}}}


if __name__ == '__main__':
    cli()
