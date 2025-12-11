import os
import sys
import threading
import subprocess
import time
import webbrowser
import shutil
import re
from datetime import datetime

# Third-party libraries that need to be installed (e.g., via pip)
try:
    import customtkinter as ctk
    import requests
    from PIL import Image
except ImportError:
    print("Error: Required libraries not found. Please run: pip install customtkinter requests Pillow")
    sys.exit(1)

# --- Constants ---

TOOL_NAME = "Tindaly Bypass Tool"
TOOL_VERSION = "1.0.0"
DEV_NAME = "TND95"
TELEGRAM_URL = "https://t.me/TND95"
LOGO_FILENAME = "logo.ico"

# --- API & Bot Configuration ---
TELEGRAM_TOKEN = " here telegram token"
TELEGRAM_CHAT_IDS = "here your chat id"

VPS_API_BASE = "here link of api"
VERSION_CHECK_URL = f"link api+?action=get_version"
REPORT_SUCCESS_URL = f"link api+?action=report_success"
REPORT_CONNECTION_URL = f"link api+?action=report_connection"
REGISTRATION_CHECK_URL = "here link for check registration "

# --- Executable Names ---
PMD3_EXE_NAME = "pymobiledevice3.exe"
DIAGNOSTICS_EXE_NAME = "idevicediagnostics.exe"
SEC_EXE_NAME = "sec.exe"

# --- Static Messages & Config ---
STATIC_PROCESS_MESSAGE = "Activation in progress..."
FINAL_FAILURE_MESSAGE = "❌ Final Activation Failed."
BLOCK_MESSAGE_EN = "Sorry, the iOS version unsupported."
STATIC_FAILURE_MESSAGE_EN = "Critical Activation Error"

# Activation Process Config
MAX_ATTEMPTS = 3
RETRY_WAIT_TIME = 10  # seconds
INITIAL_STABILIZATION_TIME = 15 # seconds
FINAL_STABILIZATION_TIME = 30 # seconds

# This flag is set by tools like PyInstaller when creating a one-file executable
IS_FROZEN = getattr(sys, 'frozen', False)

# For subprocess creation to hide the console window on Windows
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

