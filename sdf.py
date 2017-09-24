__author__ = 'Jack,Shovel&Archie. D. Comben project manger'
"""V.0.1, unstable basic version. Not all features implemented. To be fixed after Y10 exams"""

# TODO - REFACTOR this

from dxfwrite import DXFEngine as dxf

import ezdxf
import ezdxf.modern.layouts as layouts

import os
import abc

from os.path import join, expanduser

import stat
import copy


def round_down(num, divisor):
    return num - (num % divisor)


desktopPath = expanduser(join('~', 'Desktop'))

RED = 1

LINE_WEIGHT = 0.00
LASER_ERROR = 0.4


def save_read_only(drawing, path='output.dxf'):
    """Unread-only a file, then sets it to write and saves, then read-onlies it again"""
    try:
        os.chmod(path, stat.S_IWRITE)
        drawing.save()
        os.chmod(path, stat.S_IREAD)

    except FileNotFoundError:
        drawing.save()

class BoxDrawing:
    def __init__(self, x, notches_x, y, notches_y, z, notches_z, mat_thickness):
        """
        Creates an instance of the BoxDrawing class
        the base of the box uses the x

        :param x: length of x axis
        :param notches_x: int
        :param y: int
        :param notches_y: int
        :param z: int
        :param notches_z: int
        :param mat_thickness: aterial thickness
        """
        self.base = BoxBase()






'''
Super Spiffy Diagram
       .-------.
      /|      /|
     / |     / |  
    .--|----.  |
{z} |  .----|--.
    | /     | /  {y}
     .-------.
        {x}
x = length
y = width
z = height
'''
LAYER_NAME = "LINES"
MINIMUM_NOTCH_SIZE = 6
DXF_VERSION = "AC1027"
DXF_ATTRIBS = {'color' : RED, 'line_weight': LINE_WEIGHT}
LAYER_ATTRIBUTE = {'layer' : LAYER_NAME}

def add_tuple(tup1, tup2):
    return tuple(sum(x) for x in zip(tup1, tup2))

