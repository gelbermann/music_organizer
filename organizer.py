import os
# import id3reader_p3 as id3reader
from tinytag import TinyTag, TinyTagException
from shutil import move, SameFileError, rmtree
import pylast
import urllib.request as request

DIR_DEFAULT = '%A/%y - %a'
FILE_DEFAULT = '%tn - %t'


# class FileTags:
# 	"""
# 	Class to represent audio file id3 tags.
# 	The only reason for this class' existence is to handle missing tags.
# 	"""
#
# 	def __init__(self, artist, album, year, track, title):
# 		self._artist = artist if artist else "Various Artists"
# 		self._album = album if album else "Untitled Album"
# 		self._year = year if year else "yyyy"
# 		self._title = title if title else "Untitled"
# 		self.track = track
#
# 	def __str__(self):
# 		return "Artist: '{}', Album: '{}', Year: '{}', Title: '{}', Track: {}".format(self._artist, self._album,
# 																					  self._year, self._title,
# 																					  self.track)
#
# 	"""
# 	This class uses getters and setters to prevent any of its attributes
# 	from being set to None.
# 	"""
#
# 	@property
# 	def artist(self):
# 		return self._artist
#
# 	@artist.setter
# 	def artist(self, artist):
# 		self._artist = artist if artist else "Various Artists"
#
# 	@property
# 	def album(self):
# 		return self._album
#
# 	@album.setter
# 	def album(self, album):
# 		self._album = album if album else "Untitled Album"
#
# 	@property
# 	def year(self):
# 		return self._year
#
# 	@year.setter
# 	def year(self, year):
# 		self._year = year if year else "yyyy"
#
# 	@property
# 	def title(self):
# 		return self._title
#
# 	@title.setter
# 	def title(self, title):
# 		self._title = title if title else "Untitled"
#
# 	def missing_tag(self):
# 		return not self._artist or self._artist == "Various Artists" \
# 			   or not self._album or self.album == "Untitled Album" \
# 			   or not self._year or self._year == "yyyy" \
# 			   or not self._title or self._title == "Untitled" \
# 			   or not self.track


def organize(dir_path: str, dir_pattern: str = "", file_pattern: str = "", script: bool = False) -> int:
	"""
	Applies defined pattern to every directory in given path, every sub-directory,
	and every audio file.

	:param dir_path: parent directory path
	:param dir_pattern: pattern to apply to directories
	:param file_pattern: pattern to apply to audio files
	:param script: whether function is run from script or from GUI
	:return: yields percent of files organized
	"""
	if script:
		dir_pattern, file_pattern = get_patterns()

	total_files = sum([len(files) for path, dirs, files in os.walk(dir_path)])
	files_done = 0

	dir_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(dir_path):
		for file in files:
			if is_audio_file(file):
				file_path = os.path.join(path, file)
				tag = generate_tag(file_path)
				if tag:
					dir_name = generate_name(tag, dir_pattern)
					dst_path = create_directory(dir_path, dir_name)
					move_file(file_path, dst_path)
					# if not tag.missing_tag():
					if not missing_tags(tag):
						file_ext = file.split('.')[-1]
						formatted_name = "{}.{}".format(generate_name(tag, file_pattern), file_ext)
						formatted_name = os.path.join(dst_path, formatted_name)
						file_path = os.path.join(dst_path, file)
						try:
							os.rename(file_path, formatted_name)
						except FileExistsError as error:
							print("[ERROR] Couldn't rename file '{}' as it already exists.".format(formatted_name))
							print("\t{}".format(error))
							# os.rename(file_path, file)
						except OSError as error:
							print("[ERROR] Couldn't rename file '{}'.".format(formatted_name))
							print("\t{}".format(error))
			files_done += 1
			yield files_done * 100 // total_files  # percent of files covered out of all files


def missing_tags(tag) -> bool:
	return tag.artist is not None \
		   and tag.album is not None \
		   and tag.year is not None \
		   and tag.track is not None \
		   and tag.title is not None


