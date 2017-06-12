# !/usr/bin/env python
# Name :  Madhur Rawat
# Organisation: IIIT Delhi
# Date : 16/06/17

import math
import networkx as nx

#local imports
import min_cut_constants
import constants


def auxiliary_graph(G):
	''' For directed graphs
	Returns an auxiliary_graph for use to find node cut set from edge cut set
	References
	----------
	Abdol-Hossein Esfahanian. Connectivity Algorithms.
		http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
	'''
	if not G.is_directed():
		print 'Only directed graphs supported currently'
		exit()

	H = nx.DiGraph()
	for i, node in enumerate(G):
		H.add_node('%sA' % node)
		H.add_node('%sB' % node)
		H.add_edge('%sA' % node, '%sB' % node)

		# Transfer the node weight to edge weight
		H.edge['%sA' % node]['%sB' % node][min_cut_constants.HEURISTIC_WEIGHT] = G.node[node][min_cut_constants.HEURISTIC_WEIGHT]

	edges = []
	for (source, target) in G.edges_iter():
		H.add_edge('%sB' % source, '%sA' % target)

		# Set inf weight to original edge to prevent their inclusion in cut
		H.edge['%sB' % source]['%sA' % target][min_cut_constants.HEURISTIC_WEIGHT] = float('inf')

	return H

def as_graph_undirected(path_file, IS_CBGP, mapping_dict):

	G = nx.Graph()
	pf_dict = {}
	with open(path_file) as fi:
		count=0
		for line in fi:
			ll=line.strip()
			splits=ll.split(' ')
			temp_set=set()
			
			if len(splits) < 2:
				continue

			for idx in range(len(splits) - 1, 1, -1): #upto before start AS index.
				currAS = splits[idx]
				prevAS = splits[idx - 1]

				if currAS!=prevAS:	
					if IS_CBGP:
						actualCurrentAS = mapping_dict[currAS]
						actualPrevAS = mapping_dict[prevAS]
						G.add_node(actualCurrentAS)
						G.add_node(actualPrevAS)
						G.add_edge(actualCurrentAS, actualPrevAS)
						if not actualPrevAS in pf_dict:
							pf_dict[actualPrevAS] = 1
						else:
							pf_dict[actualPrevAS] = pf_dict[actualPrevAS] + 1
						
					else:						
						G.add_node(currAS)
						G.add_node(prevAS)
						G.add_edge(currAS, prevAS)
						if not prevAS in pf_dict:
							pf_dict[prevAS] = 1
						else:
							pf_dict[prevAS] = pf_dict[prevAS] + 1

				if currAS=="SUCCESS":
					print splits

	for node in G.nodes():
		G.node[node][min_cut_constants.PATH_FREQUENCY] = 0
	for node in pf_dict:
		G.node[node][min_cut_constants.PATH_FREQUENCY] = pf_dict[node]

	return (G)

def as_digraph(path_file, IS_CBGP, USING_START, mapping_dict, dest_as_list = None, G = None, pf_dict = None) :
	# All AS from which traceroute is done. Should have most AS from IL_AS.txt file
	all_start_as = set()
	all_dest_as = set()

	# All AS appearing in paths. May contain extra ASes.
	all_as_set = set()
	if G == None:
		G = nx.DiGraph()
	if USING_START:
		if dest_as_list == None:
			print "Warning . dest_as_list = None"
		START = "start"
		G.add_node(START)
	if pf_dict == None:
		pf_dict = {}

	with open(path_file) as fi:
		count=0
		for line in fi:
			ll=line.strip()
			splits=ll.split(' ')
			temp_set=set()
			
			if len(splits) < 2:
				continue

			if not splits[1] == "SUCCESS":
				all_start_as.add(mapping_dict[splits[len(splits) - 1]])
				all_dest_as.add(mapping_dict[splits[1]])

			for idx in range(len(splits) - 1, 1, -1): #upto before start AS index.
				currAS = splits[idx]
				prevAS = splits[idx - 1]

				if currAS!=prevAS:	
					if IS_CBGP:
						actualCurrentAS = mapping_dict[currAS]
						actualPrevAS = mapping_dict[prevAS]
						if not actualPrevAS in pf_dict:
							pf_dict[actualPrevAS] = 1
						else:
							pf_dict[actualPrevAS] = pf_dict[actualPrevAS] + 1
						G.add_node(actualCurrentAS)
						G.add_node(actualPrevAS)
						G.add_edge(actualCurrentAS, actualPrevAS)
						G.edge[actualCurrentAS][actualPrevAS][min_cut_constants.CAPACITY] = 1
						all_as_set.add(actualCurrentAS)
						all_as_set.add(actualPrevAS)
						if USING_START:
							if actualCurrentAS in dest_as_list:
								pass
							else:
								G.add_edge(START, actualCurrentAS)
								G.edge[START][actualCurrentAS][min_cut_constants.CAPACITY] = 1

							if actualPrevAS in dest_as_list:
								pass
							else:
								G.add_edge(START, actualPrevAS)
								G.edge[START][actualPrevAS][min_cut_constants.CAPACITY] = 1
					else:
						if not prevAS in pf_dict:
							pf_dict[prevAS] = 1
						else:
							pf_dict[prevAS] = pf_dict[prevAS] + 1
						G.add_node(currAS)
						G.add_node(prevAS)
						G.add_edge(currAS, prevAS)
						G.edge[currAS][prevAS][min_cut_constants.CAPACITY] = 1
						all_as_set.add(currAS)
						all_as_set.add(prevAS)
						if USING_START:
							if currAS in dest_as_list:
								pass
							else:
								G.add_edge(START, currAS)
								G.edge[START][currAS][min_cut_constants.CAPACITY] = 1
							if prevAS in dest_as_list:
								pass
							else:
								G.add_edge(START, prevAS)
								G.edge[START][prevAS][min_cut_constants.CAPACITY] = 1

				if currAS=="SUCCESS":
					
					print splits

	betweenness_centrality_dict = nx.betweenness_centrality(G)

	(customers, providers, peers) = compute_degrees()

	customer_conesize = get_customer_conesize()

	for node in G.nodes():
		G.node[node][min_cut_constants.PATH_FREQUENCY] = 0

		G.node[node][min_cut_constants.BETWEENNESS_CENTRALITY] = betweenness_centrality_dict[node]

		if node in customers:
			G.node[node][min_cut_constants.CUSTOMER_DEGREE] = len(customers[node])
		else:
			G.node[node][min_cut_constants.CUSTOMER_DEGREE] = 0

		if node in providers:
			G.node[node][min_cut_constants.PROVIDER_DEGREE] = len(providers[node])
		else:
			G.node[node][min_cut_constants.PROVIDER_DEGREE] = 0

		if node in peers:
			G.node[node][min_cut_constants.PEER_DEGREE] = len(peers[node])
		else:
			G.node[node][min_cut_constants.PEER_DEGREE] = 0

		if node in customer_conesize:
			G.node[node][min_cut_constants.CUSTOMER_CONE_SIZE] = customer_conesize[node]
		else:
			G.node[node][min_cut_constants.CUSTOMER_CONE_SIZE] = 0

	for node in pf_dict:
		G.node[node][min_cut_constants.PATH_FREQUENCY] = pf_dict[node]

	return (G, all_start_as, all_dest_as, pf_dict)

