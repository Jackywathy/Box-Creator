__author__ = 'Jack,Shovel&Archie. D. Comben project manger'
"""V.0.1, unstable basic version. Not all features implemented. To be fixed after Y10 exams"""

from dxfwrite import DXFEngine as dxf

import ezdxf
import os
from os.path import join, expanduser

import stat
import copy

def round_down(num, divisor):
    return num - (num%divisor)

if os.name == 'nt':
    deskTop = os.path.expanduser("~\\Desktop\\")
else:
    deskTop = os.path.expanduser("~/Desktop/")
if 'L:' in deskTop:
    deskTop = ''

RED = 1
laserThickness = 0.00
laser_error = 4 / 10

def save_read_only(drawing,path = None):
    """Unread-only a file, then sets it to write and saves, then read-onlies it again"""
    if not path:
        path = deskTop + 'output.dxf'
    try:
        os.chmod(path, stat.S_IWRITE)
        drawing.save()
        os.chmod(path, stat.S_IREAD)

    except FileNotFoundError:
        drawing.save()


class BaseShape:
    def save(self, name = 'output'):
        """A function with joins all the points in self.allpoints together and chucks it onto the same file as the directory the
           file is located at: DEPRECIATED!!! Use insert now TODO REMOVE!!!"""
        prev_point = None
        drawing = dxf.drawing('forcedsave.dxf')
        drawing.add_layer("LINES")
        for list_points in self.all_points:
            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line(prev_point, point, thickness=laserThickness, color=RED, layer = "LINES"))
                prev_point = point
        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=laserThickness, color=RED, layer = "LINES"))
        save_read_only(drawing)


    def insert(self, drawing,offset = (0,0)):
        """Inserts the drawing into the global variable main_drawing"""
        prev_point = None
        drawing.add_layer('LINES')

        for list_points in self.all_points:
            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line((prev_point[0] + offset[0], prev_point[1] + offset[1]),
                                              (point[0] + offset[0], point[1] + offset[1]),
                                              thickness=laserThickness, color=RED,layer='LINES'))
                prev_point = point
        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=laserThickness, color=RED, layer='LINES'))

    def insert_all_inline(gap,*args, insert_point = (0,0)):
        """takes in all BaseShape objects and their descendants and chucks it all into 'maindrawing' in a line. Give it a gap distance"""



class Base(BaseShape):
    """The Base shape"""
    def __init__(self, height_base, width_base, mat_thickness,
                 notch_bottom_length, notch_bottom_number,
                 notch_side_length, notch_side_number,
                 margin_error = laser_error):

        self.mat_thickness = float(mat_thickness)
        self.margin_error = margin_error
        # set some self-variables

        self.all_points = [
            [(self.mat_thickness, self.mat_thickness)],                           # bottom left
            [(width_base - self.mat_thickness, self.mat_thickness)],              # bottom right
            [(width_base - self.mat_thickness, height_base - self.mat_thickness)],# top right
            [(self.mat_thickness, height_base - self.mat_thickness)]              # top left
        ]

        self.correction = margin_error

        # width = left to right, height = up to down
        self.width = width_base
        self.height = height_base
        self.margin_error = margin_error
        # storage for the depression and notch sizes
        # [length, notches]

        if (notch_bottom_number * (notch_bottom_length + self.mat_thickness)) > self.width:
            print("The width is too short")
            raise BaseException
        elif (notch_side_number * (notch_side_length + self.mat_thickness )) > self.height:
            print("The height is too short")
            raise BaseException

        self.depression_bottom = [float(self.width - (notch_bottom_length * notch_bottom_number) - (2 * self.mat_thickness)) / notch_bottom_number,
                                  notch_bottom_number + 1]

        self.depression_side = [float(self.height - (notch_side_length * notch_side_number) - (2 * self.mat_thickness)) / notch_side_number,
                                notch_side_number + 1]

        self.notch_side = [notch_side_length,
                           notch_side_number]

        self.notch_bottom = [notch_bottom_length,
                             notch_bottom_number]
        '''
        self.all_points is a list of lists, of tuples
        [ [ (2,2), (3,3)], [ (3,4) ] ]
        in the main list, there are 4 lists
        each smaller list contains all the points
        '''
        # measure the length of the bottom notches

        point_num = 0
        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator_base(side, self.depression_bottom[0], self.depression_side[0],
                                                          notch_bottom_number, notch_bottom_length,
                                                          notch_side_number, notch_side_length,
                                                          point, self.mat_thickness,local_laser_error=margin_error)



    def recommend_notch_top(self):
        """Finds the Recommended Size of the Notches"""
        ret = []
        # try to make with 1 notches each
        approx_base = int(round_down(self.width/2, 5))
        ret.append(approx_base)

        # try to make 2 notches each side
        approx_base = int(round_down(self.width/4, 5))
        ret.append(approx_base)

        # try to make with 3 notches
        approx_base = int(round_down(self.width/6, 5))
        ret.append(approx_base)
        return ret

    def recommend_notch_side(self):
        ret = []
        approx_side = int(round_down(self.height/2, 5))
        ret.append(approx_side)

        # try to make 2 notches each side
        approx_side = int(round_down(self.height/4, 5))
        ret.append(approx_side)

        # try to make with 3 notches
        approx_side = int(round_down(self.height/6, 5))
        ret.append(approx_side)
        return ret




