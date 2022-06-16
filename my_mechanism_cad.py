#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from PIL import ImageTk, Image
import os
from functools import partial
from tkinter import messagebox
import machine_member as mb
import time
import math
import copy
from powell import *


# In[2]:


# def operating_manual() :
#     newWindow = tk.Toplevel()
#     newWindow.geometry("1000x800")
#     labelExample = tk.Label(newWindow, text = "New Window")
#     buttonExample = tk.Button(newWindow, text = "New Window button")
#     labelExample.pack()
#     buttonExample.pack()


# In[3]:


def widget_reset():
    if(mechanism.mem_num<=36) :
        for i in range(len(mem_btn_list)) :
            mem_btn_list[i].grid(row=member_row(i+1), column=member_column(i+1), rowspan=1, columnspan=1, padx=2, pady=2)
        canvas.grid(row=1, column=0, rowspan=canvas_rowspan(mechanism.mem_num), columnspan=TOOL_NUMBER, padx=5, pady=5, sticky=tk.SW)
    else :
        messagebox.showwarning('Warning', 'No more space to add new component')


# In[4]:


def canvas_rowspan(mache_num) :
    if mechanism.mem_num!=0 :
        if mechanism.mem_num>18 :
            return 18
        else :
            return mechanism.mem_num       
    else :
        return 1

def member_column(num) :
    if num>18 :
        return TOOL_NUMBER+1
    else :
        return TOOL_NUMBER       

def member_row(num) :
    if num>18 :
        return num-18
    else :
        return num     


# In[5]:


def cancel_placing(event) :
    canvas.unbind("<Button-1>")
    canvas.unbind("<Button-3>")
    canvas.configure(cursor='')


# In[6]:


def placing_object(member:'String') :
    """ """
    canvas.unbind("<Button-1>")
    canvas.unbind("<Button-3>")
    canvas.tag_unbind('selectable',"<Button-1>")
    canvas.tag_unbind('selectable',"<B1-Motion>")
    canvas.tag_unbind('selectable',"<ButtonRelease-1>")
    canvas.tag_unbind('joint',"<Control-Button-1>")
    if member=='link' :
        canvas.configure(cursor='plus')
    elif member=='slide' :
        canvas.configure(cursor='dotbox')
    elif member=='fixed_piv' :
        canvas.configure(cursor='bottom_tee')
        
    canvas.bind("<Button-1>", partial(create_object,member))
    canvas.bind("<Button-3>", cancel_placing)
    


# In[7]:


def create_object(member,event) :
    canvas.unbind("<Button-1>")
    canvas.unbind("<Button-3>")
#     canvas.tag_bind('selectable',"<Button-1>", start_moving)
#     canvas.tag_bind('selectable',"<B1-Motion>", moving_obj)
#     canvas.tag_bind('selectable',"<ButtonRelease-1>", end_move)
    canvas.tag_bind('joint',"<Control-Button-1>", choosing_mate)
    #canvas.bind("<Button-2>", B2)
    canvas.configure(cursor='')
    
    if member == 'link' :        
        mem_btn_list.append(tk.Button(win, text=f"{member}_{mechanism.link_num}", width=12, height=1, font = ("Arial",10), command=partial(link_property, mechanism.link_num)))
        mechanism.link_list.append(mb.Link(joint=[[event.x,event.y],[event.x+100,event.y]], tag=('selectable','link',f"{member}_{mechanism.link_num}") )) # new obj estiblished 
        mechanism.link_list[mechanism.link_num].draw_link(canvas)
        mechanism.link_num+=1
    elif member == 'slide' :
        mem_btn_list.append(tk.Button(win, text=f"{member}_{mechanism.slide_num}", width=12, height=1, font = ("Arial",10)))
        mechanism.slide_num+=1
    elif member=='fixed_piv' :
        """"""
        mem_btn_list.append(tk.Button(win, text=f"pivot_{mechanism.piv_num}", width=12, height=1, font = ("Arial",10), command=partial(pivot_property, mechanism.piv_num)))
        mechanism.pivot_list.append(mb.Fixed_piv(coord=[event.x,event.y],  tag=('selectable','pivot',f"pivot_{mechanism.piv_num}") )) # new obj estiblished 
        mechanism.pivot_list[mechanism.piv_num].draw_piv(canvas)
        if mechanism.piv_num==0 :
            mechanism.pivot_list[0].orig=1
            mechanism.origin=[event.x,event.y]
            canvas.create_line(event.x, event.y, event.x+30, event.y, arrow=tk.LAST, fill='blue')
            canvas.create_line(event.x, event.y, event.x, event.y-30, arrow=tk.LAST, fill='red')
        mechanism.piv_num+=1
        
    mem_btn_list[len(mem_btn_list)-1].configure(fg='red')
    mechanism.mem_num+=1 
    widget_reset()


