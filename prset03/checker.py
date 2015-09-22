#!/usr/bin/env python
import sys, json

import re


sys.path.append('model')
sys.path.append('model/strace')

import script

if(len(sys.argv) < 3):
	print "usage: "+sys.argv[0]+' /path/to/solution.json /path/to/checking.strace [-s "to show malice node"]'
	exit(0)


def path_is_in(generic, specific):
	i = 0
	if len(generic)> len(specific): return False
	

	if generic == '':
		if re.match(r'(0)|(\d+)|NULL|(0[xX][0-9a-fA-F]+)', specific): return True
	
	
	for  c in generic:
		if c != specific[i]:
			return False
		i+=1
	return True

str_json_path = sys.argv[1]
str_strace_path = sys.argv[2]

moduleJSON = open(str_json_path).read()
script.get_augmented_strace_get_set = False
check = script.get_augmented_strace(str_strace_path)

module = json.loads(moduleJSON)
module = module['model_augmented']


#for pair in check.module:
#	print [pair.syscall_1, pair.syscall_2, pair.syscall_1_arg, pair.syscall_2_arg]
#for entry in module:
#	print [entry['syscall_1'], entry['syscall_2'], entry['syscall_1_arg'], entry['syscall_2_arg']]


result = {'malicious': False, 'syscall': None, 'syscall_arg': None}

#for pair in module:
#	print pair
for pair in check.module:
	flag = False
	for entry in module:
		if pair.syscall_1 == entry['syscall_1'] and pair.syscall_2 == entry['syscall_2'] \
		and (pair.syscall_1_arg == entry['syscall_1_arg'] or path_is_in(entry['syscall_1_arg'],pair.syscall_1_arg)) \
		and (pair.syscall_2_arg == entry['syscall_2_arg'] or path_is_in(entry['syscall_2_arg'],pair.syscall_2_arg)):
			flag = True
			break
	if flag == False:
		if len(sys.argv) > 3 and sys.argv[3] == '-s': 
			#print "Malice!", pair
			result['node'] = json.loads(str(pair))
			
		result['malicious'] = True
		result['syscall'] = pair.syscall_1
		result['syscall_arg'] = pair.syscall_1_arg
		break



print json.dumps(result, sort_keys=False, indent=4)
