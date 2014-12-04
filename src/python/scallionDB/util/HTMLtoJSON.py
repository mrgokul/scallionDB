import bs4
import sys
import json

def constructJSON(soup, id=None):
    print id
    json = soup.attrs
    if id in soup.attrs:
        json['_id'] = json[id]
        del json[id]
    json["_children"] = [constructJSON(child,id) for child in soup.contents
                        	if isinstance(child,bs4.element.Tag)]
    if not json["_children"]:
        del json["_children"]
    return json
	
def toJSON(input, id):
    f = open(input)
    html = bs4.BeautifulSoup(f,"html5").find('html')
    return json.dumps(constructJSON(html,id))

def main(input, output, id):
    json = toJSON(input,id)
    f = open(output,'w')
    f.write(json)
    f.close()


if __name__ == '__main__':
    '''
    Usage
    python HTMLtoJSON <input HTML> <output JSON> <id to replace if any>
    '''
   
    if len(sys.argv) < 3:  
        raise IndexError("Need to specify Input HTML file and output JSON file")
    elif len(sys.argv) == 3:
        input, output = sys.argv[1:3]
        id = None
    else:
        input, output, id = sys.argv[1:4]
		
    main(input, output, id)