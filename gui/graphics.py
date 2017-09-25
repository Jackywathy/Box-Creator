from old import box1 as Engine
from tkinter import *

from old import box1 as Engine


class Application:
    """My application!"""

    """
    SOME FRAMES
    """

    def __init__(self):
        self.baseLeftNotchNumber = 0
        self.baseLeftNotchLength = 0
        self.baseTopNotchNumber = 0
        self.baseTopNotchLength = 0

        self.sideTopNotchNumber = 0
        self.sideTopNotchLength = 0
        self.sideLeftNotchNumber = 0
        self.sideLeftNotchLength = 0

        self.bottomLeftNotchNumber = 0
        self.bottomLeftNotchLength = 0
        self.bottomTopNotchNumber = 0
        self.bottomTopNotchLength = 0

        self.base = None
        self.recommendNotchTop = None
        self.recommendNotchSide = None
        self.root = Tk()


        self.recButton1 = StringVar()
        self.recButton2 = StringVar()
        self.recButton3 = StringVar()

        self.sideButton1 = StringVar()
        self.sideButton2 = StringVar()
        self.sideButton3 = StringVar()

        self.recButton1.set('0Notches|0Length')
        self.recButton2.set('0Notches|0Length')
        self.recButton3.set('0Notches|0Length')

        self.sideButton1.set('0Notches|0Length')
        self.sideButton2.set('0Notches|0Length')
        self.sideButton3.set('0Notches|0Length')



        self.root.minsize(100, 100)

        self.BoxMeasureFrame = Frame(self.root, pady = 20)
        self.BoxMeasureFrame.pack()
        
        Label(self.BoxMeasureFrame, text = "Box Measurements", font=("Helvetica", 20)).grid(row=0,columnspan=2, sticky=N)

        Label(self.BoxMeasureFrame, text='Length:').grid(row = 1,sticky=W)
        Label(self.BoxMeasureFrame, text='Width:').grid(row = 2,sticky=W)
        Label(self.BoxMeasureFrame, text='Height:').grid(row = 3,sticky=W)
        Label(self.BoxMeasureFrame, text='Material Thickness:').grid(row = 4,sticky=W)

        self.boxLengthEntry = Entry(self.BoxMeasureFrame)
        self.boxWidthEntry = Entry(self.BoxMeasureFrame)
        self.boxHeightEntry = Entry(self.BoxMeasureFrame)
        self.boxMatThicknessEntry = Entry(self.BoxMeasureFrame)

        self.boxLengthEntry.grid(row = 1, column=1, sticky=E,padx=5,pady = 2)
        self.boxWidthEntry.grid(row = 2, column=1, sticky=E,padx=5,pady = 2)
        self.boxHeightEntry.grid(row = 3, column=1, sticky=E,padx=5,pady = 2)
        self.boxMatThicknessEntry.grid(row = 4, column = 1, sticky = E, padx=5,pady=2)


        self.boxMeasureBigButton = Button(self.BoxMeasureFrame, text='Calculate', command= self.calculate_box_dimensions)
        self.boxMeasureBigButton.grid(row = 5, columnspan = 2)



        self.BoxNotchFrame = Frame(self.root, pady=20)
        self.BoxNotchFrame.pack()



        Label(self.BoxNotchFrame, text="Notch Measurements(TM)", font=("Helvetica", 15)).pack()#row=0,columnspan=3, sticky=N)

        self.BoxEzNotchFrame = Frame(self.BoxNotchFrame)

        self.BoxEzNotchFrame.pack()
        Label(self.BoxEzNotchFrame, text = 'Recommended Length Notches').grid(row=0, columnspan = 3)
        Button(self.BoxEzNotchFrame, textvariable = self.recButton1,command = self.notch_top_select_1).grid(row = 1)
        Button(self.BoxEzNotchFrame, textvariable = self.recButton2,command = self.notch_top_select_2).grid(row = 1,column = 1)
        Button(self.BoxEzNotchFrame, textvariable = self.recButton3,command = self.notch_top_select_3).grid(row = 1, column = 2)

        Label(self.BoxEzNotchFrame, text = 'Recommended Width Sizes').grid(row=2, columnspan = 3)
        Button(self.BoxEzNotchFrame, textvariable = self.sideButton1,command = self.notch_side_select_1).grid(row = 3)
        Button(self.BoxEzNotchFrame, textvariable = self.sideButton2,command = self.notch_side_select_2).grid(row = 3,column = 1)
        Button(self.BoxEzNotchFrame, textvariable = self.sideButton3,command = self.notch_side_select_3).grid(row = 3, column = 2)








        self.BoxAdvNotchFrame = Frame(self.root)
        #self.BoxAdvNotchFrame.pack()



        Label(self.BoxAdvNotchFrame, text="Number of Notches").grid(row=1,sticky=W)

        self.boxNumNotch = Entry(self.BoxAdvNotchFrame)
        self.boxLengthNotch = Entry(self.BoxAdvNotchFrame)
        self.boxNumNotch = Entry(self.BoxAdvNotchFrame)






        self.information = Frame(self.root)
        self.information.pack()

        self.topInfo = StringVar()
        self.widthInfo = StringVar()
        self.topInfo.set('0')
        self.widthInfo.set('0')

        Label(self.information, textvariable = self.topInfo).grid(column=0,row=0)
        Label(self.information, textvariable = self.widthInfo).grid(column=1,row=0)




        self.root.mainloop()

    def update_info(self):
        self.topInfo.set(str(self.baseTopNotchNumber) + '|' + str(self.baseTopNotchLength))
        self.widthInfo.set(str(self.baseLeftNotchNumber) + '|' + str(self.baseLeftNotchLength))

    def notch_top_select_1(self):
        self.baseTopNotchNumber = 1
        self.baseTopNotchLength = (self.recommendNotchTop[0])
        self.update_info()


    def notch_top_select_2(self):
        self.baseTopNotchNumber = 2
        self.baseTopNotchLength = (self.recommendNotchTop[1])
        self.update_info()


    def notch_top_select_3(self):
        self.baseTopNotchNumber = 3
        self.baseTopNotchLength = (self.recommendNotchTop[2])
        self.update_info()


    def notch_side_select_1(self):
        self.baseSideNotchNumber = 1
        self.baseSideNotchLength = (self.recommendNotchSide[0])
        self.update_info()

    def notch_side_select_2(self):
        self.baseSideNotchNumber = 2
        self.baseSideNotchLength = (self.recommendNotchSide[1])
        self.update_info()

    def notch_side_select_3(self):
        self.baseSideNotchNumber = 1
        self.baseSideNotchLength = (self.recommendNotchSide[2])
        self.update_info()


    def calculate_box_dimensions(self):
        self.height = self.boxHeightEntry.get()
        self.width = self.boxWidthEntry.get()
        self.length = self.boxLengthEntry.get()
        self.mat_thickness = self.boxMatThicknessEntry.get()
        errorcount = 0

        if self.height and self.width and self.length and self.mat_thickness:
            try:
                self.length = Decimal(self.length)
                try:
                    self.width = Decimal(self.width)
                    try:
                        self.height = Decimal(self.height)
                        try:
                            self.mat_thickness = Decimal(self.mat_thickness)

                            self.create_base(self.width,self.length,self.height,self.mat_thickness)
                            self.recButton1.set('1 Notch - ' + str(self.recommendNotchTop[0]) + 'Length')
                            self.recButton2.set('2 Notch - ' + str(self.recommendNotchTop[1]) + 'Length')
                            self.recButton3.set('3 Notch - ' + str(self.recommendNotchTop[2]) + 'Length')

                            self.sideButton1.set('1 Notch - '+ str(self.recommendNotchSide[0]) + 'Length')
                            self.sideButton2.set('2 Notch - '+ str(self.recommendNotchSide[1]) + 'Length')
                            self.sideButton3.set('3 Notch - '+ str(self.recommendNotchSide[2]) + 'Length')






                        except InvalidOperation:
                            tkMessageBox.showwarning('Error Message', "Invalid Material Thickness")

                    except InvalidOperation:
                        tkMessageBox.showwarning('Error Message', "Invalid Height")

                except InvalidOperation:
                    tkMessageBox.showwarning('Error Message', "Invalid Width")

            except InvalidOperation:
                tkMessageBox.showwarning('Error Message', "Invalid Length")




        else:
            if not self.height:
                errorcount += 1
            if not self.width:
                errorcount += 1
            if not self.length:
                errorcount += 1
            if not self.mat_thickness:
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

    def create_base(self,width,length,height,mat_thickness):
        self.base = Engine.Base(width,length,height,mat_thickness)
        self.recommendNotchTop = self.base.recommend_notch_top()
        self.recommendNotchSide = self.base.recommend_notch_side()








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