# In[8]:


def link_property(i):
    global newWindow
    newWindow = tk.Toplevel(win)
    newWindow.geometry("300x100")
    newWindow.title(f"link_{i} attributes")
    leng = tk.Label(newWindow, text = f"current length : { mechanism.link_list[i].length}")
    leng_enter = tk.Text(newWindow, width=10,height=1)
    ang =  tk.Label(newWindow, text = f"current angle(deg) : {round(mechanism.link_list[i].angle*180/math.pi,2)}")
    ang_enter = tk.Text(newWindow, width=10,height=1)


    ok_btn = tk.Button(newWindow, text = "OK", command=partial(link_ok, leng_enter , ang_enter,i))
    cancel_btn = tk.Button(newWindow, text = "Cancel", command=newWindow.destroy)
    
    leng.grid(row=0, column=0, rowspan=1, columnspan=1)
    leng_enter.grid(row=0, column=1, rowspan=1, columnspan=1)
    ang.grid(row=1, column=0, rowspan=1, columnspan=1)
    ang_enter.grid(row=1, column=1, rowspan=1, columnspan=1)
    ok_btn.grid(row=2, column=1, rowspan=1, columnspan=1)
    cancel_btn.grid(row=2, column=2, rowspan=1, columnspan=1)


# In[9]:


def pivot_property(i):
    global newWindow
    newWindow = tk.Toplevel(win)
    newWindow.geometry("300x100")
    newWindow.title(f"pivot_{i} attributes")
    pos = mb.pixel_to_cartesain(mechanism.origin, mechanism.pivot_list[i].joint[0].coord)
    
    text = tk.Label(newWindow, text = "position(x,y) : ")
    text.grid(row=0, column=0, rowspan=1, columnspan=1)
    coord = tk.Label(newWindow, text = f"{pos}")
    coord.grid(row=0, column=1, rowspan=1, columnspan=1)
    if i!=0 :
        x = tk.Label(newWindow, text = "x = ")
        x.grid(row=1, column=0, rowspan=1, columnspan=1)
        y = tk.Label(newWindow, text = "y = ")
        y.grid(row=2, column=0, rowspan=1, columnspan=1)
        x_enter = tk.Text(newWindow, width=10,height=1)
        x_enter.grid(row=1, column=1, rowspan=1, columnspan=1)
        y_enter = tk.Text(newWindow, width=10,height=1)
        y_enter.grid(row=2, column=1, rowspan=1, columnspan=1)
        ok_btn = tk.Button(newWindow, text = "OK", command=partial(pivot_ok,x_enter, y_enter ,i))
        ok_btn.grid(row=3, column=0, rowspan=1, columnspan=1)
    else :
        ok_btn = tk.Button(newWindow, text = "OK", command=newWindow.destroy)
        ok_btn.grid(row=3, column=0, rowspan=1, columnspan=1)
    
    cancel_btn = tk.Button(newWindow, text = "Cancel", command=newWindow.destroy)
    cancel_btn.grid(row=3, column=1, rowspan=1, columnspan=1)


