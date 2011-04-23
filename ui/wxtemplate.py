from scipy import *
from pylab import *


import wx




class BattleFrame(wx.Frame):
    def __init__(self, parent):
        bs = 50
        offx = bs * 10 + 25
        offy = 75

        wx.Frame.__init__(self, parent, title="Battleship", 
                          size=(offx+bs*10, offy+bs*10))

        self.button_human = []
        self.button_human_id = []
        self.button_computer = []
        self.button_computer_id = []

        font = wx.Font(24, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)

        for i in range(10):
            for j in range(10):
                temp_id = wx.NewId()
                self.button_human_id.append(temp_id)
                self.button_human.append(wx.Button(self, temp_id, "", 
                                                   size=(bs, bs), 
                                                   pos=(bs*i, bs*j)))
                self.Bind(wx.EVT_BUTTON, self.human_click,
                          self.button_human[i*10+j])
                self.button_human[10*i+j].SetFont(font)


        for i in range(10):
            for j in range(10):
                temp_id = wx.NewId()
                self.button_computer_id.append(temp_id)
                self.button_computer.append(wx.Button(self, temp_id, "", 
                                                   size=(bs, bs), 
                                                   pos=(offx + bs*i, bs*j)))
                self.Bind(wx.EVT_BUTTON, self.computer_click,
                          self.button_computer[i*10+j])
                self.button_computer[i*10+j].Disable()
                self.button_computer[10*i+j].SetFont(font)

       
        self.text_human = wx.StaticText(self, label="Human", 
                                        pos=(bs*2, bs*10+15), size=(100, -1), 
                                        style=wx.ALIGN_CENTER)
        self.text_computer = wx.StaticText(self, label="Computer", 
                                           pos=(bs*2+offx, bs*10+15), size=(100, -1), 
                                           style=wx.ALIGN_CENTER)

        self.text_human.SetFont(font)
        self.text_human.SetBackgroundColour("gray")

        self.text_computer.SetFont(font)
        self.text_computer.SetBackgroundColour("gray")
        self.Show(True)

    def human_click(self, event):
        index = self.button_human_id.index(event.GetId())
        
        self.text_human.SetLabel(str(index))
        self.button_human[index].Disable()
        self.button_human[index].SetBackgroundColour("red")

        self.button_computer[index].SetBackgroundColour("green")
        self.button_computer[index].SetLabel("X")
        self.Refresh()
        
    def computer_click(self, event):
        pass 

app = wx.App(False)
frame = BattleFrame(None)
app.MainLoop()
