from MyLib import *
from LootLib import *
import math


############
# UI Setup #
############

#The actual window and main frame
root=Tk()
root.option_add('*tearOff', FALSE)
root.grid_rowconfigure(0,weight=1)
overall=Frame(root)
overall.pack()
overall.grid_rowconfigure(0,weight=1)
overall.grid_rowconfigure(1,weight=1)

#For keeping track of popup dialogs, to make sure only one can be up at a time
activepopup=BooleanVar(root,value=0)


#Active Treasures
genTreasures=[]
manTreasures=[]
#Lists of TreasureFrame objects
genTFrames=[]
manTFrames=[]
#Total number of Treasures generated this session
tgenerated=[]

#PCs carrying stuff
pcCar=[]
#Storage containers
storages=[]

#The major panels of the UI
tGenFrame=LabelFrame(overall,text="Treasure Generation")
tManFrame=LabelFrame(overall,text="Treasure Management")
goodsDFrame=LabelFrame(overall,text="Object Details")
itemDFrame=LabelFrame(overall,text="Item Details")
settingsFrame=LabelFrame(overall,text="Program Settings")
logFrame=LabelFrame(tManFrame,text='Campaign Log')
tGenFrame.grid(row=0,column=0,sticky=N+S,rowspan=2)
tManFrame.grid(row=0,column=1,sticky=N+S,rowspan=2)
goodsDFrame.grid(row=0,column=2,sticky=E+W+N+S)
itemDFrame.grid(row=1,column=2,sticky=E+W+N+S)
settingsFrame.grid(row=0,column=3,sticky=N+S,rowspan=2)
tManFrame.grid_rowconfigure(0,weight=1)

#Track whether the above panels are currently displayed
managing=BooleanVar(root,value=True)
showlog=BooleanVar(value=False)
generating=BooleanVar(root,value=True)
settingsing=BooleanVar(root,value=True)



##############
# UI Methods #
##############

#Calculate magic item aura strength based on caster level
def auraCalc(itemcl,school=''):
    if itemcl > 20:
        strength='Overwhelming '
    elif itemcl > 11:
        strength='Strong '
    elif itemcl > 5:
        strength='Moderate '
    elif itemcl > 0:
        strength='Faint '
    else:
        strength='None'
    return strength+school

#Calculate Spellcraft DC to determine aura school(s)
def spellcraft(itemcl):
    if itemcl<1:
        return 'None'
    else:
        return str(15+itemcl)


#Show/Hide the togglable UI panels
def toggleGeneration():
    if generating.get():
        tGenFrame.grid_forget()
        generating.set(False)
    else:
        tGenFrame.grid(row=0,column=0,sticky=N+S)
        generating.set(True)

def toggleManagement():
    if managing.get():
        tManFrame.grid_forget()
        managing.set(False)
    else:
        tManFrame.grid(row=0,column=1,sticky=N+S,rowspan=2)
        managing.set(True)        

def toggleLog():
    if showlog.get():
        logFrame.grid_forget()
        showlog.set(False)
    else:
        logFrame.grid(row=0,column=2,sticky=N+S,rowspan=3)
        showlog.set(True)

def toggleSettings():
    if settingsing.get():
        settingsFrame.grid_forget()
        settingsing.set(False)
    else:
        settingsFrame.grid(row=0,column=3,rowspan=2,sticky=N+S)
        settingsing.set(True)


#Update any displayed Treasures in response to a settings change
def goodsSetUpd():
    for gtframe in genTFrames:
        if gtframe:
            gtframe.goodsframe.destroy()
            gtframe.buildGoods()
    for mtframe in manTFrames:
        if mtframe:
            mtframe.goodsframe.destroy()
            mtframe.buildGoods()

def itemSetUpd():
    for gtframe in genTFrames:
        if gtframe:
            gtframe.itemsframe.destroy()
            gtframe.buildItems()
    for mtframe in manTFrames:
        if mtframe:
            mtframe.itemsframe.destroy()
            mtframe.buildItems()

#
# Top Menu Bar
#
menubar=Menu(root)
filemenu=Menu(menubar,name='file')
root.config(menu=menubar)
menubar.add_cascade(menu=filemenu,label="File")
menubar.add_separator()
menubar.add_checkbutton(label="Show Treasure Generation",command=toggleGeneration)
menubar.add_checkbutton(label="Show Treasure Management",command=toggleManagement)
menubar.add_checkbutton(label='Show Campaign Log',command=toggleLog)
menubar.add("checkbutton",label="Show Settings",command=toggleSettings)

filemenu.add_command(label="New Campaign")
filemenu.add_command(label="Load Campaign")
filemenu.add_command(label="Save Campaign")
filemenu.add_separator()
filemenu.add_command(label="Load Settings from File")
filemenu.add_command(label="Save Settings to File")





