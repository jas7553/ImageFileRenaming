"""
A set of tools for renaming image files based on when the image was captured.

@author: Jason A Smith

@var PROMPT: Whether or not to ask before renaming a file
@type PROMPT: bool
"""
import os
import shutil
import sys

from datetime import datetime

from PIL import Image

DATE_TIME_ORIGINAL_KEY = 36867
DATE_TIME_ORIGINAL_FORMAT = '%Y:%m:%d %H:%M:%S'

PROMPT = True

def get_date_taken(path):
    """Get the timestamp representing when the image was taken.

    The result will be in the format of:
        '%Y-%m-%d %H.%M.%S'

    E.g.:
        '2012-01-02 20.01.49'

    If the file has no EXIF metadata for the date taken, None is returned.

    Reference:
        http://www.exiv2.org/tags.html
  
    @param path: path to the image file
    @type path: str
    @return: The timestamp representing when the image was taken
    @rtype: str or None
    """
    try:
        date_taken_timestamp = Image.open(path)._getexif()[DATE_TIME_ORIGINAL_KEY]
    except KeyError:
        return None

    date_taken = datetime.strptime(date_taken_timestamp, DATE_TIME_ORIGINAL_FORMAT)
    return date_taken.strftime('%Y-%m-%d %H.%M.%S')

def get_image_files_in_directory(path):
    """Get all the image files contained in a directory.

    @param path: path to the directory in which to search
    @type path: str
    @return: The image files in the given directory
    @rtype: generator<str>
    """
    return (file for file in get_files_in_directory(path) if is_image_file(file))

def get_files_in_directory(path):
    """Get all the files contained in a directory.

    @param path: path to the directory in which to search
    @type path: str
    @return: The files in the given directory
    @rtype: generator<str>
    """
    for _, _, files in os.walk(path):
        for file in files:
            yield file

def is_image_file(path):
    """Determine whether or not a file is an image.

    A file is an image if and only if the PIL.Image.open function does not
    raise an IOError.

    @param path: path to the file to examine
    @type path: str
    @return: True if the file is an image, False otherwise
    @rtype: bool
    """
    try:
        Image.open(path)
        return True
    except IOError:
        return False

def rename_images_by_date_taken(path):
    """Rename image files based on their DateTimeOriginal Exif metadata.

    For each image in the given directory, rename the file based on the date
    and time when the original image data was generated.

    @param path: path to the directory of images to be renamed
    @type path: str
    """
    for image_file in get_image_files_in_directory(path):
        date_taken_timestamp = get_date_taken(image_file)
        if date_taken_timestamp is not None:
            _, extension = os.path.splitext(image_file)

            new_image_file = date_taken_timestamp + extension

            print(image_file + ' -> ' + new_image_file)

            if PROMPT:
                response = input('Rename [y]? ').lower()
                should_rename = response in ('', 'y', 'yes')
            else:
                should_rename = True

            if should_rename:
                shutil.move(image_file, new_image_file)
            else:
                continue
        else:
            print('no date taken information available for ' + image_file)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            images_directory = input('Images directory: ')
        except EOFError:
            exit()
    elif len(sys.argv) == 2:
        images_directory = sys.argv[1]
    else:
        print('Usage: python ' + os.path.basename(__file__) + ' directory')
        exit()

    if not os.path.exists(images_directory):
        raise FileNotFoundError('Cannot find the file specified: ' + \
                                "'" + images_directory + "'")

    os.chdir(images_directory)
    rename_images_by_date_taken(images_directory)
