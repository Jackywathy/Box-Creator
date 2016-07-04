#import dxfwrite
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

#Sum constants

K_RED = 1
K_THICKNESS = 0.01
K_EXTRA_MATERIAL = Decimal(40) / 100



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
                    drawing.add(dxf.line(prev_point, point, thickness=K_THICKNESS, color=K_RED, layer ="LINES"))
                prev_point = point
        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=K_THICKNESS, color=K_RED, layer ="LINES"))
        save_read_only(drawing)


    def insert(self, drawing, offset = (0,0)):
        """Inserts the drawing into the drawing given"""
        prev_point = None
        drawing.add_layer('LINES')

        for list_points in self.all_points:
            for point in list_points:
                if prev_point:
                    drawing.add(dxf.line((prev_point[0] + offset[0],  prev_point[1] + offset[1]),
                                         (point[0] + offset[0],       point[1] + offset[1]),
                                         thickness=K_THICKNESS, color=K_RED, layer='LINES'))
                prev_point = point
        drawing.add(dxf.line(prev_point, self.all_points[0][0], thickness=K_THICKNESS, color=K_RED, layer='LINES'))


# height_base = breadt, width_base = length
#TODO REFACTOR CODE TO USE MORE _ VARS SO IT DOESNT SHADOW SO MUCH
class Base(BaseShape):
    """The Base of the shape. Inherits save-functions from BaseShape. Breadth is y axis, length is x axis"""
    def __init__(self, _length, _breadth, _thickness,
                 length_n_len, length_n_num,
                 breadth_n_len, breadth_n_num,
                 _correction=K_EXTRA_MATERIAL,
                 ):


        # set some self-variables

        self.all_points = [
            [(_thickness,            _thickness)],                 # bottom left
            [(_length - _thickness,  _thickness)],                 # bottom right
            [(_length - _thickness,  _breadth - _thickness)],      # top right
            [(_thickness,            _breadth - _thickness)]       # top left
        ]

        # width = left to right, height = up to down TODO REMOVE LEGACY VALUES!!!!
        self.length = self.width =  _length
        self.breadth = self.height = _breadth

        self.thickness = Decimal(_thickness)
        self.correction = _correction

        #TODO remove legacy VALUES!
        self.mat_thickness = _thickness


        # non-esistant ones- storage for the depression and notch sizes
        # [length, notches]

        if (length_n_num * length_n_len + 2 * _thickness) > _length:
            # the minimum theretical size of a box.
            raise ValueError("The length is too short")

        if (breadth_n_num * breadth_n_len + 2 * _thickness) > _breadth:
            raise ValueError("The breadth is too short")

        if (_length - (length_n_num * length_n_len + 2 * _thickness)) // length_n_num < length_n_num * _thickness:
            # depressions are smaller than thickness
            print("LENGTH IS VERY SMALL")

        if (_breadth - (breadth_n_num * breadth_n_len + 2 * _thickness)) // breadth_n_num < breadth_n_num * _thickness:
            print("BREADTH IS VERY SMALL")

        # REMOVE SOME OF THESE! TODO REMOVE THE SECOND = !

        self.depression_length = self.depression_side = [Decimal(_length - (length_n_num * length_n_num) - (2 * _thickness)) / length_n_num,
                                  length_n_num + 1]

        self.depression_breadth = self.depression_bottom = [Decimal(_breadth - (breadth_n_num * breadth_n_len) - (2 * _thickness)) / breadth_n_num,
                                breadth_n_num + 1]

        self.notch_length = self.notch_bottom =  [length_n_len, length_n_num]

        self.notch_breadth = self.notch_side = [breadth_n_len, breadth_n_num]

        '''
        self.all_points is a list of lists, of tuples
        [ [ (2,2), (3,3)], [ (3,4) ] ]
        in the main list, there are 4 lists
        each smaller list contains all the points
        '''
        # measure the length of the bottom notches

        for iteration in range(4):
            # 0 = bottom, 1 = rside, 2 = top, 3 = lside
            point = self.all_points[iteration][0]
            # start in a corner

            self.all_points[iteration] += segment_creator_base(
                iteration,
                self.depression_length[0], self.depression_breadth[0],
                length_n_num, length_n_len,
                breadth_n_num, breadth_n_len,
                point, _thickness, local_laser_error=_correction
                                                            )



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
    def __init__(self, baseObject, height, length_notch_height, number_notch_height, side = 'side', top = 0, margin_error = K_EXTRA_MATERIAL):
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
                         point, notch_thickness, local_laser_error = K_EXTRA_MATERIAL):
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
    half_laser_error = K_EXTRA_MATERIAL / 2
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
                         point, notch_thickness, top=False, laser_error = K_EXTRA_MATERIAL):
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


if __name__ == '__main__': #TODO- GRAPHICS
    length = Decimal(input("ENTER LENGTH(all mm): "))#--- x
    height = Decimal(input("ENTER HEIGHT: "))#|  y
    breadth = Decimal(input("ENTER BREADTH: "))#/ z
    thickness = Decimal(input("ENTER THICKNESS: "))
    print("Margin of error is", K_EXTRA_MATERIAL)
    
    # 5 notches is default
    try:
        default = int(input("Enter default num,. of pins, (5 is default)"))
    except ValueError:
        default = 5
    if not default:
        default = 5
    

    if input('is ' + str(default) +' notches and' +' ' + str(length // (default * 2)) + ' mm each pin on length good (Y/N)') != 'N':
        notch_len_num = default
        notch_len_len = length // (default * 2)
    else:
        notch_len_num = int(input("ENTER Number of notches, Lenght"))
        notch_len_len = Decimal(input("Enter len of notches, length"))


    if input('is ' + str(default) + ' notches and' +' '+ str(height // (default * 2)) + ' mm on each pin on height good (Y/N)') != 'N':
        notch_hei_num = default
        notch_hei_len = height // (default * 2)
    else:
        notch_hei_num = int(input("ENTER Number of notches, height"))
        notch_hei_len = Decimal(input("Enter len of notches, height"))


    if input('is ' + str(default) + ' notches and' + ' ' +str(breadth // (default * 2)) + ' mm on each pin on breadth good (Y/N)') != 'N':
        notch_bre_num = default
        notch_bre_len = breadth // (default * 2)
    else:
        notch_bre_num = int(input("ENTER Number of notches, breadth"))
        notch_bre_len = Decimal(input("Enter len of notches, breadth"))

    

    
    

    between = 20
    
    

    
    base = Base(
        _length=length, _breadth=breadth, _thickness=thickness,
        length_n_len=notch_len_len, length_n_num=notch_len_num,
        breadth_n_len=notch_bre_len, breadth_n_num=notch_bre_num,
        _correction = K_EXTRA_MATERIAL
    )
    side = Side(
        baseObject=base,
        height = height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error = K_EXTRA_MATERIAL,
        side='side'
    )

    bottom = Side(
        baseObject=base,
        height = height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error = K_EXTRA_MATERIAL,
        side = 'bottom'
    )
    main_drawing = dxf.drawing('main.dxf')
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
    save_read_only(main_drawing)



