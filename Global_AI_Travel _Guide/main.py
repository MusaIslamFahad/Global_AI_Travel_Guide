import tkinter as tk
from tkinter import ttk, scrolledtext
from tkintermapview import TkinterMapView
from utils.ai_helper import ask_ai, parse_ai_response
from utils.map_helper import add_landmark_marker, clear_markers
from utils.image_helper import get_landmark_image
from geopy.geocoders import Nominatim
import threading

from config import LIGHT_BG, LIGHT_FG, DARK_BG, DARK_FG, BUTTON_BLUE, BUTTON_ACTIVE_BLUE, DARK_BUTTON_BLUE, DARK_BUTTON_ACTIVE, LIGHT_TILE_URL, DARK_TILE_URL


# -----------------------------
# GUI Setup
# -----------------------------
root = tk.Tk()
root.title("🌏 Global AI Travel Guide")
root.geometry("1200x700")
root.minsize(900, 600)

geolocator = Nominatim(user_agent="global_travel_guide")
markers = []
images_list = []

current_theme = "light"


# -----------------------------
# Left Chat Frame
# -----------------------------
chat_frame = tk.Frame(root, bg=LIGHT_BG)
chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

input_label = tk.Label(chat_frame, text="Ask me about any city:", font=("Helvetica", 12), bg=LIGHT_BG, fg=LIGHT_FG)
input_label.pack(padx=10, pady=5, anchor="w")

chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=("Helvetica", 11),
                                        bg=LIGHT_BG, fg=LIGHT_FG, insertbackground=LIGHT_FG)
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

user_entry = tk.Entry(chat_frame, font=("Helvetica", 12), bg=LIGHT_BG, fg=LIGHT_FG, insertbackground=LIGHT_FG)
user_entry.pack(padx=10, pady=5, fill=tk.X)

# Actions Dropdown
actions = ["General", "Landmarks", "Nearby Restaurants", "Local Events"]
action_var = tk.StringVar(value=actions[0])
action_dropdown = ttk.OptionMenu(chat_frame, action_var, *actions)
action_dropdown.pack(padx=10, pady=5, fill=tk.X)

# Buttons
ask_button = tk.Button(chat_frame, text="Ask AI", width=20, bg=BUTTON_BLUE, fg="white",
                       activebackground=BUTTON_ACTIVE_BLUE, font=("Helvetica", 12))
ask_button.pack(padx=10, pady=5)

clear_button = tk.Button(chat_frame, text="Clear Map", width=20, bg=BUTTON_BLUE, fg="white",
                         activebackground=BUTTON_ACTIVE_BLUE, font=("Helvetica", 12), command=lambda: clear_markers(markers))
clear_button.pack(padx=10, pady=5)

theme_button = tk.Button(chat_frame, text="Toggle Dark/Light Mode", width=25, bg=BUTTON_BLUE, fg="white",
                         activebackground=BUTTON_ACTIVE_BLUE, font=("Helvetica", 12))
theme_button.pack(padx=10, pady=10)


# -----------------------------
# Right Map Frame
# -----------------------------
map_frame = tk.Frame(root, bg=LIGHT_BG)
map_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

map_widget = TkinterMapView(map_frame, width=800, height=700, corner_radius=0)
map_widget.pack(fill=tk.BOTH, expand=True)
map_widget.set_zoom(12)
map_widget.set_tile_server(LIGHT_TILE_URL)


# -----------------------------
# Question Handling
# -----------------------------
def send_question():
    question = user_entry.get().strip()
    action = action_var.get()
    if not question:
        return

    chat_display.insert(tk.END, f"You: {question}\n")
    chat_display.insert(tk.END, "AI is typing...\n")
    chat_display.see(tk.END)

    try:
        ai_response = ask_ai(question, action)
        description, items, city = parse_ai_response(ai_response, action)

        chat_display.delete("end-2l", "end-1l")
        chat_display.insert(tk.END, f"AI: {description}\n\n")
        chat_display.see(tk.END)

        # Center map on city
        if city:
            location = geolocator.geocode(city, timeout=10)
            if location:
                map_widget.set_position(location.latitude, location.longitude)

        # Add markers and images
        for item in items:
            add_landmark_marker(map_widget, item, city)
            img = get_landmark_image(item)
            if img:
                images_list.append(img)
                chat_display.image_create(tk.END, image=img)
                chat_display.insert(tk.END, f"\n{item}\n\n")
            else:
                chat_display.insert(tk.END, f"(No image) {item}\n\n")

        user_entry.delete(0, tk.END)

    except Exception as e:
        chat_display.insert(tk.END, f"Error: {e}\n")
        chat_display.see(tk.END)


def send_question_thread():
    threading.Thread(target=send_question, daemon=True).start()

ask_button.configure(command=send_question_thread)


# -----------------------------
# Theme Toggle
# -----------------------------
def toggle_theme():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        bg_color, fg_color = DARK_BG, DARK_FG
        btn_bg, btn_active = DARK_BUTTON_BLUE, DARK_BUTTON_ACTIVE
        tile_url = DARK_TILE_URL
    else:
        current_theme = "light"
        bg_color, fg_color = LIGHT_BG, LIGHT_FG
        btn_bg, btn_active = BUTTON_BLUE, BUTTON_ACTIVE_BLUE
        tile_url = LIGHT_TILE_URL

    root.configure(bg=bg_color)
    chat_frame.configure(bg=bg_color)
    map_frame.configure(bg=bg_color)

    input_label.configure(bg=bg_color, fg=fg_color)
    chat_display.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    user_entry.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)

    ask_button.configure(bg=btn_bg, activebackground=btn_active)
    clear_button.configure(bg=btn_bg, activebackground=btn_active)
    theme_button.configure(bg=btn_bg, activebackground=btn_active)

    map_widget.set_tile_server(tile_url)
    map_widget.configure(bg=bg_color)
    root.after(100, map_widget.reload)

theme_button.configure(command=toggle_theme)


# -----------------------------
# Run GUI
# -----------------------------
root.mainloop()