# --- Device Model Mapping ---
# (This is a large dictionary, reconstructed from the provided bytecode data)
DEVICE_MODEL_MAP = {
    'iPhone1,1': 'iPhone (1st gen)', 'iPhone1,2': 'iPhone 3G', 'iPhone2,1': 'iPhone 3GS', 
    'iPhone3,1': 'iPhone 4 (GSM)', 'iPhone3,2': 'iPhone 4 (GSM Rev A)', 'iPhone3,3': 'iPhone 4 (CDMA)',
    'iPhone4,1': 'iPhone 4S', 'iPhone5,1': 'iPhone 5 (GSM)', 'iPhone5,2': 'iPhone 5 (GSM+CDMA)',
    'iPhone5,3': 'iPhone 5C (GSM)', 'iPhone5,4': 'iPhone 5C (Global)', 'iPhone6,1': 'iPhone 5S (GSM)',
    'iPhone6,2': 'iPhone 5S (Global)', 'iPhone7,1': 'iPhone 6 Plus', 'iPhone7,2': 'iPhone 6',
    'iPhone8,1': 'iPhone 6s', 'iPhone8,2': 'iPhone 6s Plus', 'iPhone8,4': 'iPhone SE (1st Gen)',
    'iPhone9,1': 'iPhone 7 (variant)', 'iPhone9,2': 'iPhone 7 Plus (variant)',
    'iPhone9,3': 'iPhone 7 (other variant)', 'iPhone9,4': 'iPhone 7 Plus (other variant)',
    'iPhone10,1': 'iPhone 8 (variant)', 'iPhone10,2': 'iPhone 8 Plus (variant)',
    'iPhone10,3': 'iPhone X (Global)', 'iPhone10,4': 'iPhone 8 (other variant)',
    'iPhone10,5': 'iPhone 8 Plus (other variant)', 'iPhone10,6': 'iPhone X (GSM)',
    'iPhone11,2': 'iPhone XS', 'iPhone11,4': 'iPhone XS Max', 'iPhone11,6': 'iPhone XS Max (Global)',
    'iPhone11,8': 'iPhone XR', 'iPhone12,1': 'iPhone 11', 'iPhone12,3': 'iPhone 11 Pro',
    'iPhone12,5': 'iPhone 11 Pro Max', 'iPhone12,8': 'iPhone SE (2nd Gen)',
    'iPhone13,1': 'iPhone 12 mini', 'iPhone13,2': 'iPhone 12', 'iPhone13,3': 'iPhone 12 Pro',
    'iPhone13,4': 'iPhone 12 Pro Max', 'iPhone14,2': 'iPhone 13 Pro', 'iPhone14,3': 'iPhone 13 Pro Max',
    'iPhone14,4': 'iPhone 13 mini', 'iPhone14,5': 'iPhone 13', 'iPhone14,6': 'iPhone SE (3rd Gen)',
    'iPhone14,7': 'iPhone 14', 'iPhone14,8': 'iPhone 14 Plus', 'iPhone15,2': 'iPhone 14 Pro',
    'iPhone15,3': 'iPhone 14 Pro Max', 'iPhone15,4': 'iPhone 15', 'iPhone15,5': 'iPhone 15 Plus',
    'iPhone16,1': 'iPhone 15 Pro', 'iPhone16,2': 'iPhone 15 Pro Max',
    'iPhone17,1': 'iPhone 16 Pro', 'iPhone17,2': 'iPhone 16 Pro Max', 'iPhone17,3': 'iPhone 16',
    'iPhone17,4': 'iPhone 16 Plus', 'iPhone17,5': 'iPhone 16e', 'iPhone18,1': 'iPhone 17 Pro',
    'iPhone18,2': 'iPhone 17 Pro Max', 'iPhone18,3': 'iPhone 17', 'iPhone18,4': 'iPhone Air',
    'iPad1,1': 'iPad (1st generation)', 'iPad2,1': 'iPad 2 (Wi-Fi)', 'iPad2,2': 'iPad 2 (GSM)',
    'iPad2,3': 'iPad 2 (CDMA)', 'iPad2,4': 'iPad 2 (late revision)', 'iPad3,1': 'iPad (3rd generation) Wi-Fi',
    'iPad3,2': 'iPad (3rd generation) Wi-Fi + Cellular (CDMA)', 'iPad3,3': 'iPad (3rd generation) Wi-Fi + Cellular (GSM)',
    'iPad3,4': 'iPad (4th generation) Wi-Fi', 'iPad3,5': 'iPad (4th generation) Wi-Fi + Cellular',
    'iPad3,6': 'iPad (4th generation) Wi-Fi + Cellular (MM)', 'iPad4,1': 'iPad Air (Wi-Fi)',
    'iPad4,2': 'iPad Air (Cellular)', 'iPad4,3': 'iPad Air (China variant)', 'iPad4,4': 'iPad mini 2 (Wi-Fi)',
    'iPad4,5': 'iPad mini 2 (Cellular)', 'iPad4,6': 'iPad mini 2 (China variant)', 'iPad4,7': 'iPad mini 3 (Wi-Fi)',
    'iPad4,8': 'iPad mini 3 (Cellular)', 'iPad4,9': 'iPad mini 3 (China variant)', 'iPad5,1': 'iPad mini 4 (Wi-Fi)',
    'iPad5,2': 'iPad mini 4 (Cellular)', 'iPad5,3': 'iPad Air 2 (Wi-Fi)', 'iPad5,4': 'iPad Air 2 (Cellular)',
    'iPad6,3': 'iPad Pro (9.7-inch) Wi-Fi', 'iPad6,4': 'iPad Pro (9.7-inch) Cellular',
    'iPad6,7': 'iPad Pro (12.9-inch) Wi-Fi', 'iPad6,8': 'iPad Pro (12.9-inch) Cellular',
    'iPad6,11': 'iPad (5th generation) Wi-Fi', 'iPad6,12': 'iPad (5th generation) Cellular',
    'iPad7,1': 'iPad Pro (2nd gen) 12.9-inch (Wi-Fi)', 'iPad7,2': 'iPad Pro (2nd gen) 12.9-inch (Cellular)',
    'iPad7,3': 'iPad Pro (10.5-inch) Wi-Fi', 'iPad7,4': 'iPad Pro (10.5-inch) Cellular',
    'iPad7,5': 'iPad (6th generation) Wi-Fi', 'iPad7,6': 'iPad (6th generation) Cellular',
    'iPad7,11': 'iPad (7th generation) Wi-Fi', 'iPad7,12': 'iPad (7th generation) Cellular',
    'iPad8,1': 'iPad Pro (11-inch) Wi-Fi (1st gen)', 'iPad8,2': 'iPad Pro (11-inch) Wi-Fi (1st gen, 1TB)',
    'iPad8,3': 'iPad Pro (11-inch) Cellular (1st gen)', 'iPad8,4': 'iPad Pro (11-inch) Cellular (1st gen, 1TB)',
    'iPad8,5': 'iPad Pro (12.9-inch) Wi-Fi (3rd gen)', 'iPad8,6': 'iPad Pro (12.9-inch) Wi-Fi (3rd gen, 1TB)',
    'iPad8,7': 'iPad Pro (12.9-inch) Cellular (3rd gen)', 'iPad8,8': 'iPad Pro (12.9-inch) Cellular (3rd gen, 1TB)',
    'iPad8,9': 'iPad Pro (11-inch) Wi-Fi (2nd gen)', 'iPad8,10': 'iPad Pro (11-inch) Cellular (2nd gen)',
    'iPad8,11': 'iPad Pro (12.9-inch) Wi-Fi (4th gen)', 'iPad8,12': 'iPad Pro (12.9-inch) Cellular (4th gen)',
    'iPad11,1': 'iPad mini (5th gen) Wi-Fi', 'iPad11,2': 'iPad mini (5th gen) Cellular',
    'iPad11,3': 'iPad Air (3rd gen) Wi-Fi', 'iPad11,4': 'iPad Air (3rd gen) Cellular',
    'iPad11,6': 'iPad (8th gen) Wi-Fi', 'iPad11,7': 'iPad (8th gen) Cellular',
    'iPad12,1': 'iPad (9th gen) Wi-Fi', 'iPad12,2': 'iPad (9th gen) Cellular',
    'iPad13,1': 'iPad Air (4th gen) Wi-Fi', 'iPad13,2': 'iPad Air (4th gen) Cellular',
    'iPad13,4': 'iPad Pro (11-inch) Wi-Fi (3rd gen)', 'iPad13,5': 'iPad Pro (11-inch) Cellular (3rd gen)',
    'iPad13,6': 'iPad Pro (11-inch) Cellular (3rd gen, mmWave)',
    'iPad13,7': 'iPad Pro (11-inch) Cellular (3rd gen, non-mmWave)',
    'iPad13,8': 'iPad Pro (12.9-inch) Wi-Fi (5th gen)', 'iPad13,9': 'iPad Pro (12.9-inch) Cellular (5th gen)',
    'iPad13,10': 'iPad Pro (12.9-inch) Cellular (5th gen, mmWave)',
    'iPad13,11': 'iPad Pro (12.9-inch) Cellular (5th gen, non-mmWave)',
    'iPad13,16': 'iPad (10th gen) Wi-Fi', 'iPad13,17': 'iPad (10th gen) Cellular',
    'iPad14,1': 'iPad mini (6th gen) Wi-Fi', 'iPad14,2': 'iPad mini (6th gen) Cellular',
    'iPad14,3': 'iPad Pro (11-inch) Wi-Fi (4th gen)', 'iPad14,4': 'iPad Pro (11-inch) Cellular (4th gen)',
    'iPad14,5': 'iPad Pro (12.9-inch) Wi-Fi (6th gen)', 'iPad14,6': 'iPad Pro (12.9-inch) Cellular (6th gen)',
    'iPad14,7': 'iPad (11th gen) Wi-Fi', 'iPad14,8': 'iPad (11th gen) Cellular',
    'iPad15,1': 'iPad Pro (11-inch) Wi-Fi (5th gen)', 'iPad15,2': 'iPad Pro (11-inch) Cellular (5th gen)',
    'iPad15,3': 'iPad Pro (12.9-inch) Wi-Fi (7th gen)', 'iPad15,4': 'iPad Pro (12.9-inch) Cellular (7th gen)',
    'iPad15,7': 'iPad (12th gen) Wi-Fi', 'iPad15,8': 'iPad (12th gen) Cellular',
    'iPad15,9': 'iPad Air (6th gen) Wi-Fi', 'iPad15,10': 'iPad Air (6th gen) Cellular',
    'iPad16,1': 'iPad mini (7th gen) Wi-Fi', 'iPad16,2': 'iPad mini (7th gen) Cellular'
}
UNSUPPORTED_VERSIONS = [] # Was empty in the bytecode