class BoxBit(metaclass=abc.ABCMeta):
    """Base class for all shapes made out of a set of point"""
    def save(self, name='output.dxf', offset=(0,0)):
        """Creates a DXF made out of all the points this box comprised of"""
        dwg = ezdxf.new(DXF_VERSION)

        dwg.layers.new(name=LAYER_NAME, dxfattribs=DXF_ATTRIBS)
        self.insert(dwg, offset)
        # add a shiny cool polyline (also its much easier than having to loop :D)
        dwg.saveas(name)


    def insert(self, dwg, offset=(0, 0)):
        """
        Inserts the drawing into a ezdxf drawing main_drawing
        :param offset: offset on insertion

        :type drawing: ezdxf.drawing.Drawing
        """
        def add_offset(original):
            return add_tuple(original, offset)
        new_points = map(add_offset, self._all_points)

        msp = dwg.modelspace()  # type: layouts.Layout
        msp.add_lwpolyline(new_points, dxfattribs=LAYER_ATTRIBUTE)

    def insert_all_inline(gap, *args, insert_point=(0, 0)):
        """takes in all BaseShape objects and their descendants and chucks it all into 'maindrawing' in a line. Give it a gap distance"""

    def __init__(self, width, num_width_notches,
                 height, num_height_notches,
                 mat_thickness,
                 interactive=False,
                 error=LASER_ERROR
                 ):
        self._all_points = []
        self.width = width
        self.num_width_notches = num_width_notches
        self.height = height
        self.num_height_notches = num_height_notches
        self.mat_thickness = mat_thickness
        self.error = error

        self.width_notch_width = self.get_notch_size(width, num_width_notches, mat_thickness)
        if self.width_notch_width < MINIMUM_NOTCH_SIZE:
            # check if this is run in API mode
            if not interactive:
                raise InvalidDimensionsException("Width is too small")
            # if it is in user mode, ask for confirmation
            elif not ask_user(
                    "Continue? Width appears to be too small : {} < {}".format(self.width_notch_width, MINIMUM_NOTCH_SIZE)):
                raise InvalidDimensionsException("Width is too small")

        self.height_notch_width = self.get_notch_size(height, num_height_notches, mat_thickness)
        if self.height_notch_width < MINIMUM_NOTCH_SIZE:
            # check if this is run in API mode
            if not interactive:
                raise InvalidDimensionsException("Height is too small")
            # if it is in user mode, ask for confirmation
            elif not ask_user(
                    "Continue? Height appears to be too small : {} < {}".format(self.height_notch_width,
                                                                                MINIMUM_NOTCH_SIZE)):
                raise InvalidDimensionsException("Height is too small")



    @abc.abstractmethod
    def create_bottom(self, start_point):
        """Creates the bottom bit of the shape"""

    @abc.abstractmethod
    def create_right(self, start_point):
        """Creates the right bit of the shape"""

    @abc.abstractmethod
    def create_top(self, start_point):
        """Creates the top bit of the shape"""

    @abc.abstractmethod
    def create_left(self, start_point):
        """Creates the left bit of the shape"""

    @abc.abstractmethod
    def set_inital_point(self):
        """sets the inital point of object"""

    def create_shape(self):
        """Creates the shape, calling create bottom etc"""
        self.set_inital_point()

        self.create_bottom(self[-1])
        self.create_right(self[-1])
        self.create_top(self[-1])
        self.create_left(self[-1])

    def append(self, item):
        self._all_points.append(item)

    def __len__(self):
        return len(self._all_points)

    def __getitem__(self, item):
        if item < 0:
            item = len(self) + item
        return self._all_points[item]

    @staticmethod
    def get_notch_size(total_width, num_notches, mat_thickness):
        """Gets the size of each notch, if each depression is = to size of notch"""
        # total width = 2 * thickness + 2 * notch width * number notches

        # notch width = (total width - 2*thickness) / (4 * number notches )
        #  __----____----__
        # |                |
        return (total_width - 2 * mat_thickness) / (2 * num_notches)



YES_RESPONSE = 'y', 'yes', 'ye'
def ask_user(prompt):
    """Asks the user to continue. return True if yes, else false"""
    return input(str(prompt) + "(y/n)").lower() in YES_RESPONSE

class InvalidDimensionsException(Exception):
    pass

def alter_tuple(tup, x=0.0, y=0.0):
    return tup[0] + x, tup[1] + y

