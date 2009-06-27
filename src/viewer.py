import sys
import os.path
import wx

# World constants.
EARTH_RADIUS = 6.357e6 # [m]

# Main window title
TITLE = 'Satellite simulation'

# Control IDs
ID_CONTROL_SELECT_BTN = 101
ID_PROBLEM_SELECT_BTN = 102
ID_LOAD_BTN = 103
ID_STEP_BTN = 104
ID_RUN_BTN = 105
ID_TEST_BTN = 999

class Viewer(wx.Frame):
    def __init__(self, controller='', problem=''):
        wx.Frame.__init__(self, None, -1, TITLE, size = (800, 600), style = wx.DEFAULT_FRAME_STYLE)
        # Frame initializations.
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetMinSize((500, 300))
        # Child control initializations.
        self.controlInput = wx.TextCtrl(self, -1, controller)
        self.controlLabel = wx.StaticText(self, -1, 'Control file:')
        self.controlSelectBtn = wx.Button(self, ID_CONTROL_SELECT_BTN, 'Select')
        self.problemInput = wx.TextCtrl(self, -1, problem)
        self.problemLabel = wx.StaticText(self, -1, 'Problem file:')
        self.problemSelectBtn = wx.Button(self, ID_PROBLEM_SELECT_BTN, 'Select')
        self.loadBtn = wx.Button(self, ID_LOAD_BTN, 'Load')
        self.stepBtn = wx.Button(self, ID_STEP_BTN, 'Step')
        self.stepInput = wx.SpinCtrl(self, -1, '1', min=1, max=3000000, initial=1)
        self.runBtn = wx.Button(self, ID_RUN_BTN, 'Run')
        self.canvas = Canvas(self)
        # Sizer layout.
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.problemFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.commandSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.controlFileSizer, 0, flag = wx.EXPAND)
        self.mainSizer.Add(self.problemFileSizer, 0, flag = wx.EXPAND)
        self.mainSizer.Add(self.canvasSizer, 1, flag = wx.EXPAND)
        self.controlFileSizer.Add(self.controlLabel, 1, flag = wx.ALIGN_LEFT)
        self.controlFileSizer.Add(self.controlInput, 7, flag = wx.EXPAND)
        self.controlFileSizer.Add(self.controlSelectBtn, 0, flag = wx.ALIGN_RIGHT)
        self.problemFileSizer.Add(self.problemLabel, 1, flag = wx.ALIGN_LEFT)
        self.problemFileSizer.Add(self.problemInput, 7, flag = wx.EXPAND)
        self.problemFileSizer.Add(self.problemSelectBtn, 0, flag = wx.ALIGN_RIGHT)
        self.canvasSizer.Add(self.commandSizer, 0, flag = wx.EXPAND)
        self.canvasSizer.Add(self.canvas, 1, flag = wx.EXPAND)
        self.commandSizer.Add(self.loadBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.stepBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.stepInput, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.runBtn, 0, flag = wx.EXPAND)
        self.SetSizer(self.mainSizer)
        # Status bar definitions.
        self.CreateStatusBar(6)
        # Event initializations.
        self.Bind(wx.EVT_BUTTON, self.OnControlSelectBtn, id = ID_CONTROL_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnProblemSelectBtn, id = ID_PROBLEM_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnLoadBtn, id = ID_LOAD_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnStepBtn, id = ID_STEP_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnRunBtn, id = ID_RUN_BTN)
        # Simulation object.
        self.sim = None
        # Show window.
        self.Show()
    
    # Event handlers.
    def OnControlSelectBtn(self, event):
        print 'OnControlSelectBtn'
        dlg = wx.FileDialog(self, 'Open controller file', wildcard = 'Controller (*.py)|*.py', style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.controlInput.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnProblemSelectBtn(self, event):
        print 'OnProblemSelectBtn'
        dlg = wx.FileDialog(self, 'Open problem file', wildcard = 'Problem (*.obf)|*.obf', style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.problemInput.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnLoadBtn(self, event):
        print 'OnLoadBtn'
        controller_path = self.controlInput.GetValue()
        problem = self.problemInput.GetValue()
        ctrldirpath = os.path.dirname(controller_path)
        ctrlfilename = os.path.basename(controller_path)
        modulename, ext = os.path.splitext(ctrlfilename)
        sys.path.append(ctrldirpath)
        print 'Import module "%s" from %s' % (modulename, ctrldirpath)
        module = __import__(modulename)
        self.sim = module.Create(problem, 1001)
        self.UpdateStatusBar()
        
    def OnStepBtn(self, event):
        print 'OnStepBtn'
        self.sim.step(int(self.stepInput.GetValue()))
        dc = wx.ClientDC(self.canvas)
        self.canvas.PointW(dc, self.sim.sx, self.sim.sy)
        self.UpdateStatusBar()
        
    def OnRunBtn(self, event):
        print 'OnRunBtn'
        while not self.sim.completed > 0:
            self.sim.step()
            dc = wx.ClientDC(self.canvas)
            self.canvas.PointW(dc, self.sim.sx, self.sim.sy)
            self.UpdateStatusBar()
        
    def UpdateStatusBar(self):
        bar = self.GetStatusBar()
        try:
            sx = 'sx: %.3e' % self.sim.sx
            sy = 'sy: %.3e' % self.sim.sy
        except TypeError:
            sx = 'sx: -'
            sy = 'sy: -'
        try:
            vx = 'vx: %.3e' % self.sim.vx
            vy = 'vy: %.3e' % self.sim.vy
        except TypeError:
            vx = 'vx: -'
            vy = 'vy: -'
        try:
            fuel = 'fuel: %5.1f%%' % (100.0 * self.sim.current_fuel / self.sim.initial_fuel)
        except TypeError:
            fuel = 'fuel: -'
        bar.SetStatusText('t: %d' % self.sim.time, 0)
        bar.SetStatusText(sx, 1)
        bar.SetStatusText(sy, 2)
        bar.SetStatusText(vx, 3)
        bar.SetStatusText(vy, 4)
        bar.SetStatusText(fuel, 5)
        
class Canvas(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        # Requested world size.
        self.xwrq = 4 * EARTH_RADIUS
        self.ywrq = 4 * EARTH_RADIUS
        # Actual world size.
        self.xw = 4 * EARTH_RADIUS
        self.yw = 4 * EARTH_RADIUS
        # Draw area size in pixels.
        self.xp = 100
        self.yp = 100
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnSize(self, event):
        print 'Canvas.OnSize'
        size = self.GetClientSize()
        self.xp = size.x
        self.yp = size.y
        self.UpdateWorldSize()
        
    def OnPaint(self, event):
        print 'Canvas.OnPaint'
        dc = wx.PaintDC(self)
        self.CircleW(dc, 0, 0, EARTH_RADIUS)
        
    def SetWorldSize(self, xw, yw):
        self.xwrq = xw
        self.ywrq = yw
        self.UpdateWorldSize()
        
    def UpdateWorldSize(self):
        if (self.xwrq / self.xp) < (self.ywrq / self.yp):
            scale = self.ywrq / self.yp # m / pixel
        else:
            scale = self.xwrq / self.xp # m / pixel
        # Size in world coordinates.
        self.xw = scale * self.xp
        self.yw = scale * self.yp
        self.scale = scale
        self.Refresh()
        print 'Set world size:', self.xw / EARTH_RADIUS, self.yw / EARTH_RADIUS, 'Scale = %.3e m/pxl' % scale
        
    # Draw circle in world coordinates.
    def CircleW(self, dc, xw, yw, rw):
        x, y = self.PosP(xw, yw)
        r = self.DistP(rw)
        dc.DrawCircle(x, y, r)
        
    # Draw point in world coordinates.
    def PointW(self, dc, xw, yw):
        x, y = self.PosP(xw, yw)
        dc.DrawPoint(x, y)
        
    # Convert position in world coordinates to pixels.
    def PosP(self, xw, yw):
        x = xw / self.scale + self.xp / 2
        y = yw / self.scale + self.yp / 2
        return (x, y)
        
    # Convert distance in world coordinates to pixels.
    def DistP(self, dw):
        return dw / self.scale

if __name__ == '__main__':
    controller = ''
    problem = ''
    if len(sys.argv) > 1:
        controller = sys.argv[1]
    if len(sys.argv) > 2:
        problem = sys.argv[2]
    app = wx.App(False)
    viewer = Viewer(controller, problem)
    viewer.Center()
    app.MainLoop()
    