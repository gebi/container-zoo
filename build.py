#!/usr/bin/python3

import os

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

def getbase(dir):
    from_ = None
    for i in open(os.path.join(dir, 'Dockerfile'), 'r').readlines():
        i = i.lower()
        if i.startswith('from'):
            (cmd, args) = i.split(' ', 1)
            return args.rstrip()

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

cg = {}
cgr = {}

for i in walk('.', dockerfilter):
    #print(i)
    container_base = getbase(i)
    container_name = get_container_name(i)
    cg[container_name] = container_base.lstrip()

# create reverse mapping
print("Local Container:")
for k,v in cg.items():
    print("\t%s -> %s" %(k, v))
    i = cgr.get(v, set())
    i.add(k)
    cgr[v] = i

print("\nPrint dependencies:")
for (k,v) in cgr.items():
    print("\t%s <- %s" %(k,v))

print("\nBase images:")
for i in sorted(get_base_images()):
    print('\t%s'% i)

#print(cg)
