from tkinter import *
from scrolled import Scrolledframe

#A stack of collapsible LabelFrames
#Just call addBox to add an entry, then attach the contents to listing.boxes at that index.
class Listing:
    def __init__(self,parent,startrow=0,column=0,master=None):
        self.parent=parent
        self.column=column
        self.startrow=startrow
        self.mainframe=Scrolledframe(parent,stretch=True)
        self.mainframe.grid(row=startrow,column=column,sticky=N+S+E+W)


        self.scrolly=Scrollbar(parent,orient='vertical',command=self.mainframe.yview)
        self.scrolly.grid(row=startrow,column=column+1,sticky=N+E+S+W)
        self.mainframe['yscrollcommand']=self.scrolly.set
        
        self.master=master
        #Booleans for "is it currently expanded?"
        self.bools=[]
        #Buttons to replace the label and collapse/expand the frame
        self.buttons=[]
        #The actual LabelFrames
        self.boxes=[]

    def togglePanel(self,tpindex):
        if self.bools[tpindex]:
            self.boxes[tpindex].grid_forget()
            self.buttons[tpindex].grid(row=tpindex,column=0,sticky=W)
            self.bools[tpindex]=False
        else:
            self.buttons[tpindex].grid_forget()
            self.boxes[tpindex].grid(row=tpindex,column=0,sticky=E+W)
            self.boxes[tpindex].config(labelwidget=self.buttons[tpindex])
            self.bools[tpindex]=True
        self.mainframe.update_scrollregion()

    def addBox(self,text='Collapsible Box',row=None,startopen=True):
        abindex=len(self.bools)
        self.bools.append(startopen)
        self.buttons.append(Button(self.mainframe,text=text,command=lambda:self.togglePanel(abindex)))
        self.boxes.append(LabelFrame(self.mainframe,labelwidget=self.buttons[abindex],text=text))
        if startopen:
            self.boxes[abindex].grid(row=abindex,column=0,sticky=E+W)
        else:
            self.buttons[abindex].grid(row=abindex,column=0,sticky=W)

    def removeBox(self,rindex,row=None):
        if row==None:
            row=rindex
        self.buttons[rindex].destroy()
        self.boxes[rindex].destroy()
        self.bools[rindex]=False
        self.buttons[rindex]=False
        self.boxes[rindex]=False



#Generalized dialog box with protections against shenanigans like multiple dialogs or program action
class PopupBox(Toplevel):
    def __init__(self,parent,title=None,wait=True):
        Toplevel.__init__(self,parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent=parent
        self.popframe=Frame(self)
        self.popframe.pack()
        self.components=[]
        self.protocol("WM_DELETE_WINDOW",self.nope)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+150,
                                  parent.winfo_rooty()+150))
        self.grab_set()
        self.result=None
        if wait:
            parent.wait_window(self)
        
    def nope(self,popback=None):
        if popback:
            self.result = popback
        for part in self.components:
            part.destroy()
        self.popframe.destroy()
        self.destroy()

#More specialized confirmation popup
class ConfirmPopup(PopupBox):
    def __init__(self,parent,title='Confirmation Required',text='Confirm whatever you\'re doing?'):
        PopupBox.__init__(self,parent,title,False)
        self.result=0
        self.components.append(Label(self.popframe,text=text))
        self.components.append(Button(self.popframe,text="Yes",command=lambda:self.nope(conback=1)))
        self.components.append(Button(self.popframe,text="No",command=self.nope))
        self.components[0].grid(row=0,column=0,columnspan=2)
        self.components[1].grid(row=1,column=0)
        self.components[2].grid(row=1,column=1)
        parent.wait_window(self)

    def nope(self,conback=0):
        if conback==1:
            self.result=1
        PopupBox.nope(self)
