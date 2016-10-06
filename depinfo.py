#!/usr/bin/env python
""" creates a list of dependencies for Debian package from list of packets
This script scans some directory(with deb packets) and for every *.deb file
extracts name and version, then this info could be added
to 'debian/control' file.

usage: depinfo <packages_path> <control_file_path> [<filter_packets>]

"""

import os
import sys
try:
    from debian import deb822
except ImportError as err:
    sys.stderr.write(err)

_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode('utf-8'))


def filtered(items, excludes):
    """
    :type items: list
    :type exludes: list
    :return:
    """
    for path in items:
        name = os.path.basename(path)
        if (name.endswith('.deb') and
            not any(map(lambda s: s in name, excludes))):

            yield path


def extract_from_file_name(filename):
    items = filename.split('_')
    try:

        if len(items) > 1:
            name = items[0]
            version = items[1]
            sys.stdout.write(
                'Setting [ {} {} ] as a dependency\n'.format(name, version)
            )

            return name, version

    except IndexError:
        sys.stderr.write(
            'Failed: can\'t get (name, version) from file {}\n'
            .format(filename)
        )


def main(path='.', control_file_path='debian/control', excludes=''):

    if len(sys.argv) >= 3:
        path = sys.argv[1]
        control_file_path = sys.argv[2]
        try:
            excludes = sys.argv[3]
        except IndexError:
            pass
        finally:
            excludes = excludes.split(',')
    else:
        exit(1)

    if not os.path.isdir(path) and os.path.exists(control_file_path):
        exit(1)

    fl = open(control_file_path, 'rb')

    sources_control_file_obj = deb822.Sources(sequence=fl)
    packages_control_file_obj = deb822.Packages(sequence=fl)

    if 'Depends' not in packages_control_file_obj:
        sys.stderr.write('Could not find `Depends` in control file\n')
        exit(1)

    dependencies = map(extract_from_file_name,
                       filtered(os.listdir(path), excludes))

    packages_control_file_obj['Depends'] = ', '.join(
        [packages_control_file_obj['Depends']] +
        ['{} (={})'.format(k, v) for k, v in dependencies]
    )
    out = open(control_file_path, 'wb')
    out.write(_b(
        sources_control_file_obj.dump()
        + '\n'
        + packages_control_file_obj.dump()
    ))
    out.close()

    return 0

if __name__ == '__main__':
    main()
