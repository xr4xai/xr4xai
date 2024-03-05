import neuro
import risp

risp_config = {
  "leak_mode": "none",
  "min_weight": -1,
  "max_weight": 1,
  "min_threshold": -1,
  "max_threshold": 1,
  "max_delay": 5,
  "discrete": False
}

def test_net_spike_vec():

    proc = risp.Processor(risp_config)

    net = neuro.Network()
    net.set_properties(proc.get_network_properties())


    # Builds the test network from the second jupyter notebook
    node = net.add_node(0)
    node.set("Threshold", 0)
    net.add_input(0)

    for i in range(1,4):
        node = net.add_node(i)
        node.set("Threshold", 0.75)
        net.add_output(i)
        
    edge = net.add_edge(0,1)
    edge.set("Weight", 1)
    edge.set("Delay", 1)

    edge = net.add_edge(0,2)
    edge.set("Weight", 1)
    edge.set("Delay", 3)

    edge = net.add_edge(0,3)
    edge.set("Weight", 0.5)
    edge.set("Delay", 1)

    proc.load_network(net)
    print(net)
    for i in range(net.num_nodes()):
        proc.track_neuron_events(i)

    spikes = [neuro.Spike(id=0, time=i, value=1) for i in range(3)]
    proc.apply_spikes(spikes)

    proc.run(5)
    v = proc.neuron_vectors()
    print(v)

    return v
