import tkinter as tk
from tkinter import *

class Window:
    def __init__(self, name="UVsim", size="1280x720"):
        #main window def
        root = tk.Tk()
        root.title(name)
        root.configure(background="#6F7681")
        root.geometry(size)

        #Populating Left Side Bar
        loadFileButton = tk.Button(root, text="Load File", width=12, height=4)
        runProgramButton = tk.Button(root, text="Run Program", width=12, height=4)
        resetButton = tk.Button(root, text="Reset Memory", width=12, height=4)
        quitButton = tk.Button(root, text="Exit Program", width=12, height=4, command=root.destroy)
        titleLabel = tk.Label(root, text="UVSim", bg="#6F7681", bd=0, font=("Helvetica", 30))
        fancyLine = Canvas(root, width=3, height=900, bg="black", bd=0, highlightthickness=0)

        loadFileButton.grid(row=0, column=0, padx=20, pady=20)
        runProgramButton.grid(row=1, column=0, padx=20, pady=20)
        resetButton.grid(row=2, column=0, padx=20, pady=20)
        quitButton.grid(row=3, column=0, padx=20, pady=20)
        titleLabel.place(rely=1.0, relx=0, x=10, y=-5, anchor="sw")
        fancyLine.grid(row=0, column=2, rowspan=50, padx=10)

        #Populating Rest of Window
        systemLabel = tk.Label(root, text="System Messages", bg="#6F7681", bd=0, font=("Helvetica", 18))
        systemState = tk.Label(root, text="Lorem Ipsum\nLorem Ipsum", bg="white", bd=0, font=("Helvetica", 12), width=50, height=10, anchor="nw")
        systemVars = tk.Label(root, text="System Variables", bg="#6F7681", bd=0, font=("Helvetica", 18))
        varsState = tk.Label(root, text="Accumulator: +0000\nProgram Counter: 00", bg="white", bd=0, font=("Helvetica", 12), width=50, height=3, anchor="nw")
        programInstruct = tk.Label(root, text="Program Instructions", bg="#6F7681", bd=0, font=("Helvetica", 18))
        instructState = tk.Label(root, text="Lorem Ipsum\nLorem Ipsum", bg="white", bd=0, font=("Helvetica", 12), width=50, height=5, anchor="nw")
        userLabel = tk.Label(root, text="User Console", bg="#6F7681", bd=0, font=("Helvetica", 18))
        userConsole = tk.Label(root, text="Lorem Ipsum\nLorem Ipsum", bg="white", bd=0, font=("Helvetica", 12), width=50, height=8, anchor="nw")
        systemMemory = tk.Label(root, text="Memory", bg="#6F7681", bd=0, font=("Helvetica", 18))
        memoryState = tk.Label(root, text="Lorem Ipsum\nLorem Ipsum", bg="white", bd=0, font=("Helvetica", 12), width=50, height=35, anchor="nw")

        systemLabel.place(x=200, y=25)
        systemState.place(x=200, y=60)
        systemVars.place(x=200, y=260)
        varsState.place(x=200, y=295)
        programInstruct.place(x=200, y=370)
        instructState.place(x=200, y=405)
        userLabel.place(x=200, y=515)
        userConsole.place(x=200, y=547)
        systemMemory.place(x=725, y=25)
        memoryState.place(x=725, y=60)

        root.mainloop()

if __name__ == "__main__":
    screen = Window()