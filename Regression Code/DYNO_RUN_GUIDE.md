# FSAE Automated Dyno Controller (`app_ctk.py`) - Setup & Operation Guide

This guide details the step-by-step procedure to set up your computer environment, connect hardware, and run `app_ctk.py` on the FSAE Dyno.

---

> [!NOTE]
> **Prerequisite Assumption**: High Voltage (HV) and Low Voltage (LV) power systems on the dyno are already turned on, configured, and confirmed safe according to associated members.

---

## 1. Computer Environment Setup

Before connecting hardware, ensure your computer has Python installed and all required libraries configured.

### 1.1 Python Installation
Ensure **Python 3.8** or newer is installed on the host computer. Verify installation via terminal:
```bash
python --version
```

### 1.2 Virtual Environment & Dependencies
1. Open a terminal / PowerShell window and navigate to the `Regression Code` directory:
   ```bash
   cd "path/to/FSAE---Automated-Dyno/Regression Code"
   ```

2. *(Recommended)* Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install required Python packages from [`requirements.txt`](file:///c:/Users/round/OneDrive/Desktop/Scripts/FSAE---Automated-Dyno/Regression%20Code/requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```
   This installs the core dependencies:
   - `python-can` (CAN interface driver layer)
   - `cantools` (DBC parsing and message encoding/decoding)
   - `uptime` (System timing utilities)
   - `pandas` (Data processing)

4. Install CustomTkinter (GUI Framework used by [`app_ctk.py`](file:///c:/Users/round/OneDrive/Desktop/Scripts/FSAE---Automated-Dyno/Regression%20Code/app_ctk.py)):
   ```bash
   pip install customtkinter
   ```

### 1.3 PCAN-Basic Driver Installation
To allow `python-can` to communicate with PCAN USB hardware:
- **Windows**: Download and install the **PEAK-System PCAN-Basic Device Driver** setup package from the official PEAK-System website.
- **Linux**: Ensure `socketcan` or `pcan` kernel modules are loaded (`modprobe pcan`).

---

## 2. Hardware Connections

Follow these steps to establish physical communication between host PC, PCAN adapter, and Dyno systems.

### 2.1 Plugging PCAN into Computer
1. Plug the USB connector of the **PCAN** into a free USB port on the computer.
2. Confirm the LED indicator on the PCAN adapter lights up.
3. On Windows, verify in **Device Manager** under *PEAK-System hardware* that **PCAN-USB** is recognized (Channel `PCAN_USBBUS1`).

### 2.2 Connecting PCAN to Dyno CAN Channel

Connect the CAN cable on the PCAN adapter to any open CAN node on the dyno.

### 2.3 Connecting to Dyno via Ethernet

Connect an RJ45 Ethernet cable from the host computer's Ethernet adapter into the **Dyno Ethernet port**.

---

## 3. Running `app_ctk.py` on the Dyno

### 3.1 Launching the Application
Navigate to the `Regression Code` directory and execute:
```bash
python app_ctk.py
```

### 3.2 Operating the GUI Interface

1. **Select Test Profile (CSV)**:
   - Choose a predefined test CSV from the dropdown menu (loads from [`CSVs/`](file:///c:/Users/round/OneDrive/Desktop/Scripts/FSAE---Automated-Dyno/Regression%20Code/CSVs)).
   - Alternatively, click **"Add New CSV"** to import a custom CSV file.

2. **Disable Simulation Mode (CRITICAL FOR REAL DYNO OPERATION)**:
   > [!IMPORTANT]
   > Uncheck the **"Simulation Mode (Virtual CAN)"** checkbox.
   > - **Checked**: Sends messages to a virtual software bus (testing without hardware).
   > - **Unchecked**: Sends live CAN frames over physical **PCAN** adapter on `PCAN_USBBUS1` at **1 Mbps**.

3. **Advanced Settings (Math Modifiers) [Optional]**:
   - Click **▶ Advanced Settings (Math Modifiers)** to expand.
   - Adjust **Torque Add (+)** / **Torque Multiply (*)** (max multiplier 5x).
   - Adjust **Speed Add (+)** / **Speed Multiply (*)** (max multiplier 5x).

4. **Executing Test Controls**:
   - **▶ Start Test** (Green): Begins reading the selected CSV and sending CAN messages frame-by-frame (~100 Hz rate).
   - **⏸ Pause** (Yellow): Sets commanded torque and speed to `0.0` while maintaining CAN connection. Click **▶ Resume** to continue test profile.
   - **🟥 Kill** (Red): Emergency stop button. Immediately terminates CAN transmission thread and resets interface controls.

5. **Live Monitoring**:
   - **Commanded Torque**: Displays current torque value being broadcasted.
   - **Commanded Speed**: Displays current speed value being broadcasted.
   - **Progress Bar**: Displays completed lines vs total lines in CSV file.

---

> [!CAUTION]
> **Emergency Procedures**: In the event of an unexpected dyno response or physical anomaly, immediately press the **🟥 Kill** button in the GUI or unplug the PCAN USB cable from the host computer to halt CAN control signals.
