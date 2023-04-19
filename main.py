import os, re
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import pyautogui
import keyboard

VERSION = "v1.3"
ICON = "load.ico"
if not os.path.isfile(ICON):
	ICON = ""
USER = os.getlogin()
MAX_TIER = ["Annihilator", "Arch Sage", "Avenger", "Champion", "Dark Arch Templar", "Devil Incarnate",
			"Grand Inquisitor", "Grand Templar", "Hierophant", "Jounin", "Lightbinder", "Light Caster",
			"Master Stalker", "Monster Hunter", "Mystic", "Phantom Assassin", "Professional Witcher", "Prophetess",
			"Rune Master", "Sky Caster", "Sky Sorceress", "Sniper", "Stargazer", "Summoner", "White Wizard"]
ALL_CLASS_LIST = ["Annihilator", "Arch Sage", "Avenger", "Champion", "Dark Arch Templar", "Devil Incarnate",
			"Grand Inquisitor", "Grand Templar", "Hierophant", "Jounin", "Lightbinder", "Light Caster",
			"Master Stalker", "Monster Hunter", "Mystic", "Phantom Assassin", "Professional Witcher", "Prophetess",
			"Rune Master", "Sky Caster", "Sky Sorceress", "Sniper", "Stargazer", "Summoner", "White Wizard", "Arch Druid",
			"Swordsman", "Knight", "Crusader", "Imperial Knight", "Acolyte", "Cleric", "Priest", "Matriarch", "Initiate",
			"Mage", "Wizard", "Sage", "Witch Hunter", "Slayer", "Witcher", "Inquisitor", "Archer", "Hunter", "Marksman",
			"Tracker", "Druid", "Shaman", "Shapeshifter", "Thief", "Rogue", "Assassin", "Stalker", "Templar", "Arch Templar",
			"High Templar", "Dark Templar", "Ninja", "Genin", "Chunin", "Executioner", "Novice (Male)", "Novice (Female)",
			"Caster", "Clairvoyant", "Sorceress", "Illuminator"]
DEFAULT_PATH = f"C:\\Users\\{USER}\\Documents\\Warcraft III"
WAIT_TIMER = 0
CHANGELOG_FILE_NAME = "changelog.txt"

active_profile = ""
profiles = []
custom_path = ""
selected_class = ""
class_list = []
selected_code = ""


def atoi(text):
	return int(text) if text.isdigit() else text


def natural_keys(text):
	return [atoi(c) for c in re.split(r'(\d+)', text)]


def change_path():
	global custom_path, active_profile
	new_path = filedialog.askdirectory().replace("/", "\\")
	if new_path == "":
		return
	custom_path = new_path
	active_profile = ""
	update_config_file()
	refresh()


def update_config_file():
	if os.path.isfile("configuration.txt"):
		os.remove("configuration.txt")
	with open("configuration.txt", "w") as f:
		f.write(active_profile + "\n" + custom_path)


def get_stash_items(content, file_name):
	stash_items = []
	for stash in ["", "2", "3", "4", "5", "6"]:
		stash_list = []
		for item_num in range(1, 7):
			try:
				stash_item = re.search(f'call Preload\( "Stash{stash} Item {item_num}: (.*?)" \)', content).group(
					1).replace("|r", "")
				if stash_item[:2].lower() == "|c":
					stash_item = stash_item[10:]
				if stash_item == " ":
					continue
				stash_list.append(stash_item)
			except:
				print(f"{file_name}: Could not parse stash{stash} item{item_num}")
		stash_items.append(stash_list)
	return stash_items


def get_class_information(c_file):
	gold = 0
	shards = 0
	items = []
	stash_items = []
	load_code = ""
	try:
		with open(c_file, "r") as f:
			content = f.read()
			gold = re.search('call Preload\(\ "Gold: (.*?)" \)', content).group(1)
			shards = re.search('call Preload\(\ "Power Shard: (.*?)" \)', content).group(1)
			load_code = re.search('call Preload\(\ "-l (.*?)" \)', content).group(1)
			for x in range(1, 7):
				item = re.search(f'call Preload\(\ "Item {x}: (.*?)" \)', content).group(1).replace("|r", "")
				if item[:3].lower() == "|cf":
					item = item[10:]
				items.append(item)
			stash_items = get_stash_items(content, c_file)
	except:
		print(f"Could not parse: {c_file}")
	return list((gold, shards, load_code, items, stash_items))


def get_class_names():
	class_names = []
	profile_path = custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile
	try:
		for evo_class_name in os.listdir(profile_path):
			if os.path.isdir(os.path.join(profile_path, evo_class_name)) and class_is_valid(evo_class_name):
				class_names.append(evo_class_name)
		# remove if the directory is empty
		for evo_class_name in class_names:
			if not os.listdir(profile_path + "\\" + evo_class_name):
				class_names.remove(evo_class_name)
	except:
		print("Path is wrong")
	return class_names

