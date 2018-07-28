import tkinter
from tkinter import ttk
from tkinter import filedialog
import organizer
from queue import Queue, Empty
from threading import Thread
from platform import system
from os import getlogin, walk
from os.path import isdir, isfile

DONE = 'DONE'


# TODO consider using parallel workers to speed things up. Would it work, considering their task is an ordered one?
class OrganizeWorker(Thread):
	def __init__(self, queue, callback=None, callback_args=None):
		super().__init__()
		self.queue = queue
		self.callback = callback
		self.callback_args = callback_args

	def run(self):
		dir_path, dir_pattern, file_pattern = self.queue.get()
		for percent in organizer.organize(dir_path, dir_pattern, file_pattern):
			update_progress_bar(percent)  # should worker thread be able to affect GUI thread?
		self.queue.task_done()
		if self.callback is not None:
			self.callback(self.callback_args)


class DownloadWorker(Thread):
	def __init__(self, queue):
		super().__init__()
		self.queue = queue

	def run(self):
		dir_path = self.queue.get()
		for percent in organizer.fetch_album_art(dir_path):
			update_progress_bar(percent)
		self.queue.task_done()
		status.set("Done!")
		update_progress_bar(100)
		toggle_interactables()


def organize(dir_path: str):
	toggle_interactables()
	dir_pattern = entry_album_pattern.get().strip()
	file_pattern = entry_file_pattern.get().strip()
	# dir_path = entry_path.get().strip()

	if not entries_valid(dir_path, dir_pattern, file_pattern):
		toggle_interactables()
		return

	queue = Queue()
	worker = OrganizeWorker(queue, callback=clean, callback_args=dir_path)
	worker.daemon = True
	worker.start()
	progress_bar.grid()
	update_progress_bar(0)
	status.set("Organizing...")
	queue.put((dir_path, dir_pattern, file_pattern))


def clean(dir_path: str):
	update_progress_bar(0)
	status.set("Removing empty directories...")
	progress_bar.start()
	organizer.clear_remains(dir_path)
	progress_bar.stop()

	status.set("Done!")
	update_progress_bar(100)
	toggle_interactables()


def update_progress_bar(percent: int):
	progress.set(percent)
	progress_bar.update()


def entries_valid(dir_path: str, *args):
	label_status.grid()
	for arg in args:
		if arg == "":
			status.set("Cannot use empty pattern or path.")
			return False
	if dir_path == "":
		status.set("Cannot use empty pattern or path.")
		return False
	return True


def fetch_art(dir_path: str):
	# set up GUI and variables for fetching operation
	toggle_interactables()
	# dir_path = entry_path.get().strip()
	if not entries_valid(dir_path):
		toggle_interactables()
		return
	status.set("Fetching album art...")
	progress_bar.grid()

	# create separate thread for image downloading
	# to prevent GUI from freezing
	queue = Queue()
	worker = DownloadWorker(queue)
	worker.daemon = True
	worker.start()

	# begin thread work
	queue.put(dir_path)


def check_queue(queue: Queue, delay: int = 100):
	""" deprecated """
	try:
		percent = queue.get_nowait()
	except Empty:
		root.after(delay, check_queue, queue)
	else:
		if percent == DONE:
			status.set("Done!")
			update_progress_bar(100)
		else:
			update_progress_bar(percent)
			root.after(delay, check_queue, queue)


def toggle_interactables():
	interactables = [entry_album_pattern, entry_file_pattern,
					 btn_browse, btn_organize, btn_fetch_art]
	for intr in interactables:
		if intr['state'] == 'normal':
			intr.config(state=tkinter.DISABLED)
		else:
			intr.config(state=tkinter.NORMAL)


def browse(dir_path: tkinter.StringVar):
	user_selection = filedialog.askdirectory(
		# possible alternatives to os.getlogin:
		# os.getenv('USERNAME') OR os.getenv('USER') OR os.getenv('LOGNAME')
		initialdir='/home' if system() == 'Linux' else (
			dir_path.get() if dir_path.get() else 'C:/Users/{}/Desktop'.format(getlogin())),
		title="Select library directory",
	)
	if isdir(user_selection):
		dir_path.set(user_selection)