#A box displayed to hold a single generated/loaded Treasure
class TreasureFrame:
    def __init__(self, master,treasurenum,listing,panel="Gen"):
        self.master=master
       #Back-end stuff
        self.tindex=len(listing.bools)
        self.treasurenum=treasurenum
        self.saved=False
        self.name="Treasure #"+str(treasurenum+1)
        self.listing=listing
        self.panel=panel
       #Outer frame
        self.listing.addBox(text=self.name)
       #Coins
        self.buildCoins()
       #Goods
        self.buildGoods()
       #Items
        self.buildItems()

       #Treasure Notes
        Label(self.listing.boxes[self.tindex],text='Notes:').grid(row=3,column=0,sticky=W)
        self.notesVar=StringVar()
        self.notes=Text(self.listing.boxes[self.tindex],width=60,height=5)
        self.notes.grid(row=4,column=0,columnspan=4)
        
       #Bookkeeping
        #Renames the treasure
        self.renameButton=Button(self.listing.boxes[self.tindex],text="Rename Treasure", command=self.renameDiag)
        self.renameButton.grid(row=5,column=0)
        #Saves the treasure
        self.saveButton=Button(self.listing.boxes[self.tindex],text="Save Treasure",command=self.saveTreasure)
        self.saveButton.grid(row=5,column=1)
        self.saveLabel=Label(self.listing.boxes[self.tindex],text="Not saved")
        self.saveLabel.grid(row=6,column=1)
        #Deletes the treasure and removes it from display
        self.deleteButton=Button(self.listing.boxes[self.tindex],text="Remove Treasure",command=self.removeTreasure)
        self.deleteButton.grid(row=5,column=3)

        #Stuff specific to Generation or Management panels
        if panel=='Gen':
            self.rerollButton=Button(self.listing.boxes[self.tindex],text="Reroll Treasure",command=self.rerollTreasure)
            self.rerollButton.grid(row=5,column=2)

    #Handles the "Coins" part of the Treasure display
    def buildCoins(self):
        self.coinframe=Frame(self.listing.boxes[self.tindex])
        self.coinframe.grid(row=0,column=0,columnspan=4,sticky=W)
        self.coinslabel=Label(self.coinframe,text="Coins:")
        self.coinslabel.grid(row=0,column=0,sticky=E)
        self.cplabel=Label(self.coinframe,text="CP: ")
        self.cplabel.grid(row=1,column=0,sticky=E)
        self.splabel=Label(self.coinframe,text="SP: ")
        self.splabel.grid(row=1,column=2)
        self.gplabel=Label(self.coinframe,text="GP: ")
        self.gplabel.grid(row=1,column=4)
        self.pplabel=Label(self.coinframe,text="PP: ")
        self.pplabel.grid(row=1,column=6)
        self.cp=Entry(self.coinframe,width=5)
        self.sp=Entry(self.coinframe,width=5)
        self.gp=Entry(self.coinframe,width=5)
        self.pp=Entry(self.coinframe,width=5)
        self.cp.grid(row=1,column=1)
        self.sp.grid(row=1,column=3)
        self.gp.grid(row=1,column=5)
        self.pp.grid(row=1,column=7)
        if self.panel=='Gen':
            self.coinsrerollbutton=Button(self.coinframe,text="Reroll",command=self.rerollCoins)
            self.coinsrerollbutton.grid(row=0,column=1,sticky=W)
        elif self.panel=='Man':
            self.coinsellbutton=Button(self.coinframe,text="Send Coins to Sale",command=self.sellCoins)
            self.coinsellbutton.grid(row=0,column=1,sticky=W)

    #Handles the "Goods" part of the Treasure display
    def buildGoods(self):
        self.goodsframe=Frame(self.listing.boxes[self.tindex])
        self.goodsframe.grid(row=1,column=0,sticky=W)
        self.goodslabel=Label(self.goodsframe,text="Goods:")
        self.goodslabel.grid(row=0,column=0,sticky=W)
        self.goodslines=[]
        Label(self.goodsframe,text='Description').grid(row=1,column=0,sticky=W)
        if self.panel=='Gen':
            self.goodsrerollbutton=Button(self.goodsframe,text="Reroll",command=self.rerollGoods)
            self.goodsrerollbutton.grid(row=0,column=1,sticky=W)
            for gengoodcol in range(len(gengoodslabels)):
                if gengoodsdisp[gengoodcol].get():
                    Label(self.goodsframe,text=gengoodslabels[gengoodcol]).grid(row=1,column=1+gengoodcol)
        elif self.panel=='Man':
            for mangoodcol in range(len(mangoodslabels)):
                if mangoodsdisp[mangoodcol].get():
                    Label(self.goodsframe,text=mangoodslabels[mangoodcol]).grid(row=1,column=1+mangoodcol)
            
    #Handles the "Items" part of the Treasure display
    def buildItems(self):
        self.itemsframe=Frame(self.listing.boxes[self.tindex])
        self.itemsframe.grid(row=2,column=0,sticky=W,columnspan=4)
        self.itemslabel=Label(self.itemsframe,text="Items:")
        self.itemslabel.grid(row=0,column=0,sticky=W)
        self.itemlines=[]
        Label(self.itemsframe,text='Description').grid(row=1,column=0,sticky=W)
        if self.panel=='Gen':
            self.itemsrerollbutton=Button(self.itemsframe,text="Reroll",command=self.rerollItems)
            self.itemsrerollbutton.grid(row=0,column=1,sticky=W)
            for genitemcol in range(len(genitemslabels)):
                if genitemsdisp[genitemcol].get():
                    Label(self.itemsframe,text=genitemslabels[genitemcol]).grid(row=1,column=1+genitemcol)
        elif self.panel=='Man':
            for manitemcol in range(len(manitemslabels)):
                if manitemsdisp[manitemcol].get():
                    Label(self.itemsframe,text=manitemslabels[manitemcol]).grid(row=1,column=1+manitemcol)


    def setindex(self,newindex):
        self.tindex=newindex

    def getindex(self):
        return self.tindex

    def saveTreasure(self):
        stup=ConfirmPopup(root,title='Save',text='Do you want to save this treasure?')
        if stup.result:
            print ('Saving not available yet!')
            #self.saveLabel.config(text='Saved')


    #Handles the actual renaming and closes the renaming popup
    def rename(self,newname,diag=None):
        if newname=='':
            return
        self.name=newname
        self.listing.buttons[self.tindex].config(text=self.name)
        if diag!=None:
            activepopup.set(0)
            diag.destroy()
            
    #Popup dialog to rename the treasure
    def renameDiag(self):
        if activepopup.get()==1:
            return
        activepopup.set(1)
        top=Toplevel()
        top.title("Rename "+self.name)
        top.protocol("WM_DELETE_WINDOW",lambda:self.rename(self.name,diag=top))
        self.namebox=Entry(top,width=20)
        self.namebox.insert(0,self.name)
        self.namebox.grid(row=0,column=0,columnspan=2)
        self.renamebutton=Button(top,text="Rename",command=lambda:self.rename(self.namebox.get(),diag=top))
        self.cancelbutton=Button(top,text="Cancel",command=lambda:self.rename(self.name,diag=top))
        self.renamebutton.grid(row=1,column=0)
        self.cancelbutton.grid(row=1,column=1)
        

    #Triggers the reroll of a single treasure
    def rerollTreasure(self,diag=None):
        if self.saved:
            text='Are you sure you want to reroll this treasure?'
        else:
            text='This treasure has not been saved.\nAre you sure you want to reroll it?'
        rrup=ConfirmPopup(root,title='Confirm Reroll',text=text)
        if rrup.result:
            print ("Reroll "+self.name)


    #Removes this treasure from the list (and will also remove the Treasure object eventually)
    def removeTreasure(self):
        if self.saved:
            text='Are you sure you want to remove this treasure?'
        else:
            text='This treasure has not been saved.\nAre you sure you want to remove it?'
        rtup=ConfirmPopup(root,title='Remove Treasure?',text=text)
        if rtup.result:
            self.listing.removeBox(self.tindex)
            genTreasures.pop(self.tindex)
            genTFrames.pop(self.tindex)
            for frameleft in range(len(genTFrames)):
                genTFrames[frameleft].setindex(frameleft)

    def rerollCoins(self):
        if self.panel=='Gen':
            print ('Reroll Coins in '+self.name)

    def rerollGoods(self):
        if self.panel=='Gen':
            print ('Reroll Goods in '+self.name)

    def rerollItems(self):
        if self.panel=='Gen':
            print ('Reroll Items in '+self.name)

    def sellCoins(self):
        if self.panel=='Man':
            print ('Sell Coins in '+self.name)

    def moveGoods(self):
        if self.panel=='Man':
            print ('Move a Goods from '+self.name)

    def moveItem(self):
        if self.panel=='Man':
            print ('Move an Item from '+self.name)