def class_is_valid(class_name):
	if class_name in ALL_CLASS_LIST: return True
	return False

def get_class_level_and_file(class_name):
	# get level and file
	class_files = os.listdir(custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile + "\\" + class_name)
	for file in class_files:
		if os.path.isdir(
				custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile + "\\" + class_name + "\\" + file):
			class_files.remove(file)
			continue
		if not file.startswith("[Level ") or not file.endswith("].txt"):
			class_files.remove(file)
			continue
	class_files.sort(key=natural_keys)
	highest_class_file = class_files[-1]
	class_level = highest_class_file[7:-5]
	return class_level, custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile + "\\" + class_name + "\\" + highest_class_file


def update_information():
	global selected_code
	index = 0
	textbox.config(state=NORMAL)
	textbox.delete(1.0, END)
	textbox.insert(INSERT, selected_class + "\n\n")
	for x, evo_class in enumerate(class_list):
		if evo_class['class_name'] == selected_class:
			index = x
			selected_code = class_list[index]['code']
	textbox.insert(INSERT, "Gold: " + class_list[index]['gold'] + "\n")
	textbox.insert(INSERT, "Power Shards: " + class_list[index]['shards'] + "\n")
	textbox.insert(INSERT, "\nCode: " + selected_code + "\n\n")
	for x in range(0, 6):
		textbox.insert(INSERT, f"Item {x + 1}: " + class_list[index]['items'][x] + "\n")
	textbox.insert(INSERT, "\n")
	for stash in range(0, 6):
		text = ", ".join(class_list[index]['stash_items'][stash])
		if text != "":
			textbox.insert(INSERT, f"Stash{stash + 1}: {text}\n\n")
	textbox.config(state=DISABLED)


def update_class_list():
	listbox.delete(0, END)
	for x, evo_class in enumerate(class_list):
		if checkbutton_tier_4_var.get() == 1 and evo_class['class_name'] not in MAX_TIER:
			continue
		if checkbutton_max_level_var.get() == 1 and evo_class['level'] != "300":
			continue
		listbox.insert(x, f"{evo_class['class_name']} [{evo_class['level']}]")
	get_selected_list_item()


def update_gui():
	combo["values"] = profiles
	if len(combo["values"]) == 1:
		combo.current(0)
	else:
		for index, value in enumerate(combo["values"]):
			if value == active_profile:
				combo.current(index)
	update_class_list()


def load_config():
	with open("configuration.txt", "r") as f:
		lines = f.readlines()
		if len(lines) != 2:
			print("Configuration.txt has not the right amount of lines")
			return "", ""
		else:
			loaded_active_profile = lines[0].replace("\n", "")
			loaded_custom_path = lines[1].replace("\n", "")
			print("Loaded configuration.txt")
			return loaded_active_profile, loaded_custom_path


# Need CustomCommands.txt, each line is inputed in WC3.
def load_custom_commands():
	if os.path.exists("customcommands.txt"):
		with open("customcommands.txt", "r") as f:
			lines = f.readlines()
			for command_lines in lines:
				# \n char makes lines skipped if not removed.
				stripped = command_lines.strip()
				paste_code(stripped)


def get_profiles():
	path = custom_path + "\\CustomMapData\\Twilight's Eve Evo\\"
	wc3_names_directories = []
	try:
		for wc3_names_directory in os.listdir(path):
			if os.path.isdir(os.path.join(path, wc3_names_directory)):
				wc3_names_directories.append(wc3_names_directory)
		if len(wc3_names_directories) == 0:
			print("Did not find any profiles")
		return wc3_names_directories
	except:
		print("Except : Did not find any profiles")
		return []


# Root
root = Tk()
root.geometry('550x450')
root.resizable(width=0, height=0)
root.title(f"Evo File Reader {VERSION} by Ziadoma")
root.iconbitmap(ICON)


def display_godly_advancement():
	gadv_window = Toplevel(root)
	gadv_window.geometry("400x250")
	gadv_window.resizable(width=0, height=0)
	gadv_window.title("Changelog")
	gadv_window.iconbitmap(ICON)
	gadv_textbox = Text(gadv_window)
	gadv_textbox.place(x=0, y=0)
	gadv_textbox.insert("end", "Coming soon\n")

def display_changelog():
	os.startfile(CHANGELOG_FILE_NAME)

