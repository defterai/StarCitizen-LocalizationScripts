#!/usr/bin/python

import sys
import argparse
from modules.localization import * 

charactersMap = dict({
    # Fix missing in font characters
    '«': '"',
    '»': '"',
    'µ': 'μ',
    # Ukraininan cyryllic
    'ґ': 'г',
    'Ґ': 'Г',
    'і': 'i',
    'І': 'I',
    'ї': 'ï',
    'Ї': 'Ï',
    'є': 'e',
    'Є': 'E',
})

def transform_text(key, text):
    needReplace = False
    for ch in text:
        if ch in charactersMap:
            needReplace = True
            break;
    if not needReplace:
        return text
    result = ''
    replaced = set()
    for ch in text:
        rch = charactersMap.get(ch, ch)
        if rch != ch:
            replaced.update(ch)
        result += rch
    print(f'Note: replace characters in key: {key} {replaced}')
    return result

def main(args):
    try:
        if args.output:
            outputFilename = args.output
        else:
            outputFilename = args.input + ".out"
        print(f'Load {args.input}...')
        inputIni = LocalizationIni.FromIniFile(args.input)
        print(f'Transform {args.input}...')
        outputIni = LocalizationIni.Empty()
        for key, value in inputIni.getItems():
            outputIni.putKeyValue(key, transform_text(key, value))
        if not args.test:
            print(f'Save {outputFilename}...')
            outputIni.saveToIniFile(outputFilename)
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error: {0}'.format(err))
        return 1
    print('Done')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform INI file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='?', metavar='FILENAME', default='global.ini', help='Input INI file')
    parser.add_argument('-o', '--output', metavar='FILENAME', default=None, help='Directs the output to a file name of your choice or input')
    parser.add_argument('--test', action='store_true', default=False, help='Test transform mapping without write output file')
    sys.exit(main(parser.parse_args()))