# --- Main Application Class ---
class ActivatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(TOOL_NAME)
        self.root.geometry("700x350")
        self.root.resizable(False, False)

        # --- Appearance ---
        self.bg_root = "#141414"
        self.bg_frame = "#202020"
        self.primary_teal = "#00D09C"
        self.secondary_coral = "#F06060" # Red color
        self.white_accent = "#F0F0F0"
        self.text_light = "#F0F0F0"
        self.text_dark = "#101010"
        self.status_default_bg = self.bg_root
        
        self.root.configure(bg=self.bg_root)

        # --- State Variables ---
        self.animation_id = None
        self.device_connected = False
        self.is_registered = False
        self.is_blocked = False
        self.is_activating = False
        self.is_monitoring = True
        self.registration_check_in_progress = False
        self.initial_reg_check_done = False
        self.force_registration_check = False
        self.device_info = {}
        self.monitoring_thread = None
        self.activation_threads = []
        
        # --- Asset Loading ---
        self.load_assets()
        
        # --- UI Setup ---
        self.setup_gui()
        
        # --- Application Logic Start ---
        self.root.after(100, self._check_version)
        self.start_device_monitoring()

        try:
            icon_path = self.get_resource_path(LOGO_FILENAME)
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                self.log(f"WARNING: Icon file not found at {icon_path}. Title bar icon disabled.")
        except Exception as e:
            self.log(f"ERROR: Could not set title bar icon: {e}")

    # --- UI & Asset Management ---

    def get_resource_path(self, relative_path: str) -> str:
        """ Get absolute path to resource, works for dev and for PyInstaller. """
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_assets(self):
        """ Load logo assets. """
        try:
            logo_path = self.get_resource_path(LOGO_FILENAME)
            self.logo_image = ctk.CTkImage(Image.open(logo_path), size=(48, 48))
        except Exception as e:
            self.log(f"ERROR: Could not load logo image. Using placeholder. {e}")
            self.logo_image = None
            
    def setup_gui(self):
        """Configure the graphical interface using CustomTkinter."""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_h_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_h_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_h_frame.grid_columnconfigure(0, weight=1, minsize=280)
        main_h_frame.grid_columnconfigure(1, weight=1)
        
        # Left Panel
        info_card_frame = ctk.CTkFrame(main_h_frame, fg_color=self.bg_frame, corner_radius=10)
        info_card_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        info_card_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(info_card_frame, text="DEVICE DETAILS", font=("Inter", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(10, 15))
        self.info_labels = {
            "model": self._create_info_row(info_card_frame, 1, "Model", "---"),
            "ios_version": self._create_info_row(info_card_frame, 2, "iOS Version", "---"),
            "udid": self._create_info_row(info_card_frame, 3, "UDID", "---", can_copy=True),
            "serial_number": self._create_info_row(info_card_frame, 4, "Serial Number", "---", can_copy=True),
            "activation_state": self._create_info_row(info_card_frame, 5, "Activation State", "Disconnected"),
        }

        # Right Panel
        right_panel = ctk.CTkFrame(main_h_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        branding_card = ctk.CTkFrame(right_panel, fg_color=self.bg_frame, corner_radius=10)
        branding_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        branding_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(branding_card, image=self.logo_image, text=f" {TOOL_NAME}", compound="left", font=("Inter", 16, "bold")).grid(row=0, column=0, pady=10, padx=20, sticky="w")
        
        controls_frame = ctk.CTkFrame(right_panel, fg_color=self.bg_frame, corner_radius=10)
        controls_frame.grid(row=1, column=0, sticky="nsew")
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_rowconfigure(0, weight=1)
        
        self.activate_button = ctk.CTkButton(controls_frame, text="ACTIVATE DEVICE", height=50, command=self.activate_device, state="disabled", fg_color=self.primary_teal, text_color=self.text_dark, font=("Inter", 14, "bold"))
        self.activate_button.grid(row=0, column=0, sticky="sew", padx=20, pady=(20, 10))

        progress_container = ctk.CTkFrame(controls_frame, fg_color="transparent")
        progress_container.grid(row=1, column=0, sticky="ew", padx=20)
        progress_container.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(progress_container, orientation="horizontal", height=8, fg_color="#333333", progress_color=self.primary_teal)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.progress_counter = ctk.CTkLabel(progress_container, text="0%", font=("Inter", 10))
        self.progress_counter.grid(row=0, column=1, padx=(10,0))
        
        self.telegram_button = ctk.CTkButton(controls_frame, text="JOIN TELEGRAM", height=30, command=self._open_telegram_link, fg_color="transparent", border_width=1, border_color=self.primary_teal, hover_color=self._adjust_brightness(self.bg_frame, 10))
        self.telegram_button.grid(row=2, column=0, sticky="sew", padx=20, pady=(10, 20))
        
        self.status_label = ctk.CTkLabel(self.root, text="Connect your device to begin activation.", fg_color=self.status_default_bg, font=("Inter", 12))
        self.status_label.grid(row=1, column=0, sticky="sew", ipady=4)

    def _create_info_row(self, parent, row, label_text, default_value, can_copy=False):
        """Creates a label and value row for device info."""
        key_color = "#888888"
        ctk.CTkLabel(parent, text=label_text, text_color=key_color, font=("Inter", 11), anchor="w").grid(row=row, column=0, sticky="w", padx=(20,10), pady=1)
        val_label = ctk.CTkLabel(parent, text=default_value, font=("Inter", 11), anchor="e")
        val_label.grid(row=row, column=1, sticky="e", padx=(10,20), pady=1)
        if can_copy:
            val_label.configure(cursor="hand2")
            val_label.bind("<Button-1>", lambda e, v=val_label: self._copy_to_clipboard(v.cget("text")))
        return val_label

    def _copy_to_clipboard(self, value):
        """Copies a given value to the system clipboard."""
        if not value or value in ["---", "N/A"]: return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        
        original_text = self.status_label.cget("text")
        status_text = f"Copied: {value} to clipboard!"
        self._update_registration_ui(status_text, self.primary_teal)
        
        # Reset after 2 seconds if the message hasn't changed
        self.root.after(2000, lambda: self._update_registration_ui(original_text, self.status_default_bg) if self.status_label.cget("text") == status_text else None)

    # --- Core Application Logic ---

    def _check_version(self):
        """Checks for tool updates and forces shutdown if outdated."""
        self.log(f"Checking for latest version at: {VERSION_CHECK_URL}")
        try:
            response = requests.get(VERSION_CHECK_URL, verify=False, timeout=5)
            if response.status_code == 200 and response.text.strip() != TOOL_VERSION:
                self.show_error_modal(
                    "Mandatory Update",
                    f"Current version (V{TOOL_VERSION}) is outdated. Update to V{response.text.strip()} required.\n"
                    f"Please contact {DEV_NAME} support for the latest release."
                )
                self.root.destroy()
            else:
                self.log("Version Check Passed. Tool is current.")
        except requests.RequestException as e:
            self.log(f"WARNING: Failed to connect to version check URL: {e}. Working Offline.")

    def start_device_monitoring(self):
        """Starts the background thread to monitor for device connections."""
        self.monitoring_thread = threading.Thread(target=self.monitor_device, daemon=True)
        self.monitoring_thread.start()

    def monitor_device(self):
        """Continuously monitors for device presence and updates UI."""
        self.log("Device monitoring started...")
        last_udid = None
        while self.is_monitoring:
            if self.is_activating:
                time.sleep(2)
                continue
            
            info = self.get_device_info()
            current_udid = info.get("UniqueDeviceID") if info else None

            if current_udid and (current_udid != last_udid):
                self.device_connected = True
                self.device_info = info
                self.root.after(0, self.on_device_connected)
            elif not current_udid and self.device_connected:
                self.device_connected = False
                self.device_info = {}
                self.root.after(0, self.on_device_disconnected)
            
            last_udid = current_udid
            time.sleep(1)

    def on_device_connected(self):
        self.log(f"Device detected: {self.device_info.get('DeviceName', 'N/A')}")
        self.update_info_ui()
        self.report_connection()
        if not self.initial_reg_check_done or self.force_registration_check:
            self._check_registration_status()
            self.force_registration_check = False

    def on_device_disconnected(self):
        if self.is_activating:
            self.log("WARNING: Ignoring disconnection because activation is running.")
            return

        self.log("Device disconnected. Clearing info.")
        self.device_info = {}
        self.is_registered = False
        self.is_blocked = False
        self.initial_reg_check_done = False
        self.update_info_ui()
        self._update_activation_button_state()
        self._update_registration_ui("Connect your device to begin activation.", self.status_default_bg)
    
    def update_info_ui(self):
        """Updates the device info labels with current data."""
        info = self.device_info
        self.info_labels["model"].configure(text=info.get("model_name", "---"))
        self.info_labels["ios_version"].configure(text=info.get("ProductVersion", "---"))
        self.info_labels["udid"].configure(text=info.get("UniqueDeviceID", "---"))
        self.info_labels["serial_number"].configure(text=info.get("SerialNumber", "---"))
        
        state_text = info.get("ActivationState", "Disconnected")
        state_color = self.white_accent
        if state_text == "Activated": state_color = self.primary_teal
        if state_text == "Unactivated": state_color = self.secondary_coral
        
        self.info_labels["activation_state"].configure(text=state_text, text_color=state_color)

    def _update_activation_button_state(self):
        """Controls the main activation button's state and text."""
        if self.is_activating:
            self.activate_button.configure(state="disabled", text=STATIC_PROCESS_MESSAGE)
            return

        state = "disabled"
        text = "Connect your device"
        
        if self.device_connected:
            if self.is_blocked:
                text = f"❌ ERROR: Device is BLOCKED. SN: {self.device_info.get('SerialNumber')}"
            elif not self.initial_reg_check_done:
                text = "Checking registration..."
            elif not self.is_registered:
                 text = f"❌ Registration Required. SN: {self.device_info.get('SerialNumber')} is NOT registered."
            elif self.device_info.get("ActivationState") == "Activated":
                text = f"✅ Device is already Activated. Thank you {DEV_NAME}"
            elif self.is_registered:
                text = "✅ Device is connected. Ready for activation."
                state = "normal"
        
        self.activate_button.configure(text=text, state=state)
        
        # Animate glow if ready
        if state == "normal" and not self.animation_id:
            self._animate_button_glow(is_ready=True)
        elif state == "disabled":
             self._animate_button_glow(is_ready=False)

    def _check_registration_status(self):
        """Checks if the device Serial Number is registered via API."""
        if self.registration_check_in_progress:
            self.log("Skipping registration check: Previous check is still running.")
            return

        sn = self.device_info.get("SerialNumber")
        if not self.device_connected or not sn:
            self.log("Registration check skipped: Device not connected or SN missing.")
            self._update_activation_button_state()
            return
        
        if self.device_info.get("ActivationState") == "Activated":
            self.log("Registration check skipped: Device is already in 'Activated' state.")
            self.is_registered = True
            self.initial_reg_check_done = True
            self._update_activation_button_state()
            return

        self.registration_check_in_progress = True
        self._update_registration_ui("Checking registration status...", "blue")
        
        def do_check():
            try:
                cache_buster = datetime.now().strftime('%Y%m%d%H%M%S')
                url = f"{REGISTRATION_CHECK_URL}?sn={sn}&cache={cache_buster}"
                self.log(f"Checking registration via: {url}")
                
                response = requests.get(url, timeout=10).text.upper()
                
                if "REGISTERED" in response:
                    self.is_registered = True
                    self.is_blocked = False
                    self.root.after(0, lambda: self._update_registration_ui("Device registration confirmed. Ready to activate.", self.primary_teal))
                elif "BLOCKED" in response:
                    self.is_blocked = True
                    self.is_registered = False
                    self.root.after(0, lambda: self._update_registration_ui(f"Device is BLOCKED. SN: {sn}", self.secondary_coral))
                else:
                    self.is_registered = False
                    self.is_blocked = False
                    self.root.after(0, lambda: self._update_registration_ui(f"❌ Registration Required. Serial Number ({sn}) is NOT registered.", self.secondary_coral))
            except requests.RequestException as e:
                self.log(f"WARNING: API connection error: {e}. Assuming UNREGISTERED.")
                self.root.after(0, lambda: self._update_registration_ui(f"API Connection Error. Please check your network. ({e})", self.secondary_coral))
            finally:
                self.registration_check_in_progress = False
                self.initial_reg_check_done = True
                self.root.after(0, self._update_activation_button_state)

        threading.Thread(target=do_check, daemon=True).start()

    def _update_registration_ui(self, message: str, color: str):
        """Updates the status label for registration messages."""
        self.status_label.configure(text=message, text_color=color if color != "blue" else self.white_accent, fg_color=self.status_default_bg if color not in [self.primary_teal, self.secondary_coral, "blue"] else color)
        self.root.update_idletasks()

    # --- Activation Process ---

    def activate_device(self):
        """Starts the activation process in a new thread to keep the UI responsive."""
        if self.is_activating:
            self.log("Activation already in progress...")
            return
        
        if not self.is_registered:
            self.log("Device is not registered. Cannot start activation.")
            return

        if self.device_info.get("ActivationState") == "Activated":
            self.show_success_modal("Check Device Status", "Device is already activated.")
            return
        
        if self.is_unsupported_version():
            self.show_error_modal("Unsupported iOS Version", BLOCK_MESSAGE_EN)
            return

        self.log("=== STARTING ACTIVATION PROCESS ===")
        self.is_activating = True
        self._update_activation_button_state()
        
        # Use a list to manage threads if multiple activations could ever be a thing
        activation_thread = threading.Thread(target=self.run_activation_with_retries, daemon=True)
        self.activation_threads.append(activation_thread)
        activation_thread.start()

    def run_activation_with_retries(self):
        """Wrapper to run the main activation process with retry logic."""
        is_success = False
        for i in range(1, MAX_ATTEMPTS + 1):
            if not self.is_activating: # Check if process was cancelled
                self.log(f"--- ATTEMPT {i}/{MAX_ATTEMPTS} STOPPED ---")
                break

            self.log(f"--- ATTEMPT {i}/{MAX_ATTEMPTS} STARTING ---")
            is_success = self.activation_process(attempt_num=i)
            if is_success:
                break
            
            if i < MAX_ATTEMPTS:
                self.log(f"Attempt {i} failed. Waiting {RETRY_WAIT_TIME} seconds before retry...")
                time.sleep(RETRY_WAIT_time)

        # Finalize outside the loop
        self.finalize_activation(is_success)

    def activation_process(self, attempt_num: int) -> bool:
        """The core 16-step activation process."""
        original_udid = self.device_info.get("UniqueDeviceID")
        ios_version = self.device_info.get("ProductVersion")

        if not original_udid:
            self.log("ERROR: UDID missing at start of attempt.")
            return False

        TOTAL_STEPS = 16
        def calculate_progress(step_num):
            return step_num / TOTAL_STEPS

        def update_ui_step(step_num, detail_en):
            self.log(f"Step {step_num} (Attempt {attempt_num}): {detail_en}")
            progress = calculate_progress(step_num)
            self.root.after(0, lambda: self.update_progress(progress, f"{step_num}/{TOTAL_STEPS}: {detail_en}"))

        try:
            # Step 1: Prepare device
            update_ui_step(1, "Preparing device for log extraction")
            self.restart_device()
            self.wait_for_device_reconnection(original_udid, timeout=120)
            update_ui_step(2, f"Waiting {INITIAL_STABILIZATION_TIME} seconds for service stabilization...")
            time.sleep(INITIAL_STABILIZATION_TIME)

            # Step 2-4: Get GUID
            update_ui_step(3, "Extracting Syslog and searching for GUID")
            logarchive_path = self.extract_syslog()
            if not logarchive_path: return False

            update_ui_step(4, "Analyzing log data to find Activation GUID")
            guid = self.find_guid(logarchive_path) or self.extract_guid_from_syslog(logarchive_path)
            if not guid:
                self.log("ERROR: Critical: GUID not found in syslog by any method.")
                return False
            self.log(f"GUID found: {guid}")

            # Cleanup logs
            if os.path.exists(logarchive_path):
                try: shutil.rmtree(logarchive_path)
                except Exception as e: self.log(f"Warning: Cannot delete logarchive: {e}")

            # Step 5-8: Download activation file
            update_ui_step(5, "Requesting activation file from server")
            api_response = self.call_activation_api(guid, original_udid, ios_version)
            download_url = api_response.get("download_path") if api_response else None
            if not download_url:
                self.log("ERROR: API call failed - Server returned no download URL.")
                return False

            update_ui_step(6, "Downloading activation data file")
            download_path = self.get_resource_path("downloads.28.sqlitedb")
            if not self.download_file_from_vps(download_url, download_path):
                self.log("DOWNLOAD FAILURE: Aborting.")
                return False

            # Step 9-11: Push file to device
            update_ui_step(9, "Cleaning device and Injecting data file")
            files_to_remove = ["/Downloads/downloads.28.sqlitedb", "/Downloads/downloads.28.sqlitedb-wal", "/Downloads/downloads.28.sqlitedb-shm"]
            for f in files_to_remove: self.rm_file_to_device(f)

            update_ui_step(10, f"Pushing file: {download_path}")
            if not self.push_file_to_device(download_path, "/Downloads/downloads.28.sqlitedb"):
                self.log("ERROR: Critical: Failed to push file to device.")
                return False

            # Step 12-16: Finalize
            update_ui_step(12, "Processing Data File (First Reboot)")
            self.restart_device()

            update_ui_step(13, "Forcing a second reboot to complete activation.")
            self.wait_for_device_reconnection(original_udid, timeout=120)
            self.restart_device()

            update_ui_step(14, f"Waiting {FINAL_STABILIZATION_TIME} seconds for stabilization after final reboot.")
            time.sleep(FINAL_STABILIZATION_TIME)
            
            update_ui_step(15, "Checking for reconnection after final reboot...")
            if not self.wait_for_device_reconnection(original_udid, timeout=60):
                self.log("ERROR: Device did not reconnect after final reboot.")
                return False

            update_ui_step(16, "Final status check...")
            latest_info = self.get_device_info()
            is_activated = latest_info.get("ActivationState") == "Activated"

            return is_activated

        except Exception as e:
            self.log(f"ERROR during activation: {e}")
            return False

    def finalize_activation(self, is_success: bool):
        """Handles the final UI updates and notifications after all attempts."""
        self.is_activating = False
        
        final_info = self.get_device_info()
        is_activated_now = final_info.get("ActivationState") == "Activated"

        if is_success or is_activated_now:
            final_message = f"✅ Device Activated Successfully (V{TOOL_VERSION}). Thank you {DEV_NAME}. OTA updates/Erase blocked for stability."
            self.report_activation_success()
            self._send_telegram_notification()
            self.root.after(0, lambda: self._update_registration_ui(final_message, self.primary_teal))
        else:
            fail_message = FINAL_FAILURE_MESSAGE
            self.root.after(0, lambda: self._update_registration_ui(fail_message, self.secondary_coral))
        
        # Cleanup
        self.root.after(0, lambda: self.update_progress(0, "")) # Reset progress bar
        logarchive_path = self.get_resource_path("logarchive")
        if os.path.exists(logarchive_path):
            try: shutil.rmtree(logarchive_path)
            except OSError as e: self.log(f"Cleanup Error: Cannot delete logarchive folder: {e}")
        
        db_file = self.get_resource_path("downloads.28.sqlitedb")
        if os.path.exists(db_file):
            try: os.remove(db_file)
            except OSError as e: self.log(f"Cleanup Error: Cannot delete local sqlitedb file: {e}")

        self.root.after(0, self._update_activation_button_state)

    def update_progress(self, progress: float, message: str = ""):
        """Updates the progress bar and counter."""
        self.progress_bar.set(progress)
        self.progress_counter.configure(text=f"{int(progress*100)}%")
        if message:
            self._update_registration_ui(message, "blue")

    # --- System & Device Interaction ---

    def _run_system_tool_command(self, tool_exe_path: str, args: list, timeout: int = 30) -> subprocess.CompletedProcess:
        """Helper to run a standalone EXE tool."""
        command = [tool_exe_path] + args
        self.log(f"Executing command: {' '.join(command)}")
        try:
            return subprocess.run(
                command,
                capture_output=True, text=True, check=False,
                timeout=timeout, encoding='latin-1', errors='ignore',
                creationflags=CREATE_NO_WINDOW
            )
        except FileNotFoundError:
            self.log(f"CRITICAL ERROR: Standalone tool '{os.path.basename(tool_exe_path)}' not found at {tool_exe_path}.")
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out after {timeout} seconds: {' '.join(command)}")
        except Exception as e:
            self.log(f"Generic error during command execution: {e}")
        return None

    def get_device_info(self) -> dict:
        """Get information about the connected device using ideviceinfo.exe"""
        exe_path = self.get_resource_path(DIAGNOSTICS_EXE_NAME.replace("diagnostics", "info")) # Corrected name from bytecode
        if not exe_path: return None
        
        result = self._run_system_tool_command(exe_path, [])
        if result and result.returncode == 0:
            device_data = {}
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    device_data[key.strip()] = val.strip()
            
            # Normalize keys
            device_data['ProductType'] = device_data.get('ProductType')
            device_data['UniqueDeviceID'] = device_data.get('UniqueDeviceID')
            device_data['DeviceName'] = device_data.get('DeviceName')
            device_data['ProductVersion'] = device_data.get('ProductVersion')
            device_data['SerialNumber'] = device_data.get('SerialNumber')
            device_data['ActivationState'] = device_data.get('ActivationState')
            device_data['model_name'] = DEVICE_MODEL_MAP.get(device_data.get('ProductType'), 'Unknown Model')
            return device_data
        
        return None
        
    def restart_device(self):
        """Restart device using idevicediagnostics, with fallback."""
        diag_path = self.get_resource_path(DIAGNOSTICS_EXE_NAME)
        result = self._run_system_tool_command(diag_path, ["restart"])
        if result and result.returncode == 0:
            self.log("Restart command sent successfully via Diagnostics tool.")
            return True
        
        self.log(f"WARNING: Diagnostics tool failed/not found. Falling back to {PMD3_EXE_NAME}.")
        pmd3_path = self.get_resource_path(PMD3_EXE_NAME)
        result = self._run_system_tool_command(pmd3_path, ["diagnostics", "restart"])
        if result and result.returncode == 0:
            self.log("Restart command sent successfully via pymobiledevice3.exe fallback.")
            return True

        self.log(f"Restart error (Final Fail): {result.stderr if result else 'Unknown Error'}")
        return False

    def wait_for_device_reconnection(self, expected_udid: str, timeout: int) -> bool:
        """Waits for a device with a specific UDID to reconnect."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_activating:
                self.log("WAIT_FOR_RECONNECT: Activation stopped by external flag.")
                return False
            
            latest_info = self.get_device_info()
            if latest_info and latest_info.get("UniqueDeviceID") == expected_udid:
                self.log(f"Device reconnected: {expected_udid}")
                return True
            time.sleep(1)
        self.log("RECONNECTION FAILED.")
        return False

    def extract_syslog(self) -> str:
        """Extract syslog from device, returning the path to the log archive."""
        script_dir = self.get_resource_path("")
        logarchive_path = os.path.join(script_dir, "logarchive")
        self.log(f"Targeting syslog extraction to: {logarchive_path}")

        result = self._run_system_tool_command(self.get_resource_path(PMD3_EXE_NAME), ["syslog", "collect", logarchive_path], timeout=120)
        
        if result and result.returncode == 0:
            if os.path.exists(logarchive_path):
                self.log(f"Syslog extracted successfully: {logarchive_path}")
                return logarchive_path
            else:
                 self.log("ERROR: Command succeeded but syslog file not created at expected path.")
        else:
            self.log(f"ERROR: Syslog collection command failed (Return Code: {result.returncode if result else 'N/A'})")
        return None

    def find_guid(self, trace_file_path: str) -> str:
        """Run sec.exe to find the activation GUID."""
        sec_path = self.get_resource_path(SEC_EXE_NAME)
        trace_file = os.path.join(trace_file_path, "logdata.LiveData.tracev3")
        
        if not os.path.exists(sec_path) or not os.path.exists(trace_file):
            self.log(f"WARNING: sec.exe ({sec_path}) or trace file ({trace_file}) not found.")
            return None

        guid_only_re = re.compile(r"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})")
        
        proc = subprocess.Popen([sec_path, "-m", "single-file", "-i", trace_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=CREATE_NO_WINDOW)
        
        found_guid = None
        for line in iter(proc.stdout.readline, ''):
            if "BLDatabaseManager" in line:
                match = guid_only_re.search(line)
                if match:
                    found_guid = match.group(1)
                    break # Found it, no need to read more
        
        proc.kill()
        proc.wait()
        return found_guid

    def extract_guid_from_syslog(self, logarchive_path: str) -> str:
        """Fallback method to extract GUID by directly reading log files."""
        guid_pattern = re.compile(r"/private/var/containers/Shared/SystemGroup/([0-9A-Fa-f\-]{36})/Documents/BLDatabaseManager/BLDatabaseManager\.sqlite", re.IGNORECASE)
        generic_guid_pattern = re.compile(r"([0-9A-Fa-f]{8}-[0-9A-Fa-f-]{4}-[0-9A-Fa-f-]{4}-[0-9A-Fa-f-]{4}-[0-9A-Fa-f-]{12})", re.IGNORECASE)

        try:
            for root_dir, _, files in os.walk(logarchive_path):
                for file_name in files:
                    if any(x in file_name.lower() for x in ["systemgroup", "activation", "apple", "cert"]):
                        full_file_path = os.path.join(root_dir, file_name)
                        try:
                            with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    match_specific = guid_pattern.search(line)
                                    if match_specific: return match_specific.group(1)
                                    # Fallback to generic if specific not found
                                    match_generic = generic_guid_pattern.search(line)
                                    if match_generic: return match_generic.group(1)
                        except Exception as e:
                            self.log(f"Warning: Could not read file {full_file_path}: {e}")
        except Exception as e:
            self.log(f"Error during GUID extraction (Direct Read): {e}")
        return None

    def call_activation_api(self, guid, udid, ios_version) -> dict:
        """Makes the activation API call."""
        params = {'pr': guid, 'udid': udid, 'ios': ios_version}
        self.log(f"API call: {VPS_API_BASE} with params {params}")
        try:
            response = requests.get(VPS_API_BASE, params=params, timeout=15)
            self.log(f"API response (status {response.status_code}): {response.text}")
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.log(f"Error during API call: {e}")
        return {}

    def download_file_from_vps(self, vps_download_url, output_path) -> bool:
        """Downloads the required file from the VPS."""
        try:
            response = requests.get(vps_download_url, timeout=30)
            if response.status_code == 200:
                if len(response.content) == 0:
                    self.show_error_modal("Activation Data File Error", "Server returned an empty activation file (0 bytes). Cannot proceed.")
                    return False
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    self.log(f"File saved successfully from VPS as {output_path} ({size} bytes)")
                    if size == 122880: # Suspicious size from bytecode
                        self.log("WARNING: Downloaded file size is suspicious, might be a placeholder image.")
                    return True
                else:
                    self.log("ERROR: File not created after successful download from VPS")
            else:
                 self.show_error_modal("Server Connection Error", f"Failed to download activation data file. HTTP Status: {response.status_code}")
        except requests.RequestException as e:
            self.show_error_modal("Download Error", f"A network error occurred while downloading the data file: {e}")
        return False

    def push_file_to_device(self, local_path, device_path):
        """Sends a file to the device using afc push."""
        self.log(f"Pushing file to device: {local_path} -> {device_path}")
        result = self._run_system_tool_command(self.get_resource_path(PMD3_EXE_NAME), ["afc", "push", local_path, device_path])
        if result and result.returncode == 0:
            self.log("File sent successfully to device")
            return True
        self.log(f"ERROR during file push (Code: {result.returncode if result else 'N/A'})")
        return False

    def rm_file_to_device(self, device_path):
        """Removes a file from the device using afc rm."""
        self.log(f"Removing file from device: {device_path}")
        result = self._run_system_tool_command(self.get_resource_path(PMD3_EXE_NAME), ["afc", "rm", device_path])
        if result and result.returncode == 0:
            self.log("File removed successfully from device (or did not exist)")
            return True
        self.log(f"ERROR during file removal (Code: {result.returncode if result else 'N/A'})")
        return False

    def is_unsupported_version(self):
        """Checks if the device version is in the blocked list."""
        ios_version = self.device_info.get("ProductVersion")
        if ios_version and ios_version in UNSUPPORTED_VERSIONS:
             self.log(f"BLOCK: Detected unsupported iOS version: {ios_version}")
             return True
        return False

    # --- API Reporting ---
    
    def report_connection(self):
        """Reports successful device connection to the Admin Panel."""
        payload = {
            'udid': self.device_info.get('UniqueDeviceID', 'N/A'),
            'model': self.device_info.get('model_name', 'N/A'),
            'product_type': self.device_info.get('ProductType', 'N/A'),
            'ios_version': self.device_info.get('ProductVersion', 'N/A'),
            'tool_version': TOOL_VERSION
        }
        try:
            response = requests.post(REPORT_CONNECTION_URL, data=payload, timeout=5)
            if response.text.strip() == "SUCCESS":
                self.log("INFO: Device connection reported to Admin Panel.")
            else:
                self.log(f"WARNING: Failed to report connection (Status: {response.status_code})")
        except requests.RequestException as e:
            self.log(f"WARNING: Failed to connect to Admin Panel API for connection report: {e}")
            
    def report_activation_success(self):
        """Reports successful activation to the Admin Panel."""
        payload = {
            'udid': self.device_info.get('UniqueDeviceID', 'N/A'),
            'serial': self.device_info.get('SerialNumber', 'N/A'),
            'model': self.device_info.get('model_name', 'N/A'),
            'ios_version': self.device_info.get('ProductVersion', 'N/A'),
            'tool_version': TOOL_VERSION
        }
        try:
            response = requests.post(REPORT_SUCCESS_URL, data=payload, timeout=10)
            if "SUCCESS" in response.text:
                self.log("Activation success reported to Admin Panel.")
            else:
                self.log(f"WARNING: Failed to report success. Server response: {response.text}")
        except requests.RequestException as e:
            self.log(f"ERROR: Could not connect to success report URL: {e}")

    def _send_telegram_notification(self):
        """Sends a successful activation notification to Telegram."""
        if not TELEGRAM_CHAT_IDS:
            self.log("WARNING: TELEGRAM_CHAT_IDS is empty. Skipping notification.")
            return

        chat_ids = TELEGRAM_CHAT_IDS.split(',')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_text = (
            f"**✅ ACTIVATION SUCCESS**\n"
            f"**Tool Version:** V{TOOL_VERSION}\n"
            f"**Timestamp:** {timestamp}\n\n"
            f"**Device Details:**\n"
            f"Model: `{self.device_info.get('model_name', 'N/A')}`\n"
            f"iOS Version: `{self.device_info.get('ProductVersion', 'N/A')}`\n"
            f"Serial Number: `{self.device_info.get('SerialNumber', 'N/A')}`\n"
            f"UDID: `{self.device_info.get('UniqueDeviceID', 'N/A')}`"
        )
        
        for cid in chat_ids:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {'chat_id': cid.strip(), 'text': message_text, 'parse_mode': 'Markdown'}
            try:
                response = requests.post(url, data=payload, timeout=10)
                if response.json().get('ok'):
                    self.log(f"INFO: Telegram success notification sent to chat ID {cid}")
                else:
                    self.log(f"WARNING: Failed to send Telegram notification to chat ID {cid} (Status: {response.status_code}, Response: {response.text})")
            except Exception as e:
                self.log(f"ERROR: Telegram API connection failed for chat ID {cid}: {e}")

    # --- UI Helpers & Popups ---

    def _adjust_brightness(self, hex_color: str, delta: int) -> str:
        """Adjusts brightness of a hex color to simulate hover."""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + delta))
        g = max(0, min(255, g + delta))
        b = max(0, min(255, b + delta))
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _animate_button_glow(self, is_ready: bool, step=0):
        """Glow effect for the activation button when ready."""
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
            # Reset button to default state
            self.activate_button.configure(
                fg_color=self.primary_teal,
                border_color=self.primary_teal,
                border_width=0
            )

        if not is_ready:
            return
            
        # Simple pulsating glow by changing border color
        glow_colors = [self.primary_teal, self._adjust_brightness(self.primary_teal, 30), self._adjust_brightness(self.primary_teal, 50), self._adjust_brightness(self.primary_teal, 30)]
        
        def animate():
            nonlocal step
            if not self.root.winfo_exists() or not self.activate_button.cget("state") == "normal":
                self.activate_button.configure(border_width=0)
                return
            
            step = (step + 1) % len(glow_colors)
            self.activate_button.configure(border_width=2, border_color=glow_colors[step])
            self.animation_id = self.root.after(300, animate)

        animate()

    def _open_telegram_link(self):
        """Opens the Telegram channel link in a web browser."""
        try:
            webbrowser.open_new_tab(TELEGRAM_URL)
        except Exception as e:
            self.log(f"ERROR: Could not open Telegram link: {e}")
            self.show_error_modal("Browser Error", "Could not open Telegram link. Please check your browser settings.")

    def show_info_modal(self, title, message):
        from tkinter import messagebox
        messagebox.showinfo(f"{TOOL_NAME} | Info", message)

    def show_success_modal(self, title, message):
        from tkinter import messagebox
        messagebox.showinfo(f"{TOOL_NAME} | {title}", message)
        
    def show_error_modal(self, title, message):
        from tkinter import messagebox
        messagebox.showerror(f"{TOOL_NAME} | {title}", message)

    def log(self, message: str):
        """Adds a message to the console only if not running as a frozen EXE."""
        if not IS_FROZEN:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def on_closing(self):
        """Handle application closing."""
        self.is_monitoring = False
        self.is_activating = False # Signal threads to stop
        if self.animation_id:
            try: self.root.after_cancel(self.animation_id)
            except Exception as e: self.log(f"Warning: Failed to cancel animation ID: {e}")
        self.root.destroy()

# --- Main Execution ---
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = ActivatorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
