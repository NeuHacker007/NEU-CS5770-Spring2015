#! /usr/bin/env python
import re
import os
import json


def djb2(key):
    hash = 5381 
    for k in key:
       hash = ((hash << 5) + hash) + ord(k) 
    return hash


path = '../strace/'
pattern = r'(\w+)\((.*?(".*?").*?|.*)\)\s*=.*'


columns_log=open('features', 'w')
config=open('cluster_config', 'w')

count_samples=0	
database = set()
files = os.listdir(path)
files.sort()



for fn in files:
     if os.path.isfile(path + fn):
        file = path + fn
        strace = open(file, 'r').read()
        match = re.findall(pattern, strace)

        for i in match:
                feature =  (i[0] + '(' +  i[2]  +  ')')
                #m = re.match (r'.*(newfstatat).*', feature)
                #if m:
                #       continue
                database.add((feature))
		#database.add(djb2(feature))
	count_samples+=1

columns = []
database =list(database)

for i in range(len(database)):
	columns.append(database[i])
	database[i] = djb2(database[i])

print len(database)
print len(columns)	

for item in columns:
  columns_log.write("%s\n" % item)
columns_log.close()
#exit()

matrix= []
fingerprints = []
labels = []
sample = 0
for fn in files:
	if os.path.isfile(path + fn):
		# OK
		file = path + fn
		strace = open(file, 'r').read()
	        match = re.findall(pattern, strace)
                sample_fingerprint = ['0'] * len(database)
		
		for i in match:
			# change hash
	                feature =  djb2(i[0] + '(' +  i[2]  +  ')')
			
			try:
				search_index = database.index(feature)
			except ValueError:
				search_index = -1
			if search_index > -1:
				sample_fingerprint[search_index] = '1'
		
		fingerprints.append({'sample': file, 'fingerprint':sample_fingerprint})
		matrix.append(sample_fingerprint)
		labels.append(fn.split('.')[0])
		sample += 1

		config.write(fn.split('.')[0] +  ' ' +  ' '.join(sample_fingerprint) + '\n')
print sample, 'written to congfig_input'
config.close()

