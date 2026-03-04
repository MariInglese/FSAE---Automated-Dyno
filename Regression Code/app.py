import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

class DynoController:
    def __init__(self, root):
        self.root = root
        self.root.title("FSAE Automated Dyno Tester")
        self.root.geometry("800x500")

        self.running = False
        self.csv_path = tk.StringVar()
        self.dbc_path = DBC_FILE_PATH
        
        self.db = cantools.database.load_file(self.dbc_path)
        self.message_def = self.db.get_message_by_name('py_torque')

        tk.Label(root, text="FSAE Automated Dyno Control", font=("Arial,14,'bold'")).pack(pady=10)

        tk.Label(root, text="Standard Tests (from GitHub CSVs folder):", font=('Arial', 10, 'italic')).pack()
        
        self.available_csvs = [f for f in os.listdir(DEFAULT_CSV_FOLDER) if f.endswith('.csv')]
        self.selected_csv = tk.StringVar(root)
        
        if self.available_csvs:
            self.selected_csv.set(self.available_csvs[0])
            self.csv_path.set(os.path.join(DEFAULT_CSV_FOLDER, self.available_csvs[0]))
        
        # Dropdown menu
        self.dropdown = ttk.OptionMenu(
            root, self.selected_csv, self.selected_csv.get(), 
            *self.available_csvs, command=self.on_dropdown_change
        )
        self.dropdown.pack(pady=5)

        # Custom Upload
        tk.Label(root, text="Add a new CSV to Library:", font=('Arial', 10, 'italic')).pack(pady=(15, 0))
        tk.Button(root, text="Browse for CSV", command=self.browse_csv).pack(pady=5)

        # LIVE DISPLAY
        display_frame = tk.Frame(root, bg="black", padx=10, pady=10)
        display_frame.pack(pady=10,fill=tk.X, padx=20)

        # Left Side: Torque
        torque_frame = tk.Frame(display_frame, bg="black")
        torque_frame.pack(side=tk.LEFT, expand=True)

        tk.Label(torque_frame, text="COMMANDED TORQUE", fg="white", bg="black", font=("Arial", 10)).pack()
        self.torque_display = tk.Label(torque_frame, text="0.0", fg="#00FF00", bg="black", font=("Courier", 30, "bold"), width=7, anchor='w')
        self.torque_display.pack()

        # Right Side: Speed
        speed_frame = tk.Frame(display_frame, bg="black")
        speed_frame.pack(side=tk.LEFT, expand=True)

        tk.Label(speed_frame, text="COMMANDED SPEED", fg="white", bg="black", font=("Arial", 10)).pack()
        self.speed_display = tk.Label(speed_frame, text="0.0", fg="#00FFFF", bg="black", font=("Courier", 30, "bold"), width=7, anchor='w')
        self.speed_display.pack()


        # PROGRESS BAR
        tk.Label(root, text="Progress").pack(pady=10)
        self.progressbar = ttk.Progressbar(root, orient='horizontal', length=600, mode='determinate')
        self.progressbar.pack(pady=5)
        self.progress_label = tk.Label(root, text="0 / 0 Lines")
        self.progress_label.pack()

        # Control
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(pady=20)

        self.start_button = tk.Button(ctrl_frame, text="▶ Start Test", font=("Arial",15,"bold"), bg="green", fg="white", width=30, height=5, command=self.start_thread)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.kill_button = tk.Button(ctrl_frame, text="🟥 Kill", font=("Arial",15,"bold"), bg="red", fg="white", width=30, height=5, command=self.stop_test, state=tk.DISABLED)
        self.kill_button.pack(side=tk.LEFT, padx=10)

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
                
                menu = self.dropdown["menu"]
                menu.delete(0, "end")
                for csv_file in self.available_csvs:
                    menu.add_command(label=csv_file, command=tk._setit(self.selected_csv, csv_file, self.on_dropdown_change))
                    
            self.selected_csv.set(filename)
            self.on_dropdown_change(filename)
            messagebox.showinfo("Success", f"Added {filename} to CSVs folder and selected it.")

    def start_thread(self):
        if not self.csv_path.get():
            messagebox.showwarning("Input Required", "Please select a CSV file first.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.kill_button.config(state=tk.NORMAL)

        self.progressbar['value'] = 0
        self.progress_label.config(text="Initializing...")

        test_thread = threading.Thread(target=self.run_can_test, daemon=True)
        test_thread.start()
    
    def update_live_view(self, torque, speed):
        torque_val = f"{torque / 10.0}"
        self.torque_display.config(text=torque_val)
        self.speed_display.config(text=speed)

    def set_progress_max(self, total_lines):
        self.progressbar['maximum'] = total_lines
        self.progressbar['value'] = 0

    def update_progress(self, current_line, total_lines):
        self.progressbar['value'] = current_line
        self.progress_label.config(text=str(current_line) + "/" + str(total_lines))

    def run_can_test(self):
            bus = None
            try:
                # Pre count lines in CSV
                with open(self.csv_path.get(), mode='r') as f:
                    total_lines = sum(1 for line in f)
                    self.root.after(0,self.set_progress_max(total_lines))
                # Initialize PCAN Bus
                bus = can.Bus(interface='virtual', channel='PCAN_USBBUS1', bitrate=1000000)

                with open(self.csv_path.get(), mode='r') as csvfile:
                    for i, row in enumerate(csvfile):
                        if not self.running: # Check if Kill button was pressed
                            break
                        
                        # Update Progress Bar
                        self.root.after(0, self.update_progress(i + 1, total_lines))

                        col = row.split(",")
                        if len(col) < 2: continue
                        
                        torque_val = -1.0 * (float(col[1]) / 4.0)
                        Emrax_Torque = torque_val * 10.0

                        DTI_Speed = float(col[2]) * 8.72
                        # Updates live display
                        self.root.after(0, self.update_live_view, Emrax_Torque, DTI_Speed)

                        logtime = time.time()

                        SLEEP_TIME = 0.0001
                        # 10ms loop per row
                        while self.running and (time.time() < logtime + 0.01-SLEEP_TIME):
                            signals = {'torque': Emrax_Torque, 
                                       'speed': DTI_Speed}
                            data = self.message_def.encode(signals)
                            msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
                            
                            bus.send(msg)

                            #SLEEP_TIME = 0.00001  #Change this value to change sleep time
                            target = time.perf_counter() + SLEEP_TIME
                            while time.perf_counter() < target:
                                pass

                            #time.sleep(0.0001)

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
        self.start_button.config(state=tk.NORMAL)
        self.kill_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = DynoController(root)
    root.mainloop()