def get_patterns() -> (str, str):
	"""
	Displays all necessary messages about name patterns, and asks user for custom patterns.

	:return: tuple made of chosen directory name file name patterns
	"""
	print("Parameters for name patterns:", "%A - artist", "%a - album",
		  "%t - title", "%tn - track number", "%y - year", sep='\n')
	print()
	print("Default album directory pattern: ", DIR_DEFAULT, " (e.g. 'Metallica/1984 - Ride the Lightning')")
	print("Default file name pattern: ", FILE_DEFAULT, " (e.g. '01 - Fight Fire with Fire')")
	print()

	dir_pattern = input("Please enter album directory name pattern (press enter to skip): ")
	dir_pattern = DIR_DEFAULT if dir_pattern == "" else dir_pattern
	file_pattern = input("Please enter track name pattern (press enter to skip): ")
	file_pattern = FILE_DEFAULT if file_pattern == "" else file_pattern
	return dir_pattern, file_pattern


def generate_tag(file_path: str):
	"""
	Generates tags object for given audio file.

	:param file_path: file's full path.
	:return: tags object. If errors occur, returns None.
	"""
	_, file_name = os.path.split(file_path)

	# try:
	# 	reader = id3reader.Reader(file_path)
	# 	tag = FileTags(reader.get_value('performer'),
	# 				   reader.get_value('album'),
	# 				   reader.get_value('year'),
	# 				   reader.get_value('track'),
	# 				   reader.get_value('title'))
	# 	if tag.track:
	# 		tag.track = tag.track.split('/')[0]
	# except id3reader.Id3Error as error:
	# 	print("[ERROR] Couldn't read tags from file: '{}'".format(file_name))
	# 	print("\t{}".format(error))
	# 	tag = None
	# except Exception as error:
	# 	print("[ERROR] Unknown error occurred reading tags from file: '{}'".format(file_path))
	# 	print("\t{}".format(error))
	# 	tag = None
	# return tag

	try:
		tag = TinyTag.get(file_path)
	except TinyTagException as error:
		print("[ERROR] Unknown error occurred reading tags from file: '{}'".format(file_name))
		print("\t{}".format(error))
		tag = None
	except Exception as error:
		print("[ERROR] Unknown error occurred reading tags from file: '{}'".format(file_path))
		print("\t{}".format(error))
		tag = None
	return tag


def is_audio_file(file: str):
	"""
	Checks if file is one of several common audio file types.

	:param file: file name or path
	:return: True if file is audio file, False otherwise
	"""
	extensions = ('mp3', 'mp4', 'wmv', 'mpg', 'mpeg', 'm3u', 'mid',
				  'wma', 'midi', 'wav', 'm4a')  # TODO Replace id3reader with more advanced id3 tags reader
	return file.endswith(extensions)


def create_directory(dir_path: str, dir_name: str) -> str:
	"""
	Creates directory at specified path.

	:param dir_path: parent directory path
	:param dir_name: directory name
	:return: path for new directory
	"""
	new_path = os.path.join(os.path.abspath(dir_path), dir_name).strip()
	try:
		if not os.path.exists(new_path):
			os.makedirs(new_path)
			print("[!] Directory '{}' created successfully.".format(dir_name))
		else:
			print('[!] Directory "{}" already exists, no action taken.'.format(dir_name))
	except OSError as error:
		print("[ERROR] Could not create directory: '{}'".format(os.path.join(dir_path, dir_name)))
		print("\t{}".format(error))
	return new_path


def generate_name(tag, pattern: str) -> str:
	"""
	Generates the name of required directory or file, according to given tags and name pattern.

	Possible pattern parameters:
	%A - artist,
	%a - album,
	%t - title
	%tn - track number
	%y - year

	:param tag: tags object containing raw data for pattern
	:param pattern: pattern string for name generation
	:return: generated name
	"""
	return pattern \
		.replace('%A', remove_forbidden_chars(tag.artist) if tag.artist else "Various Artists") \
		.replace('%a', remove_forbidden_chars(tag.album) if tag.album else "Untitled Album") \
		.replace('%tn', str(tag.track).zfill(2) if tag.track else "") \
		.replace('%t', remove_forbidden_chars(tag.title) if tag.title else "Untitled") \
		.replace('%y', str(tag.year) if tag.year else "")


