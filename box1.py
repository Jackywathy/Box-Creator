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


# some constants
if os.name == 'nt':
    deskTop = os.path.expanduser("~\\Desktop\\")

else:
    deskTop = os.path.expanduser("~/Desktop/")

RED = 1
laserThickness = 0.01
main_drawing = dxf.drawing(deskTop + 'main_drawing.dxf')

class BaseShape:
    def save(self, name = 'output'):
        """A function with joins all the points in self.allpoints together"""
        prev_point = None
        drawing = dxf.drawing(deskTop + name + '.dxf')

        for list_points in self.all_points:

            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line(prev_point, point, thickness=laserThickness, color=RED))
                prev_point = point

        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=laserThickness, color=RED))

        try:
            os.chmod(deskTop + 'output.dxf', stat.S_IWRITE)
            drawing.save()
            os.chmod(deskTop + 'output.dxf', stat.S_IREAD)
        except FileNotFoundError:
            drawing.save()


    def insert(self, offset = (0,0)):
        """Inserts the drawing into the global variable main_drawing"""
        global main_drawing
        prev_point = None

        for list_points in self.all_points:

            for point in list_points:
                if prev_point:
                    main_drawing.add(dxf.line((prev_point[0] + offset[0], prev_point[1] + offset[1]), (point[0] + offset[0], point[1] + offset[1]), thickness=laserThickness, color=RED))
                prev_point = point

        main_drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=laserThickness, color=RED))


class Base(BaseShape):
    """The Base shape"""
    def __init__(self, height_base, width_base, height_box, mat_thickness, margin_error = 2):
        #bottom left corner is 0,0
        #create the bassseee temp stuff~!
        bottom_left = [(mat_thickness, mat_thickness)]
        top_left = [(mat_thickness, height_base - mat_thickness)]
        top_right = [(width_base-mat_thickness, height_base - mat_thickness)]
        bottom_right =  [(width_base - mat_thickness, mat_thickness)]

        # set the self-variable
        self.mat_thickness = mat_thickness
        self.all_points = [bottom_left, bottom_right, top_right, top_left]
        self.correction = margin_error
        self.width = width_base
        self.height = height_base
        self.height_box = height_box

        # non-esistant ones- storage for the depression and notch sizes
        # [length, notches]
        self.depression_bottom = [None,None]
        self.depression_side = [None,None]
        self.notch_side = [None,None]
        self.notch_bottom = [None,None]



        # linked pieces
        self.piece_bottom = None
        self.piece_side = None

        # self.all_points is a list of lists, of tuples
        # [ [ (2,2), (3,3)], [ (3,4) ] ]
        # in the main list, there are 4 lists
        # each smaller list contains all the points
        

        


    def add_notch(self, notch_bottom_length, notch_bottom_number, notch_side_length, notch_side_number):
        """Adds all the notches, given the length/number of notches"""

        # calcs to find the distance:
        # if both values are given
        # notch_bottom_length, notch_side_number

        if (notch_bottom_number * (notch_bottom_length + self.mat_thickness)) > self.width:
            print("The width is too short")
            raise BaseException
        elif (notch_side_number * (notch_side_length + self.mat_thickness )) > self.height:
            print("The height is too short")
            raise BaseException
        # measure the length of the bottom notches

        self.depression_side[1] = notch_side_number + 1
        self.depression_bottom[1] = notch_bottom_number + 1
        self.depression_bottom[0] = Decimal(self.width - (notch_bottom_length * notch_bottom_number) - (2 * self.mat_thickness)) / notch_bottom_number
        self.depression_side[0] = Decimal(self.height - (notch_side_length * notch_side_number) - (2 * self.mat_thickness)) / notch_side_number
        self.notch_bottom[1] = notch_bottom_number
        self.notch_side[1] = notch_side_number
        self.notch_side[0] = notch_side_length
        self.notch_bottom[0] = notch_bottom_length

        # the depression about the base and sides
        # main driver code: crap loads of arguments and it will do you bidding!
        #start with bottom left corner

        point_num = 0
        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator_base(side, self.depression_bottom[0], self.depression_side[0], notch_bottom_number, notch_side_number, notch_bottom_length, notch_side_length,
                                                          point, self.mat_thickness)

    def create_part_side(self):
        self.piece_side1 = Side_side(self)


    def create_part_bottom(self):
        self.piece_bottom1 = Side_bottom(self)





