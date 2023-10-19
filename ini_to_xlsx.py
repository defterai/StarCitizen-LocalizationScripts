#!/usr/bin/python

# Convert global.ini => global.ini.xlsx

import os
import sys
import pathlib
import argparse
import configparser
from modules.localization import * 


def main(args):
    try:
        print("Convert ini to xsls: {0} -> {1}".format(args.input, args.output))
        config = configparser.ConfigParser()
        if not config.read('convert.ini'):
            print('Note: No convert config file - convert.ini')
        LocalizationIni.SetEnableParseExceptions(args.no_errors)
        LocalizationIni.SetInteractiveMode(False)
        print("Process ini...")
        inputIni = LocalizationIni.FromIniFile(args.input)
        if not args.no_split and 'split-documents' in config:
            print("Split ini...")
            split = splitConfig(config['split-documents'])
            mainIni = LocalizationIni.Empty()
            splitInis = {}
            for splitFile in split.files:
                splitInis[splitFile] = LocalizationIni.Empty()
            for item in inputIni.getItems():
                keyFile = split.searchKeyFile(item[0])
                if keyFile:
                    splitInis[keyFile].putKeyValue(item[0], item[1])
                else:
                    mainIni.putKeyValue(item[0], item[1])
            print(f'Write output main {args.output}...')
            mainIni.saveToXlsxFile(args.output, 'global.ini')
            print(f'Written lines: {mainIni.getItemsCount()}')
            outPath = pathlib.Path(args.output).parent.absolute()
            for splitFile in splitInis:
                splitIni = splitInis[splitFile]
                print(f"Write output split {splitFile}.xlsx...")
                splitIni.saveToXlsxFile(os.path.join(outPath, splitFile + ".xlsx"), splitFile)
                print(f"Written lines: {splitIni.getItemsCount()}")
        else:
            print("Write output xlsx...")
            inputIni.saveToXlsxFile(args.output, "global.ini")
            print(f"Written lines: {inputIni.getItemsCount()}")
    except KeyboardInterrupt:
        print("Interrupted")
        return 1
    except Exception as err:
        print("Error: {0}".format(err))
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert INI file to multi language XLSX document.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='?', metavar='FILENAME', default='global.ini', help='Input INI file')
    parser.add_argument('-o', '--output', metavar='OUT_FILENAME', default='global.ini.xlsx', help='Directs the output to a file name of your choice')
    parser.add_argument('-l', '--lang', metavar='LANGUAGE', default='uk', help='Input file language locale')
    parser.add_argument('--no-split', action='store_true', default=False, help='Disable split output XLSX document')
    parser.add_argument('--no-errors', action='store_true', default=False, help='Do not allow errors and break after first error')
    sys.exit(main(parser.parse_args()))
