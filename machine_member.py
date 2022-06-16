#!/usr/bin/env python
# coding: utf-8


import tkinter as tk
import numpy as np
import math

class Mechanism :
    def __init__(self, origin=[0,0]) :
        self.origin = origin
        self.slide_list = []
        self.link_list = []
        self.pivot_list = []
        self.link_num = 0
        self.slide_num = 0
        self.mem_num = 0
        self.piv_num = 0
        #self.frame_num=0
        #self.rev_pair_num=0

        
#     def draw_all(self, canvas) :
#         """"""
#         for i in range(len(self.link_list)) :
#             self.link_list.draw_link(canvas)
#         for i in range(len(self.pivot_list)) :
#             self.link_list.draw_piv(canvas)           
    def find_joint(self, ID, canvas) :
        """"""
        kind, ind = (canvas.gettags(ID)[2]).split("_")
        ind = int(ind)
        if kind == 'link' :
            for i in range(2) :
                if ID==self.link_list[ind].joint[i].ID :
                    return kind, ind, i
        elif kind == 'pivot' :
            return kind, ind, 0
#     def find_list(self, kind) :
#         if kind=='link' :
#             return self.link_list
#         elif kind=='pivot' :
#             return self.pivot_list
#         elif kind=='slide' :
#             return self.slide_list

    def refresh(self, old, canvas) :
        for i in range(self.piv_num) :
            x = self.pivot_list[i].joint[0].coord[0] - old.pivot_list[i].joint[0].coord[0]
            y = self.pivot_list[i].joint[0].coord[1] - old.pivot_list[i].joint[0].coord[1]
            canvas.move(f"pivot_{i}", x, y)
            
        for i in range(self.link_num) :
#             x = self.link_list[i].joint[0].coord[0] - old.link_list[i].joint[0].coord[0] # joint_0 as original to move
#             y = self.link_list[i].joint[0].coord[1] - old.link_list[i].joint[0].coord[1]
#             angle = self.link_list[i].angle - old.link_list[i].angle
#             canvas.move(f"link_{i}", x, y)
            
            self.link_list[i].draw_link(canvas)
class Joint :
    def __init__(self,coord=[0,0]) :
        # coord in pixel
        self.coord=coord 
        self.mate_with=[] # ex : link_0_0
        self.ID=0
        self.mate_ID=0
        
class Fixed_piv :
    def __init__(self, coord=[0, 0], tag='a') :
        self.joint=[Joint(coord)]
        self.orig=0
        self.tag=tag
        self.pivID = 0
        self.state = 'limited'
    def draw_piv(self, canvas) :
        """"""
        coord=np.array(self.joint[0].coord)
        unselect_tag=list(self.tag)
        unselect_tag[0]='unselect'
        unselect_tag=tuple(unselect_tag)
        joint_tag=list(self.tag)
        joint_tag[1]='joint'
        joint_tag=tuple(joint_tag)
        self.joint[0].ID = canvas.create_oval((coord-5).tolist(), (coord+5).tolist(), fill = 'black', activefill='red', tag=joint_tag)
        canvas.create_oval((coord-15).tolist(), (coord+15).tolist(), width=2, tag=unselect_tag)
        canvas.create_line(self.joint[0].coord[0]-15, self.joint[0].coord[1], self.joint[0].coord[0]-15, self.joint[0].coord[1]+20, width=2, tag=unselect_tag)
        canvas.create_line(self.joint[0].coord[0]+15, self.joint[0].coord[1], self.joint[0].coord[0]+15, self.joint[0].coord[1]+20, width=2, tag=unselect_tag )
        canvas.create_rectangle(self.joint[0].coord[0]-20, self.joint[0].coord[1]+20, self.joint[0].coord[0]+20, self.joint[0].coord[1]+30, width=2, tag=unselect_tag)
        
class Link :
    # length in pixel(mm),default_length=2=100 pixel , joint coordinates in pixel, angle in rad
    # tag type : ('selectable', 'link', 'link_1')
    #            ('unselect', 'pivot', 'pivot_0')
    def __init__(self, length=2, joint=[[10,10],[110,10]], angle = 0, tag='link') :
        self.length = length
        self.angle = angle # x-dir positive with joint[0] being original, rad
        self.tag = tag
        self.joint = [Joint(joint[0]), Joint(joint[1])]
        self.state = 'float' # or limited if it belong to the mechanism 
        self.linkID = 0
        #self.vector = [100,0]
    def draw_link(self, canvas) :
        canvas.delete(self.tag[2])
        joint = np.array([self.joint[0].coord, self.joint[1].coord])
        joint_tag=list(self.tag)
        joint_tag[1] = 'joint'
        joint_tag = tuple(joint_tag)
        unselect_tag=list(joint_tag)
        unselect_tag[0]='unselect'
        unselect_tag=tuple(unselect_tag)
        self.linkID = canvas.create_line(self.joint[0].coord, self.joint[1].coord, tag=self.tag, activefill='red', width = 4)        
        self.joint[0].ID=canvas.create_oval((joint[0]-5).tolist(), (joint[0]+5).tolist(),  fill = 'black', activefill='red', tag=joint_tag)
        self.joint[1].ID=canvas.create_oval((joint[1]-5).tolist(), (joint[1]+5).tolist(),  fill = 'black', activefill='red', tag=joint_tag) 
        for i in range(2) :
                self.joint[i].mate_ID = canvas.create_oval((joint[i]-12).tolist(), (joint[i]+12).tolist(), width=2, state=tk.HIDDEN, tag=unselect_tag)
        
        for i in range(2) :
            if self.joint[i].mate_with!=[] :
                canvas.itemconfigure(self.joint[i].mate_ID, state=tk.NORMAL)
    def renew(self, length, angle, j0,rate) :
        self.length = length
        self.joint[0].coord = j0
        self.angle = angle #rad
        x = int(math.cos(self.angle)*self.length*rate)
        y = int(math.sin(self.angle)*self.length*rate)
        self.joint[1].coord = [self.joint[0].coord[0]+x, self.joint[0].coord[1]-y]
        
        
    def move(self, x, y, canvas) : # x,y distance in pixel, dir in Cartesian
        """"""

        new = np.array([self.joint[0].coord, self.joint[1].coord])
        new[:,0] = new[:,0] + x
        new[:,1] = new[:,1] + y
        self.joint[0].coord, self.joint[1].coord = new.tolist()[0], new.tolist()[1]
        canvas.move(self.tag[2], x, y)

#     def rotate(self, theta) : # theta in degree , CCW positive
#         """"""      
        
#         x = int(math.cos(theta)*self.length)
#         y = int(math.sin(theta)*self.length)
#         self.joint[1].coord = [self.joint[0].coord[0]+x, self.joint[0].coord[1]-y]

# class Slide :
    
#     def init(self,) :
#         """"""
#     def draw_slide(self) :
        """"""

def pixel_to_cartesain(orig, point) :
    """"""
    new = [0,0]
    new[0] = point[0] - orig[0]
    new[1] = -point[1] + orig[1]
    return new

def cartesain_to_pixel(orig, point) :
    """"""
    new = [0,0]
    new[0] = point[0] + orig[0]
    new[1] = -point[1] + orig[1]
    return new

