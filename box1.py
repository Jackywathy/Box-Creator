import dxfwrite
from dxfwrite import DXFEngine as dxf
import os
from decimal import *
import stat
import copy
# red = 1, blue = 5
# size_height = int(input('Height'))
# size_width = int(input("widht"))
# materialThickness = int(input('mat.Thickness')
# lenNotch = int(input('len_notuch')
# the length of each notch

def round_down(num, divisor):
    return num - (num%divisor)


# some constants
if os.name == 'nt':
    deskTop = os.path.expanduser("~\\Desktop\\")

else:
    deskTop = os.path.expanduser("~/Desktop/")

if 'L:' in deskTop:
    deskTop = ''

RED = 1
laserThickness = 0.01
laser_error = Decimal(40) / 100
main_drawing = dxf.drawing('main_drawing.dxf')

def save_read_only(drawing,path = None):
    """Unread-only a file, then sets it to write and saves, then read-onlies it again"""
    if not path:
        path = 'output.dxf'
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



# key vars

class Base(BaseShape):
    """The Base shape"""
    def __init__(self, height_base, width_base, mat_thickness,
                 notch_bottom_length, notch_bottom_number,
                 notch_side_length, notch_side_number,
                 margin_error = laser_error):

        self.mat_thickness = Decimal(mat_thickness)
        self.margin_error = margin_error
        # set some self-variables

        self.all_points = [
            [(self.mat_thickness, self.mat_thickness)],                           # bottom left
            [(width_base - self.mat_thickness, self.mat_thickness)],              # bottom right
            [(width_base - self.mat_thickness, height_base - self.mat_thickness)],  # top right
            [(self.mat_thickness, height_base - self.mat_thickness)]              # top left
        ]

        self.correction = margin_error

        # width = left to right, height = up to down
        self.width = width_base
        self.height = height_base
        self.margin_error = margin_error
        # non-esistant ones- storage for the depression and notch sizes
        # [length, notches]

        if (notch_bottom_number * (notch_bottom_length + self.mat_thickness)) > self.width:
            print("The width is too short")
            raise BaseException
        elif (notch_side_number * (notch_side_length + self.mat_thickness )) > self.height:
            print("The height is too short")
            raise BaseException

        self.depression_bottom = [Decimal(self.width - (notch_bottom_length * notch_bottom_number) - (2 * self.mat_thickness)) / notch_bottom_number,
                                  notch_bottom_number + 1]

        self.depression_side = [Decimal(self.height - (notch_side_length * notch_side_number) - (2 * self.mat_thickness)) / notch_side_number,
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


        if self.height < (2*self.mat_thickness + (length_notch_height + self.mat_thickness) * number_notch_height):
            print("Height too long!")
            raise BaseException



        # some more values

        self.notch_side_right = [length_notch_height,
                                 number_notch_height]

        self.depress_side_right = [Decimal(
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
    half_side_depression = Decimal(depress_side_len) / 2
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
            """ WARMING COMPLETLY BROKEN- DO NOT USE!"""  #TODO FINISH THIS!
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




def insert_line(drawing,gap,startpoint,*args):
    """Inserts all the items in 1 line, with a gap of gap"""

    for item in args:
        print(item)
        assert isinstance(item,BaseShape)

        item.insert(drawing, startpoint)
        startpoint = create_point(startpoint,item.width + gap, 0)
    drawing.save()

if __name__ == '__main__':

    if not input('Press Enter for automatic'):
        base = Base(
            height_base=200,width_base=300, mat_thickness='5',
            notch_bottom_length=30, notch_bottom_number=2,
            notch_side_length=30, notch_side_number=2,
            margin_error = laser_error
        )
        side = Side(
            baseObject=base,
            height = 100,
            length_notch_height=30,
            number_notch_height=1,
            margin_error = laser_error,
            side='side'
        )

        bottom = Side(
            baseObject=base,
            height = 100,
            length_notch_height=30,
            number_notch_height=1,
            margin_error = laser_error,
            side = 'bottom'
        )
        main_drawing = dxf.drawing('main.dxf')
        base.insert(main_drawing, (0, 0))
        side.insert(main_drawing, (500,0))
        bottom.insert(main_drawing, (1000,0))
        name = input("Name of output file")
        if name:
            main_drawing.saveas(name)
        else:
            main_drawing.save()

    else:

        length = Decimal(input('Enter Box Length'))
        width = Decimal(input('Enter Box Width'))
        height = Decimal(input("Enter Box Height"))
        materialThickness = Decimal(input('Material Thickness'))

