from selection import Selector
from constants import *

import re,json

REGEX = r"((?P<LOAD>(((?P<LOADREQ>LOAD)|(?P<SAVEREQ>SAVE))\s(?(LOADREQ)((?P<LOADTREENAME>[a-zA-Z0-9_]+)\s(?P<FILEPATH>[a-zA-Z0-9_\.\/\-\s:]+))|(?P<SAVETREENAME>[a-zA-Z0-9_]+)(?!(.+?)))))|(?P<NONLOAD>((?P<GETREQ>GET)|(?P<PUTREQ>PUT)|(?P<DELREQ>DELETE)|(?P<SHOWREQ>SHOW))\s(?(SHOWREQ)(TREES)(?!(.+?))|(?(LOADREQ)(LOADTREE)(?!(.+?))|((?P<ATTR>ATTR)|(?P<TREE>TREE)))\s(?P<TREENAME>[a-zA-Z0-9_]+)\s(?(ATTR)(?P<ATTRREF>(SELF|CHILDREN|DESCENDANTS|ANCESTORS|PARENT))|(?P<TREEREF>(SELF|PARENT|CHILDREN)))\s(?P<SELECTOR>\{.*\})(?(PUTREQ)(\s(?P<PUTTREE>\{.+\}))|(?(ATTR)((\s(?P<ATTRLIST>\[.+?\]))|\s(?P<ALLATTRJSON>\*)(?!(.+?)))|(?!(.+?)))))))"
expr = re.compile(REGEX)

def parse_request(request):
    groups = expr.finditer(request).next().groupdict()
    if groups['SELECTOR']:
        Selector(groups['SELECTOR']).toPrefix()
    parsed = {'type':None, 'request':None, 'attrs':None,'newtree':None,
              'selector':None, 'tree':None, 'path':None, 'reference':None}

    for typ, req in request_types.items():
        if groups.get(typ,None):
            break
    parsed['request'] = req
    if req == 'SHOW':
        return parsed      
    if req == 'LOAD':
        parsed['type'] = 'write'
        parsed['path'] = groups['FILEPATH']
        parsed['tree'] = groups['LOADTREENAME']
        return parsed
    if req == 'SAVE':
        parsed['tree'] = groups['SAVETREENAME']
        return parsed

    parsed['tree'] = groups['TREENAME']
    parsed['selector'] = groups['SELECTOR']
    parsed['reference'] = groups['TREEREF']
    if req == 'GET':
        parsed['type'] = 'read'
    elif req == 'PUT':
        parsed['newtree'] = groups['PUTTREE']
        parsed['type'] = 'write'
    else:
        parsed['type'] = 'write' 
		
    if groups['ATTR']:
        parsed['reference'] = groups['ATTRREF']
        if groups['ATTRLIST']:
            parsed['attrs'] = groups['ATTRLIST']
        elif groups['ALLATTRJSON']:
            parsed['attrs'] = groups['ALLATTRJSON'] 
        else:
            if parsed['newtree']:
                parsed['newtree'] = None
                parsed['attrs'] = groups['PUTTREE']
    return parsed