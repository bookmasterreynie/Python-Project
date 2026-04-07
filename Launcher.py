import tkinter as tk
from launch import launch_minecraft  # Your existing launcher script
from pathlib import Path
import os
import json
from PIL import Image, ImageTk

MC_DIR = Path(os.environ["USERPROFILE"]) / "AppData/Roaming/.minecraft"
launcher_profiles_path = MC_DIR / "launcher_profiles.json"

ACCOUNT_FILE = Path("launcher_account.json")
def get_username():
    if ACCOUNT_FILE.exists():
        with open(ACCOUNT_FILE, "r") as f:
            return json.load(f).get("username", "Player")
    return "Player"

def set_username(name):
    with open(ACCOUNT_FILE, "w") as f:
        json.dump({"username": name}, f)

def save_username(name):
    with open("launcher_account.json", "w") as f:
        json.dump({"username": name}, f)

def get_versions():
    """Return a sorted list of available Minecraft versions."""
    return sorted([v.name for v in (MC_DIR / "versions").iterdir() if v.is_dir()])

def get_versions_by_type(version_type):
    """Filter versions for Vanilla / Forge / OptiFine by name convention."""
    all_versions = get_versions()
    if version_type == "Vanilla":
        return [v for v in all_versions if "-" not in v]  # crude check: no dash
    elif version_type == "Forge":
        return [v for v in all_versions if "forge" in v.lower() or "-" in v]
    elif version_type == "OptiFine":
        return [v for v in all_versions if "optifine" in v.lower()]
    return []