# In[10]:


def pivot_ok(x,y,i) :
    x = x.get(1.0, tk.END+"-1c")
    y = y.get(1.0, tk.END+"-1c")
    if x!="" :
        x = int(x)
    else :
        x = mechanism.pivot_list[i].joint[0].coord[0]-mechanism.origin[0]
    if y!="" :
        y = int(y)
    else :
        y = mechanism.origin[1]-mechanism.pivot_list[i].joint[0].coord[1]

    old = copy.deepcopy(mechanism)
    mechanism.pivot_list[i].joint[0].coord = mb.cartesain_to_pixel(mechanism.origin,[x, y])
    mechanism.refresh(old, canvas)
    newWindow.destroy()


# In[11]:


def link_ok(leng_enter, ang_enter,i) :
    length=leng_enter.get(1.0, tk.END+"-1c")
    angle=ang_enter.get(1.0, tk.END+"-1c")
    if length!="" :
        length = float(length) 
    else :
        length = mechanism.link_list[i].length
    if angle!="" :
        angle = float(angle)        
    else :
        angle = mechanism.link_list[i].angle
    old = copy.deepcopy(mechanism)
    angle = angle*math.pi/180
    mechanism.link_list[i].renew(length, angle,mechanism.link_list[i].joint[0].coord, pix_length_rate)
        
    mechanism.refresh(old,canvas)
    newWindow.destroy()
    


# In[12]:


# def B2(event) :
#     global v
#     v+=1
#     #mechanism.link_list[0].move(10,10)
#     mechanism.link_list[0].rotate(v)
#     mechanism.link_list[0].draw_link(canvas)
#     #print(mechanism.link_list[0].joint[0].coord)


# In[13]:


# def start_moving(event) :
#     """"""
#     global first_x, first_y,dragging
#     k,i = canvas.gettags("current")[2].split("_")
#     if k!="pivot" :
#         dragging=1
#         first_x, first_y = event.x, event.y
# def moving_obj(event) :
#     """"""
#     global first_x, first_y, dragging
#     if dragging==1 :
#         canvas.move(canvas.gettags("current")[2], event.x-first_x, event.y-first_y)
#         first_x, first_y = event.x, event.y
        
        
# def end_move(event) :
#     """"""
#     global first_x, first_y, dragging
#     if dragging==1 :
#         canvas.move(canvas.gettags("current")[2], event.x-first_x, event.y-first_y)
    
#     #print(mechanism.link_list[0].joint[0].coord)
#     dragging=0


# In[14]:


def choosing_mate(event) :
    """"""
    global mate_obj
    canvas.tag_unbind('selectable',"<Button-1>")
    canvas.tag_unbind('selectable',"<B1-Motion>")
    canvas.tag_unbind('selectable',"<ButtonRelease-1>")
    #canvas.bind("<Button-3>", cancel_choosing)
    id_click = canvas.find_withtag("current")[0]
    mate_obj.append(id_click)
    canvas.itemconfigure("current", fill='yellow')
    if mate_obj.count(id_click) > 1:
        canvas.itemconfigure(id_click, fill='black')
        mate_obj = list(filter(lambda val: val !=  id_click, mate_obj)) 
def cancel_choosing() :
    global mate_obj
    for i in set(mate_obj):
        canvas.itemconfigure(i, fill='black')
    mate_obj=[]
    canvas.unbind("<Button-3>")
#     canvas.tag_bind('selectable',"<Button-1>", start_moving)
#     canvas.tag_bind('selectable',"<B1-Motion>", moving_obj)
#     canvas.tag_bind('selectable',"<ButtonRelease-1>", end_move)
    canvas.tag_bind('joint',"<Control-Button-1>", choosing_mate)


# In[15]:


