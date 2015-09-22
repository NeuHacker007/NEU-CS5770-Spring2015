import re
import os
import BitVector

path = 'strace/'
pattern = r'(\w+)\((.*(".*").*)?(.*)\)\s*=.*'
#pattern = r'(\w+)\((.*)\)\s*=.*'


count_samples=0	
database = set()
for fn in os.listdir(path):
     if os.path.isfile(path + fn):
        file = path + fn
        strace = open(file, 'r').read()
        match = re.findall(pattern, strace)

        for i in match:
                feature =  (i[0] + '(' +  i[2]  +  ')')
                m = re.match (r'.*(write\("samples|newfstatat).*', feature)
                if m:
                       continue
                #m = re.match(r'write(".*!/")')

                database.add(hash(feature))
	count_samples+=1

database =list(database)
#database = set(database)
#database.sort()
#for i in database:
#        print i

matrix= []
fingerprints = []
labels = []
sample = 0
for fn in os.listdir(path):
	if os.path.isfile(path + fn):
		# OK
		file = path + fn
		strace = open(file, 'r').read()
	        match = re.findall(pattern, strace)
                sample_fingerprint = [0] * len(database)

		for i in match:
	                feature =  hash(i[0] + '(' +  i[2]  +  ')')
			
			try:
				search_index = database.index(feature)
			except ValueError:
				search_index = -1
			if search_index > -1:
				sample_fingerprint[search_index] = 1
		
		fingerprints.append({'sample': file, 'fingerprint':sample_fingerprint})
		matrix.append(sample_fingerprint)
		labels.append(file)
		sample += 1
#print fingerprinta

#clusters = []
#while(len(fingerprints) > 10):
#	for f1 in fingerprints:
#		bv1 = BitVector( bitlist = f1['fingerprint'] )
#		for f2
#		bv2 = BitVector() #print( str( bv1.jaccard_distance( bv2 ) ) )
	
print labels
print matrix


print "Number of instructions ",  len(database)


