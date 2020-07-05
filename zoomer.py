import tkinter
import simplex_terrain
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import math


sea_level = .6
mountain_level = 3./8.*sea_level+5./8.
max_farmable = (sea_level+mountain_level)/2
snow_level = 1./8.*sea_level+7./8.

cmap_terrain_steps = colors.LinearSegmentedColormap.from_list('terrain_steps',
        [(0,'#000080'),
#         (sea_level/2,'#0000FF'),
        (sea_level*.9,'#0000FF'),
        (sea_level,'#1E90FF'),
        (sea_level+1.e-13,'#228B22'),
        (mountain_level,'yellow'),
        (snow_level,'#8B4513'),
        (1.,'white')
        ])

cmap_habitable = colors.LinearSegmentedColormap.from_list('habitable',
        [(0,'#0000FF'),
        (sea_level*.9999,'#0000FF'),
        (sea_level,'#00FF00'),
        ((mountain_level-sea_level)*.1+sea_level,'#00FF00'),
        ((mountain_level-sea_level)*.8+sea_level,'white'),
        (1.,'white')
        ])


# world_map_normed = (world_map-np.min(world_map))/(np.max(world_map)-np.min(world_map))

# a subclass of Canvas for dealing with resizing of windows
# From https://stackoverflow.com/questions/22835289/how-to-get-tkinter-canvas-to-dynamically-resize-to-window-width
class MapCanvas(tkinter.Canvas):
    """MapCanvas

    All of the meat of the code is currently in here. It handles both rendering and I/O
    """
    def __init__(self,parent,**kwargs):
        tkinter.Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-2>", self._on_right_click)
#         self.bind("<MouseWheel>", self._on_mousewheel)

        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.corner = [0,0]
        self.pixel_res = 1./self.width
        
#         self.rescale_function = lambda x: x**3
#         self.rescale_function = lambda x: np.arctanh(2*x)
        self.rescale_function = lambda x: x
        
        self.map_min = self.rescale_function(-.53)
        self.map_max = self.rescale_function(.53)
#         self.map_min = -.15
#         self.map_max = .15
        self.map_range = self.map_max-self.map_min
        self.map_norm = 1./self.map_range
        
        self.draw_modes = ['height','habitable']
        
        self.selected_draw_mode_index = 0
        
#         self.zoom_sensitivity = 0.01

        self.ter_gen = simplex_terrain.simplex_terrain_generator(seeds=0)

    def _space(self,event):
        print("Next mode")
        self.selected_draw_mode_index+=1
        if self.selected_draw_mode_index>=len(self.draw_modes):
            self.selected_draw_mode_index=0
        self.draw_world_map()
    
    def generate_height_map(self):
        world_map = self.ter_gen.sum_octave_2dgrid(bounds=[
                                                [self.corner[0],self.corner[0]+self.pixel_res*self.width],
                                                [self.corner[1],self.corner[1]+self.pixel_res*self.height]
                                                                ]
                                                        ,res=[self.width,self.height]
#                                                         ,persistence=lambda x:0.6**math.fabs(x-4) # many continents, superworld
#                                                         ,persistence=lambda x:0.6**math.fabs(x-2) # few continents, earthlike
                                                        ,persistence=lambda x:0.6**((x-3)/3)**2
                                                        )
#         print(world_map.shape)
        world_map = self.rescale_function(world_map) # rescale X-TREME
        print(np.nanmin(world_map),np.nanmax(world_map))
        world_map=np.clip(world_map,self.map_min,self.map_max).T
        world_map-=self.map_min
        world_map*=self.map_norm
        print(np.nanmin(world_map),np.nanmax(world_map))
        return world_map
    
    def draw_world_map(self):
        """draw_world_map
    
        Generates the full map and renders the image on the canvas.
        Currently regenerates everythings every time.
    
        TODO: cache things at current resolution so you can scroll around and resize more efficiently"""
#         print(np.min(world_map),np.max(world_map))
        world_map = self.generate_height_map()
        
        draw_mode_str = self.draw_modes[self.selected_draw_mode_index]
        if draw_mode_str=='height':
            world_map_coloured = cmap_terrain_steps(world_map,bytes=True)
        elif draw_mode_str=='habitable':
            world_map_coloured = cmap_habitable(world_map,bytes=True)
        
        self.world_img =  ImageTk.PhotoImage(image=Image.fromarray(world_map_coloured))
        self.create_image(0,0, anchor="nw", image=self.world_img)

    def _on_resize(self,event):
        """on_size
        
        Just updates the canvas size and redraws the map"""
        self.width = event.width
        self.height = event.height
        self.draw_world_map()
        # resize the canvas 
#         self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
#         self.scale("all",0,0,wscale,hscale)

    def recenter(self,new_center):
        self.corner[0] = new_center[0]-self.pixel_res*self.width*.5
        self.corner[1] = new_center[1]-self.pixel_res*self.height*.5
        self.draw_world_map()

    def rezoom(self,zoom,x,y):
        """recentres the map and changes zoom"""
        # hacky zoom
        new_center = [x*self.pixel_res+self.corner[0],
                        y*self.pixel_res+self.corner[1]
                        ]
        self.pixel_res*=zoom
        self.recenter(new_center)


    def _on_left_click(self,event):
        """on_leftclick
        
        zooms the map"""
#         self.recenter(event.x,event.y)
        self.rezoom(.5,event.x,event.y)

    def _on_right_click(self,event):
        """on_rightclick
        
        unzooms the map"""
        self.rezoom(2,event.x,event.y)

#     def _on_mousewheel(self,event):
#         """_on_mousewheel
#         
#         zooms"""
#         self.rezoom(2**(event.delta*self.zoom_sensitivity),event.x,event.y)


root = tkinter.Tk()
canvas = MapCanvas(root, width=1024, height=768)
root.bind("<space>",canvas._space)
canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)
canvas.draw_world_map()
root.mainloop()












