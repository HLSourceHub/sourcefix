import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import requests
import time
from PIL import Image, ImageTk
import shutil  # Import for folder deletion
import webbrowser  # For opening browser search
import sys
import platform  # For detecting the operating system
import pkgutil  # For accessing embedded resources

# List of SDKs to choose from, with names and corresponding numeric values
SDK_LIST = [
    ("Source SDK 2006", "215"),
    ("Source SDK 2007", "218"),
    ("Source SDK Base 2013 MP", "243750"),
    ("Source SDK Base 2013 SP", "243730"),
]

# Function to extract bat2exe.exe from the program resources into a specific folder
def extract_bat_to_exe(destination):
    try:
        # Check if the app is running from a packaged state (e.g., PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            # Path to the temporary folder where bundled resources are extracted
            bat2exe_source = os.path.join(sys._MEIPASS, "bat2exe.exe")
        else:
            # Fallback for development when running directly from script
            bat2exe_source = "bat2exe.exe"

        # Ensure the source file exists
        if not os.path.exists(bat2exe_source):
            raise FileNotFoundError(f"bat2exe.exe not found at {bat2exe_source}")

        # Copy the bat2exe.exe to the destination
        shutil.copy(bat2exe_source, destination)
        
        # Confirm the file exists after extraction
        if not os.path.exists(destination):
            raise FileNotFoundError(f"Failed to extract bat2exe.exe to {destination}")

        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract bat2exe.exe: {str(e)}")
        return False

# Function to locate Steam directory (for Windows only)
def locate_steam():
    steam_path = ""
    
    if platform.system() == "Windows":
        # Windows-specific Steam directory selection
        steam_path = filedialog.askdirectory(title="Select Steam Directory")
        if steam_path:
            steam_exe = os.path.join(steam_path, "Steam.exe")
            if os.path.exists(steam_exe):
                steam_entry.delete(0, tk.END)
                steam_entry.insert(0, steam_path)
            else:
                messagebox.showwarning("Warning", "Steam.exe not found in the selected directory.")
        else:
            messagebox.showinfo("Info", "Steam directory not selected.")

# Function to locate Sourcemods directory
def locate_sourcemods():
    sourcemods_path = filedialog.askdirectory(title="Select Sourcemods Directory")
    if sourcemods_path:
        sourcemods_var.set(sourcemods_path)
    else:
        messagebox.showinfo("Info", "Sourcemods directory not selected.")

# Function to locate Mod directory (specific mod within sourcemods)
def locate_mod():
    mod_path = filedialog.askdirectory(title="Select Mod Directory (within Sourcemods)")
    if mod_path:
        mod_var.set(mod_path)
    else:
        messagebox.showinfo("Info", "Mod directory not selected.")

# Function to open a browser search for the mod SDK
def open_sdk_help():
    mod_path = mod_var.get()
    if mod_path:
        mod_folder = os.path.basename(mod_path)
        search_query = f"What Source SDK does the {mod_folder} mod use?"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        webbrowser.open(search_url)
        messagebox.showinfo("SDK Search", "Starting browser search for compatible SDK...")
    else:
        messagebox.showwarning("Warning", "Please enter a mod path first.")

