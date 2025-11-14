import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
import threading
import time
import json
import os
import main as core

class Window:
    def __init__(self, name="UVsim", size="1280x720"):
        # Load colors from config
        self.primary_color, self.secondary_color = self.load_colors()
        
        # --- Main Window ---
        self.root = tk.Tk()
        self.root.title(name)
        self.root.configure(background=self.primary_color)
        self.root.geometry(size)

        # NEW CODE
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.place(x=700, y=60, width=550, height=620)

        # Clipboard for cut/copy/paste (list of strings)
        self.clipboard = []

        # --- Left Side Buttons ---
        # --- Left Side Buttons ---
        self.load_btn = tk.Button(self.root, text="Load File", width=12, height=4, command=self.load_file)
        self.load_btn.grid(row=0, column=0, padx=20, pady=20)
        
        self.run_btn = tk.Button(self.root, text="Run Program", width=12, height=4, command=self.run_program)
        self.run_btn.grid(row=1, column=0, padx=20, pady=20)
        
        self.reset_btn = tk.Button(self.root, text="Reset Program", width=12, height=4, command=self.reset_memory)
        self.reset_btn.grid(row=2, column=0, padx=20, pady=20)
        
        self.theme_btn = tk.Button(self.root, text="Theme Settings", width=12, height=4, command=self.open_theme_settings)
        self.theme_btn.grid(row=3, column=0, padx=20, pady=20)
        
        self.help_btn = tk.Button(
            self.root, 
            text="?", 
            width=2, 
            height=1,
            font=("Helvetica", 16, "bold"),
            relief=tk.RAISED,
            bd=2,
            command=self.show_help_dialog
        )
        self.help_btn.place(relx=0, rely=1.0, x=20, y=-70, anchor="sw")

        self.title_label = tk.Label(self.root, text="UVSim", bg=self.primary_color, font=("Helvetica", 30))
        self.title_label.place(rely=1.0, relx=0, x=10, y=-5, anchor="sw")
        
        self.divider = tk.Canvas(self.root, width=3, height=900, bg=self.primary_color, bd=0, highlightthickness=0)
        self.divider.grid(row=0, column=2, rowspan=50, padx=10)

        # --- NEW BUTTON TO CLOSE ACTIVE TAB --- new code

        # Place above the notebook, to the right
        self.close_tab_btn = tk.Button(
            self.root,
            text="Close Tab",
            width=10,
            height=1,
            command=self.close_tab
        )
        self.close_tab_btn.place(x=1200, y=30)  # Adjust x/y as needed for spacing

        if not self.notebook.tabs():
            self.close_tab_btn.place_forget()

        # --- System Messages ---
        self.log_frame = tk.Frame(self.root, bg=self.primary_color, bd=0, highlightthickness=0)
        self.log_frame.place(x=200, y=25)

        self.log_label = tk.Label(self.log_frame, text="System Messages", bg=self.primary_color, font=("Helvetica", 18), anchor="w")
        self.log_label.pack(fill="x", padx=0, pady=(0,4))

        # -Text widget for the log (disabled for direct editing)
        self.system_output = tk.Text(self.log_frame, height=10, width=50, state="disabled", wrap="word", font=("Helvetica", 12), bd=1, relief="solid")
        self.system_output.pack(fill="both", expand=True)
        self.systemState = self.system_output

        # --- System Variables ---
        self.vars_label = tk.Label(self.root, text="System Variables", bg=self.primary_color, font=("Helvetica", 18))
        self.vars_label.place(x=200, y=260)
        
        self.varsState = tk.Label(self.root, text="Accumulator: +000000\nProgram Counter: 00", bg="white", font=("Helvetica", 12), width=50, height=3, anchor="nw")
        self.varsState.place(x=200, y=295)

        # --- User Console ---
        self.console_label = tk.Label(self.root, text="User Console", bg=self.primary_color, font=("Helvetica", 18))
        self.console_label.place(x=200, y=370)
        
        self.userInput = tk.Entry(self.root, width=45, font=("Courier New", 12), state="disabled")
        self.userInput.place(x=200, y=405)
        self.userInput.bind("<Return>", self._submit_input)
        self.userQueue = []

        # --- Memory ---
        self.memory_label = tk.Label(self.root, text="Memory", bg=self.primary_color, font=("Helvetica", 18))
        self.memory_label.place(x=725, y=25)

        self.initial_memory = {}
        self.run_thread = None
        self.file_valid = False
        self.current_filepath = None

        # wait for 'ctrl+s'
        self.root.bind('<Control-s>', self.save_file)

        # Memory Manager initializer
        self.memory_manager = core.MemoryManager(self)

        # wait for tab switch
        self.notebook.bind("<<NotebookTabChanged>>", self.memory_manager.switch_mem)

        # Notebook Management
        self.notebook.place(x=700, y=60, width=550, height=620)
        self.close_tab_btn.place(x=1124, y=32)

        # Apply initial theme
        self.apply_theme()
        self.root.mainloop()
                                       
    # --- Color Theme Management ---
    
    def load_colors(self):
        """Load colors from config.json or return defaults."""
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    return config.get('primary_color', '#4C721D'), config.get('secondary_color', '#FFFFFF')
            except:
                pass
        return '#4C721D', '#FFFFFF'  # UVU defaults
    
    def save_colors(self):
        """Save current colors to config.json."""
        try:
            with open('config.json', 'w') as f:
                json.dump({
                    'primary_color': self.primary_color,
                    'secondary_color': self.secondary_color
                }, f, indent=2)
        except:
            pass
    
    def get_text_color(self, bg_color):
        """Code obtained using Claude AI. Return 'black' or 'white' based on background brightness."""
        hex_color = bg_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return 'black' if brightness > 128 else 'white'
    
    def apply_theme(self):
        """Apply current theme colors to all widgets."""
        primary_text = self.get_text_color(self.primary_color)
        secondary_text = self.get_text_color(self.secondary_color)
        
        # Backgrounds
        self.root.configure(bg=self.primary_color)
        self.log_frame.config(bg=self.primary_color)
        self.divider.config(bg=self.primary_color)
        
        # Labels
        self.title_label.config(bg=self.primary_color, fg=primary_text)
        self.log_label.config(bg=self.primary_color, fg=primary_text)
        self.vars_label.config(bg=self.primary_color, fg=primary_text)
        self.console_label.config(bg=self.primary_color, fg=primary_text)
        self.memory_label.config(bg=self.primary_color, fg=primary_text)
        
        # Buttons
        for btn in [self.load_btn, self.run_btn, self.reset_btn, self.theme_btn, self.help_btn]: btn.config(bg=self.secondary_color, fg=secondary_text)
    
    def open_theme_settings(self):
        """Open simple color picker dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Theme Settings")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Theme Settings", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        # Primary Color
        frame1 = tk.Frame(dialog) 
        frame1.pack(pady=10)
        tk.Label(frame1, text="Primary Color:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        primary_box = tk.Label(frame1, text="      ", bg=self.primary_color, relief=tk.RAISED, width=10, height=2)
        primary_box.pack(side=tk.LEFT, padx=5)
        
        def choose_primary():
            color = colorchooser.askcolor(initialcolor=self.primary_color, title="Choose Primary Color")
            if color[1]:
                self.primary_color = color[1]
                primary_box.config(bg=self.primary_color)
                self.apply_theme()
        
        tk.Button(frame1, text="Choose", command=choose_primary).pack(side=tk.LEFT, padx=5)
        
        # Secondary Color
        frame2 = tk.Frame(dialog)
        frame2.pack(pady=10)
        tk.Label(frame2, text="Secondary Color:", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
        secondary_box = tk.Label(frame2, text="      ", bg=self.secondary_color, relief=tk.RAISED, width=10, height=2)
        secondary_box.pack(side=tk.LEFT, padx=5)
        
        def choose_secondary():
            color = colorchooser.askcolor(initialcolor=self.secondary_color, title="Choose Secondary Color")
            if color[1]:
                self.secondary_color = color[1]
                secondary_box.config(bg=self.secondary_color)
                self.apply_theme()
        
        tk.Button(frame2, text="Choose", command=choose_secondary).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def save_and_close():
            self.save_colors()
            messagebox.showinfo("Success", "Theme saved!", parent=dialog)
            dialog.destroy()
        
        def reset_defaults():
            self.primary_color = '#4C721D'
            self.secondary_color = '#FFFFFF'
            primary_box.config(bg=self.primary_color)
            secondary_box.config(bg=self.secondary_color)
            self.apply_theme()
        
        tk.Button(btn_frame, text="Save", command=save_and_close, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset to UVU", command=reset_defaults, width=12).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def show_help_dialog(self):
        """Display help dialog with tabs."""
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("UVSim Help")
        help_dialog.geometry("600x500")
        
        from tkinter import ttk
        notebook = ttk.Notebook(help_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Program Use
        tab1 = tk.Frame(notebook)
        notebook.add(tab1, text="Program Use")
        
        text1 = tk.Text(tab1, wrap=tk.WORD, font=("Helvetica", 10))
        text1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        instructions = """To use UVSim:

1. Load a Program:
   - Click "Load File" and select a .txt program file
   - Valid formats: 4-digit (+1234) or 6-digit (+010234)

2. Run the Program:
   - Click "Run Program" to begin execution
   - Watch System Messages for output

3. Provide Input:
   - When prompted, type a number in User Console
   - Press Enter to submit

4. Monitor Execution:
   - System Variables shows Accumulator and Program Counter
   - Memory table shows all 250 memory locations

5. Other Options:
   - Reset Program: Clear memory and restart
   - Theme Settings: Customize colors

BasicML Instruction Formats:

4-digit format: +XXYY (opcode XX, address 00-99)
Example: +1007 = READ into location 07

6-digit format: +0XXYYY (opcode 0XX, address 000-249)
Example: +010025 = READ into location 025
"""
        text1.insert(1.0, instructions)
        text1.config(state=tk.DISABLED)
        
        # Tab 2: How to Edit
        tab2 = tk.Frame(notebook)
        notebook.add(tab2, text="How to Edit")
        
        text2 = tk.Text(tab2, wrap=tk.WORD, font=("Helvetica", 10))
        text2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        edit_text = """Memory Editor:

Double-click any memory cell to edit
Press Enter to save, Escape to cancel

Keyboard Shortcuts:
Ctrl+C - Copy
Ctrl+X - Cut  
Ctrl+V - Paste
Delete - Clear selection
Ctrl+S - Save program

