import dxfwrite
from dxfwrite import DXFEngine as dxf
import os
from decimal import *
import stat
# red = 1, blue = 5
#size_height = int(input('Height'))
#size_width = int(input("widht"))
#materialThickness = int(input('mat.Thickness')
#lenNotch = int(input('len_notuch')
# the length of each notch

class Base:
    def __init__(self, height_base,width_base,mat_thickness, margin_error = 2):
        #bottom left corner is 0,0
        # create the bassseee
        bottom_left = [(mat_thickness, mat_thickness)]
        top_left = [(mat_thickness, height_base - mat_thickness)]
        top_right = [(width_base-mat_thickness, height_base - mat_thickness)]
        bottom_right =  [(width_base - mat_thickness, mat_thickness)]
        self.mat_thickness = mat_thickness
        self.all_points = [bottom_left, bottom_right, top_right, top_left]
        self.correction = margin_error
        self.width = width_base
        self.height = height_base
        print(self.all_points)

        # self.all_points is a list of lists, of tuples
        # [ [ (2,2), (3,3)], [ (3,4) ] ]
        # in the main list, there are 4 lists
        # each smaller list contains all the points
        

        
    def save(self):
        prev_point = None
        drawing = dxf.drawing('output.dxf')
        print(self.all_points)
        print()

        for list_points in self.all_points:
            print('start corner', len(list_points))

            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line(prev_point, point, thickness = 2, color= 1))
                    print(prev_point,point)
                prev_point = point

            break

        #drawing.add(dxf.line(prev_point,self.all_points[0][0], thickness=10,color=1))

        os.chmod('output.dxf', stat.S_IWRITE)
        drawing.save()
        os.chmod('output.dxf', stat.S_IREAD)

    def add_notch(self,number_notch = None,len_notch=None):
        """Adds all the notches, given the length/number of notches"""

        # calcs to find the distance:
        if number_notch and len_notch:
            if (len_notch * number_notch) * 2 > self.width:
                print("The width is too short")
                return
            elif (len_notch * number_notch) * 2 > self.height:
                print("The height is too short")
                return
            # measure the length of the bottom notches
            depression_bottom = Decimal(self.width - (len_notch * number_notch)) /number_notch
            depression_side = Decimal(self.height - (len_notch * number_notch)) / number_notch
            # the depression about the base and sides
    
            
        point_num = 0
        # the main list to select from
        



        # main driver code: give it number_notch, len_notch and depression_side and depression_bottom
        #start with bottom left corner
        print('dpression', depression_bottom, depression_side)


        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator(side, depression_bottom,depression_side, number_notch, point,self.mat_thickness)
            break

def segment_creator(direction,depress_bottom, depress_side,num_notch, point, notch_thickness):
    """Takes in 1 number (direciotn) that follws this rule
    :0 = goes right
    :1 = goes up
    :2 = goes left
    :3 = goes down
    returns a list
    """
    ret = []
    half_depress_bottom = depress_bottom/2
    half_depress_side = depress_side/2
    if direction == 0:
        next_point = point
        for iteration in range(num_notch):
            next_point = (next_point[0] + half_depress_bottom, next_point[1])  # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_thickness)      # go down
            ret.append(next_point)
            next_point = (next_point[0] + depress_bottom, next_point[1])       # go right x2
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go up
            ret.append(next_point)
            next_point = (next_point[0] + half_depress_bottom, next_point[1])  # go right
            ret.append(next_point)
        


        
    return ret
            

        
        
        
        



size_height = 200
size_width = 200
materialThickness = 2
base = Base(size_height,size_width,5)


base.add_notch(5,20)

base.save()





