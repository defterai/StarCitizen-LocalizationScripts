#!/usr/bin/python

# Requirements:
# pip install transliterate

import sys
import argparse
from transliterate import translit
from modules.localization import * 

def main(args):
    try:
        if args.output:
            outputFilename = args.output
        else:
            outputFilename = 'global.ini.' + args.lang
        print(f'Load {args.input}...')
        inputIni = LocalizationIni.FromIniFile(args.input)
        print(f'Transliterate {args.input}...')
        outputIni = LocalizationIni.Empty()
        for key, value in inputIni.getItems():
            outputIni.putKeyValue(key, translit(value, args.lang, reversed=True))
        print(f'Save {outputFilename}...')
        outputIni.saveToIniFile(outputFilename)
    except KeyboardInterrupt:
        input('Interrupted')
        return 1
    except Exception as err:
        input('Error: {0}'.format(err))
        return 1
    input('Done')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transliterate INI file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='?', metavar='FILENAME', default='global.ini', help='Input INI file')
    parser.add_argument('-o', '--output', metavar='FILENAME', default=None, help='Directs the output to a file name of your choice')
    parser.add_argument('-l', '--lang', metavar='LANGUAGE', default='uk', help='Input file language locale')
    sys.exit(main(parser.parse_args()))