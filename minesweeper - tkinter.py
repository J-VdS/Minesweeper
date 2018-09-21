import random, time
import numpy as np
from tkinter import *

class minesweeper(object):
    def __init__(self, lijnen = 8, kolommen = 8, bommen = 10):
        #window input
        self.lijnen = lijnen
        self.kolommen = kolommen
        self.bommen = bommen

        self.tk = None
        self.restart()        
        self.loop()
        

    def restart(self):
        if self.tk:
            self.canvas.delete("all")
            self.tk.destroy()
        
        #window setup
        self.windowgenerator()
        self.menu()

        #afbeeldingen
        self.flagimg = PhotoImage(file='vlagje.gif')
        self.flagfout = PhotoImage(file='vlagje_fout.gif')
        self.bomimg = PhotoImage(file='bom.gif')
        
        #init spelbord
        self.bommatrix, self.bomlijst = self.bomgenerator(self.bommen)
        self.nummers = self.numgenerator()
        self.status = self.empty(self.lijnen, self.kolommen)
        self.alive = True

        #timerfuncties
        self.started = False
        self.klokje = self.canvas.create_text(2, self.lijnen*15, anchor=NW, \
                        font=('Helvetica', 10), text='TIME: 000', fill='red')

        #vlaggen
        self.vlaggen = 0
        self.numbervlag = self.canvas.create_text(self.kolommen*15-40, \
                        self.lijnen*15, fill='blue', font=('Helvetica', 10), \
                        text='%s/%s' %(self.vlaggen,len(self.bomlijst)), \
                        anchor=NW)
                                                  
        
        self.canvas.bind_all('<Button-1>', self.opentile)
        self.canvas.bind_all('<Button-3>', self.plantflag)

            
    def windowgenerator(self):
        '''
        Deze functie genereert het schermpje.
        '''
        self.tk = Tk()
        self.tk.resizable(0, 0)
        self.tk.title('MINESWEEPER')
        self.tk.wm_attributes('-topmost', 1)
        self.canvas = Canvas(self.tk, width=15*self.kolommen, \
                             height=15*(self.lijnen+1), highlightthickness=0)
        self.canvas.pack()
        #raster genereren
        self.blokwb = {}
        for i in range(self.kolommen): 
            for j in range(self.lijnen): 
                self.blokwb[(j,i)] = self.canvas.create_rectangle(i*15, j*15, \
                                        (i+1)*15, (j+1)*15, fill='#d3dfec')
                self.tk.update()

    def bomgenerator(self, bommen):
        '''
        Deze functie genereert de bommen.
        '''
        bommat = self.empty(self.lijnen, self.kolommen)
        bomlijst = []

        while len(bomlijst) < bommen:
            a = random.randint(0, self.lijnen-1)
            b = random.randint(0, self.kolommen-1)
            if (a, b) not in bomlijst:
                bomlijst.append((a, b))
                bommat[a, b] = 1
        return bommat, sorted(bomlijst)

    def numgenerator(self):
        #genereert de getallen
        nummat = self.empty(self.lijnen+2, self.kolommen+2)
        for (i,j) in self.bomlijst:
            nummat[i:i+3, j:j+3] += 1
        return nummat[1:-1, 1:-1]

    # om een tegel te openen of een vlag te planten
    def mouseloc(self):
        if not self.started:
            self.started = True
            self.init_timer()

        x = (self.tk.winfo_pointerx() - self.tk.winfo_rootx())//15
        y = (self.tk.winfo_pointery() - self.tk.winfo_rooty())//15 
        return (x,y)

    def opentile(self, evt, loc=None):
        if loc is None:
            (kolom, lijn) = self.mouseloc()
        else:
            (kolom, lijn) = loc
        vakje = (lijn, kolom)
        if kolom > self.kolommen-1 or lijn > self.lijnen-1 or not self.alive:
            return
        if self.status[lijn, kolom] > 0:
            return
        elif vakje in self.bomlijst:
            #einde spel moet nog geschreven worden
            vlagfouten = np.where((self.status==2)*(self.bommatrix == 0))
            #game over
            for i in range(len(vlagfouten[0])):
                vakje = (vlagfouten[0][i], vlagfouten[1][i])
                self.canvas.create_image(vakje[1]*15, vakje[0]*15, anchor=NW, \
                                         image=self.flagfout)
            for i in self.bomlijst:
                if self.status[i[0], i[1]] > 0:
                    continue
                self.canvas.create_image(i[1]*15, i[0]*15, anchor=NW, \
                                         image=self.bomimg)

            self.alive = False
            
            
            
        elif self.nummers[lijn, kolom] == 0:
             self.canvas.itemconfig(self.blokwb[vakje], fill='')
             self.status[lijn,kolom] = 1
             #auto opener
             for i in range(lijn-1, lijn+2):
                 for j in range(kolom-1, kolom+2):
                     if i<0 or i>(self.lijnen-1) or j<0 or j>(self.kolommen-1) \
                        or self.status[i, j] == 1:
                         continue
                     self.tk.update()
                     self.opentile(0, loc=(j, i))
             
        else:
            color = {'2':'#007e00', '1':'#0000ff', '3':'#ff0000', '4':'#e113d0', \
                     '5':'#800000', '6':'#40e0d0', '7':'#000000', '8':'#000000'}
            num = str(self.nummers[lijn, kolom])
            self.canvas.itemconfig(self.blokwb[vakje], fill='', \
                                   outline='black')
            self.canvas.create_text(5+15*kolom, 15*lijn, anchor=NW, text=num, \
                                    font=('Helvetica', 10), fill=color[num])           
            self.status[lijn, kolom] = 1
            #controleert of je gewonnen hebt
            self.winscreen()
            



    def plantflag(self, evt):
        (kolom, lijn) = self.mouseloc()
        vakje = (lijn, kolom)
        if kolom > self.kolommen-1 or lijn > self.lijnen-1 or not self.alive:
            return
        if self.status[lijn, kolom] == 1:
            return
        elif self.status[lijn, kolom] == 0:
            self.canvas.delete(self.blokwb[vakje])
            del self.blokwb[vakje]
            vw = self.canvas.create_image(kolom*15, lijn*15, anchor=NW, \
                                          image=self.flagimg)
            self.blokwb[vakje] = vw
            self.status[lijn, kolom] = 2
            self.vlaggen += 1
            self.bomvlaginfo()
            #controle of gewonnen
            self.winscreen()
        else:
            self.canvas.delete(self.blokwb[vakje])
            del self.blokwb[vakje]
            vw = self.canvas.create_rectangle(kolom*15, lijn*15, (kolom+1)*15, \
                                              (lijn+1)*15, fill='#d3dfec')
            self.blokwb[vakje] = vw
            self.status[lijn, kolom] = 0
            self.vlaggen -= 1
            self.bomvlaginfo()
        

    def empty(self, a, b, dtype='int'):
        return np.zeros([a, b], dtype=dtype)

    def get_veldsize(self):
        return (self.lijnen, self.kolommen)

    def get_window(self):
        return self.tk
    
    def init_timer(self):
        self.begin = time.time()
        self.interval = self.begin
        
    def control_time(self):
        if time.time() - self.interval > 1:
            self.interval = time.time()
            self.canvas.itemconfig(self.klokje, text='TIME: %03d' %( \
                int(self.interval - self.begin)))

    def bomvlaginfo(self):
        self.canvas.itemconfig(self.numbervlag, text='%s/%s' %(self.vlaggen, \
                                                        len(self.bomlijst)))
    def winscreen(self):
        vlaggen = np.where(self.status == 2)
        if len(vlaggen[0]) != len(self.bomlijst):
            return
        elif len(np.where(self.status >0)[0]) != self.lijnen*self.kolommen:
            return
        bomlocs = [(vlaggen[0][i],vlaggen[1][i]) for i in range(len(self.bomlijst))]
        print(self.bomlijst, bomlocs)
        if self.bomlijst == bomlocs:
            self.alive = False
            self.canvas.delete('all')
            self.canvas.create_text(15*self.kolommen//2, 15*self.lijnen//2, \
anchor=CENTER, font=('Helvetica', 10), text='You won!', color='blue')
        self.alive = False
        

    def menu(self):
        menu = Menu(self.tk)
        self.tk.config(menu=menu)
        options = Menu(menu)
        
        options.add_command(label='change dimensions',
                            command=self.change)
        options.add_command(label='restart',
                            command=self.restart)

        menu.add_cascade(label='options', menu=options)

    def change(self):
        self.tk2 = Tk()
        self.tk2.geometry('75x120')
        self.tk2.resizable(1,1)
        self.tk2.title('dimensions')
        self.tk2.wm_attributes('-topmost',1)
        self.tk2.update()

        self.label1 = Label(self.tk2, text='rows:')
        self.label2 = Label(self.tk2, text='columns:')
        self.label3 = Label(self.tk2, text='bombs:')
        self.entry1 = Entry(self.tk2, width=5)
        self.entry2 = Entry(self.tk2, width=5)
        self.entry3 = Entry(self.tk2, width=5)

        
        self.button = Button(self.tk2, text='apply',
                        command=self.apply,
                        font=('Calibri', 10),
                        width=5)
        self.label1.place(x=0,y=5)
        self.label2.place(x=0, y=25)
        self.label3.place(x=0, y=45)
        self.entry1.place(x=60, y=5)
        self.entry2.place(x=60, y=25)
        self.entry3.place(x=60, y=45)
        self.button.place(x=50, y=70)

        while 1:
            try:
                self.tk.update()
                self.tk.update_idletasks()
                self.tk2.update()
                self.tk2.update_idletasks()
                time.sleep(0.1)
            except:
                print('failed')
                return
    def apply(self):
        rijen = self.entry1.get()
        kolommen = self.entry2.get()
        bommen = self.entry3.get()

        if rijen and kolommen and bommen:
            try:
                self.rijen = int(rijen)
                self.kolommen = int(kolommen)
                self.bommen = int(bommen)
                self.tk2.destroy()
                self.restart()
            except:
                self.rijen, self.kolommen, self.bommen = 8, 8, 10
                text = Label(self.tk2, text='Invalid values!')
                text.place(x=0, y=100)
        
                 
    

    def loop(self):
        while 1:
            if self.started and self.alive:
                self.control_time()
            try:
                self.tk.update_idletasks()
                self.tk.update()
                time.sleep(0.01)
            except:
                return
    
x = minesweeper()