def coincident() :
    """"""
    global mate_obj
    name_list=[]
    ind_list=[]
    joint_ind_list=[]
    state_list=[]
    lim_ind=[]
    for i in range (len(mate_obj)) :
        name, ind, joint_ind = mechanism.find_joint(ID=mate_obj[i], canvas=canvas)
        name_list.append(name)
        ind_list.append(ind)
        joint_ind_list.append(joint_ind)

    for i in range(len(name_list)) :
        if name_list[i]=='link' : 
            if mechanism.link_list[ind_list[i]].state=='float' :
                state_list.append(0)
            else :
                state_list.append(1)
                lim_ind.append(i)
        elif name_list[i]=='pivot' :
            state_list.append(1)
            lim_ind.append(i)
            
    # 
    if state_list.count(1) == 0 :
        for i in range(len(name_list)) :
            if name_list[i]=='link' and i!=0 : 
                final = mechanism.link_list[ind_list[0]].joint[joint_ind_list[0]].coord
                x = final[0] - mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].coord[0] 
                y = final[1] - mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].coord[1]
                move_with_mate(x,y,mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].ID)
            canvas.itemconfigure(mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_ID, state=tk.NORMAL)
    # 
    elif state_list.count(1)==1 :
        """"""
        for i in range(len(name_list)) :
            if name_list[i]=='link' and i!=lim_ind[0] : 
                final=[0,0]
                if name_list[lim_ind[0]] == 'pivot' :
                    final = mechanism.pivot_list[ind_list[lim_ind[0]]].joint[joint_ind_list[lim_ind[0]]].coord
                elif name_list[lim_ind[0]] == 'link' :
                    final = mechanism.link_list[ind_list[lim_ind[0]]].joint[joint_ind_list[lim_ind[0]]].coord
                x = final[0] - mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].coord[0] 
                y = final[1] - mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].coord[1]
                mechanism.link_list[ind_list[i]].state='limited'
                move_with_mate(x,y,mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].ID)
            canvas.itemconfigure(mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_ID, state=tk.NORMAL)
    
        
       

    if len(mate_obj) > 1 :
        for i in range (len(mate_obj)) :
            for j in range (len(mate_obj)) : 
                if i!=j :
                    if name_list[i]=='link' : 
                        k,ind,j_ind = mechanism.find_joint(ID=mate_obj[j], canvas=canvas)
                        
                        if k=='link' :
                            mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.extend(mechanism.link_list[ind].joint[j_ind].mate_with)
                        elif k=='pivot' :
                            mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.extend(mechanism.pivot_list[ind].joint[j_ind].mate_with)
                    elif name_list[i] == 'pivot' :
                        k,ind,j_ind = mechanism.find_joint(ID=mate_obj[j], canvas=canvas)
                        
                        if k=='link' :
                            mechanism.pivot_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.extend(mechanism.link_list[ind].joint[j_ind].mate_with)
                        elif k=='pivot' :
                            mechanism.pivot_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.extend(mechanism.pivot_list[ind].joint[j_ind].mate_with)
        
        
        for i in range (len(mate_obj)) :
            for j in range (len(mate_obj)) :
                if i!=j :
                    k,ind,j_ind = mechanism.find_joint(ID=mate_obj[j], canvas=canvas)
                    mate=f"{k}_{ind}_{ind}" 
                    if name_list[i]=='link' : 
                        if mate not in mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_with :
                            mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.append(mate)                        
                        else :
                            messagebox.showwarning('Warning', 'Repetitive mate')
                            break                
                    elif name_list[i] == 'pivot' :
                        if mate not in mechanism.pivot_list[ind_list[i]].joint[joint_ind_list[i]].mate_with :
                            mechanism.pivot_list[ind_list[i]].joint[joint_ind_list[i]].mate_with.append(mate)
                        else :
                            messagebox.showwarning('Warning', 'Repetitive mate')
                            break                          
            else:
                continue
            break
            
    if state_list.count(1) > 1:
        """"""
        # 此處假設單固定點對單固定點, 理想為四連桿
        final=[0,0]
        global old 
        old = copy.deepcopy(mechanism) 
        for i in range(len(name_list)) :
            if name_list[i] == 'pivot' :
                final = mechanism.pivot_list[ind_list[i]].joint[joint_ind_list[i]].coord
            elif name_list[i] == 'link' :
                canvas.itemconfigure(mechanism.link_list[ind_list[i]].joint[joint_ind_list[i]].mate_ID, state=tk.NORMAL)
            
        theta_ini = np.array([1.0,1.0,1.0])
        rad, nIter = powell(F,theta_ini)
        delta = np.array(rad)/10
        animation2(delta,0)
        
    cancel_choosing()


