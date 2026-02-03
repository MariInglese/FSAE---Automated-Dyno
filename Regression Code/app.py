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
        self.root.geometry("500x400")

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
        tk.Label(root, text="OR Use a Custom File:", font=('Arial', 10, 'italic')).pack(pady=(15, 0))
        file_frame = tk.Frame(root)
        file_frame.pack(pady=5)
        self.path_entry = tk.Entry(file_frame, width=40)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_csv).pack(side=tk.LEFT)

        # LIVE DISPLAY
        display_frame = tk.Frame(root, bg="black", padx=10, pady=10)
        display_frame.pack(pady=10,fill=tk.X, padx=20)

        tk.Label(display_frame, text="LIVE TORQUE", fg="white", bg="black", font=("Arial", 10)).pack()
        self.torque_display = tk.Label(display_frame, text="0.0", fg="#00FF00", bg="black", font=("Courier", 30, "bold"))
        self.torque_display.pack()


        # Control
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(pady=20)

        self.start_button = tk.Button(ctrl_frame, text="▶ Start Test", bg="green", fg="white", width=15, command=self.start_thread)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.kill_button = tk.Button(ctrl_frame, text="🟥 Kill", bg="red", fg="white", width=15, command=self.stop_test, state=tk.DISABLED)
        self.kill_button.pack(side=tk.LEFT, padx=10)

    def on_dropdown_change(self, selection):
        self.csv_path.set(os.path.join(DEFAULT_CSV_FOLDER, selection))

    def browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path.set(path)
            self.selected_csv.set("Custom File...")

    def start_thread(self):
        if not self.csv_path.get():
            messagebox.showwarning("Input Required", "Please select a CSV file first.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.kill_button.config(state=tk.NORMAL)

        test_thread = threading.Thread(target=self.run_can_test, daemon=True)
        test_thread.start()
    
    def update_live_view(self, value):
        display_val = f"{value / 10.0}"
        self.torque_display.config(text=display_val)

    def run_can_test(self):
            bus = None
            try:
                # Initialize PCAN Bus
                bus = can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=1000000)
                
                with open(self.csv_path.get(), mode='r') as csvfile:
                    for row in csvfile:
                        if not self.running: # Check if Kill button was pressed
                            break
                            
                        col = row.split(",")
                        if len(col) < 2: continue
                        
                        torque_val = float(col[1]) * 10

                        # Updates live display
                        self.root.after(0, self.update_live_view, torque_val)

                        logtime = time.time()

                        # 10ms loop per row
                        while self.running and (time.time() < logtime + 0.01):
                            signals = {'torque': torque_val}
                            data = self.message_def.encode(signals)
                            msg = can.Message(arbitration_id=0x700, data=data, is_extended_id=False)
                            
                            bus.send(msg)
                            time.sleep(0.0001)

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

