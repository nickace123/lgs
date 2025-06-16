import tkinter as tk
from PIL import Image, ImageTk
from pygame import mixer
import threading
import time
import xml.etree.ElementTree as ET
import sys
import os
import re

# Base files and folders
file0 = "lgs.py"
file1 = "inscoperoms.xml"
file2 = "settings.xml"
folder = "themes"

# Check if base files and folder exist
if not (os.path.isfile(file0) and os.path.isfile(file1) and os.path.isfile(file2) and os.path.isdir(folder)):
    print("Error: One or more required files or folders are missing.")
    sys.exit(1)

print("All required base files and folder exist.")

try:
    tree = ET.parse("settings.xml")
    root = tree.getroot()
    selected_theme_elem = root.find("selected_theme")

    if selected_theme_elem is None or not selected_theme_elem.text.strip():
        print("Error: <selected_theme> is missing or empty in settings.xml.")
        sys.exit(1)

    SELECTED_THEME = selected_theme_elem.text.strip()

except ET.ParseError as e:
    print(f"Error parsing settings.xml: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error reading settings.xml: {e}")
    sys.exit(1)
    
# Theme path
theme_path = os.path.join("themes", SELECTED_THEME)

if not os.path.isdir(theme_path):
    print("Error: selected theme folder missing.")
    sys.exit(1)

print("Selected theme found.")

# Required theme files
required_files = [
    "tag_3do.png", "gamescreen.xml", "3do.png", "tag_nes.png", "dent_systems.png",
    "tag_segacd.png", "button_next.png", "game_default.png", "tag_atari2600.png", "main.xml",
    "tag_zxspectrum.png", "button_prev.png", "hit.mp3", "tag_sega32x.png", "tag_dreamcast.png",
    "tag_saturn.png", "tag_mastersystem.png", "tag_mame.png", "atari2600.png", "target.png",
    "tag_atari7800.png", "tag_megadrive.png", "tag_psx.png", "button_main.png", "dent_main.png",
    "Logo.png", "Logo_mini.png", "game.png", "main.png", "tag_snes.png", "miss.mp3",
    "atari7800.png", "dreamcast.png", "mame-libretro.png", "mastersystem.png",
    "megadrive.png", "nes.png", "psx.png", "saturn.png",
    "sega32x.png", "segacd.png", "snes.png", "zxspectrum.png",
]

# Check for missing theme files
missing_files = [f for f in required_files if not os.path.isfile(os.path.join(theme_path, f))]

if missing_files:
    print("Error: The following required files are missing in the theme folder:")
    for file in missing_files:
        print(f" - {file}")
    sys.exit(1)

print("All required theme files are present.")

# Store theme path as variable
THEME_PATH = theme_path + os.sep  # Adds trailing slash

XML_PATH = f"{THEME_PATH}gamescreen.xml"

if not os.path.exists(XML_PATH):
    print(f"Error: XML file '{XML_PATH}' not found.")
    sys.exit(1)

try:
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    layout = root.find("layout")
    game_name = layout.find("game_name")

    GAME_NAME_X = int(game_name.get("x"))
    GAME_NAME_Y = int(game_name.get("y"))
    GAME_NAME_FONT = eval(game_name.get("font"))  # e.g. "('Arial', 18, 'bold')"
    GAME_NAME_FILL = game_name.get("colour")
    GAME_NAME_WIDTH = int(game_name.get("width"))

except Exception as e:
    print(f"Error loading game_name from XML: {e}")
    sys.exit(1)

print("Loaded game_name settings successfully.")