# In[16]:


def animation2(delta,count) :
    j0 =[mb.cartesain_to_pixel(mechanism.origin, [0,0])]  
    for i in range(2) : # find jo
        x = mechanism.link_list[i].length*pix_length_rate*math.cos(mechanism.link_list[i].angle+delta[i])
        y = mechanism.link_list[i].length*pix_length_rate*math.sin(mechanism.link_list[i].angle+delta[i])
        j = [j0[-1][0]+x, j0[-1][1]-y]
        j0.append(j) 
    for i in range(3) : #renew link
        mechanism.link_list[i].renew(mechanism.link_list[i].length, mechanism.link_list[i].angle+delta[i], j0[i], pix_length_rate)
    mechanism.refresh(old,canvas)    
    
    if count==10:
        theta_ini = np.array([1.0,1.0,1.0])
        rad, nIter = powell(F,theta_ini)
        j0 =[mb.cartesain_to_pixel(mechanism.origin, [0,0])]  
        for i in range(2) : # find jo
            x = mechanism.link_list[i].length*pix_length_rate*math.cos(mechanism.link_list[i].angle+rad[i])
            y = mechanism.link_list[i].length*pix_length_rate*math.sin(mechanism.link_list[i].angle+rad[i])
            j = [j0[-1][0]+x, j0[-1][1]-y]
            j0.append(j) 
        for i in range(3) : #renew link
            mechanism.link_list[i].renew(mechanism.link_list[i].length, mechanism.link_list[i].angle+rad[i], j0[i], pix_length_rate)
        mechanism.refresh(old,canvas)   
    
        return       
    else:

        canvas.after(100,animation2,delta, count+1)


# In[17]:


# this function only suit for four-linkage mechanism when running coincidence
def F(x):
    # x :[delta_theta_1, delta_theta_2, delta_theta_3]
    i = 0
    a = []
    l = []
    for i in range(3) :
        a.append(mechanism.link_list[i].angle)
        l.append(mechanism.link_list[i].length*pix_length_rate)
        i+=1
    final = mb.pixel_to_cartesain(mechanism.origin, mechanism.pivot_list[1].joint[0].coord)
    c1 = l[0]*math.cos(a[0]+x[0]) + l[1]*math.cos(a[1]+x[1]) +l[2]*math.cos(a[2]+x[2])-final[0]# Constraint function
    c2 = l[0]*math.sin(a[0]+x[0]) + l[1]*math.sin(a[1]+x[1]) +l[2]*math.sin(a[2]+x[2])-final[1]
    c3 = min(0.0, x[0]-math.pi)
    c4 = min(0.0, x[1]-math.pi)
    c5 = min(0.0, x[2]-math.pi)
    c6 = max(0.0, x[0]+math.pi)
    c7 = max(0.0, x[1]+math.pi)
    c8 = max(0.0, x[2]+math.pi)
    lam = 1000000.0 # Constraint multiplier
    
    return x[0]**2 + x[1]**2 + x[2]**2 + lam*(c1**2 + c2**2 + c3**2 + c4**2 + c5**2 + c6**2 + c7**2 + c8**2)


# In[18]:


def move_with_mate(x,y,start_ID) :
    global move_tag
    move_tag=[]