class BoxBase(BoxBit):
    """The Base shape"""
    def __init__(self, width, num_width_notches, height, num_height_notches,
                 mat_thickness,
                 interactive=False,
                 error=LASER_ERROR):
        super().__init__(width, num_width_notches, height, num_height_notches, mat_thickness, interactive, error)
        self.create_shape()


    def set_inital_point(self):
        self.append((self.mat_thickness, self.mat_thickness))

    def create_bottom(self, start_point):
        """Takes in 1 number (direction) that follows this rule

        """
        # |              |
        # --____----____--
        # 1/2 notch, then notch, then notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.width_notch_width
        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        for iteration in range(self.num_width_notches):
            # 1/2 a notch right
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, notch_width / 2 - self.error, 0)
            self.append(point)

            # thickness down
            point = alter_tuple(point, 0, -self.mat_thickness)
            self.append(point)

            # 1 notch right, middle bit is slightly larger to allow for better fits
            point = alter_tuple(point, notch_width + 2 * self.error, 0)
            self.append(point)

            # thickness up
            point = alter_tuple(point, 0, +self.mat_thickness)
            self.append(point)

            # 1/2 a notch right
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, notch_width / 2 - self.error, 0)
            self.append(point)

    def create_right(self, start_point):
        # |
        # -
        #  |
        #  |
        # -
        # |
        # 1/2 notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.height_notch_width

        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        for iteration in range(self.num_height_notches):
            # 1/2 a notch up
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, notch_width / 2 - self.error)
            self.append(point)

            # thickness right
            point = alter_tuple(point, self.mat_thickness, 0)
            self.append(point)

            # 1 notch up, middle bit is slightly larger to allow for better fits
            point = alter_tuple(point, 0, notch_width + 2 * self.error)
            self.append(point)

            # thickness left
            point = alter_tuple(point, -self.mat_thickness, 0)
            self.append(point)

            # 1/2 a notch up
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, notch_width / 2 - self.error)
            self.append(point)

    def create_top(self, start_point):
        #   ____      ____
        #__|    |____|    |__
        # 1/2 notch, then notch, then notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.height_notch_width

        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        for iteration in range(self.num_width_notches):
            # 1/2 a notch left
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, -(notch_width / 2 - self.error), 0)
            self.append(point)

            # thickness up
            point = alter_tuple(point, 0, self.mat_thickness)
            self.append(point)

            # 1 notch left, middle bit is slightly larger to allow for better fits
            point = alter_tuple(point, -(notch_width + 2 * self.error), 0)
            self.append(point)

            # thickness down
            point = alter_tuple(point, 0, -self.mat_thickness)
            self.append(point)

            # 1/2 a notch left
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, -(notch_width / 2 - self.error), 0)
            self.append(point)

    def create_left(self, start_point):
        # |
        # -
        #  |
        #  |
        # -
        # |
        # 1/2 notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.height_notch_width

        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        for iteration in range(self.num_height_notches):
            # 1/2 a notch down
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, -(notch_width / 2 - self.error))
            self.append(point)

            # thickness left
            point = alter_tuple(point, -self.mat_thickness, 0)
            self.append(point)

            # 1 notch down, middle bit is slightly larger to allow for better fits
            point = alter_tuple(point, 0, -(notch_width + 2 * self.error))
            self.append(point)

            # thickness right
            point = alter_tuple(point, self.mat_thickness, 0)
            self.append(point)

            # 1/2 a notch down
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, -(notch_width / 2 - self.error))
            self.append(point)


