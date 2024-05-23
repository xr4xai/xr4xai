class Node:
    tracking_id = -1
    snn_id = -1
    posvec = None
    rotvec = None
    node_type = None



    def __init__(self, **kwargs):
        if("tracking_id" in kwargs): self.tracking_id = kwargs["tracking_id"]
        if("snn_id" in kwargs): self.snn_id = kwargs["snn_id"]
        if("node_type" in kwargs): self.node_type = kwargs["node_type"]        

class Edge:
    snn_id = -1
    source_tracking_id = -1
    sink_tracking_id = -1
    source_snn_id = -1
    sink_snn_id = -1

    def __init__(self, **kwargs):
        if("snn_id" in kwargs): self.snn_id = kwargs["snn_id"]
        if("source_tracking_id" in kwargs): self.source_tracking_id = kwargs["source_tracking_id"]
        if("sink_tracking_id" in kwargs): self.sink_tracking_id = kwargs["sink_tracking_id"]
        if("source_snn_id" in kwargs): self.source_snn_id = kwargs["source_snn_id"]
        if("sink_snn_id" in kwargs): self.sink_snn_id = kwargs["sink_snn_id"]

class Hand:
    id = -1    

class Graph:
    tag_node_dict = {}
    tag_edge_dict = {}
    snn_node_dict = {}
    snn_edge_dict = {}

    touched = True

    def __init__(self, **kwargs):
        return
    
    def print_tags(self):
        if not self.touched: return
        #print('\033[36m')
        for i in self.tag_node_dict:
            print("Track", end="#")
            print(self.tag_node_dict[i].tracking_id, end="#")
            print(self.tag_node_dict[i].snn_id, end = "#")
            print(self.tag_node_dict[i].node_type, end = "#")
            print(self.tag_node_dict[i].posvec, end = "#")
            print(self.tag_node_dict[i].rotvec)
        print('\033[0m')
        self.touched = False