class Side(BaseShape):
    """the two sides on left and right. The left bit is less big """
    def __init__(self, baseObject, height, length_notch_height, number_notch_height,side = 'side', top = 0,margin_error = laser_error):
        assert type(baseObject) == Base

        if side == 'side':
            self.width = baseObject.height
            self.height = height
            self.baseObject = baseObject
            self.mat_thickness = baseObject.mat_thickness
            self.notch_bottom = copy.deepcopy(baseObject.depression_side)
            self.depress_bottom = copy.deepcopy(baseObject.notch_side)

        elif side == 'bottom':
            self.width = baseObject.width
            self.height = height
            self.baseObject = baseObject
            self.mat_thickness = baseObject.mat_thickness
            self.notch_bottom = copy.deepcopy(baseObject.depression_bottom)
            self.depress_bottom = copy.deepcopy(baseObject.notch_bottom)

        else:
            print("Unexpected side argument: %s" % side)
            raise BaseException

      #  if self.height < (2*self.mat_thickness + (length_notch_height + self.mat_thickness) * number_notch_height):
      #      print("Height too short for that number of pins.")
      #      raise BaseException


        self.notch_side_right = [length_notch_height,
                                 number_notch_height]
        self.depress_side_right = [float(
            self.height - (2 * self.mat_thickness) - (length_notch_height * number_notch_height)) / number_notch_height,
                                   number_notch_height + 1]

        # the points
        self.all_points = [
                            [(0, 0)],
                            [(self.width - self.mat_thickness, 0)],
                            [(self.width - self.mat_thickness, self.height)],
                            [(0, self.height)]
                           ]

        point_num = 0
        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator_side(side,self.depress_bottom[0], self.depress_side_right[0], self.notch_bottom[1], self.notch_side_right[1],
                                                          self.notch_bottom[0], self.notch_side_right[0], point, self.mat_thickness, top=False)




# for base only
def segment_creator_base(direction,
                         depress_bottom_length, depress_side_length,
                         notch_bottom_number, notch_bottom_length,
                         notch_side_number, notch_side_length,
                         point, notch_thickness, local_laser_error = laser_error):
    """Takes in 1 number (direction) that follows this rule
    :0 = goes right
    :1 = goes up
    :2 = goes left
    :3 = goes down
    returns a list

    - = left
    + = right
    """
    ret = []
    half_depress_bottom = depress_bottom_length/2
    half_depress_side = depress_side_length/2
    half_laser_error = laser_error/2
    next_point = point
    if direction == 0:
        for iteration in range(notch_bottom_number):
            next_point = ((next_point[0] + half_depress_bottom - local_laser_error), next_point[1])  # go right  (minused laser cutter here )
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_thickness)      # go down
            ret.append(next_point)
            next_point = (next_point[0] + notch_bottom_length + local_laser_error, next_point[1])         # go right * length of notch (plused laser cutter)
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go upz
            ret.append(next_point)
            next_point = (next_point[0] + half_depress_bottom, next_point[1])  # go right
            ret.append(next_point)

    elif direction == 1:
        for iteration in range(notch_side_number):
            next_point = (next_point[0], next_point[1] + half_depress_side)    # go up
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])      # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_side_length + local_laser_error)         # go up * len of notch ( added laser cutter)
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])      # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + half_depress_side - local_laser_error)    # go up   (minused laser cutter

    elif direction == 2:
        for iteration in range(notch_bottom_number):
            next_point = (next_point[0] - half_depress_bottom, next_point[1])  # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go up
            ret.append(next_point)
            next_point = (next_point[0] - notch_bottom_length - local_laser_error, next_point[1])         # go left * length of notch ( minused laser cutter
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_thickness)      # go down
            ret.append(next_point)
            next_point = (next_point[0] - half_depress_bottom + local_laser_error, next_point[1])  # go left  (added laser cutter

    elif direction == 3:
        for iteration in range(notch_side_number):
            next_point = (next_point[0], next_point[1] - half_depress_side)    # go down
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])      # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_side_length - local_laser_error)         # go down * length of notch ( - laser here)
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])      # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - half_depress_side + local_laser_error)    # go down (+ laser here



    return ret


