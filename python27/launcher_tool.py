"""\
A tool to append files to zip which is in turn appended to an other file.
"""
from StringIO import StringIO
import argparse
import glob
import os
import pkgutil
import re
import shutil
import sys
import zipfile


def main():
    parser = argparse.ArgumentParser(description='Launcher assembler')

    parser.add_argument('-o', '--output', metavar='FILE', required=True,
                        help='Filename to write the result to')
    parser.add_argument('--launcher', metavar='EXE',
                        help='Launcher executable to use [default: launcher27.exe]')
    parser.add_argument('--main', required=True, metavar='FILE', help='Start this script')
    parser.add_argument('FILE', nargs='*',
                        help='Add additional files to zip')

    group = parser.add_argument_group('Wheels as dependecies')
    #~ group.add_argument('-i', '--internal-wheel', action='append', default=[],
                       #~ help='Add contents of wheel file to appended zip')
    group.add_argument('-e', '--external-wheel', action='append', default=[],
                       help='Copy wheel file as a whole')
    #~ group.add_argument('-x', '--extract-wheel',  action='append', default=[],
                       #~ help='Extract wheel file (e.g. wheels with binaries)')
    parser.add_argument('--wheel-dir', metavar='DIR', default='wheelhouse',
                        help='Directory containing the wheel files [default: (%(default)s]')

    args = parser.parse_args()

    archive_data = StringIO()
    with zipfile.ZipFile(archive_data, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(args.main, arcname='__main__.py')
        archive.writestr('launcher.py', pkgutil.get_data(__name__, 'launcher.py'))
        for filename in args.FILE:
            archive.write(filename)
        #~ for wheel in args.internal_wheel:
            

    dest_dir = os.path.dirname(args.output)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(args.output, 'wb') as exe:
        if args.launcher:
            exe.write(open(args.launcher, 'rb').read())
        else:
            exe.write(pkgutil.get_data(__name__, 'launcher27.exe'))
        exe.write(archive_data.getvalue())

    if args.external_wheel:
        wheel_destination = os.path.join(os.path.dirname(os.path.abspath(args.output)), 'wheels')
        if not os.path.exists(wheel_destination):
            os.mkdir(wheel_destination)
        for wheel in args.external_wheel:
            distribution_name = re.sub("[^\w\d.]+", "_", wheel, re.UNICODE)
            candidates = glob.glob(os.path.join(args.wheelhouse, '{}*.whl'.format(distribution_name)))
            if len(candidates) > 1:
                raise NotImplementedError('please remove other versions of wheel files, currently this tool can only cope with one versioon per distribution')
            shutil.copy2(candidates[0], wheel_destination)
        

if __name__ == '__main__':
    main()
