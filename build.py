#!/usr/bin/python3

import os
import subprocess

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


# container graph
#   container_name (from fs) -> [ base (from Dockerfile) ]
cg = {}
# container graph reverse
#   container_base_name -> [ container depending on this base ]
cgr = {}

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
for (k,v) in cgr.items():
    print("\t%s <- %s" %(k,v))

print("\nBase images:")
for i in sorted(get_base_images()):
    print('\t%s'% i)

print("\nUpdating base images:")
to_update = sorted(filter(lambda x: x.find('/') == -1, get_base_images()))
cmd = ["parallel", "docker", "pull", "--"] + to_update
print("\t%s" % cmd)
subprocess.check_call(cmd)

#print(cg)
