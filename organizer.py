import os
import id3reader_p3 as id3reader
from shutil import move, SameFileError, rmtree

log_file = None


class FileTags:
	"""
	Class to represent media file id3 tags.
	"""

	def __init__(self, artist, album, year):
		self._artist = artist if artist else "Various Artists"
		self._album = album if album else "Various Albums"
		self._year = year if year else "yyyy"

	def __str__(self):
		return "Artist: '{}', Album: '{}', Year: '{}'".format(self._artist, self._album, self._year)

	"""
	This class uses getters and setters to prevent any of its attributes
	from being set to None.
	"""

	@property
	def artist(self):
		return self._artist

	@artist.setter
	def artist(self, artist):
		self._artist = artist if artist else "Various Artists"

	@property
	def album(self):
		return self._album

	@album.setter
	def album(self, album):
		self._album = album if album else "Various Albums"

	@property
	def year(self):
		return self._year

	@year.setter
	def year(self, year):
		self._year = year if year else "yyyy"


# def display_contents(dir_path: str):
# 	for path, dirs, files in os.walk(dir_path):
# 		print("Subdirectories under " + path + ": " + str(dirs))
# 		print("Files: " + str(files))
# 		print()


def organize(dir_path: str, name_pattern: str = "%A/%y - %a") -> None:
	tag = FileTags(None, None, None)
	abs_path = os.path.abspath(dir_path)

	for path, dirs, files in os.walk(abs_path):
		for file in files:
			if is_media_file(file):
				try:
					reader = id3reader.Reader(os.path.join(path, file))
					tag.artist = reader.get_value('performer')
					tag.album = reader.get_value('album')
					tag.year = reader.get_value('year')
				except id3reader.Id3Error as error:
					print("[ERROR] Couldn't read tags from file: {}".format(os.path.join(path, file)), file)
					print("\t{}".format(error))
				except Exception as error:
					print("[ERROR] Unknown error occurred, please investigate.")
					print("\t{}".format(error))
				else:  # executed if there are no exceptions
					dir_name = generate_directory_name(tag, name_pattern)
					dst_path = create_directory(abs_path, dir_name)
					move_file(path, file, dst_path)


def is_media_file(file: str):
	"""
	Checks if file is one of several common media file types.

	:param file: file name or path
	:return: True if file is media file, False otherwise
	"""
	extensions = ('mp3', 'mp4', 'wma', 'wmv', 'avi', 'mpg', 'mpeg', 'm3u', 'mid',
				  'midi', 'wav', 'm4a')
	return file.endswith(extensions)


def create_directory(dir_path: str, dir_name: str) -> str:
	"""
	Creates directory at specified path.

	:param dir_path: parent directory path
	:param dir_name: directory name
	:return: path for new directory
	"""
	new_path = os.path.join(os.path.abspath(dir_path), dir_name)
	try:
		if not os.path.exists(new_path):
			os.makedirs(new_path)
		else:
			print('[!] Directory "{}" already exists, no action taken.'.format(dir_name))
	except OSError as error:
		print("[ERROR] Could not create directory: {}".format(os.path.join(dir_path, dir_name)))
		print("\t{}".format(error))
	else:
		print("[!] Directory {} created successfully.".format(dir_name))
	return new_path


def generate_directory_name(tag: FileTags, pattern: str) -> str:
	"""
	Generates the name of required directory, according to given tags and name pattern.

	:param tag: FileTags object containing information about the directory
	:param pattern: pattern string for name generation
	# TODO document pattern parameters
	:return: generated directory name
	"""

	# TODO handle all possible pattern values
	return pattern \
		.replace('%A', tag.artist.replace('/', '_')) \
		.replace('%y', tag.year) \
		.replace('%a', tag.album)


def move_file(src_path: str, file_name: str, dst_path: str) -> None:
	src_path = os.path.join(src_path, file_name)

	try:
		move(src_path, dst_path)
	except SameFileError:
		print("[!] File '{}' is already in destination, no action taken.".format(file_name))
	except OSError as error:
		# print("Error moving file to destination '{}' - "
		# 	  "destination is inaccessible or not writeable.".format(dst_path))
		# print(error)
		print("[ERROR] Could not move file to destination: {}".format(dst_path))
		print("\t{}".format(error))
	else:
		print("[!] File {} moved successfully.".format(file_name))


def clear_remains(dir_path: str) -> None:
	abs_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(abs_path):
		for directory in dirs:
			if contains_no_media(os.path.join(path, directory)):
				# print("[!]Directory {} contains no media".format(directory))
				try:
					# print("trying to delete {}\\{}".format(path, directory))
					rmtree(os.path.join(path, directory))
				except Exception as error:
					print("[ERROR] Could not delete directory: {}".format(directory))
					print("\t{}".format(error))
				else:
					print("[!] Directory {} deleted successfully.".format(directory))


def contains_no_media(dir_path: str) -> bool:
	for item in os.listdir(dir_path):
		item_path = os.path.join(dir_path, item)
		if (os.path.isfile(item_path) and is_media_file(item_path)) \
				or os.path.isdir(item_path):
			return False
	return True


def main():
	root = "D:\\CodeProjects\\Python\\music_test_folder"

	log_file = open(os.path.join(root, 'organizer.log'), 'w')

	organize(root)
	clear_remains(root)

	log_file.close()


if __name__ == '__main__':
	main()
