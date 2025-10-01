import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import main as core

class Window:
    def __init__(self, name="UVsim", size="1280x720"):
        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title(name)
        self.root.configure(background="#6F7681")
        self.root.geometry(size)

        # --- Left Side Buttons ---
        tk.Button(self.root, text="Load File", width=12, height=4, command=self.load_file).grid(row=0, column=0, padx=20, pady=20)
        tk.Button(self.root, text="Run Program", width=12, height=4, command=self.run_program).grid(row=1, column=0, padx=20, pady=20)
        tk.Button(self.root, text="Reset Program", width=12, height=4, command=self.reset_memory).grid(row=2, column=0, padx=20, pady=20)
        tk.Button(self.root, text="Exit Program", width=12, height=4, command=self.root.destroy).grid(row=3, column=0, padx=20, pady=20)

        tk.Label(self.root, text="UVSim", bg="#6F7681", font=("Helvetica", 30)).place(rely=1.0, relx=0, x=10, y=-5, anchor="sw")
        tk.Canvas(self.root, width=3, height=900, bg="#6F7681", bd=0, highlightthickness=0).grid(row=0, column=2, rowspan=50, padx=10)

        # --- System Messages (frame with label + scrolling log) ---
        log_frame = tk.Frame(self.root, bg="#6F7681", bd=0, highlightthickness=0)
        log_frame.place(x=200, y=25)

        log_label = tk.Label(log_frame, text="System Messages", bg="#6F7681", font=("Helvetica", 18), anchor="w")
        log_label.pack(fill="x", padx=0, pady=(0,4))

        # Text widget for the log (disabled for direct editing)
        self.system_output = tk.Text(log_frame, height=10, width=50, state="disabled", wrap="word", font=("Helvetica", 12), bd=1, relief="solid")
        self.system_output.pack(fill="both", expand=True)
        self.systemState = self.system_output

        # --- System Aspects ---
        tk.Label(self.root, text="System Variables", bg="#6F7681", font=("Helvetica", 18)).place(x=200, y=260)
        self.varsState = tk.Label(self.root, text="Accumulator: +0000\nProgram Counter: 00", bg="white", font=("Helvetica", 12), width=50, height=3, anchor="nw")
        self.varsState.place(x=200, y=295)

        tk.Label(self.root, text="Program Instructions", bg="#6F7681", font=("Helvetica", 18)).place(x=200, y=370)
        self.instructState = tk.Label(self.root, text="", bg="white", font=("Helvetica", 12), width=50, height=5, anchor="nw")
        self.instructState.place(x=200, y=405)

        tk.Label(self.root, text="User Console", bg="#6F7681", font=("Helvetica", 18)).place(x=200, y=515)
        self.userInput = tk.Entry(self.root, width=45, font=("Courier New", 12), state="disabled")
        self.userInput.place(x=200, y=547)
        self.userInput.bind("<Return>", self._submit_input)
        self.userQueue = []  # store submitted inputs

        tk.Label(self.root, text="Memory", bg="#6F7681", font=("Helvetica", 18)).place(x=725, y=25)

        # --- Memory Treeview ---
        frame = tk.Frame(self.root, bg="white")
        frame.place(x=725, y=60, width=500, height=560)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, width=18)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.memoryState = ttk.Treeview(frame, columns=("Location", "Item"), show="headings", yscrollcommand=scrollbar.set, selectmode="none", height=35)
        self.memoryState.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.memoryState.yview)

        style = ttk.Style()
        style.configure("Custom.Treeview", background="white", foreground="black", rowheight=18, font=("Courier New", 12))
        style.map("Custom.Treeview", background=[("selected", "white")], foreground=[("selected", "black")])
        self.memoryState.configure(style="Custom.Treeview")
        self.memoryState.heading("Location", text="Location")
        self.memoryState.heading("Item", text="Memory Item")
        self.memoryState.column("Location", width=80, anchor="center", stretch=False)
        self.memoryState.column("Item", width=400, anchor="w", stretch=False)

        # set up empty table with memory locations 00-99
        for i in range(100):
            tag = "even" if i % 2 == 0 else "odd"
            self.memoryState.insert("", "end", values=(f"{i:02d}", "+0000"), tags=(tag,))
        self.memoryState.tag_configure("even", background="white")
        self.memoryState.tag_configure("odd", background="#f0f0f0")

        # set up system variables
        self.initial_memory = {}
        self.run_thread = None

        # keep GUI/Window running unless closed
        self.root.mainloop()

    # --- File / Program execution ---

    def load_file(self):
        """Utilizes filedialog to open a file and read it into memory"""
        filepath = filedialog.askopenfilename(title="Select a Program File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return None
        core._programMemory.clear()
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                core._programMemory[f"{i:02d}"] = line.strip()
        for i in range(len(core._programMemory), 100):
            core._programMemory[f"{i:02d}"] = "+0000"
        self.build_memory_table(core._programMemory, save_initial=True)

    def run_program(self):
        """Utilizes threading module and calls _run_program_thread"""
        if self.run_thread and self.run_thread.is_alive():
            messagebox.showinfo("Run Program", "Program is already running.")
            return
        self.run_thread = threading.Thread(target=self._run_program_thread, daemon=True)
        self.run_thread.start()

    # --- System messages / memory ---

    def write_system(self, message):
        """Writes to the system_ouput, clears output in clear_system"""
        self.system_output.config(state="normal")
        self.system_output.insert("end", message + "\n")
        self.system_output.see("end")  # auto-scroll to bottom
        self.system_output.config(state="disabled")
    
    def clear_system(self):
        """Clear all messages from the system messages"""
        self.system_output.config(state="normal")
        self.system_output.delete("1.0", "end")  # delete everything
        self.system_output.config(state="disabled")
    
    def build_memory_table(self, memory_dict, save_initial=False):
        """Full rebuild of memory table (used on file load or reset), parameters are memory_dict and save_initial (preset to False)"""
        if save_initial:
            self.initial_memory = memory_dict.copy()

        for row in self.memoryState.get_children():
            self.memoryState.delete(row)
        for i in range(100):
            loc = f"{i:02d}"
            item = memory_dict.get(loc, "+0000")
            tag = "even" if i % 2 == 0 else "odd"
            self.memoryState.insert("", "end", values=(loc, item), tags=(tag,))

    def update_memory(self, memory_dict, save_initial=False):
        """Updates the changed values in memory. Take parameters memory_dict and save_initial (preset to False)"""
        if save_initial:
            self.initial_memory = memory_dict.copy()

        # only update rows that changed
        for i in range(100):
            loc = f"{i:02d}"
            new_val = memory_dict.get(loc, "+0000")

            # get current value in Treeview
            item_id = self.memoryState.get_children()[i]
            old_val = self.memoryState.item(item_id, "values")[1]

            if new_val != old_val:  # update only if different
                self.memoryState.item(item_id, values=(loc, new_val))
    
    def update_vars(self):
        """Update the Accumulator / Program Counter label from core variables."""

        acc = getattr(core, "_accumulator", "+0000")
        pc = getattr(core, "_programCounter", 0)
        self.varsState.config(text=f"Accumulator: {acc}\nProgram Counter: {pc:02d}")

    def reset_memory(self):
        """Resets all aspects of memory and system. Interacts with core (main module) and changes protected variables. Calls update_vars and clear_system"""
        if not self.initial_memory:
            messagebox.showinfo("Reset Memory", "No saved memory snapshot to restore.")
            return

        # Restore memory
        core._programMemory = self.initial_memory.copy()
        self.build_memory_table(core._programMemory, save_initial=False)

        # Reset Accumulator and Program Counter
        core._accumulator = "+0000"
        core._programCounter = 0
        self.update_vars()
        self.clear_system()

    # --- Input handling ---
    
    def _submit_input(self, event):
        value = self.userInput.get()
        if value:
            self.userQueue.append(value)

    def get_input(self):
        """Enable the input box, wait for integer input, then disable again."""
        self.userInput.config(state="normal")   # allow typing
        self.userInput.focus_set()

        value = None
        while value is None:
            while not self.userQueue:  # wait for Enter
                time.sleep(0.01)

            candidate = self.userQueue.pop(0).strip()

            if candidate.lstrip("+-").isdigit():  # valid integer
                value = candidate
            else:
                # Invalid → show error, keep waiting
                self.write_system("Invalid input: please enter an integer.")
                self.userInput.delete(0, tk.END)

        # clean up after valid input
        self.userInput.delete(0, tk.END)
        self.userInput.config(state="disabled")  # lock input again
        return value

    # -------- RUN PROGRAM -------

    def _run_program_thread(self):
        """Runs all instructions/code in memory. Calls class definitions and definitions from main.py."""
        self.write_system("Running program...")
        core._programCounter = 0
        try:
            while core._programCounter < 100:
                instr = core._programMemory.get(f"{core._programCounter:02d}", "+0000")
                tuple_instr = core.parse(instr)
                opcode = tuple_instr[0]

                jumped = False  # track whether branch changed PC

                if opcode == '10':  # read
                    core.read(tuple_instr, self.get_input())
                elif opcode == '11':  # write
                    self.write_system(core.write(tuple_instr))
                elif opcode == '20':  #load
                    core.load(tuple_instr)
                elif opcode == '21':  #store
                    core.store(tuple_instr)
                elif opcode == '30':  #add
                    core.add(tuple_instr)
                elif opcode == '31':  #subtract
                    core.subtract(tuple_instr)
                elif opcode == '32':  #divide
                    core.divide(tuple_instr)
                elif opcode == '33':  #multiply
                    core.multiply(tuple_instr)
                elif opcode == '40':  #branch
                    core.branch(tuple_instr)
                    jumped = True
                elif opcode == '41':  #branchneg
                    core.branchneg(tuple_instr)
                    jumped = True
                elif opcode == '42':  #branchzero
                    core.branchzero(tuple_instr)
                    jumped = True
                elif opcode == '43':
                    break  # halt

                if not jumped:
                    core._programCounter += 1

                self.root.after(0, self.update_vars)
                self.update_memory(core._programMemory)
                time.sleep(0.01)
            self.write_system("Program finished...")
        except Exception as e:
            self.write_system(f"Runtime Error: {e}")