def load_main_screen(xml_path, show_screen_func):
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found.")
        sys.exit(1)

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        if root.tag != "screen" or root.attrib.get("name") != "main":
            print("Error: Invalid root element or screen name.")
            sys.exit(1)

        bg_attr = root.attrib.get("bg")
        if not bg_attr:
            bg = os.path.join(THEME_PATH, "main.png")
        else:
            # If the bg path is relative, prepend THEME_PATH
            bg = os.path.join(THEME_PATH, bg_attr) if not os.path.isabs(bg_attr) else bg_attr

        screen_data = {
            "bg": bg,
            "zones": []
        }

        for zone in root.findall("zone"):
            try:
                name = zone.attrib["name"]
                image = zone.attrib["image"]
                x1 = int(zone.attrib["x1"])
                y1 = int(zone.attrib["y1"])
                x2 = int(zone.attrib["x2"])
                y2 = int(zone.attrib["y2"])
                target = zone.attrib["target"]

                zone_data = {
                    "name": name,
                    "image": f"{THEME_PATH}{image}",
                    "xy": (x1, y1, x2, y2),
                    "action": lambda target=target: show_screen_func(target)
                }

                screen_data["zones"].append(zone_data)

            except KeyError as e:
                print(f"Error: Missing attribute in zone: {e}")
                sys.exit(1)
            except ValueError as e:
                print(f"Error: Invalid coordinate in zone: {e}")
                sys.exit(1)

        return screen_data

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
        
def parse_inscoperoms_xml(xml_path):
    if not os.path.exists(xml_path):
        print(f"ERROR: XML file not found: {xml_path}")
        sys.exit(1)

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse XML file: {e}")
        sys.exit(1)

    root = tree.getroot()
    inscoperoms = {}

    for system in root.findall("system"):
        try:
            name = system.attrib["name"]
            gamelist = system.find("gamelist").text
            #rompath = system.find("rompath").text
            lightgunroms = []

            for rom in system.find("lightgunroms").findall("rom"):
                rom_name = rom.attrib["name"]
                rom_file = rom.attrib["file"]
                lightgunroms.append({"name": rom_name, "rom": rom_file})

            inscoperoms[name] = {
                "gamelist": gamelist,
                #"rompath": rompath,
                "lightgunroms": lightgunroms
            }

        except Exception as e:
            print(f"ERROR: Malformed entry in XML for system '{name}': {e}")
            sys.exit(1)

    return inscoperoms
class GunMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Gun Menu")
        self.root.geometry("1920x1080")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        mixer.init()

        # Canvas setup
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0)
        self.canvas.pack()

        self.coord_text = self.canvas.create_text(10, 10, anchor='nw', text="", fill="white", font=("Courier", 12))
        self.canvas.bind('<Motion>', self.track_mouse)
        self.canvas.bind('<Button-1>', self.handle_click)

        self.current_screen = ""
        self.bg_image = None
        self.image_id = None
        self.dentmain_image = ImageTk.PhotoImage(Image.open(f"{THEME_PATH}dent_main.png"))
        self.dentsub_image = ImageTk.PhotoImage(Image.open(f"{THEME_PATH}dent_systems.png"))
        self.dents = []

        try:
            target_img = Image.open(f"{THEME_PATH}target.png")
            self.target_image = ImageTk.PhotoImage(target_img)
            self.target_id = self.canvas.create_image(0, 0, anchor='nw', image=self.target_image)
        except Exception as e:
            print(f"Error loading target image: {e}")
            self.target_id = None

        systems = parse_inscoperoms_xml("inscoperoms.xml")
        # Result container
        filtered_systems = {}

        for system, data in systems.items():
            gamelist_path = data.get("gamelist")
            rompath = os.path.dirname(gamelist_path)
            lightgunroms = data.get("lightgunroms", [])
            rom_lookup = {}
            matched_roms = []

            # Load and parse gamelist.xml
            if os.path.exists(gamelist_path):
                try:
                    tree = ET.parse(gamelist_path)
                    root = tree.getroot()

                    for game in root.findall("game"):
                        path = game.findtext("path", "").strip()
                        name = game.findtext("name", "").strip()
                        image = game.findtext("image", "").strip()

                        if path:
                            if path.startswith("./"):
                                rom_file = os.path.join(rompath, os.path.basename(path))
                            else:
                                rom_file = path                            
                            image_path = image.lstrip("./")  # remove ./ if present
                            full_image = (
                                image_path if os.path.isabs(image_path)
                                else os.path.join(rompath, image_path)
                            )
                            rom_lookup[rom_file] = {
                                "name": name,
                                "image": full_image
                            }
                except Exception as e:
                    print(f"[ERROR] Failed to parse XML for {system}: {e}")
            else:
                print(f"[WARN] Missing gamelist.xml for system: {system}")

            # Match lightgunroms against gamelist
            for entry in lightgunroms:
                rom_file = entry["rom"].strip()
                rom_basename = os.path.basename(rom_file)  # strips path and ./

                # Try to match based on basename
                for key in rom_lookup:
                    if os.path.basename(key) == rom_basename:
                        romdata = rom_lookup[key]
                        matched_roms.append({
                            "name": romdata["name"],
                            "rom": key,
                            "image": romdata["image"]
                        })
                        break  # found a match, no need to keep looking

            # Keep the system with filtered roms (could be empty)
            filtered_systems[system] = {
                "gamelist": gamelist_path,
                "rompath": rompath,
                "lightgunroms": matched_roms
            }
        
        self.screens = {
            "main": load_main_screen(f"{THEME_PATH}main.xml", self.show_screen)
        }
        print("Main screen loaded successfully.")

        # Automatically generate system pages: 3do_1, 3do_2, etc.
        from math import ceil

        # Default path to XML
        XML_PATH = f"{THEME_PATH}gamescreen.xml"

        if not os.path.exists(XML_PATH):
            print(f"Error: XML file '{XML_PATH}' not found.")
            sys.exit(1)

        try:
            tree = ET.parse(XML_PATH)
            root = tree.getroot()

            # Layout Section
            layout = root.find("layout")
            button = layout.find("button")
            spacing = layout.find("spacing")
            start = layout.find("start")
            grid = layout.find("grid")
            offset = layout.find("button_frame_offset")

            BUTTON_WIDTH = int(button.get("width"))
            BUTTON_HEIGHT = int(button.get("height"))
            X_SPACING = int(spacing.get("x"))
            Y_SPACING = int(spacing.get("y"))
            START_X = int(start.get("x"))
            START_Y = int(start.get("y"))
            BUTTONS_PER_ROW = int(grid.get("buttons_per_row"))
            ROWS_PER_PAGE = int(grid.get("rows_per_page"))
            BUTTON_FRAME_OFFSET = int(offset.text) if offset is not None else 0  # fallback to 0 if not present

            # Navigation Section
            nav = root.find("navigation")
            prev = nav.find("prev")
            main = nav.find("main")
            next_ = nav.find("next")

            PREV_X = int(prev.get("x"))
            PREV_Y = int(prev.get("y"))
            PREV_WIDTH = int(prev.get("width"))
            PREV_HEIGHT = int(prev.get("height"))

            MAIN_X = int(main.get("x"))
            MAIN_Y = int(main.get("y"))
            MAIN_WIDTH = int(main.get("width"))
            MAIN_HEIGHT = int(main.get("height"))

            NEXT_X = int(next_.get("x"))
            NEXT_Y = int(next_.get("y"))
            NEXT_WIDTH = int(next_.get("width"))
            NEXT_HEIGHT = int(next_.get("height"))

        except ET.ParseError as e:
            print(f"Error parsing XML file '{XML_PATH}': {e}")
            sys.exit(1)
            
        # You can now use the variables as needed
        print("Loaded screen layout successfully.")

        GAMES_PER_PAGE = BUTTONS_PER_ROW * ROWS_PER_PAGE

        for system_name, data in filtered_systems.items():
            lightgunroms = data["lightgunroms"]
            total_pages = ceil(len(lightgunroms) / GAMES_PER_PAGE)

            for page in range(total_pages):
                screen_key = f"{system_name}_{page + 1}"
                zones = []
                page_items = lightgunroms[page * GAMES_PER_PAGE:(page + 1) * GAMES_PER_PAGE]

                for idx, item in enumerate(page_items):
                    col = idx % BUTTONS_PER_ROW
                    row = idx // BUTTONS_PER_ROW

                    x1 = START_X + col * (BUTTON_WIDTH + X_SPACING)
                    y1 = START_Y + row * (BUTTON_HEIGHT + Y_SPACING)
                    x2 = x1 + BUTTON_WIDTH
                    y2 = y1 + BUTTON_HEIGHT

                    zones.append({
                        "name": f'Game {idx + 1 + (page * GAMES_PER_PAGE)}: {item.get("name", f"Game {idx + 1 + (page * GAMES_PER_PAGE)}")}',
                        "image": item.get("image") or f"{THEME_PATH}game_default.png",
                        "overlay": f"{THEME_PATH}game.png",
                        "xy": (x1, y1, x2, y2),
                        "action": lambda sys=system_name, rom=item["rom"]: __import__('subprocess').Popen(["/opt/retropie/supplementary/runcommand/runcommand.sh", "0", "_SYS_", sys, rom])
                    })

                if page > 0:
                    prev_screen = f"{system_name}_{page}"
                    zones.append({
                        "name": "prev",
                        "image": f"{THEME_PATH}button_prev.png",
                        "xy": (PREV_X, PREV_Y, (PREV_X + PREV_WIDTH), (PREV_Y + PREV_HEIGHT)),
                        "action": lambda ps=prev_screen: self.show_screen(ps)
                    })

                zones.append({
                    "name": "main",
                    "image": f"{THEME_PATH}button_main.png",
                    "xy": (MAIN_X, MAIN_Y, (MAIN_X + MAIN_WIDTH), (MAIN_Y + MAIN_HEIGHT)),
                    "action": lambda: self.show_screen("main")
                })

                if page < total_pages - 1:
                    next_screen = f"{system_name}_{page + 2}"
                    zones.append({
                        "name": "next",
                        "image": f"{THEME_PATH}button_next.png",
                        "xy": (NEXT_X, NEXT_Y, (NEXT_X + NEXT_WIDTH), (NEXT_Y + NEXT_HEIGHT)),
                        "action": lambda ns=next_screen: self.show_screen(ns)
                    })
                    
                self.screens[screen_key] = {
                    "bg": f"{THEME_PATH}{system_name}.png",
                    "zones": zones
                }
      
        self.show_screen("main")

    def play_sound_blocking(self, path):
        mixer.music.load(path)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)

    def show_hover_text(self, text, x, y):
        if hasattr(self, "hover_text_id") and self.hover_text_id:
            self.canvas.coords(self.hover_text_id, x + 20, y + 20)
            self.canvas.itemconfig(self.hover_text_id, text=text)
        else:
            self.hover_text_id = self.canvas.create_text(
                x + 20, y + 20,
                text=text,
                font=("Arial", 14, "bold"),
                fill="yellow",
                anchor="nw"
            )
        self.canvas.tag_raise(self.hover_text_id)

    def hide_hover_text(self):
        if hasattr(self, "hover_text_id") and self.hover_text_id:
            self.canvas.delete(self.hover_text_id)
            self.hover_text_id = None
        
    def track_mouse(self, event):
        if self.target_id:
            self.canvas.coords(self.target_id, event.x - 62, event.y - 62)
            self.canvas.tag_raise(self.target_id)
            self.canvas.tag_raise(self.coord_text)

        # Show zone name at fixed location, only if it starts with "Game XX:"
        zone_name = None
        for zone in self.screens.get(self.current_screen, {}).get("zones", []):
            x1, y1, x2, y2 = zone["xy"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                name = zone["name"]
                if name.startswith("Game "):
                    # Try to parse "Game XX: Rest of name"
                    parts = name.split(":", 1)
                    if len(parts) == 2 and parts[0].strip()[5:].strip().isdigit():
                        zone_name = parts[1].strip()
                    else:
                        zone_name = name
                break

        if zone_name:
            # Truncate if too long
            if len(zone_name) > GAME_NAME_WIDTH:
                zone_name = zone_name[:GAME_NAME_WIDTH-3] + "..."

            if not hasattr(self, 'zone_name_id') or self.zone_name_id is None:
                self.zone_name_id = self.canvas.create_text(
                    GAME_NAME_X, GAME_NAME_Y,
                    text=zone_name,
                    font=GAME_NAME_FONT,
                    fill=GAME_NAME_FILL,
                    anchor="nw"
                )
            else:
                self.canvas.itemconfig(self.zone_name_id, text=zone_name)
                self.canvas.coords(self.zone_name_id, GAME_NAME_X, GAME_NAME_Y)
                self.canvas.tag_raise(self.zone_name_id)
        elif hasattr(self, 'zone_name_id') and self.zone_name_id:
            self.canvas.itemconfig(self.zone_name_id, text="")
            
    def handle_click(self, event):
        hit = False
        zones = self.screens.get(self.current_screen, {}).get("zones", [])

        for zone in zones:
            x1, y1, x2, y2 = zone["xy"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                hit = True
                threading.Thread(target=self.delayed_action, args=(zone["action"], f"{THEME_PATH}hit.mp3")).start()
                break

        if not hit:
            threading.Thread(target=self.play_sound_blocking, args=(f"{THEME_PATH}miss.mp3",)).start()

        self.create_dent(event.x, event.y)

    def delayed_action(self, action, sound_path):
        self.play_sound_blocking(sound_path)
        action()

    def create_dent(self, x, y):
        if self.current_screen == "main":
            self.dent_image = self.dentmain_image
        else:
            self.dent_image = self.dentsub_image

        dent = self.canvas.create_image(x, y, image=self.dent_image)
        self.dents.append(dent)

    def clear_dents(self):
        for dent in self.dents:
            self.canvas.delete(dent)
        self.dents = []

    def show_screen(self, name):
        if name not in self.screens:
            print(f"[ERROR] Screen '{name}' not found!")
            return
        self.clear_dents()
        self.current_screen = name
        screen = self.screens.get(name, {})
        bg_path = screen.get("bg")

        # Load and display background image
        try:
            image = Image.open(bg_path).resize((1920, 1080))
            self.bg_image = ImageTk.PhotoImage(image)
            if self.image_id:
                self.canvas.itemconfig(self.image_id, image=self.bg_image)
            else:
                self.image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.bg_image)
            self.canvas.tag_lower(self.image_id)
        except Exception as e:
            print(f"Error loading background: {e}")

        # Clear previous zone images if any
        if hasattr(self, 'zone_image_ids'):
            for zid in self.zone_image_ids:
                self.canvas.delete(zid)
        self.zone_image_ids = []


        # Default path to XML
        XML_PATH = f"{THEME_PATH}gamescreen.xml"

        if not os.path.exists(XML_PATH):
            print(f"Error: XML file '{XML_PATH}' not found.")
            sys.exit(1)

        try:
            tree = ET.parse(XML_PATH)
            root = tree.getroot()

            # Layout Section
            layout = root.find("layout")
            button = layout.find("button")
            spacing = layout.find("spacing")
            start = layout.find("start")
            grid = layout.find("grid")
            offset = layout.find("button_frame_offset")
            page_no = layout.find("page_no")

            BUTTON_WIDTH = int(button.get("width"))
            BUTTON_HEIGHT = int(button.get("height"))
            X_SPACING = int(spacing.get("x"))
            Y_SPACING = int(spacing.get("y"))
            START_X = int(start.get("x"))
            START_Y = int(start.get("y"))
            BUTTONS_PER_ROW = int(grid.get("buttons_per_row"))
            ROWS_PER_PAGE = int(grid.get("rows_per_page"))
            BUTTON_FRAME_OFFSET = int(offset.text) if offset is not None else 0

            if page_no is not None:
                PAGE_NUMBER_X = int(page_no.get("x"))
                PAGE_NUMBER_Y = int(page_no.get("y"))
                PAGE_NUMBER_FONT = eval(page_no.get("font"))
                PAGE_NUMBER_FILL = page_no.get("colour")
            else:
                PAGE_NUMBER_X = 1720
                PAGE_NUMBER_Y = 1020
                PAGE_NUMBER_FONT = ("Arial", 24, "bold")
                PAGE_NUMBER_FILL = "white"

            # Navigation Section
            nav = root.find("navigation")
            prev = nav.find("prev")
            main = nav.find("main")
            next_ = nav.find("next")

            PREV_X = int(prev.get("x"))
            PREV_Y = int(prev.get("y"))
            PREV_WIDTH = int(prev.get("width"))
            PREV_HEIGHT = int(prev.get("height"))

            MAIN_X = int(main.get("x"))
            MAIN_Y = int(main.get("y"))
            MAIN_WIDTH = int(main.get("width"))
            MAIN_HEIGHT = int(main.get("height"))

            NEXT_X = int(next_.get("x"))
            NEXT_Y = int(next_.get("y"))
            NEXT_WIDTH = int(next_.get("width"))
            NEXT_HEIGHT = int(next_.get("height"))

        except ET.ParseError as e:
            print(f"Error parsing XML file '{XML_PATH}': {e}")
            sys.exit(1)

        print("Loaded screen layout successfully.")

        # Remove previous page number if it exists
        if hasattr(self, "page_number_id") and self.page_number_id:
            self.canvas.delete(self.page_number_id)
            self.page_number_id = None

        # Extract page number from screen name (e.g., "3do_2")
        match = re.search(r"_(\d+)$", name)
        if match:
            page_num = int(match.group(1))
            self.page_number_id = self.canvas.create_text(
                PAGE_NUMBER_X,
                PAGE_NUMBER_Y,
                text=f"Page {page_num}",
                font=PAGE_NUMBER_FONT,
                fill=PAGE_NUMBER_FILL,
                anchor="se"
            )
        else:
            self.page_number_id = None


        # Draw each zone image and overlay
        for zone in screen.get("zones", []):
            try:
                x1, y1, x2, y2 = zone["xy"]
                image_path = zone.get("image")

                if not image_path or not os.path.exists(image_path):
                    print(f"[WARN] Image not found for zone '{zone.get('name')}' at path: {image_path}")
                    image_path = f"{THEME_PATH}game_default.png"

                is_nav_button = zone["name"] in ["main", "prev", "next"]
                self.zone_photos = getattr(self, 'zone_photos', {})

                if not is_nav_button and zone.get("overlay"):
                    # System/game button: offset +8 and resize to 234x184
                    base_img = Image.open(image_path).resize(((BUTTON_WIDTH - (BUTTON_FRAME_OFFSET * 2)), (BUTTON_HEIGHT - (BUTTON_FRAME_OFFSET * 2))), Image.ANTIALIAS)

                    # Replace transparency with black if present
                    if base_img.mode in ("RGBA", "LA"):
                        black_bg = Image.new("RGB", base_img.size, (0, 0, 0))
                        black_bg.paste(base_img, mask=base_img.split()[-1])  # Use alpha channel as mask
                        base_img = black_bg
                    else:
                        base_img = base_img.convert("RGB")

                    base_photo = ImageTk.PhotoImage(base_img)
                    self.zone_photos[zone["name"]] = base_photo

                    base_id = self.canvas.create_image(x1 + BUTTON_FRAME_OFFSET, y1 + BUTTON_FRAME_OFFSET, anchor='nw', image=base_photo)
                    self.zone_image_ids.append(base_id)

                    overlay_path = zone.get("overlay")
                    if overlay_path and os.path.exists(overlay_path):
                        overlay_img = Image.open(overlay_path).resize((250, 200), Image.ANTIALIAS)
                        overlay_photo = ImageTk.PhotoImage(overlay_img)
                        self.zone_photos[zone["name"] + "_overlay"] = overlay_photo

                        overlay_id = self.canvas.create_image(x1, y1, anchor='nw', image=overlay_photo)
                        self.zone_image_ids.append(overlay_id)
                else:
                    # nav buttons: normal size and position
                    base_img = Image.open(image_path).resize((x2 - x1, y2 - y1), Image.ANTIALIAS)
                    base_photo = ImageTk.PhotoImage(base_img)
                    self.zone_photos[zone["name"]] = base_photo

                    base_id = self.canvas.create_image(x1, y1, anchor='nw', image=base_photo)
                    self.zone_image_ids.append(base_id)

            except Exception as e:
                print(f"[ERROR] Failed to load zone '{zone.get('name')}': {e}")
        
        # Ensure coordinate text and target always on top
        self.canvas.tag_raise(self.coord_text)
        if self.target_id:
            self.canvas.tag_raise(self.target_id)
            self.canvas.tag_raise(self.coord_text)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = GunMenu(root)
    root.config(cursor="none")
    root.mainloop()