# Function to detect the operating system and generate launchers accordingly
def generate_launcher():
    sourcemods_path = sourcemods_var.get()
    mod_path = mod_var.get()
    selected_sdk_id = sdk_dict[sdk_var.get()]  # Get the numeric SDK ID based on the selected name

    if sourcemods_path and mod_path and selected_sdk_id:
        if not os.path.exists(sourcemods_path):
            messagebox.showerror("Error", "Invalid Sourcemods path.")
            return
        if not os.path.basename(sourcemods_path).lower() == "sourcemods":
            messagebox.showerror("Error", "Please select a 'sourcemods' folder.")
            return

        mod_folder = os.path.basename(mod_path)
        os_type = platform.system()  # Detect the OS (e.g., Windows, Linux)

        if os_type == "Windows":
            # Windows-specific batch file and .exe generation
            steam_path = steam_entry.get()
            steam_exe_name = "Steam.exe"
            batch_content = f'"{steam_path}\\{steam_exe_name}" -applaunch {selected_sdk_id} -game "{mod_path}"'
            batch_file_name = f"{mod_folder}.bat"
            batch_file_path = os.path.join(sourcemods_path, batch_file_name)

            try:
                with open(batch_file_path, "w") as batch_file:
                    batch_file.write(batch_content)
                messagebox.showinfo("Success", f"Batch file generated successfully at {batch_file_path}.")
                handle_bat_to_exe(batch_file_path, sourcemods_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error writing batch file: {str(e)}")

        else:
            messagebox.showerror("Error", "Unsupported operating system.")
    else:
        messagebox.showwarning("Warning", "Please select all paths and SDK.")

# Function to download BatToExe and convert the batch file
def handle_bat_to_exe(bat_file_path, sourcemods_path):
    bat2exe_dir = os.path.join(sourcemods_path, "bat2exe")
    if not os.path.exists(bat2exe_dir):
        os.makedirs(bat2exe_dir)

    bat_to_exe_path = os.path.join(bat2exe_dir, "bat2exe.exe")

    if not os.path.exists(bat_to_exe_path):
        if not extract_bat_to_exe(bat_to_exe_path):
            return

    time.sleep(2)

    exe_file_name = os.path.splitext(os.path.basename(bat_file_path))[0] + ".exe"
    exe_file_path = os.path.join(sourcemods_path, exe_file_name)

    try:
        subprocess.run(
            [
                bat_to_exe_path,
                "/bat", bat_file_path,
                "/exe", exe_file_path,
                "/quiet"
            ],
            check=True
        )
        messagebox.showinfo("Success", f"Executable generated successfully at {exe_file_path}.")
        enable_run_button(exe_file_path)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error during conversion: {str(e)}")
    finally:
        if os.path.exists(bat2exe_dir):
            time.sleep(3)
            shutil.rmtree(bat2exe_dir)
            messagebox.showinfo("Success", f"Temporary folders removed at {bat2exe_dir}.")
        if os.path.exists(bat_file_path):
            os.remove(bat_file_path)

# Function to enable the Run button if the executable exists
def enable_run_button(exe_file_path):
    if os.path.exists(exe_file_path):
        run_button.config(state=tk.NORMAL)

# Function to run the generated executable
def run_exe():
    sourcemods_path = sourcemods_var.get()
    mod_folder = os.path.basename(mod_var.get())
    os_type = platform.system()

    if not sourcemods_path or not mod_folder:
        messagebox.showwarning("Warning", "Please fill in all fields before running.")
        return

    if os_type == "Windows":
        exe_file_path = os.path.join(sourcemods_path, f"{mod_folder}.exe")
        if os.path.exists(exe_file_path):
            try:
                subprocess.run([exe_file_path], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to run the executable: {str(e)}")
        else:
            messagebox.showwarning("Warning", "The executable does not exist. Please generate it first.")
    else:
        messagebox.showwarning("Warning", "This feature is currently only supported on Windows.")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Creating the main window
root = tk.Tk()
root.title("Sourcemod Executable Generator")
root.geometry("450x245")
root.config(bg="black")

root.iconbitmap(resource_path("app_icon.ico"))

bg_image = Image.open(resource_path("background_art.jpg"))
bg_image = bg_image.resize((450, 245), Image.Resampling.LANCZOS)
bg_image_tk = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_image_tk, bd=0)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

steam_label = tk.Label(root, text="Steam Path:", bg="black", fg="white")
steam_label.place(x=10, y=10)
steam_entry = tk.Entry(root, width=30, bg="white", fg="black")
steam_entry.place(x=120, y=10)
steam_button = tk.Button(root, text="Steam Path", command=locate_steam, bg="gray", fg="white")
steam_button.place(x=330, y=10)

sourcemods_label = tk.Label(root, text="Sourcemods Path:", bg="black", fg="white")
sourcemods_label.place(x=10, y=50)
sourcemods_var = tk.StringVar()
sourcemods_entry = tk.Entry(root, textvariable=sourcemods_var, width=30, bg="white", fg="black")
sourcemods_entry.place(x=120, y=50)
sourcemods_button = tk.Button(root, text="Sourcemods Path", command=locate_sourcemods, bg="gray", fg="white")
sourcemods_button.place(x=330, y=50)

mod_label = tk.Label(root, text="Mod Path:", bg="black", fg="white")
mod_label.place(x=10, y=90)
mod_var = tk.StringVar()
mod_entry = tk.Entry(root, textvariable=mod_var, width=30, bg="white", fg="black")
mod_entry.place(x=120, y=90)
mod_button = tk.Button(root, text="Mod Path", command=locate_mod, bg="gray", fg="white")
mod_button.place(x=330, y=90)

sdk_label = tk.Label(root, text="Select SDK:", bg="black", fg="white")
sdk_label.place(x=10, y=125)
sdk_dict = {sdk[0]: sdk[1] for sdk in SDK_LIST}
sdk_names = [sdk[0] for sdk in SDK_LIST]
sdk_var = tk.StringVar(root)
sdk_var.set(sdk_names[0])
sdk_menu = tk.OptionMenu(root, sdk_var, *sdk_names)
sdk_menu.config(bg="black", fg="white", highlightbackground="black", highlightcolor="black", borderwidth=0)
sdk_menu.place(x=120, y=125)

generate_button = tk.Button(root, text="Generate", command=generate_launcher, bg="gray", fg="white")
generate_button.place(x=120, y=170)

run_button = tk.Button(root, text="Run", command=run_exe, state=tk.DISABLED, bg="gray", fg="white")
run_button.place(x=190, y=170)

sdk_help_button = tk.Button(root, text="What SDK?", command=open_sdk_help, bg="gray", fg="white")
sdk_help_button.place(x=330, y=130)

root.mainloop()