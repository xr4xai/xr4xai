import neuro
import risp

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../graphics" )
from qt_node import Node
from qt_edge import Edge

import json

risp_config = {
  "leak_mode": "none",
  "min_weight": -1,
  "max_weight": 1,
  "min_threshold": -1,
  "max_threshold": 1,
  "max_delay": 5,
  "discrete": False
}

def get_vecs_from_dicts(node_dict, edge_dict, min = 0.0, max = 10.0):

    proc = risp.Processor(risp_config)

    net = neuro.Network()
    net.set_properties(proc.get_network_properties())

    spikes = []

    for n in node_dict.values():
        print(n)

        node = net.add_node(n.id)
        node.set("Threshold", n.threshold)
        
        if(n.nodeType == "input"):
            print(n.id, " is input")
            
            net.add_input(n.id)
            
            for i in n.input_spikes:
                spikes.append( neuro.Spike(id=n.id, time=i, value=1) )
                

        if(n.nodeType == "output"):
            net.add_output(n.id)

    for e in edge_dict.values():
        edge = net.add_edge(e.sourceNode.id, e.sinkNode.id)
        edge.set("Weight", e.weight)
        edge.set("Delay", e.delay)


    proc.load_network(net)
    print(net)

    for i in range(net.num_nodes()):
        proc.track_neuron_events(i)

    print(spikes)
    proc.apply_spikes(spikes)

    proc.run(max)
    v = proc.neuron_vectors()
    print(v)

    return v

def write_to_file(node_dict, edge_dict, filename):

    with open(filename, "w") as file:
        
        out_node_dict = {}
        out_edge_dict = {}

        for n in node_dict:
            out_node_dict[n] = node_dict[n].outputNodeAsDict()

        
        print(out_node_dict)

        for e in edge_dict:
            out_edge_dict[e] = edge_dict[e].outputEdgeAsDict()

        print(out_edge_dict)

        out = {"config":risp_config, "nodes":out_node_dict, "edges":out_edge_dict}
        
        json.dump(out, file)

def read_from_file(filename, parent):
    global risp_config

    print("Opening file ", filename)

    with open(filename, "r") as file:
        
        dict = json.load(file)

    
    try:
        risp_config = dict["config"]
    except KeyError:
        print("No 'config' key, using default")
        
    in_node_dict = dict["nodes"]
    in_edge_dict = dict["edges"]


    node_dict = {}
    edge_dict = {}

    for n in in_node_dict:
        
        node = Node(parent, float( in_node_dict[n]["posX"] ), float( in_node_dict[n]["posY"] ) , int(n), in_node_dict[n]["nodeType"] ) 
        node.title = in_node_dict[n]["title"]
        node.threshold = float(in_node_dict[n]["threshold"])
        node.input_spikes = in_node_dict[n]["input_spikes"]

        node_dict[ int(n) ] = node


    for e in in_edge_dict:
        edge = Edge( node_dict[ int(in_edge_dict[e]["sourceNode"] ) ], node_dict[ int(in_edge_dict[e]["sinkNode"]) ] , float( in_edge_dict[e]["weight"] ), float( in_edge_dict[e]["delay"] ) )
        edge_dict[e] = edge
    
    print(node_dict)
    print(edge_dict)
    return node_dict, edge_dict


