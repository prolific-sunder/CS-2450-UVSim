import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
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

        # Clipboard for cut/copy/paste (list of strings)
        self.clipboard = []

        # --- Left Side Buttons ---
        tk.Button(self.root, text="Load File", width=12, height=2, command=self.load_file).grid(row=0, column=0, padx=20, pady=6)
        tk.Button(self.root, text="Run Program", width=12, height=2, command=self.run_program).grid(row=1, column=0, padx=20, pady=6)
        tk.Button(self.root, text="Reset Program", width=12, height=2, command=self.reset_memory).grid(row=2, column=0, padx=20, pady=6)
        
        # Edit controls
        tk.Label(self.root, text="Program Help", bg="#6F7681", font=("Helvetica", 12)).grid(row=4, column=0, pady=(10,0))
        tk.Button(self.root, text="Program Use", width=12, command=self.show_program_help).grid(row=5, column=0, padx=20, pady=4)
        tk.Button(self.root, text="How to Edit", width=12, command=self.show_edit_help).grid(row=6, column=0, padx=20, pady=4)

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

        # --- System Variables ---
        tk.Label(self.root, text="System Variables", bg="#6F7681", font=("Helvetica", 18)).place(x=200, y=260)
        self.varsState = tk.Label(self.root, text="Accumulator: +0000\nProgram Counter: 00", bg="white", font=("Helvetica", 12), width=50, height=3, anchor="nw")
        self.varsState.place(x=200, y=295)

        tk.Label(self.root, text="User Console", bg="#6F7681", font=("Helvetica", 18)).place(x=200, y=370)
        self.userInput = tk.Entry(self.root, width=45, font=("Courier New", 12), state="disabled")
        self.userInput.place(x=200, y=405)
        self.userInput.bind("<Return>", self._submit_input)
        self.userQueue = []  # store submitted inputs

        tk.Label(self.root, text="Memory", bg="#6F7681", font=("Helvetica", 18)).place(x=725, y=25)

        # --- Memory Treeview ---
        frame = tk.Frame(self.root, bg="white")
        frame.place(x=725, y=60, width=500, height=560)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, width=18)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # allow selection for editing/cut/copy/paste
        self.memoryState = ttk.Treeview(frame, columns=("Location", "Item"), show="headings", yscrollcommand=scrollbar.set, selectmode="extended", height=35)
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
        self.memoryState.tag_configure("even", background="#f7f7f7")
        self.memoryState.tag_configure("odd", background="#f0f0f0")
        # tag for invalid entries
        self.memoryState.tag_configure("invalid", background="#ffdddd")

        # allow double-click edit
        self.memoryState.bind('<Double-1>', self.on_double_click)
        # right-click context menu
        self.memoryState.bind('<Button-3>', self.show_context_menu)

        # context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_selection)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_command(label="Paste", command=self.paste_at_selection)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_instruction)

        # set up system variables
        self.initial_memory = {}
        self.run_thread = None
        self.file_valid = False
        self.current_filepath = None

        # wait for 'ctrl+s'
        self.root.bind('<Control-s>', self.save_file)

        # keep GUI/Window running unless closed
        self.root.mainloop()


    # --- Help Dialog ---
    def show_program_help(self):
        help_text = (
            "To use UVSim, first click Load File and select a .txt program file. Then press Run Program to begin execution. Input is indicated by the ability to type in the User Console box, when input is indicated type a signed or unsigned four-digit number (for example: +0045, -1234, or 0007) into the User Console and press Enter. Program output and messages will appear in the System Messages panel, while the Accumulator and Program Counter update automatically as the program runs. You can click Reset Program at any time to clear memory and restart, or Exit Program to close UVSim."
        )
        messagebox.showinfo("Program Instructions", help_text)

    def show_edit_help(self):
        help_text = (
            "Memory Table Editing Guide:\n\n"
            "• Double-click a memory cell to edit its value.\n"
            "• Right-click a row for Cut / Copy / Paste / Delete options.\n"
            "• Invalid entries are highlighted in red and listed in System Messages.\n"
            "• Selected memory cell is highlighted in white.\n"
            "• You can load, inspect, and modify memory before running the program.\n"
            "• Save your file by typing 'CTRL+S'"
        )
        messagebox.showinfo("How to Edit", help_text)

    # --- File / Program execution ---

    def load_file(self):
        """Utilizes filedialog to open a file and read it into memory"""
        try:
            filepath = filedialog.askopenfilename(title="Select a Program File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if not filepath:
                return None

            # Clear and initialize memory
            core._programMemory.clear()
            for i in range(100):
                core._programMemory[f"{i:02d}"] = "+0000"

            core._accumulator = "+0000" # Reset accumulator
            core._programCounter = 0 # Reset program counter

            # Read and validate file
            errors = []
            line_count = 0
            memory_index = 0

            with open(filepath, 'r') as f:
                for i, line in enumerate(f):
                    if memory_index >= 100:
                        errors.append(f"Line {i+1}: File exceeds 100 lines")
                        break

                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Remove inline comments
                    if '#' in line:
                        line = line.split('#')[0].strip()

                    if not line:
                        continue

                    # Validate instruction
                    try:
                        core.parse(line)
                        core._programMemory[f"{memory_index:02d}"] = line
                        line_count += 1
                        memory_index += 1
                    except Exception as e:
                        # keep the invalid instruction in memory so user can edit it
                        core._programMemory[f"{memory_index:02d}"] = line
                        errors.append(f"Line {i+1}: {str(e)}")
                        memory_index += 1

            # Update display
            self.build_memory_table(core._programMemory, save_initial=True)
            self.current_filepath = filepath
            self.file_valid = True
            self.write_system(f"Loaded file: {filepath}")

            # Report results
            if errors:
                error_msg = "File loaded, but validation errors were found:\n\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    error_msg += f"\n\n... and {len(errors) - 10} more errors"
                messagebox.showwarning("Load File - Validation Issues", error_msg)
                self.write_system(f"WARNING: File has {len(errors)} validation issue(s). Edit memory before running.")
                self.file_valid = False
            else:
                self.write_system(f"File loaded successfully: {line_count} instructions")
                self.file_valid = True

        except FileNotFoundError:
            messagebox.showerror("Load File Error", "File not found")
            self.write_system("ERROR: File not found")
            self.file_valid = False
        except PermissionError:
            messagebox.showerror("Load File Error", "Permission denied")
            self.write_system("ERROR: Cannot read file - permission denied")
            self.file_valid = False
        except Exception as e:
            messagebox.showerror("Load File Error", f"Error loading file:\n{str(e)}")
            self.write_system(f"ERROR: {str(e)}")
            self.file_valid = False

    def run_program(self):
        """Validate current editor memory and then run in a thread if valid."""
        # Re-validate current memory content before running
        errors = self.validate_memory_from_editor()
        if errors:
            err_msg = "Cannot run: memory contains validation errors:\n\n" + "\n".join(errors[:20])
            if len(errors) > 20:
                err_msg += f"\n\n... and {len(errors) - 20} more errors"
            messagebox.showerror("Run Program - Validation Errors", err_msg)
            self.write_system("ERROR: Memory validation failed. Fix errors before running.")
            self.file_valid = False
            return

        # if already running
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
            # if invalid instruction, mark invalid tag
            try:
                core.parse(item)
            except Exception:
                self.memoryState.insert("", "end", values=(loc, item), tags=("invalid",))
                continue
            self.memoryState.insert("", "end", values=(loc, item), tags=(tag,))

    def update_memory(self, memory_dict, save_initial=False):
        """Updates the changed values in memory. Take parameters memory_dict and save_initial (preset to False)"""
        if save_initial:
            self.initial_memory = memory_dict.copy()

        # only update rows that changed
        children = self.memoryState.get_children()
        for i in range(100):
            loc = f"{i:02d}"
            new_val = memory_dict.get(loc, "+0000")

            # get current value in Treeview
            item_id = children[i]
            old_val = self.memoryState.item(item_id, "values")[1]

            if new_val != old_val:  # update only if different
                # validate new value to set correct tag
                try:
                    core.parse(new_val)
                    tag = "even" if i % 2 == 0 else "odd"
                    self.memoryState.item(item_id, values=(loc, new_val), tags=(tag,))
                except Exception:
                    self.memoryState.item(item_id, values=(loc, new_val), tags=("invalid",))

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
    
    # --- Editing helpers ---

    def on_double_click(self, event):
        """Edit the memory item on double-click."""
        item_id = self.memoryState.identify_row(event.y)
        col = self.memoryState.identify_column(event.x)
        if not item_id or col != '#2':
            return
        loc, old_val = self.memoryState.item(item_id, 'values')
        new_val = simpledialog.askstring("Edit Memory", f"Edit value at {loc}", initialvalue=str(old_val))
        if new_val is None:
            return
        new_val = new_val.strip()
        # accept empty to be treated as +0000
        if new_val == '':
            new_val = "+0000"
        # update core memory and the treeview with validation
        core._programMemory[loc] = new_val
        try:
            core.parse(new_val)
            # valid
            idx = int(loc)
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.memoryState.item(item_id, values=(loc, new_val), tags=(tag,))
        except Exception as e:
            self.memoryState.item(item_id, values=(loc, new_val), tags=('invalid',))
            self.write_system(f"Validation error at {loc}: {str(e)}")

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def get_selected_indices(self):
        """Return list of (index, item_id) tuples for selected rows in ascending index order."""
        selected = self.memoryState.selection()
        children = list(self.memoryState.get_children())
        pairs = []
        for item in selected:
            try:
                idx = children.index(item)
                pairs.append((idx, item))
            except ValueError:
                continue
        pairs.sort()
        return pairs

    def copy_selection(self):
        sel = self.get_selected_indices()
        if not sel:
            messagebox.showinfo("Copy", "No selection to copy.")
            return
        self.clipboard = []
        for idx, item_id in sel:
            loc, val = self.memoryState.item(item_id, 'values')
            self.clipboard.append(val)
        self.write_system(f"Copied {len(self.clipboard)} item(s) to clipboard")

    def cut_selection(self):
        sel = self.get_selected_indices()
        if not sel:
            messagebox.showinfo("Cut", "No selection to cut.")
            return
        self.clipboard = []
        children = list(self.memoryState.get_children())
        for idx, item_id in sel:
            loc, val = self.memoryState.item(item_id, 'values')
            self.clipboard.append(val)
            # remove and shift everything below up
            # set this location to +0000 and shift subsequent down to keep 100 entries
            core._programMemory[loc] = "+0000"
        # Rebuild view from core memory
        self.build_memory_table(core._programMemory)
        self.write_system(f"Cut {len(self.clipboard)} item(s)")

    def paste_at_selection(self):
        if not self.clipboard:
            messagebox.showinfo("Paste", "Clipboard is empty.")
            return
        sel = self.get_selected_indices()
        if sel:
            start_idx = sel[0][0]
        else:
            # if nothing selected, paste at first free or at 0
            start_idx = 0
        # ensure we do not exceed 100 entries
        available = 100 - start_idx
        data_to_paste = list(self.clipboard)
        if len(data_to_paste) > available:
            data_to_paste = data_to_paste[:available]
            messagebox.showwarning("Paste", "Pasted data was truncated to fit memory (100 entries max).")
        # shift existing entries down to make room
        # work from bottom up to avoid overwriting
        for i in range(99, start_idx + len(data_to_paste) - 1, -1):
            src = f"{max(0, i - len(data_to_paste)):02d}"
            dst = f"{i:02d}"
            core._programMemory[dst] = core._programMemory.get(src, "+0000")
        # insert pasted data
        for offset, val in enumerate(data_to_paste):
            core._programMemory[f"{start_idx + offset:02d}"] = val
        self.build_memory_table(core._programMemory)
        self.write_system(f"Pasted {len(data_to_paste)} item(s) at {start_idx:02d}")

    def add_instruction(self):
        # append at end (first +0000 from top)
        children = list(self.memoryState.get_children())
        for i, item_id in enumerate(children):
            loc, val = self.memoryState.item(item_id, 'values')
            if val == "+0000":
                # edit this one
                self.memoryState.selection_set(item_id)
                self.on_double_click(type('E', (), {'x':0,'y':self.memoryState.bbox(item_id)[1]}))
                return
        messagebox.showinfo("Add", "Memory is full (100 entries).")

    def insert_instruction(self):
        # insert before selected row, shift others down
        sel = self.get_selected_indices()
        if not sel:
            idx = 0
        else:
            idx = sel[0][0]
        # if no space to shift
        if idx >= 100:
            messagebox.showinfo("Insert", "Cannot insert beyond memory limit.")
            return
        # check space
        # if last cell non-empty and would be pushed out, warn
        if core._programMemory.get('99', '+0000') != '+0000':
            if not messagebox.askyesno("Insert", "Inserting will drop the last memory entry. Continue?"):
                return
        # shift down from bottom to idx
        for i in range(99, idx, -1):
            core._programMemory[f"{i:02d}"] = core._programMemory.get(f"{i-1:02d}", "+0000")
        core._programMemory[f"{idx:02d}"] = "+0000"
        self.build_memory_table(core._programMemory)
        # let user edit the new slot
        item_id = self.memoryState.get_children()[idx]
        self.memoryState.selection_set(item_id)
        self.on_double_click(type('E', (), {'x':0,'y':self.memoryState.bbox(item_id)[1]}))

    def delete_instruction(self):
        sel = self.get_selected_indices()
        if not sel:
            messagebox.showinfo("Delete", "No selection to delete.")
            return
        children = list(self.memoryState.get_children())
        # set selected indices to +0000 and shift subsequent up
        indices = [i for i, _ in sel]
        for idx in sorted(indices):
            for j in range(idx, 99):
                core._programMemory[f"{j:02d}"] = core._programMemory.get(f"{j+1:02d}", "+0000")
            core._programMemory['99'] = "+0000"
        self.build_memory_table(core._programMemory)
        self.write_system(f"Deleted {len(indices)} row(s)")

    def validate_memory_from_editor(self):
        """Read all items from the Treeview (editor) into core._programMemory and validate each. Returns list of error strings."""
        errors = []
        children = list(self.memoryState.get_children())
        for i, item_id in enumerate(children):
            loc = f"{i:02d}"
            val = self.memoryState.item(item_id, 'values')[1]
            # empty treat as +0000
            if val == '' or val is None:
                val = "+0000"
            core._programMemory[loc] = val
            # skip default +0000
            if val in ("+0000", "0000"):
                continue
            try:
                core.parse(val)
            except Exception as e:
                errors.append(f"{loc}: {str(e)}")
                # mark invalid
                self.memoryState.item(item_id, tags=('invalid',))
        return errors
    
    # -------- SAVE PROGRAM ------

    def save_file(self, event):
        # validate editor contents into core._programMemory
        errors = self.validate_memory_from_editor()
        if errors:
            # ask user whether to proceed despite validation errors
            proceed = messagebox.askyesno(
                "Save - Validation issues",
                ("There are validation errors in memory. Do you want to save anyway?"))
            if not proceed:
                return

        # run save function
        return self.save_file_as()

    def save_file_as(self):
        """
        Prompt the user for save location (ask for filename)
        """
        # validate editor contents
        errors = self.validate_memory_from_editor()
        if errors:
            proceed = messagebox.askyesno(
                "Save As - Validation issues",
                ("There are validation errors in memory. Do you want to save anyway?"))
            if not proceed:
                return

        path = filedialog.asksaveasfilename(
            title="Save Program As",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        try:
            lines = [core._programMemory.get(f"{i:02d}", "+0000") for i in range(100)]
            last = -1
            for i, val in enumerate(lines):
                if val != "+0000":
                    last = i
            write_lines = [] if last == -1 else lines[: last + 1]
            with open(path, "w", encoding="utf-8") as f:
                for ln in write_lines:
                    f.write(str(ln).strip() + "\n")
            self.current_filepath = path
            self.file_valid = True
            self.write_system(f"Saved program to {path}")
            messagebox.showinfo("Save File As", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Save As Error", f"Error saving file:\n{str(e)}")
            self.write_system(f"ERROR saving file: {str(e)}")

    # -------- RUN PROGRAM -------

    def _run_program_thread(self):
        """Runs all instructions/code in memory. Calls class definitions and definitions from main.py."""
        self.write_system("Running program...")
        core._programCounter = 0

        try:
            while core._programCounter < 100:
                instr = core._programMemory.get(f"{core._programCounter:02d}", "+0000")

                # Skip empty memory
                if instr == "+0000" or instr == "0000":
                    core._programCounter += 1
                    continue

                # Parse instruction
                try:
                    tuple_instr = core.parse(instr)
                    opcode = tuple_instr[0]
                except Exception as e:
                    self.write_system(f"Parse Error at line {core._programCounter:02d}: {str(e)}")
                    self.write_system("Program halted")
                    return

                opcode = tuple_instr[0]
                jumped = False

                # Execute instruction with error handling
                try:
                    if opcode == '10':  # read
                        self.write_system("Please enter a number...: ")
                        core.read(tuple_instr, self.get_input())
                    elif opcode == '11':  # write
                        self.write_system(core.write(tuple_instr))
                    elif opcode == '20':  # load
                        core.load(tuple_instr)
                    elif opcode == '21':  # store
                        core.store(tuple_instr)
                    elif opcode == '30':  # add
                        core.add(tuple_instr)
                    elif opcode == '31':  # subtract
                        core.subtract(tuple_instr)
                    elif opcode == '32':  # divide
                        core.divide(tuple_instr)
                    elif opcode == '33':  # multiply
                        core.multiply(tuple_instr)
                    elif opcode == '40':  # branch
                        core.branch(tuple_instr)
                        jumped = True
                    elif opcode == '41':  # branchneg
                        jumped = core.branchneg(tuple_instr)
                    elif opcode == '42':  # branchzero
                        jumped = core.branchzero(tuple_instr)
                    elif opcode == '43':  # halt
                        self.write_system("Program halted normally")
                        break
                    else:
                        self.write_system(f"Warning: Unknown opcode '{opcode}' at line {core._programCounter:02d}")

                except Exception as e:
                    self.write_system(f"Runtime Error at line {core._programCounter:02d}: {str(e)}")
                    self.write_system("Program halted")
                    return

                if not jumped:
                    core._programCounter += 1

                self.root.after(0, self.update_vars)
                self.update_memory(core._programMemory)
                time.sleep(0.01)

            self.write_system("Program finished")

        except Exception as e:
            self.write_system(f"Fatal Error: {str(e)}")
            self.write_system("Program terminated")
