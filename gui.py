import tkinter
from tkinter import ttk
import organizer
from queue import Queue, Empty
from threading import Thread


class DownloadWorker(Thread):
	DONE = 'DONE'

	def __init__(self, queue):
		super().__init__()
		self.queue = queue

	def run(self):
		dir_path = self.queue.get()
		for percent in organizer.fetch_album_art(dir_path, self.queue):
			self.queue.put(percent)
		self.queue.task_done()
		self.queue.put('DONE')


def organize():
	dir_pattern = entry_album_pattern.get().strip()
	file_pattern = entry_file_pattern.get().strip()
	dir_path = entry_path.get().strip()

	if not entries_valid(dir_path, dir_pattern, file_pattern):
		return

	progress_bar.grid()
	status.set("Organizing...")
	for percent in organizer.organize(dir_path, dir_pattern, file_pattern):
		update_progress_bar(percent)
	update_progress_bar(0)

	status.set("Removing empty directories...")
	progress_bar.start()
	organizer.clear_remains(dir_path)
	progress_bar.stop()

	status.set("Done!")
	update_progress_bar(100)


def update_progress_bar(percent: int):
	progress.set(percent)
	progress_bar.update()


def entries_valid(dir_path, *args):
	label_status.grid()
	for arg in args:
		if arg == "":
			status.set("Cannot use empty pattern or path.")
			return False
	if dir_path == "":
		status.set("Cannot use empty pattern or path.")
		return False
	elif not organizer.os.path.isdir(dir_path):
		status.set("Path is not a directory, or is invalid.")
		return False
	elif organizer.contains_no_audio(dir_path):
		status.set("Path contains no audio files! Are you sure you got the correct path?")
		return False
	return True


def fetch_art():
	def check_queue():
		try:
			percent = queue.get_nowait()
		except Empty:
			root.after(100, check_queue)
		else:
			if percent == DownloadWorker.DONE:
				status.set("Done!")
				update_progress_bar(100)
			else:
				update_progress_bar(percent)
				root.after(100, check_queue)

	# set up GUI and variables for fetching operation
	dir_path = entry_path.get().strip()
	if not entries_valid(dir_path):
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
	root.after(200, check_queue)


def update_muspy():
	# api_url = 'https://muspy.com/api/1/artists'
	# # api_endpoint = 'artists/'
	#
	# response = requests.request('GET', api_url, auth=('6pdr8vvquufgil5kk953z7cdnfu5ih', '22051994'))
	# print(response)
	#
	# ==== status ====
	# Seems like a lot of work.
	# Relevant links: https://www.one-tab.com/page/6tYsdNNDQA2tFhg7kkaNvw
	# Best bet is to imitate the way beets use the muspy API, since on its own
	# its documentation is bare and I can't seem to get it to work.

	# temporary user notice
	progress_bar.grid_remove()
	label_status.grid()
	status.set("Under development...")


if __name__ == '__main__':
	root = tkinter.Tk()
	root.title("Music Library Organizer")
	root.geometry('570x420')
	root.minsize(width=570, height=420)
	root.maxsize(width=570, height=420)

	# ======== Frames ========

	frame_entries = tkinter.Frame(root)
	frame_entries.grid(row=2, column=1, sticky='nsew', padx=20)
	frame_entries.config(border=1, relief='sunken')
	frame_entries.grid_columnconfigure(1, weight=1)
	# frame_entries.grid_columnconfigure(2, weight=1)

	frame_buttons = tkinter.Frame(root)
	frame_buttons.grid(row=4, column=1, sticky='nsew', padx=20, pady=20)
	# frame_buttons.config(border=2, relief='sunken')
	frame_buttons.grid_columnconfigure(0, weight=1)
	frame_buttons.grid_columnconfigure(1, weight=1)
	frame_buttons.grid_columnconfigure(2, weight=1)

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

	label_path = tkinter.Label(frame_entries, text="Library path:", justify=tkinter.LEFT)
	label_path.grid(row=2, column=0, sticky='w', pady=(10, 10), padx=(10, 20))

	status = tkinter.StringVar()
	label_status = tkinter.Label(root, textvariable=status, justify=tkinter.LEFT)
	label_status.grid(row=6, column=1, sticky='w', padx=20)
	label_status.grid_remove()

	# ======== Entries ========

	entry_album_pattern = tkinter.Entry(frame_entries)
	entry_album_pattern.insert(0, organizer.DIR_DEFAULT)
	entry_album_pattern.grid(row=0, column=1, sticky='ew', pady=(10, 0), padx=(0, 20))

	entry_file_pattern = tkinter.Entry(frame_entries)
	entry_file_pattern.insert(0, organizer.FILE_DEFAULT)
	entry_file_pattern.grid(row=1, column=1, sticky='ew', pady=(10, 0), padx=(0, 20))

	entry_path = tkinter.Entry(frame_entries)
	entry_path.insert(0, "D:\CodeProjects\Python\music_test_folder")
	entry_path.grid(row=2, column=1, sticky='ew', pady=(10, 10), padx=(0, 20))

	# ======== Buttons ========

	progress = tkinter.DoubleVar()
	progress_bar = ttk.Progressbar(root, orient=tkinter.HORIZONTAL, variable=progress, maximum=100)
	progress_bar.grid(row=5, column=1, sticky='ew', padx=20)
	progress_bar.grid_remove()

	btn_organize = tkinter.Button(frame_buttons, text="Organize library", command=organize)
	btn_organize.grid(row=0, column=0)

	btn_fetch_art = tkinter.Button(frame_buttons, text="Fetch album art", command=fetch_art)
	btn_fetch_art.grid(row=0, column=1)

	btn_update_muspy = tkinter.Button(frame_buttons, text="Update Muspy", command=update_muspy)
	btn_update_muspy.grid(row=0, column=2)

	root.mainloop()
