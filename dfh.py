#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('backup_path', type=str, help='path to duplicati backup, e.g. "/media/backup"')
parser.add_argument('dp_path', type=str, help='path to duplicati database, e.g. "~/duplicati_db.sqlite"')
parser.add_argument('include_filter', type=str, help='filter of included path(s) to find, might contain "?" or "*"')
args = parser.parse_args()

if not os.path.exists(args.backup_path):
    print('{} path not found'.format(args.backup_path))

if not os.path.exists(args.dp_path):
    print('{} path not found'.format(args.dp_path))

def get_proc_output(cmd):
    cmds = cmd.split()
    proc = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    bstrs = proc.stdout.readlines()
    strs = [b.decode('utf-8') for b in bstrs]
    return strs

def get_number_of_backups():
    print('getting backup info...')
    cmd = 'duplicati-cli find file://{} --dbpath={}'.format(args.backup_path, args.dp_path)
    out = get_proc_output(cmd)
    out_ok = any(['Listing filesets' in o for o in out])
    if not out_ok:
        print('cannot get list of backups, quitting')
        sys.exit()
    min_bak = int(out[1].split('\t')[0])
    max_bak = int(out[-1].split('\t')[0])
    print('    found version ranges: [{}, {}]'.format(min_bak, max_bak))
    return (min_bak, max_bak)

min_bak, max_bak = get_number_of_backups()

def count_files():
    print('finding files meeting filter criteria...')
    cmd = 'duplicati-cli compare file://{} --dbpath={} --include="{}" --full-result {} {}'.format(
        args.backup_path, args.dp_path, args.include_filter, max_bak, min_bak)
    out = get_proc_output(cmd)
    out_ok_mod = any([' modified entries' in o for o in out])
    out_ok_add = any([' added entries' in o for o in out])
    out_ok_del = any([' deleted entries' in o for o in out])
    if not (out_ok_mod or out_ok_add or out_ok_del):
        print('cannot find file {} in backups, quitting'.format(args.include_filter))
        sys.exit()
    files = []
    for line in out:
        if line.startswith('  ~') or line.startswith('  -') or line.startswith('  +'):
            files.append(line.lstrip()[1:].lstrip().rstrip())
    print('    {} file(s) found:'.format(len(files)))
    for f in files:
        print('        {}'.format(f))
    return files

files = count_files()

def get_file_revisions_info():
    print('getting backup revisions...')
    cmd = 'duplicati-cli find file://{} --dbpath={} --include="{}" --full-result --all-versions'.format(
        args.backup_path, args.dp_path, args.include_filter)
    out = get_proc_output(cmd)
    ver_info = [o.rstrip() for o in out[2:] if o.rstrip()]
    print('    {} backup revisions found'.format(len(ver_info)))
    return ver_info

if len(files) == 1:
    ver_info = get_file_revisions_info()
assert len(ver_info) == 1 + max_bak - min_bak

def find_changed_revisions():
    print('checking file revision changes...')
    modified = []
    added = []
    deleted = []
    for lo, hi in zip(range(max_bak-1, min_bak-1, -1), range(max_bak, min_bak, -1)):
        cmd = 'duplicati-cli compare file://{} --dbpath={} --include="{}" --full-result {} {}'.format(
            args.backup_path, args.dp_path, args.include_filter, hi, lo)
        out = get_proc_output(cmd)
        out_mod = any(['1 modified entries' in o for o in out])
        out_add = any(['1 added entries' in o for o in out])
        out_del = any(['1 deleted entries' in o for o in out])
        if out_mod:
            modified.append(lo)
        if out_del:
            deleted.append(lo)
        if out_add:
            added.append(lo)
    if added:
        print('    added versions:')
        for m in added:
            print('        {}'.format(ver_info[m]))
    if modified:
        print('    modified versions:')
        for m in modified:
            print('        {}'.format(ver_info[m]))
    if deleted:
        print('    deleted versions:')
        for m in deleted:
            print('        {}'.format(ver_info[m]))
    if not (modified or added or deleted):
        print('    no modified versions found')

if len(files) > 1:
    print('    narrow your include filter in order to get history of an individual file')
else:
    find_changed_revisions()
