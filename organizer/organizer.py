import os
from shutil import move, SameFileError, rmtree
import pylast
import urllib.request
from sys import argv
import argparse
import mutagen

# constants
DIR_DEFAULT = '%A/%y - %a'
FILE_DEFAULT = '%tn - %t'
ARTIST = 'TPE1'
ALBUM = 'TALB'
TITLE = 'TIT2'
TRACK = 'TRCK'
YEAR = 'TDRC'
ALBUM_ART = 'APIC'


def organize(dir_path: str, dir_pattern: str = "", file_pattern: str = "", script: bool = False):
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

	print("\nOrganizing directory: '{}'\n".format(dir_path))

	total_files = sum([len(files) for path, dirs, files in os.walk(dir_path)])
	files_done = 0

	dir_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(dir_path):
		for file in files:
			# if is_audio_file(file):
			file_path = os.path.join(path, file).replace('\0', '')
			try:
				tag = generate_tag(file_path)
			except mutagen.MutagenError:
				continue
			if tag:
				dir_name = generate_name(tag, dir_pattern)
				dst_path = create_directory(dir_path, dir_name)
				file_ext = file.split('.')[-1]
				formatted_name = "{}.{}".format(generate_name(tag, file_pattern), file_ext)
				formatted_name = os.path.join(dst_path, formatted_name.replace('\0', ''))
				move_file(file_path, os.path.join(dst_path, formatted_name))
			files_done += 1
			yield files_done * 100 / total_files  # percent of files covered out of all files

	print("\nDone organizing directory: '{}'\n".format(dir_path))


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
	try:
		tag = mutagen.File(file_path)
	except mutagen.MutagenError as error:
		print("[ERROR] Unknown error occurred reading tags from file: '{}'".format(file_name))
		print("\t{}\t{}".format(error.__class__, error))
		tag = None
	except Exception as error:
		print("[ERROR] Unknown error occurred reading tags from file: '{}'".format(file_path))
		print("\t{}\t{}".format(error.__class__, error))
		tag = None
	return tag


def is_audio_file(file: str):
	"""
	Checks if file is one of several common audio file types.

	:param file: file name or path
	:return: True if file is audio file, False otherwise
	"""
	extensions = ('mp3', 'mp4', 'wmv', 'mpg', 'mpeg', 'm3u', 'mid',
				  'wma', 'midi', 'wav', 'm4a')
	return file.endswith(extensions)


def create_directory(dir_path: str, dir_name: str) -> str:
	"""
	Creates directory at specified path.

	:param dir_path: parent directory path
	:param dir_name: directory name
	:return: path for new directory
	"""
	new_path = os.path.join(os.path.abspath(dir_path), dir_name).split('\0')[0]
	try:
		if not os.path.exists(new_path):
			os.makedirs(new_path)
			print("[!] Directory '{}' created successfully.".format(dir_name))
		else:
			# print('[!] Directory "{}" already exists, no action taken.'.format(dir_name))
			pass
	except (OSError, ValueError) as error:
		print("[ERROR] Could not create directory: '{}'".format(os.path.join(dir_path, dir_name)))
		print("\t{}\t{}".format(error.__class__, error))
	return str(new_path)


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
		.replace('%A', remove_forbidden_chars(str(tag[ARTIST])) if tag[ARTIST] else "Various Artists") \
		.replace('%a', remove_forbidden_chars(str(tag[ALBUM])) if tag[ALBUM] else "Untitled Album") \
		.replace('%tn', str(tag[TRACK]).zfill(2) if tag[TRACK] else "") \
		.replace('%t', remove_forbidden_chars(str(tag[TITLE])) if tag[TITLE] else "Untitled") \
		.replace('%y', str(tag[YEAR]) if tag[YEAR] else "")


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
		_, file_name = os.path.split(file_path)
		move(file_path, dst_path.strip())
	except SameFileError:
		pass
	except OSError as error:
		if isinstance(error, FileNotFoundError):
			print("[!] File '{}' already in destination, no action taken.".format(file_name))
		else:
			print("[ERROR] Could not move file to destination: {}".format(dst_path))
			print("\t{}\t{}".format(error.__class__, error))
	else:
		print("[!] File '{}' moved successfully.".format(file_name))


