import os
# import fnmatch
import id3reader_p3 as id3reader


class FileTags:
	"""
	Class to represent media file id3 tags.
	"""

	def __init__(self, artist, album, year):
		self._artist = artist
		self._album = album
		self._year = year

	def __str__(self):
		return "{{Artist: '{}', Album: '{}', Year: '{}'}}".format(self._artist, self._album, self._year)

	def __hash__(self):
		return hash((self._artist, self._album, self._year))

	def __eq__(self, other):
		return self._artist == other.artist \
			   and self._album == other.album \
			   and self._year == other.year

	def __ne__(self, other):
		return not self.__eq__(other)

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


def display_contents(dir_path: str):
	for path, dirs, files in os.walk(dir_path):
		print("Subdirectories under " + path + ": " + str(dirs))
		print("Files: " + str(files))
		print()


def generate_tags(dir_path: str) -> set:
	"""
	Generates tags for all audio files in given path and its sub-directories.

	:param dir_path: path for audio files
	:return: set containing all tags as dictionaries converted to tuples
	"""
	tag = FileTags("", "", "")
	tags = set()

	# for file in [files if files else "" for path, dirs, files in os.walk(os.path.abspath(dir_path))]:
	for path, dirs, files in os.walk(os.path.abspath(dir_path)):
		for file in files:
			if is_media_file(file):
				try:
					reader = id3reader.Reader(os.path.join(path, file))
					tag.artist = reader.get_value('performer')
					tag.album = reader.get_value('album')
					tag.year = reader.get_value('year')
				except Exception as e:
					print("Error!: " + str(e))
				else:  # executed if there are no exceptions
					# if tag['artist'] is None:
					# 	pass  # TODO handle empty file tags (Various Artists)
					# else:

					# tup_file_tags = tuple(tag.items())
					# tags.add(tup_file_tags)
					print(tag)
					tags.add(tag)
	# print(len(tags))
	print()
	print("============ tags ============")
	for tag in tags:
		print(tag)
	return tags


def is_media_file(file: str):
	"""
	Checks if file is one of several common media file types.

	:param file: file name or path
	:return: True if file is media file, False otherwise
	"""
	extensions = ('mp3', 'mp4', 'wma', 'wmv', 'avi', 'mpg', 'mpeg', 'm3u', 'mid',
				  'midi', 'wav', 'm4a')
	return file.endswith(extensions)


def create_directory(dir_path: str, dir_name: str):
	"""
	Creates directory at specified path.

	:param dir_path: parent directory path
	:param dir_name: directory name
	"""
	new_path = os.path.join(os.path.abspath(dir_path), dir_name)
	try:
		if not os.path.exists(new_path):
			# print('Creating directory "{}" at path {}'.format(dir_name, dir_path))
			os.makedirs(new_path)
		else:
			pass
	# print('Directory "{}" already exists'.format(dir_name))
	except OSError as error:
		pass


# print('Error creating directory "{}" at path {}'.format(dir_name, dir_path))
# print(error)


def generate_directory_name(tag: FileTags, pattern: str = "%A/%y - %a") -> str:
	# if tag['artist'] is None:
	# 	tag['artist'] = "Various Artists"
	# if tag['album'] is None:
	# 	tag['album'] = "Various Albums"
	# if tag['year'] is None:
	# 	tag['year'] = "yyyy"

	# TODO handle all possible pattern values
	return pattern \
		.replace('%A', tag.artist.replace('/', '_')) \
		.replace('%y', tag.year) \
		.replace('%a', tag.album)


def main():
	root = "D:/CodeProjects/Python/music_test_folder"
	create_directory(root, "_ORGANIZED")

	tags = generate_tags(root)
	root = os.path.join(root, "_ORGANIZED")
	for tag in tags:
		# print(str(tag))
		# print(dict(tag))
		# tag = dict(tag)
		dir_name = generate_directory_name(tag)
		create_directory(root, dir_name)


if __name__ == '__main__':
	main()