def segment_creator_side(direction,
                         depress_bottom_len, depress_side_len,
                         num_notch_bottom, num_notch_side,
                         length_bottom_notch, length_side_notch,
                         point, notch_thickness, top=False, laser_error = laser_error):
    """Takes in 1 number (direction) that follows this rule
    :0 = goes right
    :1 = goes up
    :2 = goes left
    :3 = goes down
    returns a list

    - = left
    + = right
    """
    next_point = point
    ret = []
    half_bottom_notch = length_bottom_notch / 2
    half_side_depression = float(depress_side_len) / 2
    if direction == 0:
        # do the first special notch
        for iteration in range(num_notch_bottom):
            if iteration == 0:  # go right and then up
                next_point = (next_point[0] + notch_thickness + half_bottom_notch, next_point[1])  # go right a lot
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] + notch_thickness)  # then go up
                ret.append(next_point)

            elif iteration == num_notch_bottom -1:
                next_point = (next_point[0] + depress_bottom_len, next_point[1])  # go right * depression
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] - notch_thickness)  # go down
                ret.append(next_point)
                next_point = (next_point[0] + notch_thickness, next_point[1])  # go right * mat)thickness
                ret.append(next_point)

            else:
                next_point = (next_point[0] + depress_bottom_len,next_point[1])  # right
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] - notch_thickness)  # down
                ret.append(next_point)
                next_point = (next_point[0] + length_bottom_notch, next_point[1])  # right
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] + notch_thickness)       # up
                ret.append(next_point)

    elif direction == 1:
        next_point = (next_point[0], next_point[1] + notch_thickness)    # create the top bit and go up a ltitle
        ret.append(next_point)

        for iteration in range(num_notch_side):
            next_point = (next_point[0], next_point[1] + half_side_depression)  # go up
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])       # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + length_side_notch + laser_error)     # go up (+lasercutt
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])       # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + half_side_depression - laser_error)  # go up
            ret.append(next_point)

        next_point = (next_point[0], next_point[1] + notch_thickness)           # go up a little again
        ret.append(next_point)

    elif direction == 2:
        if top:
            """ WARNING COMPLETLY BROKEN- DO NOT USE!"""  #TODO FINISH THIS!
            for iteration in range(num_notch_bottom):
                if iteration == 0:
                    next_point = (next_point[0] - notch_thickness, next_point[1])           # go left
                    ret.append(next_point)
                    next_point = (next_point[0], next_point[1] - notch_thickness)           # go down
                    ret.append(next_point)
                elif iteration == num_notch_bottom - 1:
                    next_point = (next_point[0] - notch_thickness, next_point[1])
                    ret.append(next_point)
                else:
                    next_point = (next_point[0] - depress_bottom_len, next_point[1])       # go left
                    ret.append(next_point)
                    next_point = (next_point[0], next_point[1] + half_side_depression)  # go up
                    ret.append(next_point)
                    next_point = (next_point[0] - length_bottom_notch, next_point[1])  # go left again
                    ret.append(next_point)
                    next_point = (next_point[0], next_point[1] - half_side_depression)  # go down
                    ret.append(next_point)
    elif direction == 3:
        next_point = (next_point[0], next_point[1] - notch_thickness)
        ret.append(next_point)
        for i in range(num_notch_side):
            next_point = (next_point[0], next_point[1] - half_side_depression)  # go down
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])       # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - length_side_notch)     # go down
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])       # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - half_side_depression)  # go down
            ret.append(next_point)
        next_point = (next_point[0], next_point[1] - notch_thickness)
        ret.append(next_point)




    return ret