Right-click Menu:
- Cut, Copy, Paste
- Delete

Valid Formats:
4-digit: +1234, -0456, 1234
6-digit: +010234, -043000, 010025

Invalid instructions shown with red background
"""
        text2.insert(1.0, edit_text)
        text2.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(help_dialog, text="Close", command=help_dialog.destroy, 
                 width=15).pack(pady=10)
        
        # Center dialog
        help_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (help_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (help_dialog.winfo_height() // 2)
        help_dialog.geometry(f"+{x}+{y}")

    # --- File / Program execution ---

    def load_file(self):
        """Utilizes filedialog to open a file and read it into memory"""
        try:
            filepath = filedialog.askopenfilename(title="Select a Program File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
            if not filepath:
                return None
            
            # Initialize new tab
            self.new_frame = ttk.Frame(self.notebook, width=400, height=280)
            #self.new_frame.place(x=725, y=60, width=500, height=560)
            self.new_frame.grid(column=1, row=1)

            scrollbar = tk.Scrollbar(self.new_frame, orient=tk.VERTICAL, width=18)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # allow selection for editing/cut/copy/paste
            self.memoryState = ttk.Treeview(self.new_frame, columns=("Location", "Item"), show="headings", yscrollcommand=scrollbar.set, selectmode="extended", height=35)
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

            for i in range(250):
                tag = "even" if i % 2 == 0 else "odd"
                self.memoryState.insert("", "end", values=(f"{i:03d}", "+000000"), tags=(tag,))
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

            # Defining the new frame
            new_title = filepath.split("/")
            self.notebook.add(self.new_frame, text=new_title[-1])
            self.notebook.place(x=700, y=60, width=550, height=620)
            temp_windows = self.notebook.tabs()
            self.notebook.select(temp_windows[-1])

            # Clear and initialize memory
            core._programMemory.clear()
            for i in range(250):
                core._programMemory[f"{i:03d}"] = "+000000"

            core._accumulator = "+000000" # Reset accumulator
            core._programCounter = 0 # Reset program counter

            # Read and validate file
            errors = []
            line_count = 0
            memory_index = 0

            # First pass: read all lines and detect format
            lines = []
            with open(filepath, 'r') as f:
                for line in f:
                    lines.append(line)
            
            # Detect format by checking first non-empty, non-comment line
            detected_format = None  # Will be '4-digit' or '6-digit'
            for line in lines:
                stripped = line.strip()
                # Skip empty lines and comments
                if not stripped or stripped.startswith('#'):
                    continue
                # Remove inline comments
                if '#' in stripped:
                    stripped = stripped.split('#')[0].strip()
                if not stripped:
                    continue
                    
                # Determine length (accounting for optional sign)
                test_line = stripped if stripped[0] in ('+', '-') else '+' + stripped
                if len(test_line) == 5:
                    detected_format = '4-digit'
                    break
                elif len(test_line) == 7:
                    detected_format = '6-digit'
                    break
            
            # If 4-digit format detected, ask user if they want to convert
            convert_to_6_digit = False
            if detected_format == '4-digit':
                convert_to_6_digit = True
                # WHY DOES THIS BREAK EVERYTHING?
                '''
                convert_to_6_digit = messagebox.askyesno(
                    "4-Digit Format Detected",
                    "This file uses 4-digit instructions.\n\n"
                    "Would you like to convert to 6-digit format?\n\n"
                    "(6-digit format supports 250 memory locations)"
                )'''
                if convert_to_6_digit:
                    self.write_system("Converting 4-digit instructions to 6-digit format...")

            # Second pass: load instructions into memory
            for i, line in enumerate(lines):
                if memory_index >= 250:
                    errors.append(f"Line {i+1}: File exceeds 250 lines")
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
                
                # Convert if requested
                if convert_to_6_digit:
                    line = core.convert_4_to_6_digit(line)

                # Validate instruction
                try:
                    core.parse(line)
                    core._programMemory[f"{memory_index:03d}"] = line
                    line_count += 1
                    memory_index += 1
                except Exception as e:
                    # keep the invalid instruction in memory so user can edit it
                    core._programMemory[f"{memory_index:03d}"] = line
                    errors.append(f"Line {i+1}: {str(e)}")
                    memory_index += 1

            # Add _programMemory to the Memory Manager
            self.memory_manager.add_mem_helper(core._programMemory)

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
                self.enable_memory_editing()
                
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

    # --- Memory Editing Features ---

    def enable_memory_editing(self):
        """Allow user to double-click cells and edit the memory items."""
        self.memoryState.bind("<Double-1>", self._on_double_click_edit)
        self.root.bind("<Control-c>", self._copy_selection)
        self.root.bind("<Control-x>", self._cut_selection)
        self.root.bind("<Control-v>", self._paste_selection)
        self.root.bind("<Delete>", self._delete_selection)

        # Context menu for right-click (add/delete rows)
        self.memory_menu = tk.Menu(self.root, tearoff=0)
        self.memory_menu.add_command(label="Add Entry", command=self._add_entry)
        self.memory_menu.add_command(label="Delete Entry", command=self._delete_selection)
        self.memory_menu.add_separator()
        self.memory_menu.add_command(label="Cut", command=self._cut_selection)
        self.memory_menu.add_command(label="Copy", command=self._copy_selection)
        self.memory_menu.add_command(label="Paste", command=self._paste_selection)
        self.memoryState.bind("<Button-3>", self._show_context_menu)

        self.write_system("Memory editing enabled. Double-click to edit or right-click for options.")

    def _on_double_click_edit(self, event):
        """Handle double-click cell editing for memory values."""
        region = self.memoryState.identify("region", event.x, event.y)
        if region != "cell":
            return
        item = self.memoryState.identify_row(event.y)
        column = self.memoryState.identify_column(event.x)

        if column == "#2":  # only allow editing memory value
            x, y, width, height = self.memoryState.bbox(item, column)
            value = self.memoryState.item(item, "values")[1]

            edit_box = tk.Entry(self.memoryState, width=10, font=("Courier New", 12))
            edit_box.place(x=x, y=y, width=width, height=height)
            edit_box.insert(0, value)
            edit_box.focus()

            def save_edit(event=None):
                new_val = edit_box.get().strip()
                index = int(self.memoryState.item(item, "values")[0])
                if not self._validate_instruction(new_val):
                    messagebox.showerror("Invalid Entry", f"'{new_val}' is not a valid instruction format.")
                else:
                    self.memoryState.item(item, values=(f"{index:03d}", new_val))
                    core._programMemory[f"{index:03d}"] = new_val
                edit_box.destroy()

            edit_box.bind("<Return>", save_edit)
            edit_box.bind("<FocusOut>", lambda e: edit_box.destroy())

    def _validate_instruction(self, value):
        """Check if instruction is valid format."""
        if not value:
            return False
        try:
            core.parse(value)
            return True
        except Exception:
            return False
        
    # New code
    def close_tab(self):
        """Close the currently selected tab window."""
        selected_tab = self.notebook.select()
        if selected_tab:
            self.memory_manager.remove_mem_helper()
            self.notebook.forget(selected_tab)

        # Hide button if no tabs remain

        # For now, I'm removing this functionality as it doesn't come back if you add a new tab - Kaleb
        """
        if not self.notebook.tabs():
            self.close_tab_btn.place_forget()"""
    #End of new code

    def _copy_selection(self, event=None):
        """Copy selected rows to clipboard."""
        selection = [self.memoryState.item(i, "values")[1] for i in self.memoryState.selection()]
        if selection:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(selection))

    def _cut_selection(self, event=None):
        """Cut selected rows (copy then clear)."""
        self._copy_selection()
        for i in self.memoryState.selection():
            index = int(self.memoryState.item(i, "values")[0])
            self.memoryState.item(i, values=(f"{index:03d}", "+000000"))
            core._programMemory[f"{index:03d}"] = "+000000"

    def _paste_selection(self, event=None):
        """Paste clipboard contents starting from first selected row."""
        if not self.memoryState.selection():
            return
        start_index = int(self.memoryState.item(self.memoryState.selection()[0], "values")[0])
        pasted = self.root.clipboard_get().splitlines()

        for offset, line in enumerate(pasted):
            idx = start_index + offset
            if idx >= 250:
                messagebox.showwarning("Paste Limit", "Reached max memory size (250).")
                break
            if self._validate_instruction(line):
                self.memoryState.item(self.memoryState.get_children()[idx], values=(f"{idx:03d}", line))
                core._programMemory[f"{idx:03d}"] = line

    def _delete_selection(self, event=None):
        """Delete (clear) selected memory rows."""
        for i in self.memoryState.selection():
            index = int(self.memoryState.item(i, "values")[0])
            self.memoryState.item(i, values=(f"{index:03d}", "+000000"))
            core._programMemory[f"{index:03d}"] = "+000000"

    def _add_entry(self):
        """Add a blank new memory line if space allows."""
        current_count = len(self.memoryState.get_children())
        if current_count >= 250:
            messagebox.showwarning("Memory Full", "Maximum of 250 entries allowed.")
            return
        new_index = current_count
        self.memoryState.insert("", "end", values=(f"{new_index:03d}", "+000000"))
        core._programMemory[f"{new_index:03d}"] = "+000000"
        self.write_system(f"Added new memory entry at {new_index:03d}.")

    def _show_context_menu(self, event):
        """Display right-click context menu."""
        try:
            self.memory_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.memory_menu.grab_release()
            
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
        for i in range(250):
            loc = f"{i:03d}"
            item = memory_dict.get(loc, "+000000")
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
        for i in range(250):
            loc = f"{i:03d}"
            new_val = memory_dict.get(loc, "+000000")

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

        acc = getattr(core, "_accumulator", "+000000")
        pc = getattr(core, "_programCounter", 0)
        self.varsState.config(text=f"Accumulator: {acc}\nProgram Counter: {pc:03d}")

    def reset_memory(self):
        """Resets all aspects of memory and system. Interacts with core (main module) and changes protected variables. Calls update_vars and clear_system"""
        if not self.initial_memory:
            messagebox.showinfo("Reset Memory", "No saved memory snapshot to restore.")
            return

        # Restore memory
        core._programMemory = self.initial_memory.copy()
        self.build_memory_table(core._programMemory, save_initial=False)

        # Reset Accumulator and Program Counter
        core._accumulator = "+000000"
        core._programCounter = 0
        self.update_vars()
        #self.clear_system()

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
        # accept empty to be treated as +000000
        if new_val == '':
            new_val = "+000000"
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
            # set this location to +000000 and shift subsequent down to keep 250 entries
            core._programMemory[loc] = "+000000"
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
        # ensure we do not exceed 250 entries
        available = 250 - start_idx
        data_to_paste = list(self.clipboard)
        if len(data_to_paste) > available:
            data_to_paste = data_to_paste[:available]
            messagebox.showwarning("Paste", "Pasted data was truncated to fit memory (250 entries max).")
        # shift existing entries down to make room
        # work from bottom up to avoid overwriting
        for i in range(249, start_idx + len(data_to_paste) - 1, -1):
            src = f"{max(0, i - len(data_to_paste)):03d}"
            dst = f"{i:03d}"
            core._programMemory[dst] = core._programMemory.get(src, "+000000")
        # insert pasted data
        for offset, val in enumerate(data_to_paste):
            core._programMemory[f"{start_idx + offset:03d}"] = val
        self.build_memory_table(core._programMemory)
        self.write_system(f"Pasted {len(data_to_paste)} item(s) at {start_idx:03d}")

    def add_instruction(self):
        # append at end (first +000000 from top)
        children = list(self.memoryState.get_children())
        for i, item_id in enumerate(children):
            loc, val = self.memoryState.item(item_id, 'values')
            if val == "+000000":
                # edit this one
                self.memoryState.selection_set(item_id)
                self.on_double_click(type('E', (), {'x':0,'y':self.memoryState.bbox(item_id)[1]}))
                return
        messagebox.showinfo("Add", "Memory is full (250 entries).")

    def insert_instruction(self):
        # insert before selected row, shift others down
        sel = self.get_selected_indices()
        if not sel:
            idx = 0
        else:
            idx = sel[0][0]
        # if no space to shift
        if idx >= 250:
            messagebox.showinfo("Insert", "Cannot insert beyond memory limit.")
            return
        # check space
        # if last cell non-empty and would be pushed out, warn
        if core._programMemory.get('249', '+000000') != '+000000':
            if not messagebox.askyesno("Insert", "Inserting will drop the last memory entry. Continue?"):
                return
        # shift down from bottom to idx
        for i in range(249, idx, -1):
            core._programMemory[f"{i:03d}"] = core._programMemory.get(f"{i-1:03d}", "+000000")
        core._programMemory[f"{idx:03d}"] = "+000000"
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
        # set selected indices to +000000 and shift subsequent up
        indices = [i for i, _ in sel]
        for idx in sorted(indices):
            for j in range(idx, 249):
                core._programMemory[f"{j:03d}"] = core._programMemory.get(f"{j+1:03d}", "+000000")
            core._programMemory['249'] = "+000000"
        self.build_memory_table(core._programMemory)
        self.write_system(f"Deleted {len(indices)} row(s)")

    def validate_memory_from_editor(self):
        """Read all items from the Treeview (editor) into core._programMemory and validate each. Returns list of error strings."""
        errors = []
        children = list(self.memoryState.get_children())
        for i, item_id in enumerate(children):
            loc = f"{i:03d}"
            val = self.memoryState.item(item_id, 'values')[1]
            # empty treat as +000000
            if val == '' or val is None:
                val = "+000000"
            core._programMemory[loc] = val
            # skip default +000000
            if val in ("+000000", "000000"):
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
            lines = [core._programMemory.get(f"{i:03d}", "+000000") for i in range(250)]
            last = -1
            for i, val in enumerate(lines):
                if val != "+000000":
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
            while core._programCounter < 250:
                instr = core._programMemory.get(f"{core._programCounter:03d}", "+0000")

                # Skip empty memory
                if instr == "+000000" or instr == "000000":
                    core._programCounter += 1
                    continue

                # Parse instruction
                try:
                    tuple_instr = core.parse(instr)
                    opcode = tuple_instr[0]
                except Exception as e:
                    self.write_system(f"Parse Error at line {core._programCounter:03d}: {str(e)}")
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
                        self.write_system(f"Warning: Unknown opcode '{opcode}' at line {core._programCounter:03d}")

                except Exception as e:
                    self.write_system(f"Runtime Error at line {core._programCounter:03d}: {str(e)}")
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

