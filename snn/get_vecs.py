import neuro
import risp

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../graphics" )
from qt_node import Node
from qt_edge import Edge


risp_config = {
  "leak_mode": "none",
  "min_weight": -1,
  "max_weight": 1,
  "min_threshold": -1,
  "max_threshold": 1,
  "max_delay": 5,
  "discrete": False
}

def get_vecs_from_dicts(node_dict, edge_dict):

    proc = risp.Processor(risp_config)

    net = neuro.Network()
    net.set_properties(proc.get_network_properties())

    spikes = []

    for n in node_dict.values():
        print(n)

        node = net.add_node(n.id)
        node.set("Threshold", n.threshold)
        
        if(n.nodeType == "input"):
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

    proc.apply_spikes(spikes)

    proc.run(10)
    v = proc.neuron_vectors()
    print(v)

    return v