class BoxSide(BoxBit):
    """the two sides on left and right. The left bit is less big """

    def __init__(self, width, num_width_notches, height, num_height_notches,
                 mat_thickness,
                 interactive=False,
                 do_top=False,
                 error=LASER_ERROR):
        super().__init__(width, num_width_notches, height, num_height_notches, mat_thickness, interactive, error)
        self.do_top = do_top
        self.create_shape()

    def set_inital_point(self):
        self.append((0, 0))

    def create_bottom(self, start_point):
        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        #   .__.  .__.
        #_ _|  |__|  |_
        # mat thickness,
        # 1/2 notch, notch, notch, notch, 1/2 notch
        point = start_point
        notch_width = self.width_notch_width

        # add in the mat thickness
        point = alter_tuple(point, self.mat_thickness)
        self.append(point)

        for iteration in range(self.num_width_notches):
            # 1/2 a notch right
            # no error this time, or it will counteract the error given
            point = alter_tuple(point, notch_width / 2, 0)
            self.append(point)

            # thickness up
            point = alter_tuple(point, 0, self.mat_thickness)
            self.append(point)

            # 1 notch right
            point = alter_tuple(point, notch_width, 0)
            self.append(point)

            # thickness down
            point = alter_tuple(point, 0, -self.mat_thickness)
            self.append(point)

            # 1/2 a notch right
            point = alter_tuple(point, notch_width / 2 , 0)
            self.append(point)

    def create_right(self, start_point):
        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down

        point = start_point
        notch_width = self.height_notch_width

        point = alter_tuple(point, 0, self.mat_thickness)
        self.append(point)

        for iteration in range(self.num_height_notches):
            # mat 1/2 notch up
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, notch_width / 2 - self.error)
            self.append(point)

            # thickness right
            point = alter_tuple(point, self.mat_thickness, 0)
            self.append(point)

            # 1 notch up, middle bit is slightly larger to allow for better fits
            point = alter_tuple(point, 0, notch_width + 2 * self.error)
            self.append(point)

            # thickness left
            point = alter_tuple(point, -self.mat_thickness, 0)
            self.append(point)

            # 1/2 a notch up
            # give it 1 error on each side to allow pieces to fit together better
            point = alter_tuple(point, 0, notch_width / 2 - self.error)
            self.append(point)

        # go up a little bit more, to get to the full height
        point = alter_tuple(point, 0, self.mat_thickness)
        self.append(point)

    def create_top(self, start_point):
        #   ____      ____
        #__|    |____|    |__
        # 1/2 notch, then notch, then notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.height_notch_width
        if self.do_top:
            raise NotImplementedError()
            #    |    +   |   -
            #  x |  right | left
            #  y |   up   | down
            for iteration in range(self.num_width_notches):
                # 1/2 a notch left
                # give it 1 error on each side to allow pieces to fit together better
                point = alter_tuple(point, -(notch_width / 2 - self.error), 0)
                self.append(point)

                # thickness up
                point = alter_tuple(point, 0, self.mat_thickness)
                self.append(point)

                # 1 notch left, middle bit is slightly larger to allow for better fits
                point = alter_tuple(point, -(notch_width + 2 * self.error), 0)
                self.append(point)

                # thickness down
                point = alter_tuple(point, 0, -self.mat_thickness)
                self.append(point)

                # 1/2 a notch left
                # give it 1 error on each side to allow pieces to fit together better
                point = alter_tuple(point, -(notch_width / 2 - self.error), 0)
                self.append(point)
        else:
            point = alter_tuple(point, -(self.width - self.mat_thickness), 0)
            self.append(point)

    def create_left(self, start_point):
        # |
        # -
        #  |
        #  |
        # -
        # |
        # 1/2 notch, then notch, 1/2 notch
        #
        point = start_point
        notch_width = self.height_notch_width

        #    |    +   |   -
        #  x |  right | left
        #  y |   up   | down
        # go down 1 mat thickness
        point = alter_tuple(point, 0, -self.mat_thickness)
        self.append(point)

        for iteration in range(self.num_height_notches):
            # 1/2 a notch down
            point = alter_tuple(point, 0, -(notch_width / 2))
            self.append(point)

            # thickness right
            point = alter_tuple(point, self.mat_thickness, 0)
            self.append(point)

            # 1 notch down
            point = alter_tuple(point, 0, -notch_width)
            self.append(point)

            # thickness left
            point = alter_tuple(point, -self.mat_thickness, 0)
            self.append(point)

            # 1/2 a notch down
            point = alter_tuple(point, 0, -(notch_width / 2 ))
            self.append(point)
        point = alter_tuple(point, 0, -self.mat_thickness)
        self.append(point)





def create_point(start_point, x, y):
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
    BoxSide(50, 2, 30, 1, 3, True).save(offset=(0,0))
    print("Box Creator - unstable prototype version 0.0.1")
    print()
    name = input("What is your name? ")
    length = float(input("Box length: "))  # --- x
    breadth = float(input("Box breadth: "))  # / z
    height = float(input("Box height: "))  # |  y
    local_thickness = float(input("Material thickness: "))
    print("Margin of error is", LASER_ERROR)
    max_notch = int(min(length, breadth, height) / local_thickness / 2)
    default = int(input("Enter the number of pins. The suggested maximum is " + str(max_notch) + ": "))
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

    base = BoxBase(
        height_base=breadth, width_base=length, mat_thickness=local_thickness,
        notch_bottom_length=notch_len_len, notch_bottom_number=notch_len_num,
        notch_side_length=notch_bre_len, notch_side_number=notch_bre_num,
        margin_error=LASER_ERROR
    )
    side = Side(
        baseObject=base,
        height=height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error=LASER_ERROR,
        side='side'
    )

    bottom = Side(
        baseObject=base,
        height=height,
        length_notch_height=notch_hei_len,
        number_notch_height=notch_hei_num,
        margin_error=LASER_ERROR,
        side='bottom'
    )
    file_name = name + '_box.dxf'
    main_drawing = dxf.drawing(file_name)
    insert_point = [0, 0]
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