def create_point(start_point,x,y):
    """Takes in a point, adds the x and y to it, then adds some tolerance"""
    return (start_point[0] + x), (start_point[1] + y)




##def insert_line(drawing,gap,startpoint,*args):
##    """Inserts all the items in 1 line, with a gap of gap"""
##
##    for item in args:
##        print(item)
##        assert isinstance(item,BaseShape)
##
##        item.insert(drawing, startpoint)
##        startpoint = create_point(startpoint,item.width + gap, 0)
##    drawing.save()

if __name__ == '__main__':
    print("Box Creator - unstable prototype version 0.0.1")
    print()
    name = input("What is your name? ")
    length = float(input("Box length: "))#--- x
    breadth = float(input("Box breadth: "))#/ z
    height = float(input("Box height: "))#|  y
    mat_thickness = float(input("Material thickness: "))
    print("Margin of error is", laser_error)
    max_notch = int(min(length, breadth, height) / mat_thickness / 2)
    default = int(input("Enter the number of pins. The suggested maximum is " + str(max_notch)+": "))
    print()
    print("In AutoCAD:")
    print(" - Zoom out")
    print(" - Select By Layer and change line thickness to 0.00mm")
    print(" - Set laser specific settings through properties")
    print(" - Select ULS printer")
    print(" - Change units to mm")
    print(" - Untick fit to scale. change scale 1:1")
    print(" - Change plot area to window and draw a window around all objects to print")
    print()
    print("If the drawing was not produced correctly, please write down the values")
    print("you used above so that they can be used to identify and correct software")
    print("errors.")
    print()
    print()
    if not default:
        default = 5
    

  #  if input('is ' + str(default) +' notches and' +' ' + str(length // (default * 2)) + ' mm each pin on length good (Y/N)') != 'N':
    notch_len_num = default
    notch_len_len = length // (default * 2)
  #  else:
  #      notch_len_num = int(input("ENTER Number of notches, Lenght"))
  #      notch_len_len = Decimal(input("Enter len of notches, length"))


  #  if input('is ' + str(default) + ' notches and' +' '+ str(height // (default * 2)) + ' mm on each pin on height good (Y/N)') != 'N':
    notch_hei_num = default
    notch_hei_len = height // (default * 2)
  #  else:
  #      notch_hei_num = int(input("ENTER Number of notches, height"))
  #      notch_hei_len = Decimal(input("Enter len of notches, height"))


  #  if input('is ' + str(default) + ' notches and' + ' ' +str(breadth // (default * 2)) + ' mm on each pin on breadth good (Y/N)') != 'N':
    notch_bre_num = default
    notch_bre_len = breadth // (default * 2)
  #  else:
  #      notch_bre_num = int(input("ENTER Number of notches, breadth"))
  #      notch_bre_len = Decimal(input("Enter len of notches, breadth"))
   
    between = 3
      
    base = Base(
        height_base=breadth,width_base=length, mat_thickness=mat_thickness,
        notch_bottom_length=notch_len_len, notch_bottom_number=notch_len_num,
        notch_side_length=notch_bre_len, notch_side_number=notch_bre_num,
        margin_error = laser_error
    )
    side = Side(
        baseObject=base,
        height = height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error = laser_error,
        side='side'
    )

    bottom = Side(
        baseObject=base,
        height = height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error = laser_error,
        side = 'bottom'
    )
    file_name = name + '_box.dxf'
    main_drawing = dxf.drawing(file_name)
    insert_point = [0,0]
    base.insert(main_drawing, insert_point)
    # 0 point
    insert_point[0] += length + between

    
    side.insert(main_drawing, insert_point)
    
    insert_point[0] += breadth + between
    
    side.insert(main_drawing, insert_point)
    insert_point[0] += breadth + between


    bottom.insert(main_drawing, insert_point)
    insert_point[0] += length + between
    
    bottom.insert(main_drawing, insert_point)
    try:
        main_drawing.save()
    except PermissionError as e:
        print("Unable to save due to file open in another program.")
        input("Press enter to retry")
        main_drawing.save()
    print()
    print("Drawing has been saved.")
    