def center_window(window, width, height):
    """
    Centers a Tkinter window on the screen.

    :param window: The Tkinter root or Toplevel window
    :param width: Desired window width
    :param height: Desired window height
    """
    # Apply the size
    window.geometry(f"{width}x{height}")

    # Make sure Tkinter knows the actual window size
    window.update_idletasks()

    # Screen size
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate top-left coordinates for centering
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Re-apply geometry with offsets
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_gui():
    root = tk.Tk()
    center_window(root, 1280, 750)
    root.title("Minecraft Launcher")
    root.geometry("1200x750")
    root.configure(bg="#2b2b2b")
    root.resizable(False, False)  # False for width, False for height

    # Main container frame
    main_container = tk.Frame(root)
    main_container.pack(fill="both", expand=True)

    # Sidebar (1/6 width)
    sidebar_frame = tk.Frame(main_container, bg="#1c1c1c")
    sidebar_frame.pack(side="left", fill="y")

    # Main area (5/6 width)
    main_frame = tk.Frame(main_container, bg="#2b2b2b")
    main_frame.pack(side="right", fill="both", expand=True)

    main_container.update_idletasks()
    sidebar_frame.config(width=root.winfo_width() // 6)

    grass_img = Image.open("grass block.png")
    grass_img = grass_img.resize((50, 50), Image.LANCZOS)
    grass_photo = ImageTk.PhotoImage(grass_img)

    # Username/account
    current_username = tk.StringVar(value=get_username())
    def open_account_menu():
        account_win = tk.Toplevel(root)
        account_win.title("Account Settings")
        account_win.configure(bg="#2b2b2b")
        account_win.resizable(False, False)

        tk.Label(account_win,
                 text="Minecraft Username:",
                 fg="#ffffff",
                 bg="#2b2b2b",
                 font=("Segoe UI", 12)).pack(padx=10, pady=10)

        username_entry = tk.Entry(account_win,
                                  textvariable=current_username,
                                  font=("Segoe UI", 12))
        username_entry.pack(padx=10, pady=5)

        def save_and_close():
            new_name = username_entry.get().strip()

            # Basic Minecraft validation
            if not (1 <= len(new_name) <= 16) or not new_name.replace("_", "").isalnum():
                tk.messagebox.showerror("Invalid Username",
                                        "Username must be 1–16 characters.\nLetters, numbers, and _ only.")
                return

            set_username(new_name)          # Save to JSON
            current_username.set(new_name)  # Update UI instantly
            account_win.destroy()           # Close window

        tk.Button(account_win,
                  text="Save",
                  bg="#128947",
                  fg="#ffffff",
                  activebackground="#0f6d39",
                  command=save_and_close).pack(pady=10)

    # Sidebar label, clickable
    username_label = tk.Label(sidebar_frame, textvariable=current_username,
                              fg="#ffffff", bg="#1c1c1c", font=("Segoe UI", 16, "bold"), cursor="hand2")
    username_label.pack(pady=20)
    username_label.bind("<Button-1>", lambda e: open_account_menu())

    tk.Label(sidebar_frame, text="Launch Type:", fg="#ffffff", bg="#1c1c1c",
             font=("Segoe UI", 14, "bold")).pack(pady=10)

    for t in ["Vanilla", "Forge", "OptiFine"]:

        # Frame to hold button + dropdown
        category_frame = tk.Frame(sidebar_frame, bg="#1c1c1c")
        category_frame.pack(pady=5)

        # Dropdown frame (hidden initially)
        dropdown_frame = tk.Frame(category_frame, bg="#111111")

        def toggle_dropdown(category=t, frame=dropdown_frame):
            if frame.winfo_ismapped():
                frame.pack_forget()  # collapse
            else:
                # Clear old buttons
                for widget in frame.winfo_children():
                    widget.destroy()

                versions = get_versions_by_type(category)

                for v in versions:
                    tk.Button(
                        frame,
                        text=v,
                        anchor="w",
                        font=("Segoe UI", 10),
                        bg="#111111",
                        fg="#ffffff",
                        activebackground="#333333",
                        relief="flat",
                        width=10,
                        command=lambda version=v: current_version.set(version)
                    ).pack(fill="x", padx=15, pady=2)

                frame.pack(padx=25, pady=1)

        # Category button
        tk.Button(
            category_frame,
            text=t,
            width=12,
            font=("Segoe UI", 12),
            bg="#2b2b2b",
            fg="#ffffff",
            activebackground="#333333",
            relief="raised",
            bd=2,
            highlightthickness=0,
            command=toggle_dropdown
        ).pack(padx=25, pady=1)

    # Load image
    original_image = Image.open("background.png")

    canvas = tk.Canvas(main_frame, bg="#2b2b2b", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def redraw_image(event):
        canvas.delete("all")

        # Keep image aspect ratio based on original height
        aspect_ratio = original_image.width / original_image.height

        # Stretch image to fill canvas width
        new_width = event.width
        new_height = int(new_width / aspect_ratio)

        # Optionally, limit vertical size so it doesn't overflow
        max_height = int(event.height * 0.8)
        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)

        resized = original_image.resize((new_width, new_height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(resized)

        # Store reference
        canvas.image = bg_photo
        canvas.grass = grass_photo

        # Place top-left horizontally
        canvas.create_image(0, 90, anchor="nw", image=bg_photo)
        canvas.create_image(27, 714, image=grass_photo)



    root.title("Minecraft Launcher")

    current_version = tk.StringVar(value="No version selected")
    version_label = tk.Label(canvas, textvariable=current_version, fg="#ffffff", bg="#2b2b2b",
                             font=("Arial", 12))
    release_version = tk.StringVar(value="Release")
    release_label = tk.Label(canvas, textvariable=release_version, fg="#ffffff", bg="#2b2b2b",
                             font=("Arial", 12, "bold"))

    play_btn = tk.Button(
        canvas,
        text="PLAY",
        font=("Arial", 18, "bold"),
        bg="#128947",
        fg="#ffffff",
        activebackground="#0f6d39",
        width=20,
        height=2,
        command=lambda: launch_selected_version(current_version.get())
    )

    def place_overlay_widgets(event):
        version_label.place(x=55, y=720)
        play_btn.place(x=500, y=707, anchor="center")
        release_label.place(x=55, y=700)

    canvas.bind("<Configure>", redraw_image)
    canvas.bind("<Configure>", place_overlay_widgets, add="+")

    # Launch function
    def launch_selected_version(version):
        if version == "No version selected":
            tk.messagebox.showwarning("No version", "Select a version first!")
        else:
            launch_minecraft(version)

    root.mainloop()

if __name__ == "__main__":
    create_gui()