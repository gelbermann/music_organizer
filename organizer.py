import os
# import fnmatch
import id3reader_p3 as id3reader


def display_contents(dir_path: str):
	for path, dirs, files in os.walk(dir_path):
		print("Subfolders under " + path + ": " + str(dirs))
		print("Files: " + str(files))
		print()


def generate_tags(dir_path: str) -> set:
	"""
	Generates tags for all audio files in given path and its sub-directories.

	:param dir_path: path for audio files
	:return: set containing all tags as dictionaries converted to tuples
	"""
	file_tags = {'artist': "",  # TODO segregate this from the function. Maybe make a class?
				 'album': "",
				 'year': ""}
	tags = set()

	# for file in [files if files else "" for path, dirs, files in os.walk(os.path.abspath(dir_path))]:
	for path, dirs, files in os.walk(os.path.abspath(dir_path)):
		for file in files:
			if is_media_file(file):
				try:
					reader = id3reader.Reader(os.path.join(path, file))
					file_tags['artist'] = reader.get_value('performer')
					file_tags['album'] = reader.get_value('album')
					file_tags['year'] = reader.get_value('year')
				except Exception as e:
					print("Error!: " + str(e))
				else:  # executed if there are no exceptions
					if file_tags['artist'] is None:
						pass  # TODO handle empty file tags (Various Artists)
					else:
						tup_file_tags = tuple(file_tags.items())
						tags.add(tup_file_tags)
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
			print('Creating directory "{}" at path {}'.format(dir_name, dir_path))
			os.makedirs(new_path)
		else:
			print('Directory "{}" already exists'.format(dir_name))
	except OSError as error:
		print('Error creating directory "{}" at path {}'.format(dir_name, dir_path))


if __name__ == '__main__':
	root = "D:/CodeProjects/Python/music_test_folder"
	create_directory(root, "_ORGANIZED")

	tags = generate_tags(root)
	root = os.path.join(root, "_ORGANIZED")
	for tag in tags:
		print(dict(tag))
		tag = dict(tag)
		pattern = "%A/%y - %a"
		directory = pattern\
			.replace('%A', tag['artist'].replace('/', '_')) \
			.replace('%y', tag['year']) \
			.replace('%a', tag['album'])
		create_directory(root, directory)
