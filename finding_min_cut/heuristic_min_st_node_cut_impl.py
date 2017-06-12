# !/usr/bin/env python
# Name :  Madhur Rawat
# Organization: IIIT Delhi
# Date : 29/06/17

from __future__ import division
import math


#local import
import min_cut_constants
from as_graph_utility import is_reachable
from min_cut_utility import BFS
from min_cut_utility import print_path_if_reachable
from as_graph_utility import auxiliary_graph
from minimum_st_edge_cut import min_st_edge_cut



''' Takes a list of node_characteristics to be used for heuristic and 
	sets weight of nodes according to the heuristic
'''
def set_heuristic_weight(G, node_characteristics_list):

	for node in G.nodes():
		heuristic_weight = 0
		for node_characteristic in node_characteristics_list:
			heuristic_weight = heuristic_weight + G.node[node][node_characteristic]
		if heuristic_weight > 0:
			G.node[node][min_cut_constants.HEURISTIC_WEIGHT] = 1/heuristic_weight
		else: 
			G.node[node][min_cut_constants.HEURISTIC_WEIGHT] = 0.0

''' Returs a list of node_characteristics for the given heuristic
'''
def node_characteristic_list_for_heuristic(heuristic):
	if heuristic == min_cut_constants.HEURISTIC.PATH_FREQUENCY:
		return [min_cut_constants.PATH_FREQUENCY]
	elif heuristic == min_cut_constants.HEURISTIC.CUSTOMER_DEGREE:
		return [min_cut_constants.CUSTOMER_DEGREE]
	elif heuristic == min_cut_constants.HEURISTIC.PROVIDER_DEGREE:
		return [min_cut_constants.PROVIDER_DEGREE]
	elif heuristic == min_cut_constants.HEURISTIC.PEER_DEGREE:
		return [min_cut_constants.PEER_DEGREE]
	elif heuristic == min_cut_constants.HEURISTIC.CUSTOMER_CONE_SIZE:
		return [min_cut_constants.CUSTOMER_CONE_SIZE]
	elif heuristic == min_cut_constants.HEURISTIC.ALPHA_CENTRALITY:
		return [min_cut_constants.ALPHA_CENTRALITY]
	elif heuristic == min_cut_constants.HEURISTIC.BETWEENNESS_CENTRALITY:
		return [min_cut_constants.BETWEENNESS_CENTRALITY]



def defense_st_cut(G, source, sink, heuristic = None):

	if heuristic == None:
		heuristic = min_cut_constants.HEURISTIC.PATH_FREQUENCY
	node_characteristics_list = node_characteristic_list_for_heuristic(heuristic)
	
	set_heuristic_weight(G, node_characteristics_list)

	A = auxiliary_graph(G)

	R, st_edge_cut = min_st_edge_cut(A, '%sB' % source, '%sA' % sink)

	st_node_cut = set()

	for (source, sink) in st_edge_cut:
		AS_source = source[:-1]
		AS_sink = sink[:-1]
		# print st_edge_cut
		if AS_source == AS_sink:
			st_node_cut.add(AS_source)
		else:
			print "Warning. AS_source not equal to AS_sink. Non auxiliary edge cannot be in cut"
			print "Possibly no node-cut was found"
			break

	return st_node_cut




















	# st_cut = set()
	# st_cut_right_rem_nodes_dict = dict()
	# st_cut_left_rem_nodes_dict = dict()






	# for residual_path in residual_paths:
	# 	residual_path.reverse()
		
	# 	max_val = float('-inf')
	# 	max_node = None
	# 	max_left_remaining_path = []
	# 	max_right_remaining_path = []
	# 	for i, node in enumerate(residual_path):
	# 		if G.node[node][node_characteristic] > max_val:
	# 			max_val = G.node[node][node_characteristic]
	# 			max_node = node
	# 			max_right_remaining_path = residual_path[i + 1:]
	# 			max_left_remaining_path = residual_path[:i]

	# 	st_cut.add(max_node)
	# 	if not max_node in st_cut_right_rem_nodes_dict:
	# 		st_cut_right_rem_nodes_dict[max_node] = [max_right_remaining_path]
	# 	else:
	# 		st_cut_right_rem_nodes_dict[max_node].append(max_right_remaining_path)

	# 	if not max_node in st_cut_left_rem_nodes_dict:
	# 		st_cut_left_rem_nodes_dict[max_node] = [max_left_remaining_path]
	# 	else:
	# 		st_cut_left_rem_nodes_dict[max_node].append(max_left_remaining_path)

	# 	H = G.copy()
	# 	H.remove_nodes_from(st_cut)
	# print
	# print
	# print 'source', source, 'sink', sink
	# print 'st_cut', st_cut


	# if is_reachable(H, source, sink):
	# 	for cut_node in st_cut:
	# 		print
	# 		print 'cut_node', cut_node
	# 		print 'st_cut_right_rem_nodes_dict', st_cut_right_rem_nodes_dict
	# 		print 'st_cut_left_rem_nodes_dict', st_cut_left_rem_nodes_dict

	# 		replaced = False
	# 		if cut_node in st_cut_right_rem_nodes_dict:
	# 			st_cut_right_rem_paths = st_cut_right_rem_nodes_dict[cut_node]
	# 			for st_cut_right_rem_path in st_cut_right_rem_paths:
	# 				if st_cut_right_rem_path == None:
	# 					continue
	# 				for rem_node in st_cut_right_rem_path:
	# 					if is_reachable(H, source, rem_node):
	# 						print rem_node, 'source',print_path_if_reachable(H, source, sink)

	# 						st_cut.remove(cut_node)
	# 						st_cut.add(rem_node)
	# 						H = G.copy()
	# 						H.remove_nodes_from(st_cut)
	# 						print_path_if_reachable(H, source, sink)
	# 						replaced = True

	# 		if cut_node in st_cut_left_rem_nodes_dict and not replaced:
	# 			st_cut_left_rem_paths = st_cut_left_rem_nodes_dict[cut_node]
	# 			for st_cut_left_rem_path in st_cut_left_rem_paths:
	# 				if st_cut_left_rem_path == None:
	# 					continue
	# 				for rem_node in st_cut_left_rem_path:
	# 					if is_reachable(H, rem_node, sink):
	# 						print rem_node, 'sink', print_path_if_reachable(H, source, sink)
	# 						st_cut.remove(cut_node)
	# 						st_cut.add(rem_node)
	# 						H = G.copy()
	# 						H.remove_nodes_from(st_cut)
	# 						print_path_if_reachable(H, source, sink)

	# return st_cut
	
		