#Method that will eventually load Treasures from files.            
def loadTreasure(panel):
    print('Load Treasure in panel: '+panel)

    
        
#############################
# Treasure Generation Panel #
#############################        
#Generates a treasure based on current settings
def generateTreasure(cr,coins,goods,items,):
    tnum=len(tgenerated)
    genTFrames.append(TreasureFrame(tGenFrame,tnum,genListing))
    genTreasures.append("Treasure "+str(tnum))
    tgenerated.append("Treasure "+str(tnum))
    tGenFrame.update()

#A frame to hold individual Treasure panels
genListing=Listing(tGenFrame,startrow=2)

#
# Treasure Generation Bar
#
treasureGen=Frame(tGenFrame)
treasureGen.grid(row=0,column=0)
Label(treasureGen,text="Challenge Rating:").grid(column=0)
tgCRvar=IntVar(treasureGen)
tgCRvar.set(1)
tgCR = OptionMenu(treasureGen, tgCRvar, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
tgCR.grid(column=1,row=0)
Label(treasureGen,text="Coins:").grid(column=2,row=0)
Label(treasureGen,text="Goods:").grid(column=4,row=0)
Label(treasureGen,text="Items:").grid(column=6,row=0)
tgCoinVar=StringVar(treasureGen)
tgCoinVar.set("Standard")
tgGoodsVar=StringVar(treasureGen)
tgGoodsVar.set("Standard")
tgItemsVar=StringVar(treasureGen)
tgItemsVar.set("Standard")
tgCoins = OptionMenu(treasureGen, tgCoinVar, "None","Standard","Double","Triple")
tgGoods = OptionMenu(treasureGen, tgGoodsVar, "None","Standard","Double","Triple")
tgItems = OptionMenu(treasureGen, tgItemsVar, "None","Standard","Double","Triple")
tgCoins.grid(column=3,row=0)
tgGoods.grid(column=5,row=0)
tgItems.grid(column=7,row=0)
tgGenerate=Button(treasureGen,text="Generate Loot!",command=lambda:generateTreasure(tgCRvar.get(),tgCoinVar.get(),tgGoodsVar.get(),tgItemsVar.get()))
tgGenerate.grid(column=0,row=1,columnspan=8)

#Will eventually allow loading of treasures
tLoadButton=Button(tGenFrame,text="Load Treasure from File",command=lambda:loadTreasure('Gen'))
tLoadButton.grid(row=3,column=0,sticky=S)




#############################
# Treasure Management Panel #
#############################

#A single PC and the stuff assigned to them via the program
class PCarry:
    def __init__(self,listing,name='Swirly'):
        self.listing=listing
        self.name=name
        self.pcindex=len(listing.bools)
        listing.addBox(text=name)
        
        self.frame=listing.boxes[self.pcindex]
        self.goodsframe=Frame(self.frame)
        self.goodsframe.grid(row=0,column=0,sticky=W,columnspan=2)
        self.itemsframe=Frame(self.frame)
        self.itemsframe.grid(row=1,column=0,sticky=W,columnspan=2)
        Label(self.goodsframe,text='Goods:').grid(row=0,column=0,sticky=W)
        Label(self.itemsframe,text='Items:').grid(row=0,column=0,sticky=W)
        self.renamebutton=Button(self.frame,text='Rename Character',command=self.renameDiag)
        self.renamebutton.grid(row=2,column=0)
        self.removebutton=Button(self.frame,text='Remove Character',command=self.remove)
        self.removebutton.grid(row=2,column=1)

    def getindex(self):
        return self.pcindex

    def setindex(self,newindex):
        self.pcindex=newindex

    def getname(self):
        return self.name

    #Handles the actual renaming and closes the renaming popup
    def rename(self,newname,diag=None):
        if newname=='':
            return
        self.name=newname
        self.listing.buttons[self.pcindex].config(text=self.name)
        if diag!=None:
            activepopup.set(0)
            diag.destroy()
            
    #Popup dialog to rename the PC
    def renameDiag(self):
        if activepopup.get()==1:
            return
        activepopup.set(1)
        top=Toplevel()
        top.title("Rename "+self.name)
        top.protocol("WM_DELETE_WINDOW",lambda:self.rename(self.name,diag=top))
        self.namebox=Entry(top,width=20)
        self.namebox.insert(0,self.name)
        self.namebox.grid(row=0,column=0,columnspan=2)
        self.renamebutton=Button(top,text="Rename",command=lambda:self.rename(self.namebox.get(),diag=top))
        self.cancelbutton=Button(top,text="Cancel",command=lambda:self.rename(self.name,diag=top))
        self.renamebutton.grid(row=1,column=0)
        self.cancelbutton.grid(row=1,column=1)

    def remove(self):
        if True:
            text='Are you sure you want to remove this character?'
        rcup=ConfirmPopup(root,title='Remove Character?',text=text)
        if rcup.result:
            self.listing.removeBox(self.pcindex)
            pcCar.pop(self.pcindex)
            for frameleft in range(len(pcCar)):
                pcCar[frameleft].setindex(frameleft)


#A storage container, vehicle, and/or beast of burden
class StorageCon:
    def __init__(self,listing,name='Hateful Mule'):
        self.listing=listing
        self.name=name
        self.scindex=len(listing.bools)
        listing.addBox(text=name)

        self.frame=listing.boxes[self.scindex]
        self.goodsframe=Frame(self.frame)
        self.goodsframe.grid(row=0,column=0,sticky=W,columnspan=2)
        self.itemsframe=Frame(self.frame)
        self.itemsframe.grid(row=1,column=0,sticky=W,columnspan=2)
        Label(self.goodsframe,text='Goods:').grid(row=0,column=0,sticky=W)
        Label(self.itemsframe,text='Items:').grid(row=0,column=0,sticky=W)
        Label(self.goodsframe,text='Weight').grid(row=0,column=1,sticky=W)
        Label(self.itemsframe,text='Weight').grid(row=0,column=1,sticky=W)
        self.totalweight=IntVar(value=0)
        Label(self.frame,text='Total Weight:').grid(row=2,column=0,sticky=W)
        Label(self.frame,textvariable=self.totalweight).grid(row=2,column=1,sticky=W)
        self.renamebutton=Button(self.frame,text='Rename',command=self.renameDiag)
        self.renamebutton.grid(row=3,column=0)
        self.removebutton=Button(self.frame,text='Remove',command=self.remove)
        self.removebutton.grid(row=3,column=1)

    def getindex(self):
        return self.scindex

    def setindex(self,newindex):
        self.scindex=newindex

    def getname(self):
        return self.name

    #Handles the actual renaming and closes the renaming popup
    def rename(self,newname,diag=None):
        if newname=='':
            return
        self.name=newname
        self.listing.buttons[self.scindex].config(text=self.name)
        if diag!=None:
            activepopup.set(0)
            diag.destroy()
            
    #Popup dialog to rename the container
    def renameDiag(self):
        if activepopup.get()==1:
            return
        activepopup.set(1)
        top=Toplevel()
        top.title("Rename "+self.name)
        top.protocol("WM_DELETE_WINDOW",lambda:self.rename(self.name,diag=top))
        self.namebox=Entry(top,width=20)
        self.namebox.insert(0,self.name)
        self.namebox.grid(row=0,column=0,columnspan=2)
        self.renamebutton=Button(top,text="Rename",command=lambda:self.rename(self.namebox.get(),diag=top))
        self.cancelbutton=Button(top,text="Cancel",command=lambda:self.rename(self.name,diag=top))
        self.renamebutton.grid(row=1,column=0)
        self.cancelbutton.grid(row=1,column=1)

    def remove(self):
        if True:
            text='Are you sure you want to remove this storage container?'
        scup=ConfirmPopup(root,title='Remove Storage?',text=text)
        if scup.result:
            self.listing.removeBox(self.scindex)
            storages.pop(self.scindex)
            #genTFrames.pop(self.pcindex)
            for frameleft in range(len(storages)):
                storages[frameleft].setindex(frameleft)


def sellOff():
    print('Sell everything!')


#
# Panel to list party Treasures
#
campName=StringVar(value='Untitled Campaign')
campNameBox=Entry(tManFrame,textvariable=campName)
campNameBox.grid(row=0,column=0,sticky=N+W)
campTreasures=Frame(tManFrame)
campTreasures.grid(row=1,column=0,sticky=N+E+S+W)
loadTreasureButton=Button(tManFrame,text='Load Treasure from File',command=lambda:loadTreasure('Man'))
loadTreasureButton.grid(row=2,column=0,sticky=S)
#
# Assigned Item Subpanel #
#
assignedPanel=LabelFrame(tManFrame,text='Assigned Treasure')
assignedPanel.grid(row=0,column=1,rowspan=3,sticky=N+S)
atList=Listing(assignedPanel)
atList.mainframe.grid(row=0,column=0,sticky=N+S)
#Carried Treasure (on PCs)
atList.addBox('Carried Treasure',0)
carryList=Listing(atList.boxes[0])
pcAdd=Button(atList.boxes[0],text="Add Character",command=lambda:pcCar.append(PCarry(carryList)))
pcAdd.grid(row=1,column=0,sticky=W+S)
#Stored Treasure (storage, containers, mules, etc.)
atList.addBox('Stored Treasure',1)
storeList=Listing(atList.boxes[1])
storeAdd=Button(atList.boxes[1],text="Add Storage",command=lambda:storages.append(StorageCon(storeList)))
storeAdd.grid(row=1,column=0,sticky=W+S)
#Sale Treasure
atList.addBox('Treasure to Sell',2)
Label(atList.boxes[2],text='Coins').grid(row=0,column=0,sticky=W,columnspan=3)
sellcoinAmts=[0,0,0,0]
coinsForSale=StringVar(value='PP: '+str(sellcoinAmts[0])+'  GP: '+str(sellcoinAmts[1])+'  SP: '+str(sellcoinAmts[2])+'  CP: '+str(sellcoinAmts[3]))
Label(atList.boxes[2],textvariable=coinsForSale).grid(row=1,column=0,sticky=W,columnspan=3)
Label(atList.boxes[2],text='Goods').grid(row=2,column=0,sticky=W)
Label(atList.boxes[2],text='Items').grid(row=4,column=0,sticky=W)
Label(atList.boxes[2],text='Value (gp)').grid(row=2,column=1,sticky=E)
sellGoodsFrame=Frame(atList.boxes[2])
sellItemsFrame=Frame(atList.boxes[2])
sellGoodsFrame.grid(row=3,column=0,sticky=E+W,columnspan=2)
sellItemsFrame.grid(row=5,column=0,sticky=E+W,columnspan=2)
totalsaleAmts=[0,0,0,0]
divsaleAmts=[0,0,0,0]
#Number of shares to divide proceeds into
shares=IntVar(value=1)
#What coin type are you selling / changing up to
topcoin=StringVar(value='GP')
#Go to a moneychanger to step up lower denominations?
changeup=BooleanVar(value=0)
#How much of the top denomination is available?
changerpool=IntVar(value=0)
#What percentage does the moneychanger charge?
changercut=IntVar(value=0)
selloffButton=Button(atList.boxes[2],text='Sell All',command=sellOff)
selloffButton.grid(row=6,column=0,sticky=W)
Label(atList.boxes[2],text='Shares:').grid(row=6,column=1)
Entry(atList.boxes[2],textvariable=shares,width=2).grid(row=6,column=2)

#
# Campaign Log
#
clogscroll=Scrollbar(logFrame)
clogscroll.pack(side=RIGHT,fill=Y)
clogbox=Text(logFrame,yscrollcommand=clogscroll.set,width=35)
clogbox.pack(side=LEFT,fill=BOTH)
clogscroll.config(command=clogbox.yview)




##################
# Details Panels #
##################

def updateObject():
    print('Update the Goods object being detailed')

def deleteObject():
    print('Delete the Goods object being detailed')

def updateItem():
    print('Update the Item being detailed')

def deleteItem():
    print('Delete the Item being detailed')

#Goods object details
odcols=7
odTreasure=StringVar(goodsDFrame,value="None")
odTSource=StringVar(goodsDFrame,value="")
odTLabel=Label(goodsDFrame,text="Treasure: "+odTreasure.get()+" ("+odTSource.get()+")")
odTLabel.grid(row=0,column=0,sticky=W,columnspan=odcols)
Label(goodsDFrame,text="Object Description:").grid(row=1,column=0,sticky=W,columnspan=odcols)
oDescEntry=Entry(goodsDFrame,width=60)
oDescEntry.grid(row=2,column=0,sticky=W,columnspan=odcols)
Label(goodsDFrame,text="Value:").grid(row=3,column=0,sticky=W)
oValEntry=Entry(goodsDFrame,width=7)
oValEntry.grid(row=3,column=1)
Label(goodsDFrame,text="gp").grid(row=3,column=2,sticky=W)
Label(goodsDFrame,text="Weight:").grid(row=3,column=3,sticky=W)
oWtEntry=Entry(goodsDFrame,width=7)
oWtEntry.grid(row=3,column=4)
Label(goodsDFrame,text="lb").grid(row=3,column=5,sticky=W)
Label(goodsDFrame,text="Notes:").grid(row=5,column=0,sticky=W,columnspan=odcols)
Label(goodsDFrame,text="Tier:").grid(row=1,column=odcols-2,sticky=E)
oTier=StringVar(goodsDFrame,value="A")
oTierLabel=Label(goodsDFrame,textvariable=oTier)
oTierLabel.grid(row=1,column=odcols-1,sticky=W)
odNotes=Text(goodsDFrame,width=45,height=5)
odNotes.grid(row=6,column=0,sticky=W,columnspan=odcols)
odUpdate=Button(goodsDFrame,text="Update Object",command=updateObject)
odUpdate.grid(row=7,column=0,columnspan=3,sticky=E+W)
odDelete=Button(goodsDFrame,text="Delete Object",command=deleteObject)
odDelete.grid(row=7,column=3,columnspan=3,sticky=E+W)

#Item details
idcols=9
idTreasure=StringVar(itemDFrame,value="None")
idTSource=StringVar(itemDFrame,value="")
idTLabel=Label(itemDFrame,text="Treasure: "+idTreasure.get()+" ("+idTSource.get()+")")
idTLabel.grid(row=0,column=0,sticky=W,columnspan=odcols)
Label(itemDFrame,text="Item Description:").grid(row=1,column=0,sticky=W,columnspan=idcols)
iDescEntry=Entry(itemDFrame,width=60)
iDescEntry.grid(row=2,column=0,sticky=W,columnspan=idcols)

Label(itemDFrame,text="Item Type:").grid(row=3,column=0,sticky=W)
iType=Entry(itemDFrame,width=15)
iType.grid(row=3,column=1,sticky=W,columnspan=2)
Label(itemDFrame,text="Value:").grid(row=3,column=3,sticky=W)
iValEntry=Entry(itemDFrame,width=5)
iValEntry.grid(row=3,column=4)
Label(itemDFrame,text="gp").grid(row=3,column=5,sticky=W)
Label(itemDFrame,text="Weight:").grid(row=3,column=6,sticky=W)
iWtEntry=Entry(itemDFrame,width=5)
iWtEntry.grid(row=3,column=7)
Label(itemDFrame,text="lb").grid(row=3,column=8,sticky=W)

Label(itemDFrame,text="Caster Level:").grid(row=5,column=0)
iCL=Entry(itemDFrame,width=2)
iCL.insert(0,'0')
iCL.grid(row=5,column=1)
Label(itemDFrame,text="Spellcraft DC:").grid(row=5,column=2,sticky=E)
scDCVar=StringVar(itemDFrame,value=spellcraft(int(iCL.get())))
scDC=Label(itemDFrame,textvariable=scDCVar)
scDC.grid(row=5,column=3)
iAura=StringVar(itemDFrame,value=auraCalc(int(iCL.get())))
Label(itemDFrame,text="Aura:").grid(row=5,column=4,sticky=E)
auraLabel=Label(itemDFrame,textvariable=iAura,anchor=W,justify=LEFT,wraplength=140)
auraLabel.grid(row=5,column=5,columnspan=3,rowspan=2,sticky=N+W)
Label(itemDFrame,text="Notes:").grid(row=6,column=0,sticky=W,columnspan=idcols)
Label(itemDFrame,text="Item level:").grid(row=1,column=idcols-3,sticky=E,columnspan=2)
iLvl=StringVar(itemDFrame,value="1/2")
iLvlLabel=Label(itemDFrame,textvariable=iLvl)
iLvlLabel.grid(row=1,column=idcols-1,sticky=W)
idNotes=Text(itemDFrame,width=45,height=5)
idNotes.grid(row=7,column=0,sticky=W,columnspan=idcols)
iUpdate=Button(itemDFrame,text="Update Item",command=updateItem)
iUpdate.grid(row=8,column=0,sticky=E+W,columnspan=3)
iDelete=Button(itemDFrame,text="Delete Item",command=deleteItem)
iDelete.grid(row=8,column=3,sticky=E+W,columnspan=4)




##################
# Settings Panel #
##################
settingListing=Listing(settingsFrame)


#Program settings
settingListing.addBox(text="Program Settings",row=0)
Label(settingListing.boxes[0],text="This space neglectfully left blank").pack()

#
#Generator settings
#
settingListing.addBox(text='Treasure Generation Settings',row=1)
Label(settingListing.boxes[1],text="Spellcraft / Auras").grid(row=0,column=0,columnspan=3,sticky=W)
scOpt=IntVar(value=1)
Radiobutton(settingListing.boxes[1],text="Caster Level",variable=scOpt,value=1).grid(row=1,column=0)
Radiobutton(settingListing.boxes[1],text="Spellcraft DC",variable=scOpt,value=2).grid(row=1,column=1)
Radiobutton(settingListing.boxes[1],text="Both",variable=scOpt,value=3).grid(row=1,column=2)
#Checks for which information to display in the generator panel, made modular to allow more entries to be easily added
#(just add them to the "labels" lists)
Label(settingListing.boxes[1],text="Goods Display").grid(row=3,column=0,columnspan=3,sticky=W)
gengoodslabels=["Tier","Value","Weight"]
gengoodsdisp=[]
gengoodstoggle=[]
for check in range(len(gengoodslabels)):
    gengoodsdisp.append(BooleanVar(value=1))
    gengoodstoggle.append(Checkbutton(settingListing.boxes[1],text=gengoodslabels[check],variable=gengoodsdisp[check],onvalue=1,offvalue=0,command=goodsSetUpd))
    gengoodstoggle[check].grid(row=4,column=check,sticky=W)
Label(settingListing.boxes[1],text="Items Display").grid(row=5,column=0,columnspan=3,sticky=W)
genitemslabels=['Level','Type','Book','Spellcraft','Aura','Value','Weight']
genitemsdisp=[]
genitemstoggle=[]


for check2 in range(len(genitemslabels)):
    genitemsdisp.append(BooleanVar(value=1))
    genitemstoggle.append(Checkbutton(settingListing.boxes[1],text=genitemslabels[check2],variable=genitemsdisp[check2],onvalue=1,offvalue=0,command=itemSetUpd))
    genitemstoggle[check2].grid(row=6,column=check2,sticky=W)



#Manager settings
settingListing.addBox(text="Treasure Management Settings",row=2)
Label(settingListing.boxes[2],text="Base / Sell Value").grid(row=0,column=0,columnspan=3,sticky=W)
valOpt=IntVar(value=1)
Radiobutton(settingListing.boxes[2],text="Base Value",variable=valOpt,value=1).grid(row=1,column=0)
Radiobutton(settingListing.boxes[2],text="Sell Value",variable=valOpt,value=2).grid(row=1,column=1)
Radiobutton(settingListing.boxes[2],text="Base (Sell)",variable=valOpt,value=3).grid(row=1,column=2)
#Checks for which information to display in the manager panel, made modular to allow more entries to be easily added
#(just add them to the "labels" lists
Label(settingListing.boxes[2],text="Goods Display").grid(row=3,column=0,columnspan=3,sticky=W)
mangoodslabels=["Value","Weight"]
mangoodsdisp=[]
mangoodstoggle=[]
for check3 in range(len(mangoodslabels)):
    mangoodsdisp.append(BooleanVar(value=1))
    mangoodstoggle.append(Checkbutton(settingListing.boxes[2],text=mangoodslabels[check3],variable=mangoodsdisp[check3],onvalue=1,offvalue=0,command=goodsSetUpd))
    mangoodstoggle[check3].grid(row=4,column=check3,sticky=W)
Label(settingListing.boxes[2],text="Items Display").grid(row=5,column=0,columnspan=3,sticky=W)
manitemslabels=['Value','Weight','Type','Book']
manitemsdisp=[]
manitemstoggle=[]
for check4 in range(len(manitemslabels)):
    manitemsdisp.append(BooleanVar(value=1))
    manitemstoggle.append(Checkbutton(settingListing.boxes[2],text=manitemslabels[check4],variable=manitemsdisp[check4],onvalue=1,offvalue=0,command=itemSetUpd))
    manitemstoggle[check4].grid(row=6,column=check4,sticky=W)
#Carry/Store/Sell settings
Label(settingListing.boxes[2],text="Treasure Sale Settings").grid(row=7,column=0,sticky=W,columnspan=2)
Label(settingListing.boxes[2],text='Sell For:').grid(row=8,column=0,sticky=W)
Radiobutton(settingListing.boxes[2],text='PP',variable=topcoin,value='PP').grid(row=8,column=1,sticky=W)
Radiobutton(settingListing.boxes[2],text='GP',variable=topcoin,value='GP').grid(row=8,column=2,sticky=W)
Checkbutton(settingListing.boxes[2],text='Trade up coins',variable=changeup).grid(row=8,column=3,sticky=W)
changeframe=Frame(settingListing.boxes[2])
changeframe.grid(row=9,column=0,sticky=W,columnspan=4)
Label(changeframe,text='Coins available:').grid(row=0,column=0,sticky=W)
Entry(changeframe,textvariable=changerpool,width=5).grid(row=0,column=1,sticky=W)
Label(changeframe,text='   ').grid(row=0,column=2,sticky=W)
Label(changeframe,text='Moneychanger fee:').grid(row=0,column=3,sticky=W)
Entry(changeframe,textvariable=changercut,width=2).grid(row=0,column=4,sticky=W)
Label(changeframe,text='%').grid(row=0,column=5,sticky=W)


#Book settings
settingListing.addBox(text='Book Settings',row=3)
Label(settingListing.boxes[3],text='Splatbooks to Include:').grid(row=0,column=0,sticky=W)

bookChecks=[]
splatbooks=len(bookAbvs)-2
bookcols=2
bookrows=math.ceil(splatbooks/bookcols)

def booksUpd():
    print ('Books updated')

def checkAllBooks():
    for bcheck in bookChecks:
        bcheck.select()
    booksUpd()

def checkNoBooks():
    for bcheck in bookChecks:
        bcheck.deselect()
    booksUpd()

allBooksButton=Button(settingListing.boxes[3],text="Include All",command=checkAllBooks)
allBooksButton.grid(row=0,column=1)
noBooksButton=Button(settingListing.boxes[3],text="Include None",command=checkNoBooks)
noBooksButton.grid(row=0,column=2)

splatframe=Frame(settingListing.boxes[3])
splatframe.grid(row=1,columnspan=3)
for brow in range(bookrows):
    for bcol in range(bookcols):
        bentry=brow*bookcols+bcol
        if bentry<splatbooks:
            bookChecks.append(Checkbutton(splatframe,text=bookNames[bentry+2]+' ('+bookAbvs[bentry+2]+')',command=booksUpd))
            bookChecks[bentry].grid(row=1+brow,column=bcol,sticky=W)