def clear_remains(dir_path: str) -> None:
	"""
	Deletes every directory that is either empty,
	or has no audio files in it.

	As of now, doesn't handle read-only files.
	Also has a bug where some directories aren't deleted, but no error is thrown.
	Possibly related to paths containing Hebrew.

	:param dir_path: parent directory path
	"""
	print("\nCleaning directory: '{}'\n".format(dir_path))

	abs_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(abs_path):
		for directory in dirs:
			if contains_no_audio(os.path.join(path, directory)):
				try:
					rmtree(os.path.join(path, directory))
				except Exception as error:
					print("[ERROR] Could not delete directory: '{}'".format(directory))
					print("\t{}\t{}".format(error.__class__, error))
				else:
					print("[!] Directory '{}' deleted successfully.".format(directory))
	print("\nDone cleaning directory: '{}'\n".format(dir_path))


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


def fetch_album_art(dir_path: str, script: bool = False):
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
			return 0
		else:
			print()

	print("\nFetching art for directory: '{}'\n".format(dir_path))

	total_albums = 0
	for _, _, files in os.walk(dir_path):  # can probably be achieved more efficiently
		total_albums += 1 if [file for file in files
							  if is_audio_file(file) and "folder.jpg" not in files] else 0
	done = 0

	for url, path, tags in get_image_urls(dir_path):
		if issubclass(type(url), Exception):  # if url is an error object
			print("[ERROR] Could not download album art for:\t'{}'".format(path))
			print("\t{}\t{}".format(url.__class__, url))
		else:
			try:
				urllib.request.urlretrieve(url, path)
			except (urllib.request.HTTPError, FileNotFoundError) as error:
				print("[ERROR] Could not download album art:\t'{}'".format(path))
				print("\t{}\t{}".format(error.__class__, error))
			except Exception as error:
				print("[ERROR] Unknown error occurred while retrieving album art:")
				print("\t{}".format(path))
				print("\t{}\t{}".format(error.__class__, error))
			else:
				with open(path, 'rb') as album_art:
					data = album_art.read()
					for tag in tags:
						tag[ALBUM_ART] = mutagen.id3.APIC(encoding=3, mime='image/jpeg', type=3,
														  desc=u'Cover', data=data)
						tag.save()
				print("[!] Album art successfully retrieved:\t{}".format(path))
		done += 1
		yield done * 100 / total_albums
	print("\nDone fetching art for directory: '{}'\n".format(dir_path))


def get_image_urls(dir_path: str) -> tuple:
	"""
	Gets image urls for every album art under given directory, including under subdirectories.

	:param dir_path: given directory
	:return: yields tuple that consists of: (error if occurs or url, url path, album tags)
	"""
	network = pylast.LastFMNetwork(api_key='d43c497febfef4ba166a51eca0932b90',
								   api_secret='1ce6e93f6e2c1329262484f41901ad2c')
	dir_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(dir_path):
		if not contains_no_audio(path) and "folder.jpg" not in files:
			tags = []
			for file in files:
				tags.append(generate_tag(os.path.join(path, file)))
			if tags:
				try:
					album = network.get_album(tags[0][ARTIST], tags[0][ALBUM])
					image_url = album.get_cover_image()  # by default returns 300x300 sized image
					image_url = image_url.replace('300x300', '600x600')
				except Exception as error:
					yield (error, path, None)
				else:
					# yields (image url, final image path, album tags) tuple
					yield (image_url, os.path.join(path, "folder.jpg"), tags)


def main(arg_list):
	if arg_list:
		parser = argparse.ArgumentParser(description='Organize and fetch album art for your music library.')
		parser.add_argument('-d', '--directory', nargs='+', required=True)
		args = parser.parse_args()
		root = args.directory[0]
	else:
		root = "D:\CodeProjects\Python\music_organizer\music_test_folder"

	for percent in organize(root, script=True):
		pass
	clear_remains(root)
	for percent in fetch_album_art(root, script=True):
		pass


if __name__ == '__main__':
	main(argv[1:])

# ========= Last.fm API account ========= #
# Application name	music_organizer
# API key	d43c497febfef4ba166a51eca0932b90
# Shared secret	1ce6e93f6e2c1329262484f41901ad2c
# Registered to	nivgmann