def remove_forbidden_chars(string: str) -> str:
	# .replace('\'', '_') \
	return string \
		.replace('*', '_') \
		.replace('.', '_') \
		.replace('"', '_') \
		.replace('/', '_') \
		.replace('[', '_') \
		.replace(']', '_') \
		.replace(':', '_') \
		.replace(';', '_') \
		.replace('|', '_') \
		.replace('=', '_') \
		.replace('?', '_') \
		.replace(',', '_')


def move_file(file_path: str, dst_path: str) -> None:
	"""
	Moves file to new location.

	:param file_path: full path for file, as string
	:param dst_path: destination directory's path, as string
	"""
	try:
		move(file_path, dst_path)
	except SameFileError:
		pass
	except OSError as error:
		print("[ERROR] Could not move file to destination: {}".format(dst_path))
		print("\t{}".format(error))
	else:
		_, tail = os.path.split(file_path)
		print("[!] File '{}' moved successfully.".format(tail))


def clear_remains(dir_path: str) -> None:
	"""
	Deletes every directory that is either empty,
	or has no audio files in it.

	As of now, doesn't handle read-only files.
	Also has a bug where some directories aren't deleted, but no error is thrown.
	Possibly related to paths containing Hebrew.

	:param dir_path: parent directory path
	"""
	abs_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(abs_path):
		for directory in dirs:
			if contains_no_audio(os.path.join(path, directory)):
				# print("[!] Directory {} contains no audio".format(directory))
				try:
					# print("trying to delete {}\\{}".format(path, directory))
					rmtree(os.path.join(path, directory))
				except Exception as error:
					print("[ERROR] Could not delete directory: '{}'".format(directory))
					print("\t{}".format(error))
				else:
					print("[!] Directory '{}' deleted successfully.".format(directory))


def contains_no_audio(dir_path: str) -> bool:
	"""
	Checks if directory contains audio files.

	:param dir_path: directory path
	:return: False if contains audio files, True otherwise
	"""
	for path, dirs, files in os.walk(dir_path):
		for file in files:
			if is_audio_file(os.path.join(path, file)):
				return False
	return True


def fetch_album_art(dir_path: str, script=False) -> int:
	"""
	Downloads album art for all albums in given directory, and all its sub-directories.

	:param dir_path: directory path
	:param script: whether function is run from script or from GUI
	:return: yields percent of files organized
	"""
	if script:
		print()
		fetch = input("Do you want to download album art for all albums? [Y/N]: ")
		if fetch.lower() == 'n':
			return
		else:
			print()

	total_files = sum([len(files) for path, dirs, files in os.walk(dir_path)])
	files_done = 0

	network = pylast.LastFMNetwork(api_key='d43c497febfef4ba166a51eca0932b90',
								   api_secret='1ce6e93f6e2c1329262484f41901ad2c')
	for path, dirs, files in os.walk(dir_path):
		if not contains_no_audio(path) and (files[0] if files else None) \
				and "cover_art.jpg" not in files:
			tag = generate_tag(os.path.join(path, files[0]))
			if tag:
				try:
					album = network.get_album(tag.artist, tag.album)
					image_url = album.get_cover_image()  # by default returns 300x300 sized image
					image_url = image_url.replace('300x300', '600x600')
					request.urlretrieve(image_url, os.path.join(path, "cover_art.jpg"))
				except (pylast.MalformedResponseError, pylast.NetworkError) as error:
					print("[ERROR] Could not download album art for:\t'{}'".format(tag))
					print("\t{}".format(error))
				except Exception as error:
					print("[ERROR] Unknown error occurred while retrieving album art for:")
					print("\t{}".format(tag))
					print("\t{}".format(error))
				else:
					print("[!] Album art successfully retrieved for:\t{}".format(tag))
		files_done += len(files)
		yield files_done * 100 // total_files


def main():
	# root = "D:/Niv/Music"
	root = "D:\CodeProjects\Python\music_test_folder"
	print("*** WARNING! DO NOT CONTINUE BEFORE CLOSING ALL OPEN FILES IN RELEVANT FOLDER! ***")
	print()

	organize(root, script=True)
	clear_remains(root)
	fetch_album_art(root)


if __name__ == '__main__':
	main()

# ========= Last.fm API account ========= #
# Application name	music_organizer
# API key	d43c497febfef4ba166a51eca0932b90
# Shared secret	1ce6e93f6e2c1329262484f41901ad2c
# Registered to	nivgmann
