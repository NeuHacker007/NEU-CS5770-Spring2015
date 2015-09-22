import sys, re, json
from operator import itemgetter

from collections import OrderedDict

class Node:
	def __init__(self, call_1, call_2):
                self.syscall_1 = call_1
                self.syscall_2 = call_2
	def __str__(self):
	
        	return json.dumps(self.__dict__)

	def __eq__(self, other): 
        	return self.__dict__ == other.__dict__

class Augmented_node:
	def __init__(self, call_1, call_2,  arg_1, arg_2):
		self.syscall_1 = call_1
		self.syscall_2 = call_2
		self.syscall_1_arg  = arg_1
		self.syscall_2_arg = arg_2
	def __str__(self):
        	return json.dumps(self.__dict__, sort_keys=True)

	def __eq__(self, other): 
        	return self.__dict__ == other.__dict__

class FSA_node:
        def __init__(self, call,  arg, id=0):
                self.syscall = call
                self.arg = arg
		self.id = id
                self.successors = []
        def __str__(self):
                return str(self.__dict__)
		#return json.dumps(self.__dict__, sort_keys=True)

        def __eq__(self, other):
                return self.__dict__ == other.__dict__	
	def check(self, other):
		return (self.syscall == other.syscall and self.arg == other.arg)
class Node_list:
	def __init__(self, l):
		self.module = l
	def __str__(self):
		out = '"module": ['
		i = 0
		for node in self.module:
			out += str(node)
			if (i != len(self.module)-1):
				out += ', '
			i += 1
		return out + ']'
	def str_for_json_load(self, include_mod=False):	
		out = '{['
                i = 0
                for node in self.module:
                        out += str(node)
                        if (i != len(self.module)-1):
                                out += ', '
                        i += 1                
		return out + ']}'
	def __len__(self):
		return len(self.module)			
strace_nb=0
def get_strace(*path):
	global strace_nb
	module = []
	strace = ''
	for path_l in path:
                strace += open(path_l).read()
	m =  re.findall(r'(\w+)\(.*', strace)
	l = len(m)
	strace_nb+=l
	for i in range(l):
		if i != l-1:
			module.append( [m[i] , m[i+1]])
	
	node_set = []
	for entry in module:
                        n = Node(entry[0], entry[1])
                        if n not in node_set:
                                node_set.append(n)
	return Node_list(node_set)

get_augmented_strace_get_set = True
def get_augmented_strace(*path):
	global get_augmented_strace_get_set
        module = []
        strace = ''
	for path_l in path:
		strace += open(path_l).read()

        m = re.findall(r'(\w+)\(((".*?")|(NULL)|(\w+)|(0[xX][0-9a-fA-F]+)|(\d+))(,.*)?\)\s*=.*', strace)
	l = len(m)
	#print "strace Augmented, ", l
	i = 0
	syscall_pairs = []
	args = []
	for t in m:
		if i != l-1:
			t = list(t)
                        t_s = list(m[i+1])
                        t[1] = t[1].replace('"', '')
                        t_s[1] = t_s[1].replace('"', '')
                        t =  tuple(t)
                        t_s = tuple(t_s)
                        syscall_pairs.append( [t[0], t_s[0]])
                        args.append([t[1], t_s[1]])
                        module.append( [ t[0] , t[1], t_s[0], t_s[1]]  )
        	i += 1

	# If we just want to show every thing, without going into merging...
	if not get_augmented_strace_get_set:
		list_augmented_nodes = []
		for m in module:
	                list_augmented_nodes.append(Augmented_node(m[0], m[2], m[1],  m[3]))
		get_augmented_strace_get_set = True
		return Node_list(list_augmented_nodes)
	
	
	i = 0
	matching_d={}
	module_list=[]
	for entry in syscall_pairs:
		
		entry = tuple(entry)
		if entry in matching_d.keys():
			continue
		#print "     Now working     ------------"
		#print  "   " + str(entry)
		#print " ---- "
		matching_d[entry]= {}
		matching_d[entry]['i'] = i
		matching_d[entry]['arg_1'] = []
		matching_d[entry]['arg_2'] = []
		
		module_entry = None#{'node' : entry, 'i': i}
                module_list.append(module_entry)

		index = 0
		for x in syscall_pairs:
			x = tuple(x)
			if x == entry:	
				matching_d[entry]['arg_1'].append( args[index][0])
                                matching_d[entry]['arg_2'].append( args[index][1])
			index += 1
		
			
		# now apply long_substr
		matching_d[entry]['arg_1_longsubstr'] = long_common_arr(matching_d[entry]['arg_1'])
                matching_d[entry]['arg_2_longsubstr'] = long_common_arr(matching_d[entry]['arg_2'])
		
		#if entry[0] == 'brk': 	
		#	print "remove"
		#	matching_d[entry]['arg_1_longsubstr'] = ''
		#if entry[1] == 'brk':
		#	print "remove 2" 
		#	matching_d[entry]['arg_2_longsubstr'] = ''
		module_list[i] = Augmented_node(entry[0], entry[1], matching_d[entry]['arg_1_longsubstr'],  matching_d[entry]['arg_2_longsubstr'])
		#print_list_each (module_list)
		#print "--------------------------------"
		i += 1
	#print_list (syscall_pairs)
	#print_list(module)
	list_augmented_nodes = []
	for key in matching_d.keys():
		#print "Entry:", key
		#print 'Arg 1 : ',matching_d[key]['arg_1_longsubstr']
                #print 'Arg 2 : ',matching_d[key]['arg_2_longsubstr']
		#print "Args 1 list:", matching_d[key]['arg_1']
		#print "Args 2 list:", matching_d[key]['arg_2']
		#print "------------"
		list_augmented_nodes.append(Augmented_node(key[0], key[1], matching_d[key]['arg_1_longsubstr'],  matching_d[key]['arg_1_longsubstr']))
	
	#sorted_list =sorted(module_list, key=itemgetter('i')) 
	
	return Node_list(module_list)
	al = Node_list(list_augmented_nodes)
	#print_list(al.l)
	return al


