try:
	import tkinter
except ImportError:  # enable python 2
	import Tkinter as tkinter
from tkinter import ttk

DIR_DEFAULT = '%A/%y - %a'
FILE_DEFAULT = '%tn - %t'


def organize(progress_bar):
	dir_pattern = entry_album_pattern.get()
	file_pattern = entry_file_pattern.get()
	print(dir_pattern, file_pattern, sep='\t')
	progress_bar.grid()
	progress_bar.start()


def fetch_art():
	pass


if __name__ == '__main__':
	root = tkinter.Tk()
	root.title("Music Library Organizer")
	root.geometry('570x420')
	root.minsize(width=570, height=420)
	root.maxsize(width=570, height=420)

	# ======== Frames ========

	frame_entries = tkinter.Frame(root)
	frame_entries.grid(row=2, column=1, sticky='nsew', padx=20)
	frame_entries.config(border=2, relief='sunken')
	frame_entries.grid_columnconfigure(1, weight=1)
	# frame_entries.grid_columnconfigure(2, weight=1)

	frame_buttons = tkinter.Frame(root)
	frame_buttons.grid(row=4, column=1, sticky='nsew', padx=20, pady=20)
	# frame_buttons.config(border=2, relief='sunken')
	frame_buttons.grid_columnconfigure(0, weight=1)
	frame_buttons.grid_columnconfigure(1, weight=1)

	# ======== Labels ========

	instructions_text = '\n'.join(
		["Use the following placeholders to build a name pattern for album directories and audio file names:",
		 "", "%A\tartist", "%a\talbum", "%t\ttitle", "%tn\ttrack number", "%y\tyear",
		 "", "Default album directory pattern:\t'{}'\t(e.g. 'Metallica/1984 - Ride the Lightning')".format(DIR_DEFAULT),
		 "Default file name pattern:\t\t'{}'\t(e.g. '01 - Fight Fire with Fire')".format(FILE_DEFAULT)])
	label_instructions = tkinter.Label(root, text=instructions_text, justify=tkinter.LEFT)
	label_instructions.grid(row=1, column=1, sticky='w', pady=20, padx=20)

	label_album_pattern = tkinter.Label(frame_entries, text="Album pattern:", justify=tkinter.LEFT)
	label_album_pattern.grid(row=0, column=0, sticky='w', pady=(10, 0), padx=(10, 20))

	label_file_pattern = tkinter.Label(frame_entries, text="File pattern:", justify=tkinter.LEFT)
	label_file_pattern.grid(row=1, column=0, sticky='w', pady=(10, 0), padx=(10, 20))

	label_path = tkinter.Label(frame_entries, text="Library path:", justify=tkinter.LEFT)
	label_path.grid(row=2, column=0, sticky='w', pady=(10, 10), padx=(10, 20))

	# ======== Entries ========

	entry_album_pattern = tkinter.Entry(frame_entries)
	entry_album_pattern.insert(0, "%A/%y - %a")
	entry_album_pattern.grid(row=0, column=1, sticky='ew', pady=(10, 0), padx=(0, 20))

	entry_file_pattern = tkinter.Entry(frame_entries)
	entry_file_pattern.insert(0, "%tn - %t")
	entry_file_pattern.grid(row=1, column=1, sticky='ew', pady=(10, 0), padx=(0, 20))

	entry_path = tkinter.Entry(frame_entries)
	entry_path.grid(row=2, column=1, sticky='ew', pady=(10, 10), padx=(0, 20))

	# ======== Buttons ========

	progress = 0
	progress_bar = ttk.Progressbar(root, orient=tkinter.HORIZONTAL, variable=progress)
	progress_bar.grid(row=5, column=1, sticky='ew', padx=20)
	progress_bar.grid_remove()

	btn_organize = tkinter.Button(frame_buttons, text="Organize library", command=lambda: organize(progress_bar))
	btn_organize.grid(row=0, column=0)

	btn_fetch_art = tkinter.Button(frame_buttons, text="Fetch album art", command=fetch_art)
	btn_fetch_art.grid(row=0, column=1)

	root.mainloop()
