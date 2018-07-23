import os
from tinytag import TinyTag, TinyTagException
from shutil import move, SameFileError, rmtree
import pylast
import urllib.request as request
from concurrent.futures import ThreadPoolExecutor
from functools import partial

DIR_DEFAULT = '%A/%y - %a'
FILE_DEFAULT = '%tn - %t'


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
				file_path = os.path.join(path, file).replace('\0', '')
				tag = generate_tag(file_path)
				if tag:
					dir_name = generate_name(tag, dir_pattern)
					dst_path = create_directory(dir_path, dir_name)
					move_file(file_path, dst_path)
					if not missing_tags(tag):
						file_ext = file.split('.')[-1]
						formatted_name = "{}.{}".format(generate_name(tag, file_pattern), file_ext)
						formatted_name = os.path.join(dst_path, formatted_name.replace('\0', ''))
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
			yield files_done * 100 / total_files  # percent of files covered out of all files


def missing_tags(tag) -> bool:
	"""
	Checks whether any of the important tags are missing from a tags object.

	:param tag: tags object
	:return: True if 'artist', 'album', 'year', 'track' or 'title' tag is missing. False otherwise.
	"""
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
	new_path = os.path.join(os.path.abspath(dir_path), dir_name).split('\0')[0]
	try:
		if not os.path.exists(new_path):
			os.makedirs(new_path)
			print("[!] Directory '{}' created successfully.".format(dir_name))
		else:
			print('[!] Directory "{}" already exists, no action taken.'.format(dir_name))
	except (OSError, ValueError) as error:
		# print(r'%s' % os.path.join(dir_path, dir_name))
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
		# print(file_path)
		# print(dst_path)
		move(file_path, dst_path.strip())
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
				try:
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

	# total_files = sum([len(files) for path, dirs, files in os.walk(dir_path)])
	# files_done = 0
	images_data = []
	total_actions = 0

	# # TODO replace with generator
	# network = pylast.LastFMNetwork(api_key='d43c497febfef4ba166a51eca0932b90',
	# 							   api_secret='1ce6e93f6e2c1329262484f41901ad2c')
	# for path, dirs, files in os.walk(dir_path):
	# 	# if not contains_no_audio(path) and (files[0] if files else None) \ # TODO test changes
	# 	# if not contains_no_audio(path) and [file for file in files if is_audio_file(file)][0] \
	# 	# 				and "cover_art.jpg" not in files:
	# 	if not contains_no_audio(path) and "cover_art.jpg" not in files:
	# 		file = [file for file in files if is_audio_file(file)][0] if files else None  # get first audio file
	# 		if file:
	# 			# tag = generate_tag(os.path.join(path, files[0]))
	# 			tag = generate_tag(os.path.join(path, file))
	# 			if tag:
	# 				try:
	# 					album = network.get_album(tag.artist, tag.album)
	# 					image_url = album.get_cover_image()  # by default returns 300x300 sized image
	# 					image_url = image_url.replace('300x300', '600x600')
	# 					# create tuple and add to image_urls list. tuple structure: (final image path, image url)
	# 					images_data.append((image_url, os.path.join(path, "cover_art.jpg"), tag))
	# 					# request.urlretrieve(image_url, os.path.join(path, "cover_art.jpg"))
	# 					total_actions += 1
	# 				except (pylast.MalformedResponseError, pylast.NetworkError) as error:
	# 					print("[ERROR] Could not download album art for:\t'{}'".format(tag))
	# 					print("\t{}\t{}".format(error.__class__, error))
	# 				except Exception as error:
	# 					print("[ERROR] Unknown error occurred while retrieving album art for:")
	# 					print("\t{}".format(tag))
	# 					print("\t{}".format(error))
	# 				# else:
	# 				# 	print("[!] Album art successfully retrieved for:\t{}".format(tag))
	# 	# files_done += len(files)
	# 	# yield files_done * 100 / total_files

	# for path, url in images_data:
	# 	print("path: {}".format(path))
	# 	print("url: {}".format(url))
	done = 0
	for url, path, tag in get_image_urls(dir_path):  # TODO call generator
		if issubclass(type(url), Exception): # if url is an error object
				print("[ERROR] Could not download album art for:\t'{}'".format(tag))
				print("\t{}\t{}".format(url.__class__, url))
		else:
			try:
				# print("trying to download '{}'".format(path))
				request.urlretrieve(url, path)
			except (pylast.MalformedResponseError, pylast.NetworkError) as error:
				print("[ERROR] Could not download album art for:\t'{}'".format(path))
				print("\t{}".format(error))
			except Exception as error:
				print("[ERROR] Unknown error occurred while retrieving album art for:")
				print("\t{}".format(path))
				print("\t{}\t{}".format(error.__class__, error))
			else:
				print("[!] Album art successfully retrieved for:\t{}".format(path))
		done += 1
		# yield done * 100 / total_actions # TODO make it work


def get_image_urls(dir_path: str) -> str:
	network = pylast.LastFMNetwork(api_key='d43c497febfef4ba166a51eca0932b90',
								   api_secret='1ce6e93f6e2c1329262484f41901ad2c')
	dir_path = os.path.abspath(dir_path)
	for path, dirs, files in os.walk(dir_path):
		if not contains_no_audio(path) and "cover_art.jpg" not in files:
			file = [file for file in files if is_audio_file(file)][0] if files else None  # get first audio file
			if file:
				tag = generate_tag(os.path.join(path, file))
				if tag:
					try:
						album = network.get_album(tag.artist, tag.album)
						image_url = album.get_cover_image()  # by default returns 300x300 sized image
						image_url = image_url.replace('300x300', '600x600')
						# total_actions += 1
					# except (pylast.MalformedResponseError, pylast.NetworkError) as error:
					# 	print("[ERROR] Could not download album art for:\t'{}'".format(tag))
					# 	print("\t{}\t{}".format(error.__class__, error))
					# 	yield (None, os.path.join(path, "cover_art.jpg"), tag)
					except Exception as error:
						# print("[ERROR] Unknown error occurred while retrieving album art for:")
						# print("\t{}".format(tag))
						# print("\t{}".format(error))
						yield (error, path, tag)
					else:
						# yield tuple. tuple structure: (image url, final image path, album tags)
						yield (image_url, os.path.join(path, "cover_art.jpg"), tag)
				# else:
				# 	print("[!] Album art successfully retrieved for:\t{}".format(tag))
	# files_done += len(files)
	# yield files_done * 100 / total_files


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
