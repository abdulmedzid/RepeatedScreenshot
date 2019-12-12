import os
import platform
import subprocess
import time, threading
import pyautogui
import tkinter as tk
from tkinter import filedialog

LABLEL_FONT = 'Arial 10 normal'

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

class LabelSpinner(tk.Frame):
    def __init__(self, parent, labelText, spinFrom, spinTo):
        tk.Frame.__init__(self, parent)
        
        # label
        self.label = tk.Label(
            self, 
            text=labelText, 
            font=LABLEL_FONT
        )

        self.label.grid(
            row = 0, column = 0, sticky=tk.W, padx=5, pady=5
        )

        # spinner
        self.spinner = tk.Spinbox(
            self,
            from_ = spinFrom,
            to = spinTo
        )

        self.spinner.config(
            justify=tk.RIGHT,
            font=LABLEL_FONT
        )

        self.spinner.grid(
            row = 0, column = 1, sticky=tk.W, padx=5, pady=5
        )

    def get(self):
        return self.spinner.get()

class TimeInput(tk.Frame):
    def __init__(self, parent, labelFrameText):
        tk.Frame.__init__(self, parent)
        self.labelFrame = tk.LabelFrame(self, text=labelFrameText)
        self.labelFrame.pack(padx=10, pady=10)
        self.minuteLabelSpinner = LabelSpinner(self.labelFrame, 'Minutes:', 0, 99)
        self.minuteLabelSpinner.pack(padx=10, pady=5)
        self.secondsLabelSpinner = LabelSpinner(self.labelFrame, 'Seconds:', 0, 59)
        self.secondsLabelSpinner.pack(padx=10, pady=5)

    def getTimeInSec(self):
        minuteInput = int(self.minuteLabelSpinner.get())
        secondsInput = int(self.secondsLabelSpinner.get())
        return int(minuteInput*60 + secondsInput)

class IntervalInput(TimeInput):
    def __init__(self, parent):
        TimeInput.__init__(self, parent, ' Screenshot frequency ')

class DurationInput(TimeInput):
    def __init__(self, parent):
        TimeInput.__init__(self, parent, ' Screenshoting duration ')

class SaveDirectoryInput(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.labelFrame = tk.LabelFrame(self, text=' Save directory ')
        self.labelFrame.pack(padx=10, pady=10)
    
        self.outputDirText = tk.Entry(
            self.labelFrame,
            bg='#dddddd',
            fg="#505050",
            font='Helvetica 10 normal',
            width=33
        )
        self.outputDirText.config(
            state=tk.DISABLED
        )
        self.outputDirText.grid(
            row=0,  column = 0, sticky=tk.W, padx=10, pady=10
        )

        tk.Button(
            self.labelFrame,
            text='Search dir',
            width = 10,
            command=self.selectOutputDir
        ).grid(
            row=1, column = 0, sticky=tk.E, padx = 5, pady = 5
        )

        self.saveDirPath = ''

    def selectOutputDir(self):
        self.saveDirPath = filedialog.askdirectory()
        self.outputDirText.config(state=tk.NORMAL)
        self.outputDirText.delete(0, tk.END)
        self.outputDirText.insert(tk.END, self.saveDirPath)
        self.outputDirText.config(state=tk.DISABLED)

    def getSaveDirPath(self):
        return self.saveDirPath

class ControlDialog(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        # Stop button
        self.stopButton = tk.Button(
            self, 
            text="Stop", 
            width=10,
            #command=endScreenshoting
        )
        self.stopButton.config(state=tk.DISABLED)
        self.stopButton.grid(
            row=0, column=0, padx=5, pady=10
        )

        # Start button
        self.startButton = tk.Button(
            self, 
            text="Start", 
            width=10,
            command=self.startScreenshoting
        )
        self.startButton.grid(
            row=0, column=1, padx=5, pady=10
        )

        self.startButtonActive = True

    def startScreenshoting(self):
        self.intervalInSec = self.parent.intervalInput.getTimeInSec()
        self.durationInSec = self.parent.durationInput.getTimeInSec()
        self.saveDirPath = self.parent.saveDirInput.getSaveDirPath()
        if self.isInputValid(self.intervalInSec, self.durationInSec, self.saveDirPath):
            self.numberOfScreenshotsTaken = 0
            self.numberOfNeededScreenshots = int(self.durationInSec / self.intervalInSec)
            self.shouldStopScreenshoting = False
            threading.Timer(self.intervalInSec, self.takeScreenshot).start()

    def takeScreenshot(self):
        if self.shouldTakeScreenshot():
            self.numberOfScreenshotsTaken += 1
            screenshot = pyautogui.screenshot()
            screenshot.save(self.saveDirPath + '/{}.jpg'.format(self.numberOfScreenshotsTaken))
            threading.Timer(self.intervalInSec, self.takeScreenshot).start()
        else:
            self.shouldStopScreenshoting = True
            self.switchButtonActivity()
            open_file(self.saveDirPath)

    def shouldTakeScreenshot(self):
        return self.numberOfScreenshotsTaken <= self.numberOfNeededScreenshots and not self.shouldStopScreenshoting

    def switchButtonActivity(self):
        if (self.startButtonActive):
            self.startButton.config(state=tk.DISABLED)
            self.stopButton.config(state=tk.NORMAL)
            self.startButtonActive = False
        else:
            self.startButton.config(state=tk.NORMAL)
            self.stopButton.config(state=tk.DISABLED)
            self.startButtonActive = True


    def isInputValid(self, intervalInSec, durationInSec, saveDirPath):
        return intervalInSec != 0 and durationInSec != 0 and os.path.exists(saveDirPath)

class MainApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.intervalInput = IntervalInput(self)
        self.intervalInput.pack()
        self.durationInput = DurationInput(self)
        self.durationInput.pack()
        self.saveDirInput = SaveDirectoryInput(self)
        self.saveDirInput.pack()
        self.controlDialog = ControlDialog(self)
        self.controlDialog.pack()

if __name__ == '__main__':
    root = tk.Tk()
    MainApp(root).pack(side='top', fill='both', expand=True)
    root.mainloop()