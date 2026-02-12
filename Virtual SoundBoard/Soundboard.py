import customtkinter as ctk
from tkinter import simpledialog, messagebox, filedialog, Menu
import pygame
import os
import json

# Initialize pygame mixer
pygame.mixer.init()

# Define your color palette (Black and Yellow Theme)
PRIMARY_COLOR = "#FFD700"
SECONDARY_COLOR = "#1E1E1E"  # Dark Gray (almost black)
ACCENT_COLOR = "#FF9F1C"    # Yellow (same as stop button)
TEXT_COLOR = "#FFFFFF"      # White for better contrast on dark
HOVER_COLOR = "#B8860B"    # Dark Goldenrod (darker yellow hover)
ADD_TILE_BG = "#333333"      # Darker Gray for add tile
ADD_TILE_HOVER = "#555555" # Slightly lighter gray hover
TILE_BG = "#2C2C2C"        # Medium Dark Gray for tiles
TILE_TEXT = "#EEEEEE"      # Light Gray for tile text

class SoundBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Soundboard")

        # Set default window size and make it resizable
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        self.root.configure(bg=SECONDARY_COLOR)

        # Load existing sounds and key bindings
        self.sound_buttons_data = self.load_data("sounds.json")
        self.key_bindings = self.load_data("key_bindings.json")
        self.tile_widgets = {}

        # Frame for tiles with grid layout
        self.tile_frame = ctk.CTkFrame(root, fg_color=SECONDARY_COLOR)
        self.tile_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.tile_frame.grid_columnconfigure(list(range(6)), weight=1)
        self.tile_row = 0
        self.tile_col = 0
        self.num_columns = 6

        # Style for the "New" tile
        self.new_tile_style = {
            "fg_color": ADD_TILE_BG,
            "hover_color": ADD_TILE_HOVER,
            "text_color": TEXT_COLOR,
            "corner_radius": 8,
            "width": 70,
            "height": 70
        }
        self.tile_style = {
            "fg_color": TILE_BG,
            "text_color": TILE_TEXT,
            "hover_color": HOVER_COLOR,
            "corner_radius": 8,
            "width": 70,
            "height": 70
        }

        # Create "Add New Tile" button
        self.add_new_tile_button = ctk.CTkButton(
            self.tile_frame,
            text="New",
            compound="top",
            font=ctk.CTkFont(size=12, weight="bold"),
            **self.new_tile_style,
            command=self.prompt_add_sound
        )
        self.add_new_tile_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.new_tile_key_label = ctk.CTkLabel(self.tile_frame, text="", text_color=TEXT_COLOR, font=ctk.CTkFont(size=10))
        self.new_tile_key_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
        self.update_new_tile_key_display()
        self.update_new_tile_interaction() # Bind right-click for the 'New' tile

        self.tile_row = 0
        self.tile_col = 1

        # Create existing sound tiles
        first_tile = True
        for original_name, path in self.sound_buttons_data.items():
            name = "New" if first_tile else original_name
            new_tile = self.create_sound_tile(name, path, self.tile_style)
            self.tile_widgets[name] = new_tile
            if first_tile:
                first_tile = False
            self.tile_col += 1
            if self.tile_col >= self.num_columns:
                self.tile_col = 0
                self.tile_row += 2
                self.add_new_tile_button.grid(row=self.tile_row, column=0, padx=5, pady=5, sticky="nsew")
                self.new_tile_key_label.grid(row=self.tile_row + 1, column=0, padx=5, pady=(0, 5), sticky="ew")
                self.tile_col = 1

        # Volume control
        volume_style = {"fg_color": SECONDARY_COLOR, "progress_color": PRIMARY_COLOR, "button_color": PRIMARY_COLOR, "button_hover_color": HOVER_COLOR}
        self.volume_scale = ctk.CTkSlider(root, from_=0, to=1, number_of_steps=10, command=self.set_volume, **volume_style)
        self.volume_scale.set(0.5)
        self.volume_scale.pack(pady=20, padx=20, fill="x")

        # Stop button
        stop_button_style = {"fg_color": ACCENT_COLOR, "text_color": TEXT_COLOR, "hover_color": "#FFB347"}
        self.stop_button = ctk.CTkButton(root, text="Stop Sound", fg_color=ACCENT_COLOR, text_color=TEXT_COLOR, hover_color="#FFB347", command=self.stop_sound)
        self.stop_button.pack(pady=20, padx=20, fill="x")

        # Bind keys
        self.bind_keys()

        # Configure row weights
        for i in range(10):
            self.tile_frame.grid_rowconfigure(i * 2, weight=1)
            self.tile_frame.grid_rowconfigure(i * 2 + 1, weight=0)

        # Update tile sizes on resize
        self.root.bind("<Configure>", self.on_window_resize)

    def update_new_tile_key_display(self):
        """Updates the key binding display below the 'New' tile."""
        if "New" in self.key_bindings and self.key_bindings["New"]:
            self.new_tile_key_label.configure(text=f"[{self.key_bindings['New']}]")
        else:
            self.new_tile_key_label.configure(text="")

    def update_new_tile_interaction(self):
        """Binds right-click to the 'New' tile to show its context menu."""
        self.add_new_tile_button.bind("<Button-3>", self.show_context_menu_new_tile)

    def show_context_menu_new_tile(self, event):
        """Displays the right-click context menu for the 'New' tile."""
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Edit Key Binding", command=self.prompt_rebind_new_tile)
        context_menu.add_command(label="Delete Key Binding", command=self.delete_key_binding_new_tile)
        context_menu.tk_popup(event.x_root, event.y_root)

    def prompt_rebind_new_tile(self):
        """Prompts the user to rebind the 'New' tile action."""
        current_binding = self.key_bindings.get("New", "None")
        new_binding = simpledialog.askstring("Rebind 'New' Tile", f"Enter new key binding for the 'New' tile (current: '{current_binding}'):")
        if new_binding is not None:
            if new_binding:
                if new_binding in [v for k, v in self.key_bindings.items() if k != "New"]:
                    messagebox.showerror("Error", f"Key '{new_binding}' is already assigned to a sound tile.")
                    return
                self.key_bindings["New"] = new_binding
            elif "New" in self.key_bindings:
                del self.key_bindings["New"]
                messagebox.showinfo("Info", "Key binding for 'New' tile removed.")
            self.save_data("key_bindings.json", self.key_bindings)
            try:
                self.root.unbind(current_binding)
            except Exception as e:
                print(f"Error unbinding key '{current_binding}' for 'New' tile: {e}")
            if new_binding:
                try:
                    self.root.bind(new_binding, self.prompt_add_sound)
                except Exception as e:
                    messagebox.showerror("Key Binding Error", f"Could not bind key '{new_binding}' for 'New' tile: {e}")
            self.update_new_tile_key_display()

    def delete_key_binding_new_tile(self):
        """Deletes the key binding for the 'New' tile."""
        if "New" in self.key_bindings:
            key_to_unbind = self.key_bindings.pop("New")
            self.save_data("key_bindings.json", self.key_bindings)
            try:
                self.root.unbind(key_to_unbind)
            except Exception as e:
                print(f"Error unbinding key '{key_to_unbind}' for 'New' tile: {e}")
            self.update_new_tile_key_display()
            messagebox.showinfo("Info", f"Key binding '{key_to_unbind}' for 'New' tile deleted.")
        else:
            messagebox.showinfo("Info", "No key binding assigned to the 'New' tile.")

    def on_window_resize(self, event):
        """Adjust tile sizes to maintain a square aspect ratio."""
        tile_width = (self.tile_frame.winfo_width() - 20) // self.num_columns
        tile_height = tile_width
        self.add_new_tile_button.configure(width=tile_width, height=tile_height)
        for tile in self.tile_widgets.values():
            if isinstance(tile, tuple):
                tile_widget, _ = tile
                tile_widget.configure(width=tile_width, height=tile_height)
            else:
                tile.configure(width=tile_width, height=tile_height)

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return {}

    def save_data(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f)

    def prompt_add_sound(self):
        """Opens file explorer and adds a new sound tile."""
        file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.mp3;*.wav;*.ogg")])
        if file_path:
            file_name_with_ext = os.path.basename(file_path)
            file_name = os.path.splitext(file_name_with_ext)[0]
            self.add_new_sound_tile(file_name, file_path)

    def add_new_sound_tile(self, name, path):
        """Adds a new sound tile to the grid and saves its data."""
        new_tile = self.create_sound_tile(name, path, self.tile_style)
        self.tile_widgets[name] = new_tile
        self.sound_buttons_data[name] = path

        self.save_data("sounds.json", self.sound_buttons_data)
        self.regrid_tiles()

    def create_sound_tile(self, name, path, style):
        tile = ctk.CTkButton(self.tile_frame, text=name, compound="top", font=ctk.CTkFont(size=12, weight="bold"), command=lambda: self.play_sound(path) if path else None, **style)
        tile.bind("<Button-3>", lambda event: self.show_context_menu(event, name, tile))
        tile.bind("<Enter>", lambda event: self.on_enter(tile))
        tile.bind("<Leave>", lambda event: self.on_leave(tile))
        row = self.tile_row * 2
        tile.grid(row=row, column=self.tile_col, padx=5, pady=5, sticky="nsew")
        key_label = ctk.CTkLabel(self.tile_frame, text="", text_color=TEXT_COLOR, font=ctk.CTkFont(size=10))
        key_label.grid(row=row + 1, column=self.tile_col, padx=5, pady=(0, 5), sticky="ew")
        self.tile_widgets[name] = (tile, key_label)
        self.update_key_label(name)
        if name in self.key_bindings and path:
            try:
                self.root.bind(self.key_bindings[name], lambda event, path=file_path: self.play_sound(path))
            except Exception as e:
                messagebox.showerror("Key Binding Error", f"Could not bind key '{self.key_bindings[name]}': {e}")
        return (tile, key_label)

    def update_key_label(self, name):
        """Updates the key binding label below a tile."""
        if name in self.tile_widgets and isinstance(self.tile_widgets[name], tuple) and len(self.tile_widgets[name]) == 2:
            tile, label = self.tile_widgets[name]
            if name in self.key_bindings and self.key_bindings[name]:
                label.configure(text=f"[{self.key_bindings[name]}]")
            else:
                label.configure(text="")
        elif name == "New":
            self.update_new_tile_key_display()

    def show_context_menu(self, event, tile_name, tile_widget):
        """Displays the right-click context menu for sound tiles."""
        context_menu = Menu(self.root, tearoff=0)
        context_menu.add_command(label="Edit Name", command=lambda: self.prompt_edit_name(tile_widget, tile_name))
        context_menu.add_command(label="Edit Key Binding", command=lambda: self.edit_key_binding(tile_name))
        context_menu.add_command(label="Delete Key Binding", command=lambda: self.delete_key_binding(tile_name, tile_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Delete Tile", command=lambda: self.confirm_delete_tile(tile_name, tile_widget))

        context_menu.tk_popup(event.x_root, event.y_root)

    def prompt_edit_name(self, tile_widget, old_name):
        """Prompts for a new name and updates the tile."""
        new_name = simpledialog.askstring("Edit Tile Name", "Enter new name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            if old_name in self.tile_widgets:
                widget_info = self.tile_widgets.pop(old_name)
                if isinstance(widget_info, tuple) and len(widget_info) == 2:
                    tile, label = widget_info
                    tile.configure(text=new_name)
                    self.tile_widgets[new_name] = (tile, label)
                else:
                    self.tile_widgets[new_name] = widget_info
            self.sound_buttons_data[new_name] = self.sound_buttons_data.pop(old_name)
            if old_name in self.key_bindings:
                self.key_bindings[new_name] = self.key_bindings.pop(old_name)
            self.save_data("sounds.json", self.sound_buttons_data)
            self.save_data("key_bindings.json", self.key_bindings)
            self.bind_keys()
            self.regrid_tiles()

    def edit_key_binding(self, tile_name):
        """Allows the user to change the key binding for a sound tile."""
        current_binding = self.key_bindings.get(tile_name, "None")
        new_binding = simpledialog.askstring("Edit Key Binding", f"Enter new key binding for '{tile_name}' (current: '{current_binding}'):")
        if new_binding is not None:
            if new_binding:
                if new_binding in [v for k, v in self.key_bindings.items() if k != "New" and k != tile_name]:
                    messagebox.showerror("Error", f"Key '{new_binding}' is already assigned to another action.")
                    return
                self.key_bindings[tile_name] = new_binding
            elif tile_name in self.key_bindings:
                del self.key_bindings[tile_name]
                messagebox.showinfo("Info", f"Key binding for '{tile_name}' removed.")
            self.save_data("key_bindings.json", self.key_bindings)
            self.unbind_key(tile_name)
            file_path = self.sound_buttons_data.get(tile_name)
            if new_binding and file_path:
                try:
                    self.root.bind(new_binding, lambda event, path=file_path: self.play_sound(path))
                except Exception as e:
                    messagebox.showerror("Key Binding Error", f"Could not bind key '{new_binding}' for '{tile_name}': {e}")
            self.update_key_label(tile_name)

    def delete_key_binding(self, tile_name, tile_widget):
        """Deletes the key binding for a tile."""
        if tile_name in self.key_bindings:
            key_to_unbind = self.key_bindings.pop(tile_name)
            self.save_data("key_bindings.json", self.key_bindings)
            self.unbind_key(tile_name)
            self.update_key_label(tile_name)
            messagebox.showinfo("Info", f"Key binding '{key_to_unbind}' for '{tile_name}' deleted.")
        else:
            messagebox.showinfo("Info", f"No key binding assigned to '{tile_name}'.")

    def confirm_delete_tile(self, name, tile):
        """Confirms before deleting a tile."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            self.delete_tile(name, tile)

    def on_enter(self, tile):
        tile.configure(fg_color=HOVER_COLOR)
        if tile == self.add_new_tile_button:
            tile.configure(fg_color=ADD_TILE_HOVER)

    def on_leave(self, tile):
        tile.configure(fg_color=TILE_BG)
        if tile == self.add_new_tile_button:
            tile.configure(fg_color=ADD_TILE_BG)

    def play_sound(self, file_path):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except pygame.error as e:
            messagebox.showerror("Playback Error", f"Could not play sound '{os.path.basename(file_path)}': {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred during playback: {e}")

    def stop_sound(self):
        pygame.mixer.music.stop()

    def delete_tile(self, name, tile):
        """Deletes a sound tile and its associated data."""
        if name in self.tile_widgets:
            widget_info = self.tile_widgets.pop(name)
            if isinstance(widget_info, tuple) and len(widget_info) == 2:
                tile_widget, key_label = widget_info
                tile_widget.destroy()
                key_label.destroy()
            else:
                widget_info.destroy()
        if name in self.sound_buttons_data:
            del self.sound_buttons_data[name]
        if name in self.key_bindings:
            del self.key_bindings[name]
        self.save_data("sounds.json", self.sound_buttons_data)
        self.save_data("key_bindings.json", self.key_bindings)
        self.unbind_key(name)
        self.regrid_tiles()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def bind_keys(self):
        for name, key in self.key_bindings.items():
            if name in self.sound_buttons_data:
                file_path = self.sound_buttons_data[name]
                try:
                    self.root.bind(key, lambda event, path=file_path: self.play_sound(path))
                except Exception as e:
                    messagebox.showerror("Key Binding Error", f"Could not bind key '{key}' for '{name}': {e}")
            if name == "New":
                try:
                    self.root.bind(key, self.prompt_add_sound)
                except Exception as e:
                    messagebox.showerror("Key Binding Error", f"Could not bind key '{key}' for 'New' tile: {e}")
        self.update_new_tile_key_display()
        for name in self.tile_widgets:
            self.update_key_label(name)

    def unbind_key(self, name):
        if name in self.key_bindings:
            key = self.key_bindings[name]
            try:
                self.root.unbind(key)
            except Exception as e:
                print(f"Error unbinding key '{key}' for '{name}': {e}")

    def regrid_tiles(self):
        for widget in self.tile_frame.winfo_children():
            widget.grid_forget()

        self.tile_row = 0
        self.tile_col = 0
        tile_width = (self.tile_frame.winfo_width() - 20) // self.num_columns
        tile_height = tile_width
        self.add_new_tile_button.configure(width=tile_width, height=tile_height, text="New", compound="top")
        self.add_new_tile_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.new_tile_key_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
        self.update_new_tile_key_display()
        self.update_new_tile_interaction()

        self.tile_row = 0
        self.tile_col = 1
        for name, widgets in self.tile_widgets.items():
            if isinstance(widgets, tuple) and len(widgets) == 2:
                tile, key_label = widgets
                tile.configure(width=tile_width, height=tile_height, text=name, compound="top")
                row = self.tile_row * 2
                tile.grid(row=row, column=self.tile_col, padx=5, pady=5, sticky="nsew")
                key_label.grid(row=row + 1, column=self.tile_col, padx=5, pady=(0, 5), sticky="ew")
                self.update_key_label(name)
                self.tile_col += 1
                if self.tile_col >= self.num_columns:
                    self.tile_col = 0
                    self.tile_row += 1
                    self.add_new_tile_button.grid(row=self.tile_row * 2, column=0, padx=5, pady=5, sticky="nsew")
                    self.new_tile_key_label.grid(row=self.tile_row * 2 + 1, column=0, padx=5, pady=(0, 5), sticky="ew")
                    self.tile_col = 1
            elif isinstance(widgets, ctk.CTkButton):
                widgets.configure(width=tile_width, height=tile_height, text=name, compound="top")
                row = self.tile_row * 2
                widgets.grid(row=row, column=self.tile_col, padx=5, pady=5, sticky="nsew")
                self.tile_col += 1
                if self.tile_col >= self.num_columns:
                    self.tile_col = 0
                    self.tile_row += 1
                    self.add_new_tile_button.grid(row=self.tile_row * 2, column=0, padx=5, pady=5, sticky="nsew")
                    self.new_tile_key_label.grid(row=self.tile_row * 2 + 1, column=0, padx=5, pady=(0, 5), sticky="ew")
                    self.tile_col = 1

        # Ensure add button is placed even if no other tiles exist
        if not self.tile_widgets:
            self.add_new_tile_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
            self.new_tile_key_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")

        # Ensure row weights are configured for vertical expansion
        for i in range(self.tile_row + 1):
            self.tile_frame.grid_rowconfigure(i * 2, weight=1)
            self.tile_frame.grid_rowconfigure(i * 2 + 1, weight=0)



if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = SoundBoardApp(root)
    root.mainloop()
