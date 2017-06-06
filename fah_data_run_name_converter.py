#!/usr/bin/env python

""" Renumber all RUN folders of a F@H dataset to correspond to RMSD.
    For instance, RUN0 will be the lowest in RMSD (Angstrom)
    and RUN N should be the highest in RMSD.
    The script accepts the working directory of the data Proj<#>
    and a .csv with the mapping values in the following format:

        OLD RUN, RMSD, NEW RUN
"""
import argparse
import os
import re


def valid_file(path):
    """ Function to check the existence of a file.
        Used in conjunction with argparse to check that the given parameter
        files exist.
    """
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(
            '\"{}\" does not exist'.format(path) +
            '(must be in the same directory or specify full path).')
    return path


def valid_dir(path):
    """ Function to check the existence of a directory.
        Used in conjunction with argparse to check that the given parameter
        dataset exist.
    """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(
            '\"{}\" does not exist'.format(path) +
            '(must be in the same directory or specify full path).')
    return path


class FAHDataRunNameConverter(object):

    """Class for renumbering all RUN folders of a F@H dataset to correspond to RMSD."""

    def __init__(self, working_directory, mapper, dry_run=False):
        if not os.path.isdir(working_directory):
            raise OSError(
                2, 'No such file or directory', working_directory)
        self.working_directory = os.walk(working_directory)
        if not os.path.isfile(mapper):
            raise OSError(2, 'No such file or directory', mapper)
        self.mapper = mapper
        self.mapper_dict = self.create_mapper_dict()
        self.dry_run = dry_run

    def create_mapper_dict(self):
        """Method to create the mapper dictionary"""
        mapper_file = open(self.mapper, mode='r')
        mapper_lines = mapper_file.readlines()
        mapper_line_splits = [line.rstrip().split(',')
                              for line in mapper_lines]
        mapper_dict = {line_split[0]: (line_split[1], line_split[2])
                       for line_split in mapper_line_splits}
        return mapper_dict

    def display_mapper_info(self):
        """Method that displays mapper input information."""
        print '{0}Mapper Information{0}'.format('-' * 6)
        format_string = '{:<10}{:<10}{:<10}'
        print format_string.format('OLD RUN', 'RMSD', 'NEW RUN')
        for key, value in self.mapper_dict.iteritems():
            print format_string.format(key, value[0], value[1])
        print '-' * 30

    def convert_generator(self):
        """Method to genenerate conversion values."""
        for root, _, _ in self.working_directory:
            if 'RUN' in root:
                if 'CLONE' not in root:
                    root_search = re.search('(?<=RUN)\d+', root)
                    if root_search is not None:
                        root_run_number = root_search.group(0)
                        new_run_number = self.mapper_dict.get(root_run_number)[1]
                        new_root = root.replace(root_run_number, new_run_number)
                        yield root, new_root
                    else:
                        pass

    def display_dry_run_info(self):
        """Method to display dry-run information."""
        for root, new_root in self.convert_generator():
            print '{:<26} -> {}'.format(root, new_root)
        print '-' * 30

    def convert(self):
        """Method for renaming RUN folders to RMSD-determined name."""
        for root, new_root in self.convert_generator():
            try:
                os.rename(root, new_root)
            except OSError:
                print '{0}ERROR{0}'.format('-' * 12)
                print '{:<26} -x> {}'.format(root, new_root)
                print '{} already exists.'.format(new_root)
                print '{}'.format('-' * 30)

    def __main__(self):
        """The RUN folder converter."""
        if self.dry_run:
            self.display_mapper_info()
            self.display_dry_run_info()
        else:
            self.convert()
        print 'Done.'


if __name__ == '__main__':
    MODULE_DESCRIPTION = str("Renumber all RUN folders of a F@H dataset to correspond to RMSD.\n" +
                             "For instance, RUN0 will be the lowest in RMSD (Angstrom)\n" +
                             "and RUN N should be the highest in RMSD.\n" +
                             "The script accepts the working directory of the data Proj<#>\n" +
                             "and a .csv with the mapping values in the following format:\n\n" +
                             "OLD RUN, RMSD, NEW RUN")
    ARGUMENT_PARSER = argparse.ArgumentParser(description=MODULE_DESCRIPTION,
                                              formatter_class=argparse.RawTextHelpFormatter)
    ARGUMENT_PARSER.add_argument('project_root',
                                 type=valid_dir,
                                 metavar='PROJECT_ROOT',
                                 help='Path to the root of the F@H project')
    ARGUMENT_PARSER.add_argument('mapper',
                                 type=valid_file,
                                 metavar='MAPPER',
                                 help='A .csv with the mapping values')
    ARGUMENT_PARSER.add_argument('--dry-run',
                                 action='store_true',
                                 default=False,
                                 help='Display verbose output' +
                                 '...without doing scary stuff. Promise.')
    ARGS = ARGUMENT_PARSER.parse_args()
    FAHDataRunNameConverter(ARGS.project_root,
                            ARGS.mapper,
                            ARGS.dry_run).__main__()