import json,os

class Tree(object):
	def __init__(self,name):
		self.name = name
	def getNode(name,reference,node_details):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: GETTREE - Name of a tree must be alpha numeric")
		else:
			raise SyntaxError("Error: GETTREE - Name of a tree cannot be empty")
		if not(reference and reference.upper() in ["SELF","PARENT","CHILDREN"]):
			raise SyntaxError("Error: GETTREE - Invalid reference type. Valid references are SELF, PARENT and CHILDREN")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: GETTREE - Invalid JSON")
			else:
				raise SyntaxError("Error: GETTREE - Attribute details are not of type dict")
		return (' '.join(["GET","TREE",str(name),str(reference).upper(),str(node_details)]))
	
	def getAttrs(name,reference,node_details,attribute_list):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: GETATTR - Name of a tree must be alpha numeric")
		else:
			raise SyntaxError("Error: GETATTR - Name of a tree cannot be empty")
		if not(reference and reference.upper() in ["SELF","PARENT","CHILDREN","ANCESTOR","DESCENDANT"]):
			raise SyntaxError("Error: GETATTR - Invalid reference type. Valid references are SELF, PARENT, CHILDREN, ANCESTOR and DESCENDANT")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: GETATTR - Invalid JSON")
			else:
				raise SyntaxError("Error: GETATTR - Attribute details are not of type dict")
		if attribute_list:
			if not(isinstance(attribute_list,list) or attribute_list == '*'):
				raise SyntaxError("Error: GETATTR - Invalid Syntax for Attribute list! It can be a list of attibutes or * for all attributes")
			if isinstance(attribute_list,list):
				if ("_children" in attribute_list):
					raise Exception("Warning: GETATTR - _children isn't a valid attribute")
				if not(all([isinstance(each,basestring) for each in attribute_list])):
					raise SyntaxError("Error: GETATTR - Invalid list of attributes! Only Strings are permitted inside the attribute list")
		else:
			raise SyntaxError("Error: GETATTR - Attribute list cannot be empty!")
		return (' '.join(["GET","ATTR",str(name),str(reference).upper(),str(node_details),str(attribute_list)]))
		
	def putNode(name,reference,node_details,newnode_json):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: PUTTREE - Name of a tree must be alpha numeric")
		else:
			raise SyntaxError("Error: PUTTREE - Name of a tree cannot be empty")
		if not(reference and reference.upper() in ["SELF"]):
			raise SyntaxError("Error: PUTTREE - Invalid reference type. Valid reference is SELF")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: PUTTREE - Invalid JSON for referring existing node")
			else:
				raise SyntaxError("Error: PUTTREE - Attribute details are not of type dict")
		if newnode_json:
			if isinstance(newnode_json,dict):
				try:
					newnode_json = json.dumps(newnode_json)
				except:
					raise SyntaxError("Error: PUTTREE - INVALID New Node JSON!!")
			else:
				raise SyntaxError("Error: PUTTREE - New Node definition should be of dict type")
		return (' '.join(["PUT","TREE",str(name),str(reference).upper(),str(node_details),str(newnode_json)]))
		
	def putAttrs(name,reference,node_details,newnode_json):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: PUTATTR - Name of a tree must be alpha numeric")
		else:
			raise SyntaxError("Error: PUTATTR - Name of a tree cannot be empty")
		if not(reference and reference.upper() in ["SELF","PARENT","CHILDREN","ANCESTOR","DESCENDANT"]):
			raise SyntaxError("Error: PUTATTR - Invalid reference type. Valid references are SELF, PARENT, CHILDREN, DESCENDANT  and ANCESTOR")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: PUTATTR - Invalid JSON for referring existing node")
			else:
				raise SyntaxError("Error: PUTATTR - Attribute details are not of type dict")
		if newnode_json:
			if isinstance(newnode_json,dict):
				if "_id" in newnode_json.keys() or "_children" in newnode_json.keys() :
					raise Exception("Warning: PUTATTR - _id & _children aren't the permissible types that can be put")
				try:
					newnode_json = json.dumps(newnode_json)
				except:
					raise SyntaxError("Error: PUTATTR - INVALID New Node JSON!")
			else:
				raise SyntaxError("Error: PUTATTR - New Node definition should be of dict type")
		else:
			raise SyntaxError("Error: PUTATTR - New Node JSON cannot be empty!")
			
		return (' '.join(["PUT","ATTR",str(name),str(reference).upper(),str(node_details),str(newnode_json)]))
	
	def delNode(name,reference,node_details):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: DELETETREE - Name of a tree must be alpha numeric")
		else:
			raise SyntaxError("Error: DELETETREE - Name of a tree cannot be empty")
		if not(reference and reference.upper() in ["SELF"]):
			raise SyntaxError("Error: DELETETREE - Invalid reference type. Valid reference is SELF")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: DELETETREE - Invalid JSON")
			else:
				raise SyntaxError("Error: DELETETREE - Attribute details are not of type dict")
		return (' '.join(["DELETE","TREE",str(name),str(reference).upper(),str(node_details)]))
	
	def delAttrs(name,reference,node_details,attribute_list):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: DELATTR - Name of the attribute must be alpha numeric")
		else:
			raise SyntaxError("Error: DELATTR - Name of th attribute cannot be empty")
		if not(reference and reference.upper() in ["SELF","PARENT","CHILDREN","ANCESTOR","DESCENDANT"]):
			raise SyntaxError("Error: DELATTR - Invalid reference type. Valid references are SELF, PARENT, CHILDREN, DESCENDANT  and ANCESTOR")
		if node_details:
			if isinstance(node_details,dict):
				try:
					node_details = json.dumps(node_details)
				except:
					raise SyntaxError("Error: DELATTR - Invalid JSON")
			else:
				raise SyntaxError("Error: DELATTR - Attribute details are not of type dict")
		if attribute_list:
			if not(isinstance(attribute_list,list)):
				raise SyntaxError("Error: DELATTR - Invalid Syntax for Attribute list! It can be a list of attibutes or * for all attributes")
			if isinstance(attribute_list,list):
				if ("_id" in attribute_list):
					raise Exception("Warning: DELATTR - _id isn't a valid attribute")
				if not(all([isinstance(each,basestring) for each in attribute_list])):
					raise SyntaxError("Error: DELATTR - Invalid list of attributes! Only Strings are permitted inside the attribute list")
		else:
			raise SyntaxError("Error: DELATTR - Attribute list cannot be empty!")
		return (' '.join(["DEL","ATTR",str(name),str(reference).upper(),str(node_details),str(attribute_list)]))
	
	def loadTree(name,path):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: GETATTR - Name of the attribute must be alpha numeric")
		else:
			raise SyntaxError("Error: GETATTR - Name of the attribute cannot be empty")
	
		if path:
			try:
				cwd = os.getcwd()
				os.chdir(path)
				os.chdir(cwd)
			except:
				raise OSError("Error: LOADTREE - Invalid Path! Specified Path Doesnot Exist")
		return (' '.join(["LOAD",name,path]))
	
	def descTree(name):
		if name:
			if not(str(name).isalnum()):
				raise SyntaxError("Error: GETATTR - Name of the attribute must be alpha numeric")
		else:
			raise SyntaxError("Error: GETATTR - Name of th attribute cannot be empty")
		return (' '.join(["DESCRIBE",name]))
		
	def showTrees():
		return (' '.join(["SHOW","TREES"]))