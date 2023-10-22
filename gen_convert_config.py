#!/usr/bin/python

import os
import sys
import argparse
import configparser

def main(args):
    try:
        config = configparser.ConfigParser()
        config.optionxform = str
        config.add_section('general')
        config.set('general', 'exclude_translate_keys', '')
        config.add_section('verify')
        config.set('verify', 'english_words_mismatch', 'true' if args.english_words_mismatch else 'false')
        config.set('verify', 'space_before_newline', 'true' if args.space_before_newline else 'false')
        config.set('verify', 'lost_newline', 'true' if args.lost_newline else 'false')
        config.add_section('split-documents')
        for document in args.documents:
            config.set('split-documents', document, '')
        fileName = os.path.join(args.output_path, 'convert.ini')
        with open(fileName, 'w') as configfile:
            config.write(configfile)
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error:', err)
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate convert configuration file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('documents', nargs='+', metavar='NAMES', help='Names of split documents INI (exclude main document)')
    parser.add_argument('-o', '--output-path', metavar='DIR', default='./', help='Output directory used to store config file')
    parser.add_argument('--english-words-mismatch', action='store_true', default=False, help='Verify flag to detect english words mismatch')
    parser.add_argument('--space-before-newline', action='store_true', default=False, help='Verify flag to detect spaces before new lines')
    parser.add_argument('--lost-newline', action='store_true', default=False, help='Verify flag to detect lost new lines')
    sys.exit(main(parser.parse_args()))