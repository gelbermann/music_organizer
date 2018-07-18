import os
import id3reader_p3 as id3reader
import shutil


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

	# def __hash__(self):
	# 	return hash((self._artist, self._album, self._year))
	#
	# def __eq__(self, other):
	# 	return self._artist == other.artist \
	# 		   and self._album == other.album \
	# 		   and self._year == other.year
	#
	# def __ne__(self, other):
	# 	return not self.__eq__(other)

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


# # def generate_tags(dir_path: str) -> set:
# def generate_tags(dir_path: str):
# 	"""
# 	Generates tags for all audio files in given path and its sub-directories.
#
# 	:param dir_path: path for audio files
# 	:return: set containing all tags as dictionaries converted to tuples
# 	"""
# 	tag = FileTags(None, None, None)
# 	# tag = {'artist': None,
# 	# 			 'album': None,
# 	# 			 'year': None}
# 	print(tag)
# 	tags = set()
# 	abs_path = os.path.abspath(dir_path)
#
# 	# for file in [files if files else "" for path, dirs, files in os.walk(abs_path)]:
# 	for path, dirs, files in os.walk(abs_path):
# 		for file in files:
# 			if is_media_file(file):
# 				try:
# 					reader = id3reader.Reader(os.path.join(path, file))
# 					tag.artist = reader.get_value('performer')
# 					tag.album = reader.get_value('album')
# 					tag.year = reader.get_value('year')
# 				except id3reader.Id3Error as e:
# 					print("Id3Error!: " + str(e))
# 				except Exception as e:
# 					print("General Error!: " + str(e))
# 				else:  # executed if there are no exceptions
# 					print(tag)
# 					tags.add(tag)
# 					# print("Tag is in set: {}".format("True" if tag in tags else "False"))
# 					print("=" * 40)
# 					for _tag in tags:
# 						print(tag)
# 					print()
# 	print()
# 	print("============ tags ============")
# 	for tag in tags:
# 		print(tag)
# 	return tags


def create_directories(dir_path: str, name_pattern: str = "%A/%y - %a"):
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
				except id3reader.Id3Error as e:
					print("Id3Error!: " + str(e))
				except Exception as e:
					print("General Error!: " + str(e))
				else:  # executed if there are no exceptions
					dir_name = generate_directory_name(tag, name_pattern)
					dst_path = create_directory(abs_path, dir_name)
					print()
					print("path:\t{}".format(path))
					copy_file(path, file, dst_path)
				finally:
					print()


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
			print('Creating directory "{}" at path {}'.format(dir_name, dir_path))
			os.makedirs(new_path)
		else:
			print('Directory "{}" already exists, no action taken'.format(dir_name))
	except OSError as error:
		print('Error creating directory "{}" at path {}'.format(dir_name, dir_path))
		# print(error)
	finally:
		print()
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


def copy_file(src_path: str, file_name: str, dst_path: str):
	src_path = os.path.join(src_path, file_name)

	try:
		shutil.copy(src_path, dst_path)
	except shutil.SameFileError:
		print("File '{}' is already in destination, no action taken".format(file_name))
	except OSError as error:
		print("Error copying file to destination '{}' "
			  "destination is not writeable or inaccessible.".format(dst_path))
		print(error)
	else:
		print("File {} copied successfully".format(file_name))
	finally:
		print()


def main():
	root = "/home/nivgelbermann/dev/python/music_test_folder"

	# === OLD CODE ==== generating tags set
	# tags = generate_tags(root)
	# root = os.path.join(root, "_ORGANIZED")
	# for tag in tags:
	# 	dir_name = generate_directory_name(tag)
	# 	create_directory(root, dir_name)

	# create_directory(root, "_ORGANIZED")
	# root = os.path.join(root, "_ORGANIZED")

	create_directories(root)


# TODO iterate over all directories, delete ones with no media files


if __name__ == '__main__':
	main()
