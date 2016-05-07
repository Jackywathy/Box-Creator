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


# some constants
if os.name == 'nt':
    deskTop = os.path.expanduser("~\\Desktop\\")
else:
    deskTop = os.path.expanduser("~/Desktop/")


class BaseShape:
        def save_desktop(self):
            prev_point = None
            drawing = dxf.drawing(deskTop + 'output.dxf')
            print(self.all_points)
            print()

            for list_points in self.all_points:
                print('start corner', len(list_points))

                for point in list_points:
                    if prev_point:
                        drawing.add(dxf.line(prev_point, point, thickness = 2, color= 1))
                        print(prev_point,point)
                    prev_point = point

            drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=2,color=1))

            os.chmod(deskTop + 'output.dxf', stat.S_IWRITE)
            drawing.save()
            os.chmod(deskTop + 'output.dxf', stat.S_IREAD)


class Base(BaseShape):
    """The Base shape"""
    def __init__(self, height_base, width_base, height_box, mat_thickness, margin_error = 2):
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
        self.height_box = height_box
        self.depression_bottom = None
        self.depression_side = None
        self.piece_bottom = None
        self.piece_side = None

        print(self.all_points)

        # self.all_points is a list of lists, of tuples
        # [ [ (2,2), (3,3)], [ (3,4) ] ]
        # in the main list, there are 4 lists
        # each smaller list contains all the points
        

        
    def save(self):
        prev_point = None
        drawing = dxf.drawing(deskTop + 'output.dxf')
        print(self.all_points)
        print()

        for list_points in self.all_points:
            print('start corner', len(list_points))

            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line(prev_point, point, thickness = 2, color= 1))
                    print(prev_point,point)
                prev_point = point

        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=2,color=1))

        os.chmod(deskTop + 'output.dxf', stat.S_IWRITE)
        drawing.save()
        os.chmod(deskTop + 'output.dxf', stat.S_IREAD)

    def add_notch(self, numberNotchBottom = None, lengthNotchBottom=None, numberNotchSide = None, lengthNotchSide=None):
        """Adds all the notches, given the length/number of notches"""

        # calcs to find the distance:
        # if both values are given


        if numberNotchBottom and numberNotchSide and numberNotchSide and lengthNotchSide:
            if (numberNotchBottom * numberNotchSide) * 2 > self.width:
                print("The width is too short")
                raise BaseException
            elif (numberNotchSide * lengthNotchSide) * 2 > self.height:
                print("The height is too short")
                raise BaseException
            # measure the length of the bottom notches
            self.depression_bottom = Decimal(self.width - (numberNotchBottom * lengthNotchBottom) - (2 * self.mat_thickness)) / numberNotchBottom
            self.depression_side = Decimal(self.height - (numberNotchSide * lengthNotchSide) - (2 * self.mat_thickness)) / numberNotchSide
            # the depression about the base and sides
            

        # the main list to select from
        self.numberNotchBottom = numberNotchBottom
        self.lengthNotchBottom = lengthNotchBottom
        self.numberNotchSide = numberNotchSide
        self.lengthNotchSide = lengthNotchSide




        # main driver code: give it number_notch, len_notch and depression_side and depression_bottom
        #start with bottom left corner
        print('dpression', self.depression_bottom, self.depression_side)

        point_num = 0
        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator_base(side, self.depression_bottom, self.depression_side, numberNotchBottom, numberNotchSide,
                                                          lengthNotchBottom, lengthNotchSide, point, self.mat_thickness)

    def create_part_side(self):
        self.piece_side1 = Side_side(self)


    def create_part_bottom(self):
        self.piece_bottom1 = Side_bottom(self)


class Side_side(BaseShape):
    """the two sides on left and right. The left bit is less big """
    def __init__(self, baseObject):
        assert type(baseObject) == Base
        self.width = baseObject.height
        self.height = baseObject.height_box
        self.baseObject = baseObject

        self.bottomNotchLength = baseObject.depression_side
        self.bottomNotchNumber = baseObject.numberNotchSide

        self.mat_thickness = baseObject.mat_thickness

        self.num_notch_bottom = baseObject.height

        self.bottomLeft = [(0, 0)]
        self.bottomRight = [(self.width - self.mat_thickness, 0)]
        self.topRight = [(self.width - self.mat_thickness, self.height)]
        self.topLeft = [(0, self.height)]

        self.allpoints = [self.bottomLeft, self.bottomRight, self.topRight, self.topLeft]

        self.depress_bottom = Decimal(self.width - (self.bottomNotchLength * self.bottomNotchNumber)) / (self.bottomNotchNumber - 1)


        self.add_notch()

    def add_notch(self):

        point_num = 0
        for iteration in range(4):
            point = self.allpoints[point_num][0]
            point_num += 1
            #self.allpoints[iteration] += segment_creator_side(iteration,

    def height_notch(self, numberNotch = None, lenNotch = None):
        if numberNotch and lenNotch:   # calculate the depression of the height notches
            self.depress_height = Decimal(self.height - (4 * self.mat_thickness) - (numberNotch * lenNotch)) / (numberNotch - 1)

class Side_bottom:
    """The two sides on the bottom and top. The right bit is less big"""






# for base only
def segment_creator_base(direction,depress_bottom, depress_side, num_notch_bottom, num_notch_side, length_bottom_notch, length_side_notch, point, notch_thickness):
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
    half_depress_bottom = depress_bottom/2
    half_depress_side = depress_side/2
    next_point = point

    if direction == 0:
        for iteration in range(num_notch_bottom):
            next_point = (next_point[0] + half_depress_bottom, next_point[1])  # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_thickness)      # go down
            ret.append(next_point)
            next_point = (next_point[0] + length_bottom_notch, next_point[1])         # go right * length of notch
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go up
            ret.append(next_point)
            next_point = (next_point[0] + half_depress_bottom, next_point[1])  # go right
            ret.append(next_point)

    elif direction == 1:
        for iteration in range(num_notch_side):
            next_point = (next_point[0], next_point[1] + half_depress_side)    # go up
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])      # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + length_side_notch)         # go up * len of notch
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])      # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + half_depress_side)    # go up

    elif direction == 2:
        for iteration in range(num_notch_bottom):
            next_point = (next_point[0] - half_depress_bottom, next_point[1])  # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go up
            ret.append(next_point)
            next_point = (next_point[0] - length_bottom_notch, next_point[1])         # go left * length of notch
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - notch_thickness)      # go down
            ret.append(next_point)
            next_point = (next_point[0] - half_depress_bottom, next_point[1])  # go left

    elif direction == 3:
        for iteration in range(num_notch_side):
            next_point = (next_point[0], next_point[1] - half_depress_side)    # go down
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])      # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - length_side_notch)         # go down * length of notch
            ret.append(next_point)
            next_point = (next_point[0] + notch_thickness, next_point[1])      # go right
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] - half_depress_side)    # go down
        


    print(ret)
    return ret
            

def segment_creator_side(direction,depress_bottom, depress_side, num_notch_bottom, num_notch_side, length_bottom_notch, length_side_notch, point, notch_thickness):
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
    if direction == 0:
        pass
        
        
        



size_height = 400
size_width = 200
base = Base(size_height,size_width, 100, 5)


base.add_notch(4, 30, 4, 50)

base.save()





