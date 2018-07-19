import os
import id3reader_p3 as id3reader
from shutil import move, SameFileError, rmtree
import pylast
import urllib.request as request


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
	# tag = FileTags(None, None, None)
	abs_path = os.path.abspath(dir_path)

	tag = None
	for path, dirs, files in os.walk(abs_path):
		for file in files:
			if is_media_file(file):
				file_path = os.path.join(path, file)
				# try:
				# 	reader = id3reader.Reader(file_path)
				# 	tag.artist = reader.get_value('performer')
				# 	tag.album = reader.get_value('album')
				# 	tag.year = reader.get_value('year')
				# except id3reader.Id3Error as error:
				# 	print("[ERROR] Couldn't read tags from file: '{}'".format(file_path), file)
				# 	print("\t{}".format(error))
				# except Exception as error:
				# 	print("[ERROR] Unknown error occurred, please investigate.")
				# 	print("\t{}".format(error))
				# else:  # executed if there are no exceptions
				# 	dir_name = generate_directory_name(tag, name_pattern)
				# 	dst_path = create_directory(abs_path, dir_name)
				# 	move_file(file_path, dst_path)
				tag = generate_tag(file_path)
				if tag:
					dir_name = generate_directory_name(tag, name_pattern)
					dst_path = create_directory(abs_path, dir_name)
					move_file(file_path, dst_path)


def generate_tag(file_path: str) -> FileTags:
	"""
	Generates FileTags object for given media file.

	:param file_path: file's full path.
	:return: FileTags object. If errors occur, returns None.
	"""
	_, file_name = os.path.split(file_path)
	tag = FileTags(None, None, None)

	try:
		reader = id3reader.Reader(file_path)
		tag.artist = reader.get_value('performer')
		tag.album = reader.get_value('album')
		tag.year = reader.get_value('year')
	except id3reader.Id3Error as error:
		print("[ERROR] Couldn't read tags from file: '{}'".format(file_name))
		print("\t{}".format(error))
		tag = None
	except Exception as error:
		print("[ERROR] Unknown error occurred, please investigate.")
		print("\t{}".format(error))
		tag = None
	return tag


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
			print("[!] Directory '{}' created successfully.".format(dir_name))
	# else:
	# 	print('[!] Directory "{}" already exists, no action taken.'.format(dir_name))
	except OSError as error:
		print("[ERROR] Could not create directory: '{}'".format(os.path.join(dir_path, dir_name)))
		print("\t{}".format(error))
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
		.replace('%A', tag.artist.replace('/', '//')) \
		.replace('%y', tag.year) \
		.replace('%a', tag.album)


def move_file(file_path: str, dst_path: str) -> None:
	"""
	Moves file to new location.

	:param file_path: full path for file, as string
	:param dst_path: destination directory's path, as string
	"""
	try:
		move(file_path, dst_path)
	except SameFileError:
		# print("[!] File '{}' is already in destination, no action taken.".format(file_name))
		pass
	except OSError as error:
		# print("Error moving file to destination '{}' - "
		# 	  "destination is inaccessible or not writeable.".format(dst_path))
		# print(error)
		print("[ERROR] Could not move file to destination: {}".format(dst_path))
		print("\t{}".format(error))
	else:
		_, tail = os.path.split(file_path)
		print("[!] File '{}' moved successfully.".format(tail))


def clear_remains(dir_path: str) -> None:
	"""
	Deletes every directory that is either empty,
	or has no media files in it.

	As of now, doesn't handle read-only files.

	:param dir_path: parent directory path
	"""
	abs_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(abs_path):
		for directory in dirs:
			if contains_no_media(os.path.join(path, directory)):
				# print("[!]Directory {} contains no media".format(directory))
				try:
					# print("trying to delete {}\\{}".format(path, directory))
					rmtree(os.path.join(path, directory))
				except Exception as error:
					print("[ERROR] Could not delete directory: '{}'".format(directory))
					print("\t{}".format(error))
				else:
					print("[!] Directory '{}' deleted successfully.".format(directory))


def contains_no_media(dir_path: str) -> bool:
	"""
	Checks if directory contains media files.

	:param dir_path: directory path
	:return: False if contains media files, True otherwise
	"""
	for item in os.listdir(dir_path):
		item_path = os.path.join(dir_path, item)
		if (os.path.isfile(item_path) and is_media_file(item_path)) \
				or os.path.isdir(item_path):
			return False
	return True


def fetch_album_art(dir_path: str) -> None:
	"""
	Downloads album art for all albums in given directory, and all its sub-directories.

	:param dir_path: directory path
	"""
	tag = None
	network = pylast.LastFMNetwork(api_key='d43c497febfef4ba166a51eca0932b90',  # TODO try catch?
								   api_secret='1ce6e93f6e2c1329262484f41901ad2c')  # source code doesn't seem to require
	for path, dirs, files in os.walk(dir_path):
		if not contains_no_media(path) and (files[0] if files else None) \
				and "cover_art.jpg" not in files:
			tag = generate_tag(os.path.join(path, files[0]))
			if tag:
				try:
					album = network.get_album(tag.artist, tag.album)
					image_url = album.get_cover_image()  # by default returns 300x300 sized image
					image_url = image_url.replace('300x300', '600x600')
					request.urlretrieve(image_url, os.path.join(path, "cover_art.jpg"))
				except pylast.MalformedResponseError or pylast.NetworkError as error:
					print("[ERROR] Could not download album art for:\t'{}'".format(tag))
					print("\t{}".format(error))
				except Exception as error:
					print("[ERROR] Unknown error occurred, please investigate.")
					print("\t{}".format(tag))
					print("\t{}".format(error))
				else:
					print("[!] Album art successfully retrieved for {}".format(tag))


def main():
	root = "D:\\CodeProjects\\Python\\music_test_folder"

	organize(root)
	clear_remains(root)
	fetch_album_art(root)


if __name__ == '__main__':
	main()

# ========= Last.fm API account ========= #
# Application name	music_organizer
# API key	d43c497febfef4ba166a51eca0932b90
# Shared secret	1ce6e93f6e2c1329262484f41901ad2c
# Registered to	nivgmann
