#import box1 as Engine
from tkinter import *
import tkinter.messagebox as tkMessageBox
from decimal import *
class Application:
    """My application!"""

    """
    SOME FRAMES
    """

    def __init__(self):
        self.root = Tk()
        self.root.minsize(100, 100)

        Label(self.root, text = "Enter Box Measurements", font=("Helvetica", 14)).grid(row=0,columnspan=2, sticky=W)

        Label(self.root, text='Length:').grid(row = 1)
        Label(self.root, text='Width:').grid(row = 2)
        Label(self.root, text='Height:').grid(row = 3)

        self.boxLengthEntry = Entry(self.root)
        self.boxWidthEntry = Entry(self.root)
        self.boxHeightEntry = Entry(self.root)


        self.boxLengthEntry.grid(row = 1, column=1, sticky=E,padx=5,pady = 2)
        self.boxWidthEntry.grid(row = 2, column=1, sticky=E,padx=5,pady = 2)
        self.boxHeightEntry.grid(row = 3, column=1, sticky=E,padx=5,pady = 2)

        self.boxMeasureBigButton = Button(self.root, text='Calculate', command=  self.calculate_box_dimensions)
        self.boxMeasureBigButton.grid(row=4, columnspan = 2,pady = 20)






        self.root.mainloop()
    def calculate_box_dimensions(self):
        self.height = self.boxHeightEntry.get()
        self.width = self.boxWidthEntry.get()
        self.length = self.boxLengthEntry.get()

        if self.height and self.width and self.length:
            try:
                self.height = int(self.height)
            except ValueError:
                tkMessageBox.showwarning('Error Message', "Incorrect Height")

            try:
                self.height = int(self.length)
            except ValueError:
                tkMessageBox.showwarning('Error Message', "Incorrect Length")

            try:
                self.height = int(self.width)
            except ValueError:
                tkMessageBox.showwarning('Error Message', "Incorrect Width")




        else:
            errorcount = 0
            if not self.height:
                errorcount += 1
            if not self.width:
                errorcount += 1
            if not self.length:
                errorcount += 1


            tkMessageBox.showwarning(
                'Error Message',
               'Missing %d Dimension(s)' % errorcount
            )
















    def start_loop(self):
        self.root.startloop()

    def destroy_self(self):
        self.root.destroy()

    def user_interface(self):
        print()




def callback(event):
    print(event.x, event.y)
'''
frame = Frame(root,width = 200, height = 200)
frame.bind('<Button-1>', callback)
frame.bind('<Key>', callback)
frame.pack()

root.mainloop()
'''

main = Application()
