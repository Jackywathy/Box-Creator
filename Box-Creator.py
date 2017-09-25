__author__ = 'Jack,Shovel&Archie. D. Comben project manger'
"""V.0.2, stable basic version. Most features implemented."""

# switched to ezdxf as it allows AC1027 dxf files
import ezdxf
import ezdxf.modern.layouts as layouts

import os
import abc

from os.path import join, expanduser

import stat


RED = 1

LINE_WEIGHT = 0.00
LASER_ERROR = 0.4


def save_read_only(drawing, path='output.dxf'):
    """Unread-only a file, then sets it to write and saves, then read-onlies it again"""
    try:
        os.chmod(path, stat.S_IWRITE)
        drawing.saveas(path)
        os.chmod(path, stat.S_IREAD)
    except FileNotFoundError:
        # file doesnt exist
        drawing.saveas(path)



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
DXF_VERSION = "AC1027"
DXF_ATTRIBS = {'color' : RED, 'line_weight': LINE_WEIGHT}
LAYER_ATTRIBUTE = {'layer' : LAYER_NAME}

def add_tuple(tup1, tup2):
    return tuple(sum(x) for x in zip(tup1, tup2))

def create_dxf_drawing():
    dwg = ezdxf.new(DXF_VERSION)
    dwg.layers.new(name=LAYER_NAME, dxfattribs=DXF_ATTRIBS)
    return dwg

class BoxBit(metaclass=abc.ABCMeta):


    """Base class for all shapes made out of a set of point"""
    def save(self, name='output.dxf', offset=(0,0)):
        """Creates a DXF made out of all the points this box comprised of"""
        dwg = create_dxf_drawing()

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

    def __init__(self, width, num_width_notches,
                 height, num_height_notches,
                 mat_thickness,
                 interactive=False,
                 error=LASER_ERROR
                 ):
        """Converted in length and width, length=x, width=y"""
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

    def __str__(self):
        return str(self._all_points)



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
        notch_width = self.width_notch_width

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
        notch_width = self.width_notch_width
        if self.do_top:
            #    |    +   |   -
            #  x |  right | left
            #  y |   up   | down
            for iteration in range(self.num_width_notches):
                # 1/2 a notch left
                point = alter_tuple(point, -(notch_width / 2), 0)
                self.append(point)

                # thickness down
                point = alter_tuple(point, 0, -self.mat_thickness)
                self.append(point)

                # 1 notch left
                point = alter_tuple(point, -notch_width, 0)
                self.append(point)

                # thickness up
                point = alter_tuple(point, 0, self.mat_thickness)
                self.append(point)

                # 1/2 a notch left
                point = alter_tuple(point, -(notch_width / 2) , 0)
                self.append(point)

            # thickness left
            point = alter_tuple(point, -self.mat_thickness, 0)
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




MINIMUM_NOTCH_SIZE = 10
SPACING = 5

def get_max_notch(total_width, not_width, mat_thickness):
    """gets the maximum size of a notch"""
    # total width = 2 * thickness + 2 * notch width * number notches
    # num notches = (total_width - 2*thickness) / (2 * notch_width)
    #  __----____----__
    # |                |
    return (total_width - 2 * mat_thickness) / (2 * not_width)

def unittest():
    BoxBase(50, 2, 100, 2, 3).save('base.dxf')
    BoxSide(50, 2, 30, 1, 3, True).save('side1.dxf')
    BoxSide(100, 2, 30, 1, 3, True).save('side2.dxf')


def test2():
    length = 100
    notches = 3
    width = 200
    height = 240
    local_thickness = 3
    closed_box = True
    base = BoxBase(
        length, notches, width, notches, local_thickness,
    )

    # side on the top/bottom of base
    side1 = BoxSide(
        length, notches, height, notches, local_thickness, do_top=closed_box
    )

    # side on the left/right
    side2 = BoxSide(
        width, notches, height, notches, local_thickness, do_top=closed_box
    )
    print(side1)
    dwg = create_dxf_drawing()
    bases = 2 if  closed_box else 1
    insert_point = [0,0]

    #for _ in range(bases):
    #    base.insert(dwg, insert_point)
    #    insert_point[0] += base.width + SPACING

    for _ in range(1):
        side1.insert(dwg, insert_point)
        insert_point[0] += side1.width + SPACING

    #for _ in range(2):
    #    side2.insert(dwg, insert_point)
    #    insert_point[0] += side2.width + SPACING

    save_read_only(dwg, 'test2.dxf')



DB = True
version = '0.2'
#test2()
def main():
    print("Box Creator - unstable prototype version {}".format(version))
    print()
    name = input("What is your name? ")
    length = float(input("Box length: "))  # --- x
    width = float(input("Box breadth: "))  # / z
    height = float(input("Box height: "))  # |  y
    local_thickness = float(input("Material thickness: "))
    print("Margin of error is", LASER_ERROR)
    max_notch = int(get_max_notch(min(length, width, height), MINIMUM_NOTCH_SIZE, 3))
    notches = int(input("Enter the number of pins. The suggested maximum is " + str(max_notch) + ": "))
    closed_box = ask_user("Closed box?")
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

    base = BoxBase(
        length, notches, width, notches, local_thickness,
    )

    # side on the top/bottom of base
    side1 = BoxSide(
        length, notches, height, notches, local_thickness, do_top=closed_box
    )

    # side on the left/right
    side2 = BoxSide(
        width, notches, height, notches, local_thickness, do_top=closed_box
    )

    file_name = name + '_box.dxf'
    dwg = create_dxf_drawing()

    insert_point = [0, 0]

    if closed_box:
        bases = 2
    else:
        bases = 1

    for _ in range(bases):
        base.insert(dwg, insert_point)
        insert_point[0] += base.width + SPACING

    for _ in range(2):
        side1.insert(dwg, insert_point)
        insert_point[0] += side1.width + SPACING

    for _ in range(2):
        side2.insert(dwg, insert_point)
        insert_point[0] += side2.width + SPACING

    try:
        save_read_only(dwg, file_name)
    except PermissionError as e:
        print("Unable to save due to file open in another program.")
        input("Press enter to retry")
        save_read_only(dwg, file_name)


    print()
    print("Drawing has been saved.")


if __name__ == '__main__':
    main()