def is_reachable(G, s, d):
		visited = dict()
		for vertex in G.nodes():
			visited[vertex] = False
		queue=[]
		queue.append(s)
		visited[s] = True
		while queue:
		    n = queue.pop(0)
		    if n == d:
		        return True
		    for i in G.neighbors(n):
		        if visited[i] == False:
		            queue.append(i)
		            visited[i] = True
		return False

def get_customer_conesize():
	CONESIZE = constants.TEST_DATA + "customer_conesize.txt"
	fi = open(CONESIZE)
	conesizes = dict()
	for line in fi:
		line = line.strip()
		splits = line.split()
		AS = splits[0]
		conesize = splits[1]
		if not AS in conesizes:
			conesizes[AS] = int(conesize)

	return conesizes

def compute_degrees():
	CAIDAREL = constants.TEST_DATA + "caidarel.txt"
	fi = open(CAIDAREL)
	customers = {}
	providers = {}
	peers = {}
	for line in fi:
		line = line.strip()
		splits = line.split()
		provider = splits[0]
		customer = splits[1]
		rel = splits[2]

		if rel == "1":
			if not provider in customers:
				customers[provider] = {customer}
			else:
				customers[provider].add(customer)
			if not customer in providers:
				providers[customer] = {provider}
			else:
				providers[customer].add(provider)
		elif rel == "0":
			if not provider in peers:
				peers[provider] = {customer}
			else:
				peers[provider].add(customer)
			if not customer in peers:
				peers[customer] = {provider}
			else:
				peers[customer].add(provider)

		else:
			
			print "Invalid caidarel file"
			exit()
	return (customers, providers, peers)


def paths_between_st_util(G, u, d, visited, path):
	visited[u]= True
	path.append(u)
	print 'path: ', len(path)
	if u ==d:
	    print 'path: ', list(reversed(path))
	else:
	    for i in G.neighbors(u):

	        if visited[i]==False:
	            paths_between_st_util(G, i, d, visited, path)
	path.pop()
	visited[u]= False

def paths_between_st(G ,source, sink):
	print 'paths_between_st', source, sink
	visited = dict()
	for vertex in G.nodes():
		visited[vertex] = False
	path = []
	paths_between_st_util(G, source, sink,visited, path)

if __name__ == "__main__":

	# Test auxiliary graph
	# G = nx.DiGraph()
	# G.add_nodes_from((4,5,6))
	# G.node[4][min_cut_constants.HEURISTIC_WEIGHT] = 100
	# G.node[5][min_cut_constants.HEURISTIC_WEIGHT] = 500
	# G.node[6][min_cut_constants.HEURISTIC_WEIGHT] = 900
	# G.add_edge(4,5)
	# G.add_edge(5,6)

	# H = auxiliary_graph(G)
	# for (s,t) in H.edges_iter():
	# 	print s, t, type(H.edge[s][t])
	compute_degrees()

	
