from selection import Selector

import re,json

REGEX = r"((?P<GETREQ>GET)|(?P<PUTREQ>PUT)|(?P<DELREQ>DELETE))\s((?P<Attr>ATTR)|(?P<Tree>TREE))\s(?P<ObjName>[a-zA-Z0-9_]+)\s(?(Attr)(SELF|CHILDREN|DESCENDANT|ANCESTOR|PARENT)|(?(GETREQ)(SELF|CHILDREN|PARENT)|(SELF)))\s(?P<JSON>\{.+?\})(?(PUTREQ)(\s(?P<JSON2>\{.+\}))|(?(Attr)(\s(?P<LIST2>\[.+?\]))|(?!(.+?))))"
expr = re.compile(REGEX)

def parse_request(request):
    groups = expr.finditer(request).next().groupdict()
    if groups['JSON']:
        Selector(groups['JSON']).toPrefix()
    return groups