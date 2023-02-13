import os, re
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

VERSION = "v1.1"
ICON = "load.ico"
if not os.path.isfile(ICON):
	ICON = ""
USER = os.getlogin()
MAX_TIER = ["Annihilator", "Arch Sage", "Avenger", "Champion", "Dark Arch Templar", "Devil Incarnate", "Grand Inquisitor", "Grand Templar", "Hierophant", "Jounin", "Lightbinder", "Light Caster", "Master Stalker", "Monster Hunter", "Mystic", "Phantom Assassin", "Professional Witcher", "Prophetess", "Rune Master", "Sky Caster", "Sky Sorceress", "Sniper", "Summoner", "White Wizard"]
DEFAULT_PATH = f"C:\\Users\\{USER}\\Documents\\Warcraft III"

active_profile = ""
profiles = []
custom_path = ""
selected_class = ""
class_list = []


def atoi(text):
	return int(text) if text.isdigit() else text


def natural_keys(text):
	return [atoi(c) for c in re.split(r'(\d+)', text)]


def change_path():
	global custom_path, active_profile, custom_path, profiles, class_list, DEFAULT_PATH, selected_class
	new_path = filedialog.askdirectory().replace("/", "\\")
	if new_path == "":
		return
	custom_path = new_path
	os.remove("configuration.txt")
	active_profile = ""
	update_config_file()
	refresh()


def update_config_file():
	if os.path.isfile("configuration.txt"):
		os.remove("configuration.txt")
	with open("configuration.txt", "w") as f:
		f.write(active_profile + "\n" + custom_path)


def get_class_information(c_file):
	gold = 0
	shards = 0
	items = []
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
	except:
		print(f"Could not parse: {c_file}")
	return list((gold, shards, load_code, items))


def get_class_names():
	class_names = []
	profile_path = custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile
	try:
		for evo_class_name in os.listdir(profile_path):
			if os.path.isdir(os.path.join(profile_path, evo_class_name)):
				class_names.append(evo_class_name)
		# remove if the directory is empty
		for evo_class_name in class_names:
			if not os.listdir(profile_path + "\\" + evo_class_name):
				class_names.remove(evo_class_name)
	except:
		print("Path is wrong")
	return class_names


def get_class_level_and_file(class_name):
	# get level and file
	class_files = os.listdir(custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile + "\\" + class_name )
	for file in class_files:
		if os.path.isdir(custom_path + "\\CustomMapData\\Twilight's Eve Evo\\" + active_profile + "\\" + class_name + "\\" + file):
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
	index = 0
	textbox.config(state=NORMAL)
	textbox.delete(1.0, END)
	textbox.insert(INSERT, selected_class + "\n\n")
	for x, evo_class in enumerate(class_list):
		if evo_class['class_name'] == selected_class:
			index = x
	textbox.insert(INSERT, "Gold: " + class_list[index]['gold'] + "\n")
	textbox.insert(INSERT, "Power Shards: " + class_list[index]['shards'] + "\n\n")
	for x in range(0, 6):
		textbox.insert(INSERT, f"Item {x+1}: " + class_list[index]['items'][x] + "\n")
	textbox.insert(INSERT, "\nCode: " + class_list[index]['code'])
	textbox.config(state=DISABLED)


def update_class_list():
	listbox.delete(0, END)
	for x, evo_class in enumerate(class_list):
		if checkbutton_tier_4_var.get() == 1 and evo_class['class_name'] not in MAX_TIER:
			continue
		if checkbutton_max_level_var.get() == 1 and evo_class['level'] != "300":
			continue
		listbox.insert(x, f"{evo_class['class_name']} [{evo_class['level']}]")


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
		print("Did not find any profiles")
		return []


# Root
root = Tk()
root.geometry('550x450')
root.resizable(width=0, height=0)
root.title(f"Evo File Reader {VERSION} by Ziadoma")
root.iconbitmap(ICON)


def display_changelog():
	changelog_window = Toplevel(root)
	changelog_window.geometry("400x250")
	changelog_window.resizable(width=0, height=0)
	changelog_window.title("Changelog")
	changelog_window.iconbitmap(ICON)
	changelog_textbox = Text(changelog_window)
	changelog_textbox.place(x=0, y=0)
	changelog_textbox.insert("end", "v1.1\n")
	changelog_textbox.insert("end", "- Added Sky Sorceress and Lightbinder to the\nfilters.\n- Fixed a bug that could not read the file when\nthere was another directory\n\n")
	changelog_textbox.insert("end", "v1.0\n")
	changelog_textbox.insert("end", "- Added refresh feature to update the information\n- Added change path feature\n- Added support for multiple battlenet accounts")
	changelog_textbox.config(state=DISABLED)
	changelog_textbox.tag_add('v1.1', '1.0', '1.end')
	changelog_textbox.tag_config('v1.1', font='none 10 bold')
	changelog_textbox.tag_add('v1.0', '7.0', '7.end')
	changelog_textbox.tag_config('v1.0', font='none 10 bold')


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
								"Feel free to contact me on discord: Ziadoma#1337")
	about_textbox.config(state=DISABLED)
	about_textbox.tag_add('word', '1.0', '1.end')
	about_textbox.tag_config('word', font='none 10 bold')


# Menu
menu_bar = Menu(root)
config_menu = Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Set Wacraft3 path", command=change_path)
config_menu.add_separator()
config_menu.add_command(label="Close application", command=root.quit)
menu_bar.add_cascade(label="Edit", menu=config_menu)
changelog_menu = Menu(menu_bar, tearoff=0)
changelog_menu.add_command(label="Changelog", command=display_changelog)
changelog_menu.add_command(label="About", command=display_about)
menu_bar.add_cascade(label="Help", menu=changelog_menu)
root.config(menu=menu_bar)

# Checkbutton
checkbutton_max_level_var = IntVar()
checkbutton_tier_4_var = IntVar()
Checkbutton(root, text="Max Level", variable=checkbutton_max_level_var, command=update_class_list).place(x=10, y=10)
Checkbutton(root, text="Tier4", variable=checkbutton_tier_4_var, command=update_class_list).place(x=100, y=10)


def get_selected_list_item(event):
	global selected_class
	selection = event.widget.curselection()
	if selection:
		index = selection[0]
		class_name = listbox.get(index)
		selected_class_list = class_name.split(" ")
		if len(selected_class_list) == 2:
			selected_class = selected_class_list[0]
		else:
			selected_class = selected_class_list[0] + " " + selected_class_list[1]
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
	textbox.config(state=NORMAL)
	textbox.delete(1.0, END)
	textbox.config(state=DISABLED)


# Button
button = Button(root, width=15, height=1, bd=1, text="Refresh", command=refresh)
button.place(x=408, y=9)


# main
def main():
	global active_profile, custom_path, profiles, class_list, selected_class
	profiles = []
	selected_class = ""
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
				class_list.append(dict(class_name=evo_class, level=level, gold=class_information[0], shards=class_information[1], code=class_information[2], items=class_information[3]))
	update_gui()


main()
root.mainloop()
