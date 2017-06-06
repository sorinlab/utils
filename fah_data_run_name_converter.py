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
    value = str(path)
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError(
            '\"{}\" does not exist'.format(value) +
            '(must be in the same directory or specify full path).')
    return value


def valid_dir(path):
    """ Function to check the existence of a directory.
        Used in conjunction with argparse to check that the given parameter
        dataset exist.
    """
    value = str(path)
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(
            '\"{}\" does not exist'.format(value) +
            '(must be in the same directory or specify full path).')
    return value


class FAHDataRunNameConverter(object):

    def __init__(self, working_directory, mapper, dry_run=False):
        if not os.path.isdir(working_directory):
            raise OSError(
                2, 'No such file or directory', '{}'.format(working_directory))
        self.working_directory = working_directory
        if not os.path.isfile(mapper):
            raise OSError(2, 'No such file or directory', '{}'.format(mapper))
        self.mapper = mapper
        self.dry_run = dry_run

    def convert(self):
        mapper_file = open(self.mapper, mode='r')
        mapper_lines = mapper_file.readlines()
        mapper_line_splits = [line.rstrip().split(',')
                              for line in mapper_lines]
        mapper_dict = {line_split[0]: (line_split[1], line_split[2])
                       for line_split in mapper_line_splits}
        if self.dry_run:
            print '{}Mapper Information{}'.format('-' * 6, '-' * 6)
            format_string = '{:<10}{:<10}{:<10}'
            print format_string.format('OLD RUN', 'RMSD', 'NEW RUN')
            for key, value in mapper_dict.iteritems():
                print format_string.format(key, value[0], value[1])
            print '-' * 30
        working_directory_walk = os.walk(self.working_directory)
        for root, _, _ in working_directory_walk:
            if 'RUN' in root:
                if 'CLONE' not in root:
                    root_search = re.search('(?<=RUN)\d+', root)
                    root_run_number = root_search.group(0)
                    run_mapper_info = mapper_dict.get(root_run_number)
                    new_run_number = run_mapper_info[1]
                    new_root = root.replace(root_run_number, new_run_number)
                    if self.dry_run:
                        print '{:<26} -> {}'.format(root, new_root)
                    else:
                        os.rename(root, new_root)
        if self.dry_run:
            print '-' * 30
        else:
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
    ARGUMENT_PARSER.add_argument('--dry_run',
                                 action='store_true',
                                 default=False,
                                 help='Display verbose output.')
    ARGS = ARGUMENT_PARSER.parse_args()
    FAHDataRunNameConverter(
        ARGS.project_root, ARGS.mapper, ARGS.dry_run).convert()