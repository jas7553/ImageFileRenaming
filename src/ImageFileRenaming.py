"""
A set of tools for renaming image files based on when the image was captured.

@author: Jason A Smith
"""
import argparse
import os
import shutil

from datetime import datetime

from PIL import Image

DATE_TIME_ORIGINAL_KEY = 36867
DATE_TIME_ORIGINAL_FORMAT = '%Y:%m:%d %H:%M:%S'

VERBOSE = False

def get_date_taken(filepath):
    """Get the timestamp representing when the image was taken.

    The result will be in the format of:
        '%Y-%m-%d %H.%M.%S'

    E.g.:
        '2012-01-02 20.01.49'

    If the file has no EXIF metadata for the date taken, None is returned.

    Reference:
        http://www.exiv2.org/tags.html
  
    @param filepath: path to the image file
    @type filepath: str
    @return: The timestamp representing when the image was taken
    @rtype: str or None
    """
    try:
        date_taken_timestamp = Image.open(filepath)._getexif()[DATE_TIME_ORIGINAL_KEY]
    except KeyError:
        return None

    date_taken = datetime.strptime(date_taken_timestamp, DATE_TIME_ORIGINAL_FORMAT)
    return date_taken.strftime('%Y-%m-%d %H.%M.%S')

def get_image_files_in_directory(dirpath, should_recurse=False):
    """Get all the image files contained in a directory.

    @param dirpath: path to the directory in which to search
    @type dirpath: str
    @return: The image files in the given directory
    @rtype: generator<str>
    """
    return (filepath for filepath
            in get_files_in_directory(dirpath, should_recurse)
            if is_image_file(filepath))

def get_files_in_directory(dirpath, should_recurse=False):
    """Gets all the filepaths in a directory.

    @param dirpath: path to the directory in which to search
    @type dirpath: str
    @param should_recurse: Recurse into sub-directories and return those filepaths as well
    @type should_recurse: bool
    @return: The files in the given directory
    @rtype: generator<str>
    """
    os_walk_values = os.walk(dirpath) if should_recurse else [next(os.walk(dirpath))]
    for dirpath, _, filenames in os_walk_values:
        for filename in filenames:
            yield dirpath + os.sep + filename

def is_image_file(filepath):
    """Determine whether or not a file is an image.

    A file is an image if and only if the PIL.Image.open function does not
    raise an IOError.

    @param filepath: path to the file to examine
    @type filepath: str
    @return: True if the file is an image, False otherwise
    @rtype: bool
    """
    try:
        Image.open(filepath)
        return True
    except IOError:
        return False

def rename_images_by_date_taken(dirpath, should_recurse=False, should_force=False):
    """
    Applies rename_image_by_date_taken to all images files in a given directory.

    @param dirpath: path to the directory of images to be renamed
    @type dirpath: str
    @param should_force: whether or not the user should be prompted before moving the file
    @type should_force: bool
    """
    for filepath in get_image_files_in_directory(dirpath, should_recurse):
        rename_image_by_date_taken(filepath, should_force)

def rename_image_by_date_taken(filepath, should_force=False):
    """Rename image files based on their DateTimeOriginal Exif metadata.

    For each image in the given directory, rename the file based on the date
    and time when the original image data was generated.

    @param filepath: path to the image file to be renamed
    @type filepath: str
    @param should_force: whether or not the user should be prompted before moving the file
    @type should_force: bool
    """
    if not is_image_file(filepath):
        return

    dir_name, _ = os.path.split(filepath)
    date_taken_timestamp = get_date_taken(filepath)
    _, extension = os.path.splitext(filepath)

    if date_taken_timestamp is None:
        if VERBOSE: print('No date taken information for "' + filepath + '"')
        return

    new_filepath = dir_name + os.sep + date_taken_timestamp + extension

    if should_force:
        should_rename = True
        if VERBOSE: print('Renaming: "' + filepath + '" -> "' + new_filepath + '"')
    else:
        try:
            response = input('Rename "' + filepath + '" -> "' + new_filepath + '" [n]? ').lower()
        except (EOFError, KeyboardInterrupt):
            exit()
        should_rename = response in ('y', 'yes')

    if should_rename:
        shutil.move(filepath, new_filepath)

if __name__ == '__main__':
    program_description = 'Rename all the image FILEs (the current directory by default), ' + \
                          'based on when the image was captured.'
    parser = argparse.ArgumentParser(description=program_description)

    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Read all files under each directory, recursively.')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Do not prompt, just rename the image file(s) without asking.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Be extra verbose.')
    parser.add_argument('files', metavar='FILE', nargs='*', default='.')

    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    for path in args.files:
        if not os.path.exists(path):
            raise FileNotFoundError('Cannot find the file specified: "' + path + '"')

        elif os.path.isdir(path):
            rename_images_by_date_taken(path, should_recurse=args.recursive, should_force=args.force)

        elif os.path.isfile(path):
            rename_image_by_date_taken(path, should_force=args.force)

        else:
            raise RuntimeError('Unexpected case: path exists but is not a file or directory')
