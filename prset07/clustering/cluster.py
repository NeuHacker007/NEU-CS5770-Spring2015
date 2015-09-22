import sys, numpy, scipy
from scipy.cluster.hierarchy import *
from scipy.spatial.distance import pdist, squareform
import json

import matplotlib.pyplot as plt


def search_id(node, id):
        if node.get_id() ==  id:
                return node

        found = None
        if node.left:
                found = search_id( node.left, id)
        if found == None:
                if node.right:
                        found =  search_id( node.right, id )

        return found

def get_children(node, children):
        if node.right:
                children.append(node.right)
                children.extend(get_children(node.right, []))
        if node.left:
                children.append(node.left)
                children.extend(get_children(node.left, []))

        return children


def print_node(id):
	global ROOT, id2name, labels
	leaf_labels = []
	data = []	

        node = search_id(ROOT, id)
	children =  get_children(node, [])
	if len(children)>0:
		for c in children:
			if c.is_leaf():
				sample_name = str(id2name[c.get_id()])
				idx = labels.index(sample_name) 
				leaf_labels.append( sample_name )
				data.append(matrix[idx]) 
		return (leaf_labels, data)
	else:
		sample_name = str(id2name[node.get_id()])
                idx = labels.index(sample_name)

		return ([id2name[node.get_id()]], [matrix[idx]])




config_file = open(sys.argv[1],'r')
labels = []
matrix = []
i = 0
for line in config_file:
	data = line.strip().split()
	labels.append(data[0])
	row = [int(x) for x in data[1:]]
	matrix.append(row)	
	
	i+=1
features_list=[]
features_file=open('features')
for j in features_file:
	features_list.append(j.split()[0])
n=i
k=10

id2name = dict(zip(range(len(labels)), labels))
X = numpy.array(matrix)
print X.shape
D = (pdist(X, 'jaccard'))
Z = linkage(D, method='average')

leaves = leaves_list(Z)
ROOT = to_tree(Z, rd=False)

print 'How many leaves we got?', len(leaves)


#plt.figure(figsize=(30,10))
color_t=Z[-(k-1),2]
P =dendrogram(Z,color_threshold=color_t, labels=labels, truncate_mode='lastp')
plt.title('Reduced:  Dendrogram for All samples')
plt.savefig('graphics/1-3.png')
plt.show()
plt.clf()



def cluster(t):
	global Z
	T = fcluster(Z, t, 'distance')
	T = fclusterdata(X, t, criterion='distance', metric='jaccard', method='average')
	L = leaders(Z, T) 

	_s = 0
	_c = 2
	_counter = 0
	if len(sys.argv) > 2 and sys.argv[2] == 'json':
		result= {'clusters': []}
		for leader_node in L[0]:
			
			cluster = {}
			cluster['samples'] = []
			cluster['features'] = []

			(leaves, newMatrix) = print_node(leader_node)
			_ss=0
			newMatrix_arr=numpy.array(newMatrix)
			matched = numpy.all(newMatrix_arr == newMatrix_arr[0,:], axis = 0)
			for col in range(len(matched)):
				if newMatrix[0][col] == 0: continue
				test = matched[col]
				if test == True:
					_ss+=1
					cluster['features'].append(features_list[col])				
			#cluster['number_of_features']=_ss
			"""if len(newMatrix) < 2:  #< 2 or len(newMatrix) > 24 :
				#print 'skipped:', len(newMatrix)
				_s +=1
				_c+=1
				continue
			"""
			_l = len(leaves)
			if _l == 1:
				_s += 1 
			if(len(sys.argv) > 4):
				cluster['samples'].append( len(leaves) )
			else:
				cluster['samples'].append( leaves )
			_counter+=len(leaves)

			"""
			_X = numpy.array(newMatrix)
			_D = (pdist(_X, 'jaccard'))
			_Z = linkage(_D, method='complete')
			plt.cla()
			plt.clf()
			fig=plt.figure()
			plt.title('Cluster: ' + str(_c)  +  ', samples: '+ str(len(leaves))  )
			dendrogram(_Z, labels=leaves, leaf_rotation=60)
			plt.savefig('graphics/{0}.png'.format(_c))
			plt.close(fig)
			"""
			#show()
			result['clusters'].append(cluster)

			_c+=1

		print json.dumps(result, sort_keys=False, indent=1)

		print 'Using t=', str(t), ' How many Clusters?=', len(L[0]), ' Singleton=',str(_s)
		print 'Total:', _counter

if len(sys.argv) > 3:
	t = 0.345
	try:
		t = float(sys.argv[3])
	except Error:
		print 'Error passing the threshold value'
	cluster(t)
else:
	cluster(0.31)

