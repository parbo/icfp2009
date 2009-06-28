import sys
import math
import os.path
import wx
import wx.lib.newevent

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
ID_ZOOM_IN_BTN = 106
ID_ZOOM_OUT_BTN = 107
ID_OUTFILE_SELECT_BTN = 108
ID_WRITE_BTN = 109
ID_SHOW_HISTORY_BOX = 110
ID_SHOW_ZOOM_BOX = 111
ID_SHOW_ORBIT_BOX = 112
ID_INFO_BTN = 113
ID_RUN_EVENT = 150
ID_TEST_BTN = 999

RunSimEvent, EVT_RUN_SIM = wx.lib.newevent.NewCommandEvent()

class Viewer(wx.Frame):
    def __init__(self, controller='', problem='', conf=1001, outfile='out.osf'):
        wx.Frame.__init__(self, None, -1, TITLE, size = (1000, 800), style = wx.DEFAULT_FRAME_STYLE)
        # Frame initializations.
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetMinSize((500, 300))
        # Zoom window
        self.zoomWindow = ZoomWindow(self, 5e4)
        self.zoomWindow.Move((1020, 10))
        # Child control initializations.
        self.controlInput = wx.TextCtrl(self, -1, controller)
        self.controlLabel = wx.StaticText(self, -1, 'Control file:')
        self.controlSelectBtn = wx.Button(self, ID_CONTROL_SELECT_BTN, 'Select')
        self.problemInput = wx.TextCtrl(self, -1, problem)
        self.problemLabel = wx.StaticText(self, -1, 'Problem file:')
        self.problemSelectBtn = wx.Button(self, ID_PROBLEM_SELECT_BTN, 'Select')
        self.outfileInput = wx.TextCtrl(self, -1, outfile)
        self.outfileLabel = wx.StaticText(self, -1, 'Output file:')
        self.outfileSelectBtn = wx.Button(self, ID_OUTFILE_SELECT_BTN, 'Select')
        self.configInput = wx.SpinCtrl(self, -1, str(conf), min=1000, max=9999, initial=conf)
        self.writeBtn = wx.Button(self, ID_WRITE_BTN, 'Write Result')
        self.writeBtn.Disable()
        self.loadBtn = wx.Button(self, ID_LOAD_BTN, 'Load')
        self.stepBtn = wx.Button(self, ID_STEP_BTN, 'Step')
        self.stepInput = wx.SpinCtrl(self, -1, '100', min=1, max=3000000, initial=100)
        self.runBtn = wx.Button(self, ID_RUN_BTN, 'Run')
        self.zoomInBtn = wx.Button(self, ID_ZOOM_IN_BTN, 'Zoom In')
        self.zoomOutBtn = wx.Button(self, ID_ZOOM_OUT_BTN, 'Zoom Out')
        self.infoBtn = wx.Button(self, ID_INFO_BTN, 'Info')
        self.showHistoryBox = wx.CheckBox(self, ID_SHOW_HISTORY_BOX, 'Show history')
        self.showOrbitBox = wx.CheckBox(self, ID_SHOW_ORBIT_BOX, 'Show orbits')
        self.showZoomBox = wx.CheckBox(self, ID_SHOW_ZOOM_BOX, 'Zoom window')
        self.canvas = Canvas(self)
        # Sizer layout.
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.problemFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.outFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.commandSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.controlFileSizer, 0, flag = wx.EXPAND)
        self.mainSizer.Add(self.problemFileSizer, 0, flag = wx.EXPAND)
        self.mainSizer.Add(self.outFileSizer, 0, flag = wx.EXPAND)
        self.mainSizer.Add(self.canvasSizer, 1, flag = wx.EXPAND)
        self.controlFileSizer.Add(self.controlLabel, 1, flag = wx.ALIGN_LEFT)
        self.controlFileSizer.Add(self.controlInput, 7, flag = wx.EXPAND)
        self.controlFileSizer.Add(self.controlSelectBtn, 0, flag = wx.ALIGN_RIGHT)
        self.problemFileSizer.Add(self.problemLabel, 1, flag = wx.ALIGN_LEFT)
        self.problemFileSizer.Add(self.problemInput, 7, flag = wx.EXPAND)
        self.problemFileSizer.Add(self.problemSelectBtn, 0, flag = wx.ALIGN_RIGHT)
        self.outFileSizer.Add(self.outfileLabel, 1, flag = wx.ALIGN_LEFT)
        self.outFileSizer.Add(self.outfileInput, 7, flag = wx.EXPAND)
        self.outFileSizer.Add(self.outfileSelectBtn, 0, flag = wx.ALIGN_RIGHT)
        self.canvasSizer.Add(self.commandSizer, 0, flag = wx.EXPAND)
        self.canvasSizer.Add(self.canvas, 1, flag = wx.EXPAND)
        self.commandSizer.Add(self.writeBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.loadBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.configInput, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.stepBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.stepInput, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.runBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.zoomInBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.zoomOutBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.infoBtn, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.showHistoryBox, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.showOrbitBox, 0, flag = wx.EXPAND)
        self.commandSizer.Add(self.showZoomBox, 0, flag = wx.EXPAND)
        self.SetSizer(self.mainSizer)
        # Status bar definitions.
        bar = self.CreateStatusBar(8)
        bar.SetStatusWidths([-2, -2, -2, -2, -2, -2, -2, -3])
        # Event initializations.
        self.Bind(wx.EVT_BUTTON, self.OnControlSelectBtn, id = ID_CONTROL_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnProblemSelectBtn, id = ID_PROBLEM_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnOutfileSelectBtn, id = ID_OUTFILE_SELECT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnWriteBtn, id = ID_WRITE_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnLoadBtn, id = ID_LOAD_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnStepBtn, id = ID_STEP_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnRunBtn, id = ID_RUN_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnZoomInBtn, id = ID_ZOOM_IN_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnZoomOutBtn, id = ID_ZOOM_OUT_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnInfoBtn, id = ID_INFO_BTN)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowHistoryBox, id = ID_SHOW_HISTORY_BOX)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowOrbitBox, id = ID_SHOW_ORBIT_BOX)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowZoomBox, id = ID_SHOW_ZOOM_BOX)
        self.Bind(EVT_RUN_SIM, self.OnRunEvent, id = ID_RUN_EVENT)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        # Simulation object.
        self.sim = None
        self.sim_running = False
        # Show window.
        self.Move((10, 10))
        self.Show()
    
    # Event handlers.
    def OnControlSelectBtn(self, event):
        #print 'OnControlSelectBtn'
        dlg = wx.FileDialog(self, 'Open controller file', wildcard = 'Controller (*.py)|*.py', style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.controlInput.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnProblemSelectBtn(self, event):
        #print 'OnProblemSelectBtn'
        dlg = wx.FileDialog(self, 'Open problem file', wildcard = 'Problem (*.obf)|*.obf', style = wx.OPEN | wx.FILE_MUST_EXIST | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.problemInput.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnOutfileSelectBtn(self, event):
        #print 'OnOutfileSelectBtn'
        dlg = wx.FileDialog(self, 'Select output file', wildcard = 'Output file (*.osf)|*.osf', style = wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.outfileInput.SetValue(dlg.GetPath())
        dlg.Destroy()
        
    def OnWriteBtn(self, event):
        #print 'OnWriteBtn'
        filename = self.outfileInput.GetValue()
        if filename != '':
            f = open(filename, 'wb')
            f.write(str(self.sim.submission))
            f.close()
        
    def OnLoadBtn(self, event):
        #print 'OnLoadBtn'
        self.writeBtn.Disable()
        controller_path = self.controlInput.GetValue()
        problem = self.problemInput.GetValue()
        ctrldirpath = os.path.dirname(controller_path)
        ctrlfilename = os.path.basename(controller_path)
        modulename, ext = os.path.splitext(ctrlfilename)
        sys.path.append(ctrldirpath)
        print 'Import module "%s" from %s' % (modulename, ctrldirpath)
        module = __import__(modulename)
        self.sim = module.Create(problem, int(self.configInput.GetValue()))
        sizex, sizey = self.sim.world_size
        self.canvas.SetWorldSize(sizex, sizey)
        self.UpdateStatusBar()
        
    def OnStepBtn(self, event):
        #print 'OnStepBtn'
        self.Run(int(self.stepInput.GetValue()))
        
    def OnRunBtn(self, event):
        #print 'OnRunBtn'
        if self.sim_running:
            self.sim_running = False
            self.runBtn.SetLabel('Run')
        else:
            self.sim_running = True
            self.runBtn.SetLabel('Stop')
            self.AddPendingEvent(RunSimEvent(id=ID_RUN_EVENT))
            
    def OnZoomInBtn(self, event):
        #print 'OnZoomInBtn'
        self.canvas.Zoom(2.0 / 3.0)
        
    def OnZoomOutBtn(self, event):
        #print 'OnZoomOutBtn'
        self.canvas.Zoom(1.5)
        
    def OnInfoBtn(self, event):
        #print 'OnInfoBtn'
        for ix, sat in enumerate(self.sim.state.satellites):
            print 'Satellite %d orbit' % (ix + 1)
            print 'x:          %.5e' % sat.orbit.x
            print 'y:          %.5e' % sat.orbit.y
            print 'Semi-major: %.5e' % sat.orbit.a
            print 'Semi-minor: %.5e' % sat.orbit.b
            print 'Angle:      %.5f' % sat.orbit.angle
            print 'c:          %.5e' % sat.orbit.c
            print 'e:          %.5f' % sat.orbit.e
        
    def OnShowHistoryBox(self, event):
        #print 'OnShowHistoryBox'
        self.canvas.Refresh()
        
    def OnShowOrbitBox(self, event):
        #print 'OnShowOrbitBox'
        self.canvas.Refresh()
        
    def OnShowZoomBox(self, event):
        #print 'OnShowZoomBox'
        if self.showZoomBox.GetValue():
            self.zoomWindow.Show()
        else:
            self.zoomWindow.Hide()
        
    def OnRunEvent(self, event):
        #print 'OnRunEvent'
        self.Run(int(self.stepInput.GetValue()))
        
    def OnClose(self, event):
        #print 'OnClose'
        self.zoomWindow.Destroy()
        self.Destroy()
        
    def Run(self, steps):
        states = self.sim.step(steps)
        dc = wx.ClientDC(self.canvas)
        if self.showHistoryBox.GetValue():
            for state in states:
                self.canvas.DrawState(dc, self, state)
            if self.sim_running:
                self.AddPendingEvent(RunSimEvent(id=ID_RUN_EVENT))
        else:
            self.canvas.Refresh()
        self.zoomWindow.Refresh()
        self.UpdateStatusBar()
        if self.sim.completed:
            self.writeBtn.Enable()
            self.runBtn.SetLabel('Run')
            self.sim_running = False
        
    def UpdateStatusBar(self):
        bar = self.GetStatusBar()
        try:
            sx = 'sx: %.3e' % self.sim.state.sx
            sy = 'sy: %.3e' % self.sim.state.sy
            r = 'r: %.3e' % math.sqrt(self.sim.state.sx ** 2 + self.sim.state.sy ** 2)
        except TypeError:
            sx = 'sx: -'
            sy = 'sy: -'
            r = 'r: -'
        try:
            vx = 'vx: %.3e' % self.sim.state.vx
            vy = 'vy: %.3e' % self.sim.state.vy
        except TypeError:
            vx = 'vx: -'
            vy = 'vy: -'
        try:
            fuel = 'fuel: %.3e (%5.1f%%)' % (self.sim.state.current_fuel, 100.0 * self.sim.state.current_fuel / self.sim.initial_fuel)
        except TypeError:
            fuel = 'fuel: -'
        bar.SetStatusText('t: %d' % self.sim.time, 0)
        bar.SetStatusText('s: %.1f' % self.sim.state.score, 1)
        bar.SetStatusText(r, 2)
        bar.SetStatusText(sx, 3)
        bar.SetStatusText(sy, 4)
        bar.SetStatusText(vx, 5)
        bar.SetStatusText(vy, 6)
        bar.SetStatusText(fuel, 7)
        
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
        #print 'Canvas.OnSize'
        size = self.GetClientSize()
        self.xp = size.x
        self.yp = size.y
        self.UpdateWorldSize()
        
    def OnPaint(self, event):
        #print 'Canvas.OnPaint'
        dc = wx.PaintDC(self)
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.WHITE_BRUSH)
        self.CircleW(dc, 0, 0, EARTH_RADIUS)
        parent = self.GetParent()
        if parent.sim is not None:
            target_orbit = parent.sim.get_target_orbit()
            if target_orbit is not None:
                dc.SetPen(wx.GREEN_PEN)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                self.CircleW(dc, 0, 0, target_orbit)
            if parent.showHistoryBox.GetValue():
                for state in parent.sim.history:
                    try:
                        self.DrawState(dc, parent, state)
                    except TypeError:
                        pass
            else:
                try:
                    self.DrawState(dc, parent, parent.sim.history[-1])
                except TypeError:
                    pass
                if parent.sim_running:
                    self.AddPendingEvent(RunSimEvent(id=ID_RUN_EVENT))
        
    def SetWorldSize(self, xw, yw):
        self.xwrq = xw
        self.ywrq = yw
        self.UpdateWorldSize()
        
    def Zoom(self, factor):
        self.SetWorldSize(factor * self.xwrq, factor * self.ywrq)
        
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
        
    def DrawState(self, dc, parent, state):
        showHistory = parent.showHistoryBox.GetValue()
        showOrbit = parent.showOrbitBox.GetValue()
        dc.SetPen(wx.RED_PEN)
        for sat in state.satellites:
            if showHistory:
                self.PointW(dc, sat.sx, sat.sy)
            else:
                if showOrbit and (sat.orbit is not None):
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)
                    points = sat.orbit.points()
                    dc.DrawPolygon([wx.Point(*self.PosP(*p)) for p in points])
                x, y = self.PosP(sat.sx, sat.sy)
                dc.SetBrush(wx.RED_BRUSH)
                dc.DrawCircle(x, y, 3)
        dc.SetPen(wx.BLACK_PEN)
        dc.SetBrush(wx.BLACK_BRUSH)
        if showHistory:
            self.PointW(dc, state.sx, state.sy)
        else:
            x, y = self.PosP(state.sx, state.sy)
            dc.DrawCircle(x, y, 3)
        
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
        
class ZoomWindow(wx.Frame):
    def __init__(self, parent, world_size):
        wx.Frame.__init__(self, parent, -1, 'Zoom:', size = (300, 300), style = wx.MINIMIZE_BOX | wx.CAPTION | wx.RESIZE_BORDER)
        # Frame initializations.
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetMinSize((200, 200))
        # Scale settings.
        self.xwrq = world_size
        self.ywrq = world_size
        self.scale = world_size / 200
        self.xp = 200
        self.yp = 200
        # Status bar.
        self.CreateStatusBar(2)
        # Distance to closest satellite.
        self.dist = 1e7
        # Event handlers.
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def OnSize(self, event):
        #print 'Zoom.OnSize'
        self.SetWorldSize(self.xwrq, self.ywrq)
        
    def OnPaint(self, event):
        #print 'Zoom.OnPaint'
        dc = wx.PaintDC(self)
        try:
            self.dist = 1e7
            state = self.GetParent().sim.state
            dc.SetPen(wx.RED_PEN)
            dc.SetBrush(wx.RED_BRUSH)
            for sat in state.satellites:
                dx = (sat.sx - state.sx) / self.scale
                dy = (sat.sy - state.sy) / self.scale
                x = self.xp / 2 + dx
                y = self.yp / 2 + dy
                v = math.sqrt(sat.vx ** 2 + sat.vy ** 2)
                dc.DrawCircle(x, y, 3)
                dc.DrawLine(x, y, x + 20 * sat.vx / v, y + 20 * sat.vy / v)
                self.dist = min(self.dist, math.sqrt((sat.sx - state.sx) ** 2 + (sat.sy - state.sy) ** 2))
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(wx.BLACK_BRUSH)
            x = self.xp / 2
            y = self.yp / 2
            v = math.sqrt(state.vx ** 2 + state.vy ** 2)
            dc.DrawCircle(x, y, 3)
            dc.DrawLine(x, y, x + 20 * state.vx / v, y + 20 * state.vy / v)
        except TypeError:
            pass
        except AttributeError:
            pass
        self.UpdateStatusBar()
        
    def SetWorldSize(self, xw, yw):
        size = self.GetClientSize()
        self.xp = size.x
        self.yp = size.y
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
        self.SetLabel('Zoom: %.0f m/pixel' % scale)
        self.UpdateStatusBar()
        
    def UpdateStatusBar(self):
        bar = self.GetStatusBar()
        bar.SetStatusText('wx: %dm' % self.xw, 0)
        d = ('d: %.0fm' % self.dist) if self.dist < 1e7 else 'd: -'
        bar.SetStatusText(d, 1)

if __name__ == '__main__':
    controller = ''
    problem = ''
    conf = 1001
    if len(sys.argv) > 1:
        controller = sys.argv[1]
    if len(sys.argv) > 2:
        problem = sys.argv[2]
    if len(sys.argv) > 3:
        conf = int(sys.argv[3])
    app = wx.App(False)
    viewer = Viewer(controller, problem, conf)
    app.MainLoop()
    