import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import time
import threading
import os

try:
    import can
    import cantools
except ImportError:
    print("Error: Missing dependencies. Run 'pip install -r requirements.txt'")

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_FOLDER = os.path.join(SCRIPT_DIRECTORY, 'CSVs')
DBC_FILE_PATH = os.path.join(SCRIPT_DIRECTORY, 'DBCs', 'dyno_auto.dbc')

# Set application appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DynoController:
    def __init__(self, root):
        self.root = root
        self.root.title("FSAE Automated Dyno Tester")
        self.root.geometry("850x640")
        
        self.running = False
        self.paused = False
        self.simulation_mode = tk.BooleanVar(value=True)
        self.csv_path = tk.StringVar()
        self.dbc_path = DBC_FILE_PATH
        self.total_csv_lines = 0
        
        self.db = cantools.database.load_file(self.dbc_path)
        self.message_def = self.db.get_message_by_name('py_torque')

        # === 1. HEADER SECTION ===
        self.header = ctk.CTkLabel(root, text="FSAE Automated Dyno Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 10))

        # === 2. CONFIGURATION SECTION ===
        self.config_frame = ctk.CTkFrame(root, corner_radius=10)
        self.config_frame.pack(padx=20, pady=10, fill="x")

        self.config_label = ctk.CTkLabel(self.config_frame, text="Test Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        self.config_label.pack(pady=(10, 5))
        
        self.available_csvs = [f for f in os.listdir(DEFAULT_CSV_FOLDER) if f.endswith('.csv')]
        
        self.selected_csv = tk.StringVar(root)
        if self.available_csvs:
            self.selected_csv.set(self.available_csvs[0])
            self.csv_path.set(os.path.join(DEFAULT_CSV_FOLDER, self.available_csvs[0]))
        
        self.file_picker_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.file_picker_frame.pack(pady=(5, 15))

        self.dropdown = ctk.CTkOptionMenu(
            self.file_picker_frame, 
            variable=self.selected_csv, 
            values=self.available_csvs, 
            command=self.on_dropdown_change,
            width=300
        )
        self.dropdown.pack(side="left", padx=10)

        self.browse_button = ctk.CTkButton(self.file_picker_frame, text="Add New CSV", command=self.browse_csv, width=120)
        self.browse_button.pack(side="left", padx=10)

        self.sim_check = ctk.CTkCheckBox(self.config_frame, text="Simulation Mode (Virtual CAN)", variable=self.simulation_mode, font=ctk.CTkFont(size=13))
        self.sim_check.pack(pady=(0, 15))

        # --- Advanced Settings ---
        self.adv_settings_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.adv_settings_frame.pack(pady=(0, 10), fill="x", padx=10)

        self.adv_toggle_btn = ctk.CTkButton(self.adv_settings_frame, text="▶ Advanced Settings (Math Modifiers)", 
                                            font=ctk.CTkFont(size=13, weight="bold"), 
                                            fg_color="transparent", text_color=("gray10", "gray90"),
                                            hover_color=("gray70", "gray30"), anchor="w",
                                            command=self.toggle_adv_settings)
        self.adv_toggle_btn.pack(fill="x", pady=(0, 5))

        self.math_frame = ctk.CTkFrame(self.adv_settings_frame, fg_color="transparent")

        # Torque modifiers
        self.torque_math_frame = ctk.CTkFrame(self.math_frame, fg_color="transparent")
        self.torque_math_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(self.torque_math_frame, text="Torque +:").pack(side="left", padx=(0, 5))
        self.torque_add_var = tk.StringVar(value="0")
        self.torque_add_entry = ctk.CTkEntry(self.torque_math_frame, textvariable=self.torque_add_var, width=60, height=25)
        self.torque_add_entry.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.torque_math_frame, text="Torque *:").pack(side="left", padx=(0, 5))
        self.torque_mult_var = tk.StringVar(value="1")
        self.torque_mult_entry = ctk.CTkEntry(self.torque_math_frame, textvariable=self.torque_mult_var, width=60, height=25)
        self.torque_mult_entry.pack(side="left")

        # Speed modifiers
        self.speed_math_frame = ctk.CTkFrame(self.math_frame, fg_color="transparent")
        self.speed_math_frame.pack(side="left", expand=True)

        ctk.CTkLabel(self.speed_math_frame, text="Speed +:").pack(side="left", padx=(0, 5))
        self.speed_add_var = tk.StringVar(value="0")
        self.speed_add_entry = ctk.CTkEntry(self.speed_math_frame, textvariable=self.speed_add_var, width=60, height=25)
        self.speed_add_entry.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.speed_math_frame, text="Speed *:").pack(side="left", padx=(0, 5))
        self.speed_mult_var = tk.StringVar(value="1")
        self.speed_mult_entry = ctk.CTkEntry(self.speed_math_frame, textvariable=self.speed_mult_var, width=60, height=25)
        self.speed_mult_entry.pack(side="left")

        # === 3. LIVE DISPLAY SECTION ===
        self.display_frame = ctk.CTkFrame(root, fg_color="#1a1a1a", corner_radius=15)
        self.display_frame.pack(padx=20, pady=10, fill="x")

        # Left Side: Torque
        self.torque_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self.torque_frame.pack(side="left", expand=True, pady=25)

        self.torque_title = ctk.CTkLabel(self.torque_frame, text="COMMANDED TORQUE", text_color="gray70", font=ctk.CTkFont(size=14, weight="bold"))
        self.torque_title.pack()
        self.torque_display = ctk.CTkLabel(self.torque_frame, text="0.0", text_color="#00FF00", font=ctk.CTkFont(family="Courier", size=50, weight="bold"), width=250, anchor="w")
        self.torque_display.pack()

        # Right Side: Speed
        self.speed_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self.speed_frame.pack(side="left", expand=True, pady=25)

        self.speed_title = ctk.CTkLabel(self.speed_frame, text="COMMANDED SPEED", text_color="gray70", font=ctk.CTkFont(size=14, weight="bold"))
        self.speed_title.pack()
        self.speed_display = ctk.CTkLabel(self.speed_frame, text="0.0", text_color="#00FFFF", font=ctk.CTkFont(family="Courier", size=50, weight="bold"), width=250, anchor="w")
        self.speed_display.pack()

        # === 4. PROGRESS SECTION ===
        self.progress_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.progress_frame.pack(padx=40, pady=10, fill="x")

        self.progressbar = ctk.CTkProgressBar(self.progress_frame, mode='determinate', height=12)
        self.progressbar.pack(fill="x")
        self.progressbar.set(0)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Ready to Start | 0 Lines", text_color="gray60", font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=(5, 0))

        # === 5. CONTROL BUTTONS SECTION ===
        self.ctrl_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.ctrl_frame.pack(pady=15)

        # Style override variables
        self.c_green = "#28a745"
        self.c_green_h = "#218838"
        self.c_orange = "#ffc107"
        self.c_orange_h = "#e0a800"
        self.c_red = "#dc3545"
        self.c_red_h = "#c82333"

        self.start_button = ctk.CTkButton(self.ctrl_frame, text="▶ Start Test", font=ctk.CTkFont(size=18, weight="bold"), fg_color=self.c_green, hover_color=self.c_green_h, width=180, height=50, command=self.start_thread)
        self.start_button.pack(side="left", padx=10)

        self.pause_button = ctk.CTkButton(self.ctrl_frame, text="⏸ Pause", font=ctk.CTkFont(size=18, weight="bold"), fg_color=self.c_orange, text_color="black", hover_color=self.c_orange_h, width=180, height=50, command=self.toggle_pause, state="disabled")
        self.pause_button.pack(side="left", padx=10)

        self.kill_button = ctk.CTkButton(self.ctrl_frame, text="🟥 Kill", font=ctk.CTkFont(size=18, weight="bold"), fg_color=self.c_red, hover_color=self.c_red_h, width=180, height=50, command=self.stop_test, state="disabled")
        self.kill_button.pack(side="left", padx=10)

    # === Functions ===

    def toggle_adv_settings(self):
        if self.math_frame.winfo_ismapped():
            self.math_frame.pack_forget()
            self.adv_toggle_btn.configure(text="▶ Advanced Settings (Math Modifiers)")
        else:
            self.math_frame.pack(fill="x")
            self.adv_toggle_btn.configure(text="▼ Advanced Settings (Math Modifiers)")

    def on_dropdown_change(self, selection):
        self.csv_path.set(os.path.join(DEFAULT_CSV_FOLDER, selection))

    def browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            filename = os.path.basename(path)
            dest_path = os.path.join(DEFAULT_CSV_FOLDER, filename)
            
            if not os.path.exists(dest_path):
                with open(path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
            
            if filename not in self.available_csvs:
                self.available_csvs.append(filename)
                self.dropdown.configure(values=self.available_csvs)
                    
            self.selected_csv.set(filename)
            self.on_dropdown_change(filename)
            messagebox.showinfo("Success", f"Added {filename} to CSVs folder and selected it.")

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.configure(text="▶ Resume", fg_color=self.c_green, text_color="white", hover_color=self.c_green_h)
        else:
            self.pause_button.configure(text="⏸ Pause", fg_color=self.c_orange, text_color="black", hover_color=self.c_orange_h)

    def start_thread(self):
        if not self.csv_path.get():
            messagebox.showwarning("Input Required", "Please select a CSV file first.")
            return
        
        self.running = True
        self.paused = False
        
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal", text="⏸ Pause", fg_color=self.c_orange, text_color="black", hover_color=self.c_orange_h)
        self.kill_button.configure(state="normal")

        self.progressbar.set(0)
        self.progress_label.configure(text="Initializing...")

        test_thread = threading.Thread(target=self.run_can_test, daemon=True)
        test_thread.start()
    
    def update_live_view(self, torque, speed):
        torque_val = f"{torque / 10.0:.1f}"
        speed_val = f"{speed * 8.72:.1f}"
        self.torque_display.configure(text=torque_val)
        self.speed_display.configure(text=speed_val)

    def set_progress_max(self, total_lines):
        self.total_csv_lines = total_lines
        self.progressbar.set(0)

    def update_progress(self, current_line):
        if self.total_csv_lines > 0:
            percentage = current_line / self.total_csv_lines
            self.progressbar.set(percentage)
            self.progress_label.configure(text=f"Running | {current_line} / {self.total_csv_lines} Lines")

    def run_can_test(self):
        bus = None
        try:
            # Pre count lines in CSV
            with open(self.csv_path.get(), mode='r') as f:
                total_lines = sum(1 for line in f)
                self.root.after(0, self.set_progress_max, total_lines)
            
            # Initialize PCAN Bus
            interface_type = 'virtual' if self.simulation_mode.get() else 'pcan'
            bus = can.Bus(interface=interface_type, channel='PCAN_USBBUS1', bitrate=1000000)

            with open(self.csv_path.get(), mode='r') as csvfile:
                for i, row in enumerate(csvfile):
                    if not self.running: # Check if Kill button was pressed
                        break
                    
                    while self.paused and self.running:
                        signals = {'torque': 0.0, 'speed': 0.0}
                        data = self.message_def.encode(signals)
                        msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
                        bus.send(msg)
                        self.root.after(0, self.update_live_view, 0.0, 0.0)
                        time.sleep(0.01)

                    if not self.running:
                        break
                    
                    # Update Progress Bar
                    self.root.after(0, self.update_progress, i + 1)

                    col = row.split(",")
                    if len(col) < 3: continue
                    
                    try:
                        t_add = float(self.torque_add_var.get() or 0)
                    except ValueError:
                        t_add = 0.0
                    try:
                        t_mult = float(self.torque_mult_var.get() or 1)
                        if(t_mult > 5): raise Exception("Torque multiplier too high (5x max)")
                    except ValueError:
                        t_mult = 1.0

                    try:
                        s_add = float(self.speed_add_var.get() or 0)
                    except ValueError:
                        s_add = 0.0
                    try:
                        s_mult = float(self.speed_mult_var.get() or 1)
                        if(s_mult > 5): raise Exception("Speed multiplier too high (5x max)")
                    except ValueError:
                        s_mult = 1.0

                    torque_val = -1.0 * (float(col[1]) / 4.0)
                    torque_val = (torque_val * t_mult) + t_add
                    Emrax_Torque = torque_val * 10.0
                    
                    DTI_Speed = float(col[2])
                    DTI_Speed = (DTI_Speed * s_mult) + s_add
                    
                    # Updates live display
                    self.root.after(0, self.update_live_view, Emrax_Torque, DTI_Speed)

                    logtime = time.time()
                    SLEEP_TIME = 0.0001
                    
                    # 10ms loop per row
                    while self.running and (time.time() < logtime + 0.01 - SLEEP_TIME):
                        signals = {'torque': Emrax_Torque, 'speed': DTI_Speed}
                        data = self.message_def.encode(signals)
                        msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
                        
                        bus.send(msg)

                        target = time.perf_counter() + SLEEP_TIME
                        while time.perf_counter() < target:
                            pass

        except Exception as e:
            error_msg = str(e)
            if "PCAN" in error_msg or "handle" in error_msg:
                messagebox.showerror("Hardware Error", "PCAN not found")
            else:
                messagebox.showerror("CAN Error", error_msg)
        finally:
            if bus is not None:
                bus.shutdown()
            self.running = False
            self.root.after(0, self.reset_ui) # Safely update UI from thread

    def stop_test(self):
        self.running = False

    def reset_ui(self):
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="⏸ Pause", fg_color=self.c_orange, text_color="black")
        self.kill_button.configure(state="disabled")
        self.progress_label.configure(text=f"Stopped | {self.total_csv_lines} Lines Total")


if __name__ == "__main__":
    app_root = ctk.CTk()
    app = DynoController(app_root)
    app_root.mainloop()