def print_list(module, name="LIST"):
	print "Print list, " + name + ":" + str(len(module))
        print module
	print "END Print List --------"
	return
	
def print_list_each(module, name="LIST"):
        print "Print list, " + name + ":" + str(len(module))
        for m in module: print m
        print "END Print List --------"
        return

def long_common_str(str1, str2):
	s = ''
	c =''
	least = len(str1)
	if (len(str2) < least): least = len(str2)
	for i in range(least):
		c = str1[i]
		if c == str2[i]:
			s += c
		else: break
	return s
def long_common_arr(data):
	s = ''
	for string in data:
        	m = re.match(r'(\d+)|(NULL)|(0[xX][0-9a-fA-F]+)',string, re.I)
        	if m:
        		return ''
	if len(data) > 0: 
		s = data[0]
		for i in range(len(data)):
			if i != len(data) - 1:
				s = long_common_str(s, data[i+1])
	return s




def get_fsa(*path):
        module = []
	iterate_model = []
        strace = ''
	level=0
        for path_l in path:
		# first, build current level
                strace = open(path_l).read()
       		m = re.findall(r'(\w+)\(((".*?")|(NULL)|(\w+)|(0[xX][0-9a-fA-F]+)|(\d+))(,.*)?\)\s*=.*', strace)
        	l = len(m)
        	i = 0
        	for t in m:
                        t = list(t)
                        t[1] = t[1].replace('"', '')
                        t =  tuple(t)
                        module.append( FSA_node( t[0] ,  t[1], i))
                	i += 1
		# now iterate through previous model
		if level==0:
			for node in module:
				iterate_model.append(node)
			level +=1
			continue

		i_1 = 0
		i_2 = 0
		for node in module:
			for base_node in iterate_model:		
				if node.check(base_node):
					#Find successors
					successors = base_node.successors
					i = base_node.id+1
					for succ in module[node.id+1:]:
						added = False
						if i < len(iterate_model) and not succ.check(iterate_model[i]):
							flag = False
							for exist_succ in base_node.successors:
							 	if exist_succ.check(succ): flag =True
							if flag == False: 
								successors.append(succ)
								added = True
						if (added == False):
							break
						i+=1
								
					base_node.successors = successors

		for node in module:
                        flag = False
                        for base_node in iterate_model:
                                if node.check(base_node):
                                        flag = True
                                        break

                        if flag == False:
                                node.id = len(iterate_model)
                                iterate_model.append(node)

		level +=1
	#print_list_each(iterate_model)
	return Node_list(iterate_model)	



if len(sys.argv) > 1 and sys.argv[1] == '-s':

	s1 = 'strace/prset03_cat.strace'
	s2 = 'strace/prset03_cat_2.strace' 
	s3 = 'strace/prset03_hash.strace'
	s4 = 'strace/prset03_hash_2.strace'
	s5 = 'strace/prset03_verify.strace'
	s6 = 'strace/prset03_verify_2.strace'
	s7 = 'strace/exploit.strace'

	module = get_strace(s1,s2,s3,s4,s5,s6)
#get_augmented_strace_get_set=False
	module_aug     = get_augmented_strace(s1,s2,s3,s4,s5,s6)
	module_malice = get_augmented_strace(s7)
	module_fsa = get_fsa(s1,s2)
#for i in module_malice.module:
#	flag = False
#	for x in module.module:
#		if(i.syscall_1 == x.syscall_1 and i.syscall_2 == x.syscall_2):
#			flag = True
#			continue
#	if flag == False:
#		print "couldn't find this in module"
#		print i	


#print_list(module_aug, 'Augmented Module')
#print_list(module, 'Model Coverage')
#print_list(module_malice, "malice system calls path")

def out_fsa():
	out = '{"module": ['                    
	cc = 0
	for i in module_fsa.module:
		out += '{"syscall": "'+i.syscall+'", "id": '+str(i.id)+', "arg": "'+i.arg+'"'
		out += ', "successors": '
		if len(i.successors) > 0:
			out += '[ '
			c = 0
			for s in i.successors:
				out += str(s.id)
				if c!=len(i.successors)-1: out += ','
				c+=1
			out += ' ]'
		else:
			out += 'null'
		out += '}'
		if cc!=len(module_fsa.module)-1: out += ','	
		cc+=1	
	out +=']}'
	return out



if len(sys.argv) > 1 and sys.argv[1] == '-s':
	result = {}
	result['model'] = json.loads('{'+str(module)+'}')['module']
	result['mimicry_possible'] = True
	result['model_augmented'] = json.loads('{'+str(module_aug)+'}')['module']
	result['mimicry_augmented_possible'] = False
	result['model_fsa'] = json.loads(out_fsa())
	sort_order = ['model', 'mimicry_possible', 'model_augmented', 'mimicry_augmented_possible', 'model_fsa']
	result_ordered = OrderedDict(sorted(result.iteritems(), key=lambda (k, v): sort_order.index(k)))
	print json.dumps(result_ordered, indent=4)	