class Side_side(BaseShape):
    """the two sides on left and right. The left bit is less big """
    def __init__(self, baseObject, newmat = None):
        assert type(baseObject) == Base
        self.width = baseObject.height
        self.height = baseObject.height_box
        self.baseObject = baseObject


        # some more values
        self.notch_bottom = copy.deepcopy(baseObject.depression_side)
        self.notch_side = [None,None]
        self.depress_side = [None, None]
        self.depress_bottom = [None, self.notch_bottom[1] - 1]

        if not newmat:
            self.mat_thickness = baseObject.mat_thickness
        else:
            self.mat_thickness = newmat

        # the points
        self.bottomLeft = [(0, 0)]
        self.bottomRight = [(self.width - self.mat_thickness, 0)]
        self.topRight = [(self.width - self.mat_thickness, self.height)]
        self.topLeft = [(0, self.height)]
        self.all_points = [self.bottomLeft, self.bottomRight, self.topRight, self.topLeft]

        # fidn the size of depressions
        self.depress_bottom[0] = Decimal(self.width - (2 * self.mat_thickness) - (self.depress_bottom[1] * self.notch_bottom[0])) / self.depress_bottom[1]
        self.isheight = True # TODO fALSE

    def add_notch(self):
        if not self.isheight:
            print('Initiatize height notches first')
            raise BaseException

        point_num = 0
        for side in range(4):
            point = self.all_points[point_num][0]
            point_num += 1
            self.all_points[side] += segment_creator_side(side,self.depress_bottom[0], self.depress_side[0], self.notch_bottom[1], self.notch_side[1],
                                                          self.notch_bottom[0], self.notch_side[0], point, self.mat_thickness, top=False)


    def height_notch(self, length_notch, number_notch):
        """Create the depress side and notch_side variables. Include two end bits as part of number_notch"""

        # number of complete depressions = number of notches, but 2 mat_thickness bits at top and bottom
        self.depress_side[0]  = Decimal(self.height - (2 * self.mat_thickness) - (length_notch* number_notch)) / number_notch
        self.depress_side[1] = number_notch + 1
        self.notch_side[1] = number_notch
        self.notch_side[0] = length_notch
        self.isheight = True
        self.add_notch()


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
            next_point = (next_point[0], next_point[1] + notch_thickness)      # go upz
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
        


    return ret
            

def segment_creator_side(direction,depress_bottom, depress_side, num_notch_bottom, num_notch_side, length_bottom_notch, length_side_notch, point, notch_thickness, top = False):
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
    half_side_depression = depress_side / 2
    if direction == 0:
        # do the first special notch
        for iteration in range(num_notch_bottom):
            if iteration == 0:  # go right and then up
                next_point = (next_point[0] + notch_thickness + half_bottom_notch, next_point[1])  # go right a lot
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] + notch_thickness)  # then go up
                ret.append(next_point)

            elif iteration == num_notch_bottom -1:
                next_point = (next_point[0] + depress_bottom, next_point[1])  # go right * depression
                ret.append(next_point)
                next_point = (next_point[0], next_point[1] - notch_thickness)  # go down
                ret.append(next_point)
                next_point = (next_point[0] + notch_thickness, next_point[1])  # go right * mat)thickness
                ret.append(next_point)

            else:
                next_point = (next_point[0] + depress_bottom,next_point[1])  # right
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
            next_point = (next_point[0], next_point[1] + length_side_notch)     # go up
            ret.append(next_point)
            next_point = (next_point[0] - notch_thickness, next_point[1])       # go left
            ret.append(next_point)
            next_point = (next_point[0], next_point[1] + half_side_depression)  # go up
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
                    next_point = (next_point[0] - depress_bottom, next_point[1])       # go left
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

        
        



size_height = 200
size_width = 200
base = Base(size_height,size_width, 100, 5)


base.add_notch(50,2,50,2)

base.save()

base.create_part_side()

side1 = base.piece_side1
side1.height_notch(20,1)
base.insert()
side1.insert((300,0))
side1.insert((-300,0))
side1.insert((0,300))
side1.insert((0,-300))