if __name__ == '__main__':
	root = tkinter.Tk()
	root.title("Music Library Organizer")
	root.geometry('570x420')
	root.resizable(False, False)

	# ======== Frames ========

	frame_entries = tkinter.Frame(root)
	frame_entries.grid(row=2, column=1, sticky='nsew', padx=20)
	frame_entries.config(border=1, relief='sunken')
	frame_entries.grid_columnconfigure(2, weight=1)

	frame_buttons = tkinter.Frame(root)
	frame_buttons.grid(row=4, column=1, sticky='nsew', padx=20, pady=20)
	frame_buttons.grid_columnconfigure(0, weight=1)
	frame_buttons.grid_columnconfigure(1, weight=1)
	# frame_buttons.grid_columnconfigure(2, weight=1)

	# ======== Labels ========

	instructions_text = '\n'.join(
		["Use the following placeholders to build a name pattern for album directories and audio file names:",
		 "", "%A\tartist", "%a\talbum", "%t\ttitle", "%tn\ttrack number", "%y\tyear",
		 "", "Default album directory pattern:\t'{}'\t(e.g. 'Metallica/1984 - Ride the Lightning')".format(
			organizer.DIR_DEFAULT),
		 "Default file name pattern:\t\t'{}'\t(e.g. '01 - Fight Fire with Fire')".format(organizer.FILE_DEFAULT)])
	label_instructions = tkinter.Label(root, text=instructions_text, justify=tkinter.LEFT)
	label_instructions.grid(row=1, column=1, sticky='w', pady=20, padx=20)

	label_album_pattern = tkinter.Label(frame_entries, text="Album pattern:", justify=tkinter.LEFT)
	label_album_pattern.grid(row=0, column=0, sticky='w', pady=(10, 0), padx=(10, 20))

	label_file_pattern = tkinter.Label(frame_entries, text="File pattern:", justify=tkinter.LEFT)
	label_file_pattern.grid(row=1, column=0, sticky='w', pady=(10, 0), padx=(10, 20))

	label_path = tkinter.Label(frame_entries, text="Library directory:", justify=tkinter.LEFT)
	label_path.grid(row=2, column=0, sticky='w', pady=(10, 10), padx=(10, 20))

	library_path = tkinter.StringVar()
	label_sel_path = tkinter.Label(frame_entries, textvariable=library_path, justify=tkinter.LEFT)
	label_sel_path.grid(row=2, column=2, sticky='w', pady=(10, 10), padx=(0, 20))

	status = tkinter.StringVar()
	label_status = tkinter.Label(root, textvariable=status, justify=tkinter.LEFT)
	label_status.grid(row=6, column=1, sticky='w', padx=20)
	label_status.grid_remove()

	# ======== Entries ========

	entry_album_pattern = tkinter.Entry(frame_entries)
	entry_album_pattern.insert(0, organizer.DIR_DEFAULT)
	entry_album_pattern.grid(row=0, column=1, sticky='ew', pady=(10, 0), padx=(0, 20), columnspan=2)

	entry_file_pattern = tkinter.Entry(frame_entries)
	entry_file_pattern.insert(0, organizer.FILE_DEFAULT)
	entry_file_pattern.grid(row=1, column=1, sticky='ew', pady=(10, 0), padx=(0, 20), columnspan=2)

	# ======== Buttons ========

	btn_browse = tkinter.Button(frame_entries, text="Browse", width=10, command=lambda: browse(library_path))
	btn_browse.grid(row=2, column=1, sticky='w', pady=(10, 10), padx=(0, 10))

	progress = tkinter.DoubleVar()
	progress_bar = ttk.Progressbar(root, orient=tkinter.HORIZONTAL, variable=progress, maximum=100)
	progress_bar.grid(row=5, column=1, sticky='ew', padx=20)
	progress_bar.grid_remove()

	btn_organize = tkinter.Button(frame_buttons, text="Organize library", width=14,
								  command=lambda: organize(library_path.get()))
	btn_organize.grid(row=0, column=0)

	btn_fetch_art = tkinter.Button(frame_buttons, text="Fetch album art", width=14,
								   command=lambda: fetch_art(library_path.get()))
	btn_fetch_art.grid(row=0, column=1)

	root.mainloop()