def display_about():
	about_window = Toplevel(root)
	about_window.geometry("400x250")
	about_window.resizable(width=0, height=0)
	about_window.title("About")
	about_window.iconbitmap(ICON)
	about_textbox = Text(about_window)
	about_textbox.place(x=0, y=0)
	about_textbox.insert("end", "Evo File Reader by Ziadoma\n")
	about_textbox.insert("end", "This program reads Twilight Eve Evo savefiles and \ndisplays the information.\n\n"
								"Set the path to:\n\"{Drive}\\Users\\{USER}\\Documents\\Warcraft III\"\n\n"
								"Feel free to contact us on discord: Ziadoma#1337 - AlArrache#0209")
	about_textbox.config(state=DISABLED)
	about_textbox.tag_add('word', '1.0', '1.end')
	about_textbox.tag_config('word', font='none 10 bold')


# Menu
menu_bar = Menu(root)
config_menu = Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Set Warcraft3 path", command=change_path)
config_menu.add_separator()
config_menu.add_command(label="Close application", command=root.quit)
menu_bar.add_cascade(label="Edit", menu=config_menu)
help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Godly Farm Check", command=display_godly_advancement)
help_menu.add_command(label="Changelog", command=display_changelog)
help_menu.add_command(label="About", command=display_about)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

# Checkbutton
checkbutton_max_level_var = IntVar()
checkbutton_tier_4_var = IntVar()
Checkbutton(root, text="Max Level", variable=checkbutton_max_level_var, command=update_class_list).place(x=10, y=10)
Checkbutton(root, text="Tier4", variable=checkbutton_tier_4_var, command=update_class_list).place(x=100, y=10)


def get_selected_list_item(event=None):
	global selected_class
	update = True

	if event:
		selection = event.widget.curselection()
		if selection:
			index = selection[0]
			class_name = listbox.get(index)
			selected_class_list = class_name.split(" ")[:-1]
			selected_class = " ".join(selected_class_list)
	else:
		items = listbox.get(0, listbox.size())
		for item in items:
			if item[:-6] == selected_class:
				update = False
		if update:
			class_name = listbox.get(0)
			selected_class_list = class_name.split(" ")[:-1]
			selected_class = " ".join(selected_class_list)
	update_information()


# Listbox
listbox = Listbox(root, width=30, height=23, selectmode=SINGLE, exportselection=False)
listbox.bind('<<ListboxSelect>>', get_selected_list_item)
listbox.place(x=10, y=40)

# Text
textbox = Text(root, width=40, height=23)
textbox.config(state=DISABLED)
textbox.place(x=215, y=40)

# Label
label = Label(root, text="Profile: ")
label.place(x=215, y=10)


def update_selected_profile(event):
	global active_profile
	active_profile = event.widget.get()
	update_config_file()
	main()


# Combobox
profile_selected = StringVar()
combo = ttk.Combobox(root, textvariable=profile_selected, state="readonly", width=14)
combo.bind('<<ComboboxSelected>>', update_selected_profile)
combo.place(x=270, y=10)


def refresh():
	main()


# Using Keyboard instead of pyautogui for faster response time. Making Sleeps obsolete
def paste_code(pasted_item):
	war3 = pyautogui.getWindowsWithTitle('Warcraft III')[0]
	war3.activate()
	# pyautogui.sleep(WAIT_TIMER)
	keyboard.send('enter')
	# pyautogui.sleep(WAIT_TIMER)
	keyboard.write(pasted_item)
	# pyautogui.sleep(WAIT_TIMER)
	keyboard.send('enter')


def copy_code():
	if selected_code is not None:
		if len(selected_code) >= 124:
			first_half = selected_code[0:124]
			second_half = selected_code[124:]
			paste_code('-lc')
			paste_code(first_half)
			paste_code(second_half)
			paste_code('-le')
		else:
			paste_code('-l ' + selected_code)
	load_custom_commands()


# Button refresh
button = Button(root, width=8, height=1, bd=1, text="Refresh", command=refresh)
button.place(x=475, y=9)

# Button Load code
button2 = Button(root, width=8, height=1, bd=1, text="Load code", command=copy_code)
button2.place(x=400, y=9)


# main
def main():
	global active_profile, custom_path, profiles, class_list
	profiles = []
	class_list = []
	if os.path.isfile("configuration.txt"):
		active_profile, custom_path = load_config()
	else:
		custom_path = DEFAULT_PATH
	profiles = get_profiles()

	if profiles:
		if active_profile == "":
			active_profile = profiles[0]
			update_config_file()
		class_name_list = get_class_names()
		if class_name_list:
			for evo_class in class_name_list:
				level, file = get_class_level_and_file(evo_class)
				class_information = get_class_information(file)
				class_list.append(
					dict(class_name=evo_class, level=level, gold=class_information[0], shards=class_information[1],
						code=class_information[2], items=class_information[3], stash_items=class_information[4]))
		update_gui()


main()
root.mainloop()