#     global movex, movey,count
    movex=x
    movey=y
    count=0
    kind, ind, i = mechanism.find_joint(start_ID, canvas)
    move_tag.append(f"{kind}_{ind}")
    mate_search(kind, ind, i)
    mate_search(kind, ind, 1-i)
    animation( movex, movey,0,move_tag)
    


# In[19]:


def mate_search(kind, ind, i) :
    global move_tag
          
    if mechanism.link_list[ind].joint[i].mate_with==[] :
        """"""
    elif kind=='link' :
        for j in mechanism.link_list[ind].joint[i].mate_with :
            kind1, ind1, i1 = j.split("_")
            move_tag.append(f"{kind1}_{ind1}")
            if kind1=='link' :
                mate_search(kind1, ind1, 1-i1)
            elif kind1=='slide' :
                """"""
    elif kind=='slide' :
        """"""


# In[20]:


def animation( movex, movey, count,tag) : 
    
    for i in range(len(tag)) :
        k,j = tag[i].split("_")
        j = int(j)
        if count<10 :
            if k == 'link' :       
                mechanism.link_list[j].move(move_step(movex),move_step(movey),canvas)
            
        elif count==10 :
            if k == 'link' :  
                """"""
                mechanism.link_list[j].move(-move_step(movex)*10+movex, -move_step(movey)*10+movey,canvas)

    if count==10:
        return       
    else:
#         time.sleep(0.1)
#         animation()
        canvas.after(100,animation,movex, movey, count+1,tag)


# In[21]:


def move_step(dis) :
    if dis>0 :
        return (dis-dis%10)/10
    else :
        return (dis+abs(dis)%10)/10


# In[22]:


# # this function only suit for four-linkage mechanism
# def S(x):
#     # x :[delta_theta_1, delta_theta_2]
#     i = 0
#     a = []
#     l = []
#     x0 = mechanism.link_list[0].length*pix_length_rate*math.cos(mechanism.link_list[0].angle+del_rad*dire)
#     y0 = mechanism.link_list[0].length*pix_length_rate*math.sin(mechanism.link_list[0].angle+del_rad*dire)
#     for i in range(1,3) :
#         a.append(mechanism.link_list[i].angle)
#         l.append(mechanism.link_list[i].length*pix_length_rate)
#         i+=1
#     final = mb.pixel_to_cartesain(mechanism.origin, mechanism.pivot_list[1].joint[0].coord)
#     c1 = l[0]*math.cos(a[0]+x[0]) + l[1]*math.cos(a[1]+x[1]) + x0 -final[0]# Constraint function
#     c2 = l[0]*math.sin(a[0]+x[0]) + l[1]*math.sin(a[1]+x[1]) + y0 -final[1]
#     c3 = min(0.0, x[0]-math.pi)
#     c4 = min(0.0, x[1]-math.pi)
#     c5 = min(0.0, x[2]-math.pi)
#     c6 = max(0.0, x[0]+math.pi)
#     c7 = max(0.0, x[1]+math.pi)
#     c8 = max(0.0, x[2]+math.pi)
#     lam = 1000000.0 # Constraint multiplier
    
#     return x[0]**2 + x[1]**2 + x[2]**2 + lam*(c1**2 + c2**2 + c3**2 + c4**2 + c5**2 + c6**2 + c7**2 + c8**2)


# In[23]:


# def simulation(count=0) :
#     canvas.bind("<Button-3>", cancel_simul)
#     if simulation == 0 :
#         canvas.unbind("<Button-3>")
#     else :
#         global old 
#         old = copy.deepcopy(mechanism) 
#         j0 =[mb.cartesain_to_pixel(mechanism.origin, [0,0])]
#         x0 = mechanism.link_list[0].length*pix_length_rate*math.cos(mechanism.link_list[0].angle+del_rad*dire)
#         y0 = mechanism.link_list[0].length*pix_length_rate*math.sin(mechanism.link_list[0].angle+del_rad*dire)
#         j0.append(mb.cartesain_to_pixel(mechanism.origin, [x0,y0]))
#         theta_ini = np.array([1.0,1.0])
#         rad, nIter = powell(S,theta_ini)
#         for i in range(2) : # find jo
#             x = mechanism.link_list[i].length*pix_length_rate*math.cos(mechanism.link_list[i].angle+rad[i])
#             y = mechanism.link_list[i].length*pix_length_rate*math.sin(mechanism.link_list[i].angle+rad[i])
#             j = [j0[-1][0]+x, j0[-1][1]-y]
#             j0.append(j) 
#         for i in range(3) : #renew link
#             mechanism.link_list[i].renew(mechanism.link_list[i].length, mechanism.link_list[i].angle+rad[i], j0[i], pix_length_rate)
#         mechanism.refresh(old,canvas)    
        
        
        
        
        
#         if dire==1:
#             if count==200 :
#                 dire=-1
#                 canvas.after(10,simulation,count-1)
#             else :
#                 canvas.after(10,simulation,count+1)
#         else :
#             if count==200 :
#                 dire=1
#                 canvas.after(10,simulation,count+1)
#             else :
#                 canvas.after(10,simulation,count-1 )


# In[24]:


# def cancel_simul() :
#     global simulation 
#     simulation = 0


# In[25]:


win = tk.Tk()
win.title("機構模擬系統")
win.geometry("1250x640")
#win.resizable(False, False)
TOOL_NUMBER = 9
# mache_num = 0
# link_num = 0
# slide_num = 0
count = 0
mem_btn_list = [] # list of member button
tool_list = [] # list of tool button 
pic_list = []
# link_list = []
# slide_list = []
mechanism = mb.Mechanism()
old = mb.Mechanism()
pix_length_rate = 50 #50 pixels = 1 unit 
dire = 1 # 1 for counter-clockwise
del_rad = math.pi/100
simulation = 0
mate_obj=[]
# menubar=tk.Menu(win)       # 建立頂層功能列
# menubar.add_command(label="操作說明", command = operating_manual)     # 新增選項
#win.config(menu=menubar)

for i in range(4) :
    pic_list.append(tk.PhotoImage(file=f'picture/{i}.png', master = win))
    pic_list[i]=pic_list[i].subsample(2)
pic_1 = tk.PhotoImage(file='picture/test.png', master = win)
pic_1=pic_1.subsample(4)

tool_list.append(tk.Button(win, image=pic_list[0], width=1200/(TOOL_NUMBER+2), height=60, command=partial(placing_object, 'link')))
tool_list.append(tk.Button(win, image=pic_list[1], width=1200/(TOOL_NUMBER+2), height=60, command=partial(placing_object, 'slide'))) 
tool_list.append(tk.Button(win, image=pic_list[2], width=1200/(TOOL_NUMBER+2), height=60, command=partial(placing_object, 'fixed_piv'))) 
tool_list.append(tk.Button(win, image=pic_list[3], width=1200/(TOOL_NUMBER+2), height=60, command=coincident)) 
tool_list.append(tk.Button(win, image=pic_1, width=1200/(TOOL_NUMBER+2), height=60)) 
tool_list.append(tk.Button(win, image=pic_1, width=1200/(TOOL_NUMBER+2), height=60)) 
tool_list.append(tk.Button(win, image=pic_1, width=1200/(TOOL_NUMBER+2), height=60))
tool_list.append(tk.Button(win, image=pic_1, width=1200/(TOOL_NUMBER+2), height=60))
tool_list.append(tk.Button(win, image=pic_1, width=1200/(TOOL_NUMBER+2), height=60))

canvas = tk.Canvas(win, width=1000, height=560, background="white")
for i in range(TOOL_NUMBER) :
    tool_list[i].grid(row=0, column=i, rowspan=1, columnspan=1)

widget_reset()


win.mainloop()


# In[ ]:





# In[ ]:





# In[ ]:




