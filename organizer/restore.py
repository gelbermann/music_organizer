import os
import mutagen
from sys import exit


def get_contents(dir_path: str):
	""" Returns a list of (file path, file's mutagen tags) tuples """
	if not os.path.isdir(dir_path):
		print("Directory path invalid, exiting...")
		exit()

	contents = []
	for path, dirs, files in os.walk(dir_path):
		for file in files:
			tag = mutagen.File(file)


if __name__ == "__main__":
	pass
