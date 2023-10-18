#!/usr/bin/python

# Convert global.ini => global.ini.xlsx

import sys
import pathlib
import argparse
import configparser
from modules.localization import * 


def main(args):
    try:
        print(f'Convert ini to xlsx (with ref {args.ref}): {args.input} -> {args.output}')
        config = configparser.ConfigParser()
        if not config.read('convert.ini'):
            print('Note: No convert config file - convert.ini')
        LocalizationIni.SetEnableParseExceptions(args.no_errors)
        LocalizationIni.SetInteractiveMode(False)
        print(f'Process ini {args.input}...')
        inputIni = LocalizationIni.FromIniFile(args.input)
        print('Process reference ini {args.ref}...')
        referenceIni = LocalizationIni.FromIniFile(args.ref)
        if not args.no_split and 'split-documents' in config:
            print("Split ini...")
            split = splitConfig(config['split-documents'])
            mainXlsx = MultiLangXlsx.Empty(args.lang)
            mainXlsx.setAutoMarkEmptyAsTranslated(True)
            splitXlsxDocs = {}
            for splitFile in split.files:
                splitXlsxDocs[splitFile] = MultiLangXlsx.Empty(args.lang)
                splitXlsxDocs[splitFile].setAutoMarkEmptyAsTranslated(True)
            for key, value in referenceIni.getItems():
                translateValue = inputIni.getKeyValue(key)
                if args.all_keys or translateValue:
                    keyFile = split.searchKeyFile(key)
                    if keyFile:
                        splitXlsxDocs[keyFile].append(key, value, translateValue)
                    else:
                        mainXlsx.append(key, value, translateValue)
            print(f'Write output main {args.output}...')
            mainXlsx.saveToXlsxFile(args.output, 'global.ini')
            print(f'Written lines: {mainXlsx.getItemsCount()}')
            outPath = pathlib.Path(args.output).parent.absolute()
            for splitFile, splitXlsx in splitXlsxDocs.items():
                print(f'Write output split {splitFile}.xlsx...')
                splitXlsx.saveToXlsxFile(os.path.join(outPath, splitFile + ".xlsx"), splitFile)
                print(f'Written lines: {splitXlsx.getItemsCount()}')
        else:
            print('Write output xlsx...')
            outputXlsx = MultiLangXlsx.Empty(args.lang)
            for key, value in referenceIni.getItems():
                translateValue = inputIni.getKeyValue(key)
                if args.all_keys or translateValue:
                    outputXlsx.append(key, value, translateValue)
            outputXlsx.saveToXlsxFile(args.output, args.input)
            print(f'Written lines: {outputXlsx.getItemsCount()}')
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error: {0}'.format(err))
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert INI file to multi language XLSX document with reference global_ref.ini.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='?', metavar='FILENAME', default='global.ini', help='Input INI file')
    parser.add_argument('-o', '--output', metavar='OUT_FILENAME', default='global.ini.xlsx', help='Directs the output to a file name of your choice')
    parser.add_argument('-r', '--ref', metavar='REF_FILENAME', default='global_ref.ini', help='Reference game global.ini');
    parser.add_argument('-l', '--lang', metavar='LANGUAGE', default='uk', help='Input file language locale')
    parser.add_argument('--all-keys', metavar='ENABLED', type=bool, default=True, help='Add all keys from reference ini even they not translated')
    parser.add_argument('--no-split', action='store_true', default=False, help='Disable split output XLSX document')
    parser.add_argument('--no-errors', action='store_true', default=False, help='Do not allow errors and break after first error')
    sys.exit(main(parser.parse_args()))
