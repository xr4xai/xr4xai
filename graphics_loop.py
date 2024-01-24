from graphics import *
import numpy as np
import time

def projector_display(G):
    win = GraphWin(width, height)

    background = Rectangle(Point(0,0), Point(width, height))
    background.setFill('black')

    # This is for proof of concept. We will need to come back in here and do a bunch of
    # Linear Algebra to actually get something that is useable
    while True:
        background.draw(win)

        if(np.any(G.tag_node_dict[0:2].position) == None): 
            time.sleep(1/15)
            continue
        min_x = G.tag_node_dict[0].position[0]
        max_x = G.tag_node_dict[1].position[0]
        min_y = G.tag_node_dict[1].position[1]
        max_y = G.tag_node_dict[2].position[1]


        draw_node_list = []
    
        for i in G.tag_node_dict:
            nx = G.tag_node_dict[i].position[0]
            ny = G.tag_node_dict[i].position[1]

            pt = Point( (nx - min_x)/(max_x - min_x) * width, (ny - min_y)/(max_y - min_y) * height)
            draw_node_list.append(pt)

        for i in draw_node_list:
            cir = Circle(i, 30)
            cir.setFill('orange')
            cir.draw(win)

        time.sleep(1/30)

    win.close()


