#!/usr/bin/python

# Convert:
# - global.ini.xlsx => global_base.ini & global.ini
# - global.ini.xliff => global_base.ini & global.ini

import sys
import argparse
import configparser
from modules.localization import * 

def main(args):
    try:
        print(f'Split multi language: {args.file} -> {args.base}, {args.translate}')
        splitDocuments = []
        config = configparser.ConfigParser()
        if config.read('convert.ini'):
            if args.no_split and 'split-documents' in config:
                splitDocuments = splitConfig(config['split-documents']).files
        else:
            print('Note: No convert config file - convert.ini')
        LocalizationIni.SetEnableParseExceptions(args.no_errors)
        LocalizationIni.SetInteractiveMode(False)
        print(f'Process multi language {args.file}...')
        inputInis = LocalizationIni.FromMultilang(args.file, splitDocuments)
        print(f'Write output base {args.base}...')
        inputInis[0].saveToIniFile(args.base)
        print(f'Write output translate {args.translate}...')
        inputInis[1].saveToIniFile(args.translate)
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error: {0}'.format(err))
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split multi language translation document to global_base.ini and global.ini.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', metavar='FILENAME', help='Input multi language translation document (XLSX, XLIFF)')
    parser.add_argument('-b', '--base', metavar='OUT_FILENAME', default='global_base.ini', help='Directs the output of source to a file name of your choice')
    parser.add_argument('-o', '--translate', metavar='OUT_FILENAME', default='global.ini', help='Directs the output of translation to a file name of your choice')
    parser.add_argument('--no-split', action='store_true', default=False, help='Disable support split input documents configured by split-documents section in convert.ini')
    parser.add_argument('--no-errors', action='store_true', default=False, help='Do not allow errors and break after first error')
    sys.exit(main(parser.parse_args()))
