import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import requests

# List of SDKs to choose from, with names and corresponding numeric values
SDK_LIST = [
    ("Source SDK 2006", "215"),
    ("Source SDK 2007", "218"),
    ("Source SDK Base 2013 MP", "243750"),
    ("Source SDK Base 2013 SP", "243730"),
]

# URL for BatToExeConverter.exe download (replace with a valid URL if available)
BAT2EXE_URL = "https://github.com/HLSourceHub/sourcelibraryfix/raw/refs/heads/main/bat2exe.exe"  # Replace with actual URL

# Function to download BatToExeConverter.exe
def download_bat_to_exe(destination):
    try:
        response = requests.get(BAT2EXE_URL, stream=True)
        response.raise_for_status()  # Raise an error for HTTP issues
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download BatToExeConverter: {str(e)}")
        return False

# Function to locate Steam directory
def locate_steam():
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

# Function to generate batch file
def generate_batch():
    steam_path = steam_entry.get()
    sourcemods_path = sourcemods_var.get()
    mod_path = mod_var.get()
    selected_sdk_id = sdk_dict[sdk_var.get()]  # Get the numeric SDK ID based on the selected name

    if steam_path and sourcemods_path and mod_path and selected_sdk_id:
        if not os.path.exists(steam_path):
            messagebox.showerror("Error", "Invalid Steam path.")
            return
        if not os.path.basename(sourcemods_path).lower() == "sourcemods":
            messagebox.showerror("Error", "Please select a 'sourcemods' folder.")
            return

        mod_folder = os.path.basename(mod_path)

        # Construct the batch file content
        steam_exe_name = "Steam.exe"
        batch_content = f'"{steam_path}\\{steam_exe_name}" -applaunch {selected_sdk_id} -game "{mod_path}"'

        # Save .bat file to the sourcemods folder
        batch_file_name = f"{mod_folder}.bat"
        batch_file_path = os.path.join(sourcemods_path, batch_file_name)

        try:
            with open(batch_file_path, "w") as batch_file:
                batch_file.write(batch_content)
            messagebox.showinfo("Success", f"Batch file generated successfully at {batch_file_path}.")
            # Call function to download BatToExe and convert the batch file
            handle_bat_to_exe(batch_file_path, sourcemods_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error writing batch file: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Please select all paths and SDK.")

# Function to download BatToExe and convert the batch file
def handle_bat_to_exe(bat_file_path, sourcemods_path):
    bat_to_exe_path = os.path.join(sourcemods_path, "bat2exe.exe")

    # Check if BatToExeConverter needs to be downloaded
    if not os.path.exists(bat_to_exe_path):
        if not download_bat_to_exe(bat_to_exe_path):
            return

    # Construct output .exe path
    exe_file_name = os.path.splitext(os.path.basename(bat_file_path))[0] + ".exe"
    exe_file_path = os.path.join(sourcemods_path, exe_file_name)

    try:
        # Run BatToExeConverter in silent mode
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
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error during conversion: {str(e)}")
    finally:
        # Clean up: Remove BatToExeConverter and batch file
        if os.path.exists(bat_to_exe_path):
            os.remove(bat_to_exe_path)
        if os.path.exists(bat_file_path):
            os.remove(bat_file_path)

# Creating the main window
root = tk.Tk()
root.title("Batch File Generator")
root.geometry("450x300")

# Steam Path Label and Entry
steam_label = tk.Label(root, text="Steam Path:")
steam_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
steam_entry = tk.Entry(root, width=30)
steam_entry.grid(row=0, column=1, padx=10, pady=10)
steam_button = tk.Button(root, text="Steam Path", command=locate_steam)
steam_button.grid(row=0, column=2, padx=10, pady=10)

# Sourcemods Path Label and Entry
sourcemods_label = tk.Label(root, text="Sourcemods Path:")
sourcemods_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
sourcemods_var = tk.StringVar()
sourcemods_entry = tk.Entry(root, textvariable=sourcemods_var, width=30)
sourcemods_entry.grid(row=1, column=1, padx=10, pady=10)
sourcemods_button = tk.Button(root, text="Sourcemods Path", command=locate_sourcemods)
sourcemods_button.grid(row=1, column=2, padx=10, pady=10)

# Mod Path Label and Entry
mod_label = tk.Label(root, text="Mod Path:")
mod_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
mod_var = tk.StringVar()
mod_entry = tk.Entry(root, textvariable=mod_var, width=30)
mod_entry.grid(row=2, column=1, padx=10, pady=10)
mod_button = tk.Button(root, text="Mod Path", command=locate_mod)
mod_button.grid(row=2, column=2, padx=10, pady=10)

# SDK Dropdown List
sdk_label = tk.Label(root, text="Select SDK:")
sdk_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
sdk_dict = {sdk[0]: sdk[1] for sdk in SDK_LIST}
sdk_names = [sdk[0] for sdk in SDK_LIST]
sdk_var = tk.StringVar(root)
sdk_var.set(sdk_names[0])
sdk_menu = tk.OptionMenu(root, sdk_var, *sdk_names)
sdk_menu.grid(row=3, column=1, padx=10, pady=10)

# Generate Button
generate_button = tk.Button(root, text="Generate", command=generate_batch)
generate_button.grid(row=4, column=1, pady=20)

# Run the Tkinter event loop
root.mainloop()
