from tkinter import Frame


class Scrolledframe(Frame):

	def cget(self,item):
		return Frame.cget(self,item) if not hasattr(self,item) else getattr(self,item)
	__getitem__ = cget

	def configure(self,cnf=None,**kw):
		if kw:cnf=Tkinter._cnfmerge((cnf,kw))
		for key in cnf.keys():
			Frame.configure(self,cnf) if not hasattr(self,key) else setattr(self,key,cnf[key])
	def __setitem__(self,item,value):self.configure({item:value})

	def __call__(self):
		return self.client

	def __init__(self,master=None,stretch=True,cnf={},**kw):
		Frame.__init__(self,master,cnf,**kw)
		self.client=Frame(self,border=0)

		# width and height of Scrolledframe
		self.W=1.0
		self.H=1.0
		# top left corner coordinates of client frame
		self.client_x=0
		self.client_y=0
		# width and height of client frame
		self.client_w=1.0
		self.client_h=1.0
		# scrollcommands (default)
		self.xscrollcommand=lambda *args:None
		self.yscrollcommand=lambda *args:None
		# scrollincrements
		self.xscrollincrement=5
		self.yscrollincrement=5
		# stretches
		self.stretch=stretch
		self.stretch_x=stretch
		self.stretch_y=stretch

		self.bind("<Expose>",self.update_scrollregion)

	def xview(self,event,value,units='pages'):
		if event == "moveto":
			fraction=float(value)
			if fraction <= 0.0:self.client_x=0
			elif fraction >= float(self.client_w-self.W)/self.client_w:self.client_x=self.W-self.client_w
			else:self.client_x=int(-self.client_w*fraction)
		elif event == "scroll":
			amount=int(value)
			if self.client_x == 0 and amount < 0:return
			if self.client_x <= self.W-self.client_w and amount > 0:return
			self.client_x=self.client_x-(amount*self.xscrollincrement if units == "units" else amount*self.W*0.99)
		else:return

		self.update_scrollx()
		self.client.place_configure(x=self.client_x)

	def yview(self,event,value,units='pages'):
		if event == "moveto":
			fraction=float(value)
			if fraction <= 0.0:self.client_y=0
			elif fraction >= float(self.client_h-self.H)/self.client_h:self.client_y=self.H-self.client_h
			else:self.client_y=int(-self.client_h*fraction)
		elif event == "scroll":
			amount=int(value)
			if self.client_y == 0 and amount < 0:return
			if self.client_y <= self.H-self.client_h and amount > 0:return
			self.client_y=self.client_y-(amount*self.yscrollincrement if units == "units" else amount*self.H)
		else:return

		self.update_scrolly()
		self.client.place_configure(y=self.client_y)

	def update_scrollx(self,*args):
		low=0.0 if self.client_x >= 0 else -float(self.client_x)/self.client_w
		high=1.0 if self.client_x+self.client_w <= self.W else low+float(self.W)/self.client_w
		if low <= 0.0:
			self.client_x=0
		elif high >= 1.0:
			self.client_x=self.W-self.client_w
			low=-float(self.client_x)/self.client_w
		self.stretch_x=self.stretch if (self.client_w < self.W) else False
		self.xscrollcommand(low,high)

	def update_scrolly(self,*args):
		low=0.0 if self.client_y >= 0 else -float(self.client_y)/self.client_h
		high=1.0 if self.client_y+self.client_h <= self.H else low+float(self.H)/self.client_h
		if low <= 0.0:
			self.client_y=0
		elif high >= 1.0:
			self.client_y=self.H-self.client_h
			low=-float(self.client_y)/self.client_h
		self.stretch_y=self.stretch if (self.client_h < self.H) else False
		self.yscrollcommand(low,high)

	def update_scrollregion(self,*args):
		if len(self.client.children):
			self.client_w=self.client.winfo_reqwidth()
			self.client_h=self.client.winfo_reqheight()
			self.W=self.winfo_width()
			self.H=self.winfo_height()

			self.update_scrolly()
			self.update_scrollx()

			self.client.place_configure(
				anchor="nw",
				y=self.client_y,height=self.H if self.stretch_y else self.client_h,
				x=self.client_x,width=self.W if self.stretch_x else self.client_w
			)
		else:
			self.xscrollcommand(0.0,1.0)
			self.yscrollcommand(0.0,1.0)
			self.client.place_forget()

if __name__ == "__main__":
	from tkinter import Label,Tk,Scrollbar,Checkbutton,BooleanVar
	root=Tk(None)

	scrollframe=Scrolledframe(root,stretch=True)

	Label(scrollframe(),relief="solid",background="#d6feca",text="label 1 to see how does it work !").pack(padx=1,pady=2,anchor="w")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 2 to see how does it work !").pack(padx=1,pady=2,anchor="e")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 3 to see how does it work !").pack(padx=1,pady=2,anchor="center")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 4 to see how does it work !").pack(padx=1,pady=2,fill="both")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 5 to see how does it work !").pack(padx=1,pady=2,anchor="w",expand="yes")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 6 to see how does it work !").pack(padx=1,pady=2,anchor="e",expand="yes")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 7 to see how does it work !").pack(padx=1,pady=2,anchor="center",expand="yes")
	Label(scrollframe(),relief="solid",background="#d6feca",text="label 8 to see how does it work !").pack(padx=1,pady=2,fill="both",expand="yes")

	scrollx=Scrollbar(root,orient="horizontal",command=scrollframe.xview)
	scrollx.grid(row=1,column=0,sticky="nwse")
	scrolly=Scrollbar(root,orient="vertical",command=scrollframe.yview)
	scrolly.grid(row=0,column=1,sticky="nwse")
	scrollframe["xscrollcommand"]=scrollx.set
	scrollframe["yscrollcommand"]=scrolly.set

	scrollframe.grid(row=0,column=0,sticky="nwse")

	checkvar=BooleanVar(root,value=scrollframe["stretch"])
	def set_stretch():
		scrollframe["stretch"]=True if checkvar.get() else False
		scrollframe.update_scrollregion()

	stretch=Checkbutton(root,anchor="w",onvalue=True,offvalue=False,variable=checkvar,text="Stick contained frame to container",command=set_stretch)
	stretch.grid(sticky="nwse",padx=2,pady=2)

	root.title("Scrolled Frame")
	root.columnconfigure(0,weight=1)
	root.rowconfigure(0,weight=1)

	root.mainloop()
