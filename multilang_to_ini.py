#!/usr/bin/python

# Convert:
# - global.ini.xlsx [& global_ref.ini] => global.ini
# - global.ini.xliff [& global_ref.ini] => global.ini
# - global.ini.original & global.ini.translation [& global_ref.ini] => global.ini

import sys
import argparse
import configparser
from modules.localization import * 

versionFormat = ' - v{0}'
versionAddKeys = set(['pause_ForegroundMainMenuScreenName'])
excludeTranslateKeys = set(['mobiGlas_ui_notification_Party_Title'])
innerThroughtKeys = None

def isInnerThroughtKey(key):
    global innerThroughtKeys
    if innerThroughtKeys is None:
        with open("inner_throught_keys.txt", "r") as f:
            innerThroughtKeys = f.read().splitlines() 
    for innerThroughtKey in innerThroughtKeys:
        if key.startswith(innerThroughtKey):
            return True
    return False

def compareFormats(refValue, origValue):
    refFormats = LocalizationIni.GetUnnamedFormats(refValue)
    origFormats = LocalizationIni.GetUnnamedFormats(origValue)
    if refFormats != origFormats:
        return False
    refFormats = LocalizationIni.GetNamedFormats(refValue)
    origFormats = LocalizationIni.GetNamedFormats(origValue)
    return LocalizationIni.IsNamedFormatEquals(refFormats, origFormats)

def threeWayMerge(key, refValue, origValue, translateValue, args):
    if (refValue == origValue):
        return translateValue
    if not args.no_outdated_translation and compareFormats(refValue, origValue):
        print(f'Warning: outdated translation key used: {key}')
        return translateValue
    print(f'Warning: reference key used: {key}')
    return refValue

def isTranslatableKey(key, args):
    if key in excludeTranslateKeys:
        print(f'Note: exclude translate key: {key}')
        return False
    if args.no_inner_thought and isInnerThroughtKey(key):
        print(f'Note: exclude inner thought key: {key}')
        return False
    return True


def main(args):
    try:
        print(f'Convert multi language to ini (with ref {args.ref}): {args.files} -> {args.output}')
        splitDocuments = []
        verifyOptions = { 'allowed_characters_file': args.allowed_codepoints }
        LocalizationIni.SetEnableParseExceptions(args.no_errors)
        LocalizationIni.SetInteractiveMode(args.interactive)
        config = configparser.ConfigParser()
        if config.read('convert.ini'):
            if 'general' in config:
                generalConfig = dict(config.items('general'))
                if 'exclude_translate_keys' in generalConfig:
                    excludeTranslateKeys.update([x.strip() for x in filter(None, generalConfig['exclude_translate_keys'].split(',')) if len(x.strip()) > 0])
            if 'verify' in config:
                verifyOptions.update(dict(config.items('verify')))
            if 'split-documents' in config:
                splitDocuments = splitConfig(config['split-documents']).files
        else:
            print('Note: No convert config file - convert.ini')
        if not args.build_import and args.interactive and args.version is None:
            version = input('Enter version (optional): ')
        else:
            version = args.version
        if not args.no_ref:
            print('Process reference ini...')
            referenceIni = LocalizationIni.FromIniFile(args.ref)
        if len(args.files) == 1:
            print(f'Process multi language {args.files[0]}...')
            inputInis = LocalizationIni.FromMultilang(args.files[0], splitDocuments)
            originalIni = inputInis[0]
            translateIni = inputInis[1]
        elif len(args.files) == 2:
            originalIni = LocalizationIni.FromIniFile(args.files[0])
            translateIni = LocalizationIni.FromIniFile(args.files[1])
        else:
            print(f'Error: Too many input files specified - {args.files}')
            return 1
        if originalIni.getItemsCount() > 0:
            print('Translated keys: {0}/{1} ({2:.2f}%)'.format(translateIni.getItemsCount(), originalIni.getItemsCount(),
                                                               translateIni.getItemsCount() / originalIni.getItemsCount() * 100))
            print('           left: {0}'.format(originalIni.getItemsCount() - translateIni.getItemsCount()))
        if args.check:
            print('Check translation...')
            LocalizationVerifier.SetEnableVerifyExceptions(args.no_errors)
            LocalizationVerifier.SetInteractiveMode(args.interactive)
            LocalizationVerifier(verifyOptions).verify(originalIni, translateIni)
        print('Write output...')
        outputIni = LocalizationIni.Empty()
        if referenceIni:
            if args.build_import:
                print('WARNING: Build import ini mode')
                for key, value in referenceIni.getItems():
                    if translateIni.isContainKey(key) and value == originalIni.getKeyValue(key):
                        outputIni.putKeyValue(key, translateIni.getKeyValue(key))
            else:
                for key, value in referenceIni.getItems():
                    writeValue = value
                    if translateIni.isContainKey(key) and isTranslatableKey(key, args):
                        writeValue = threeWayMerge(key, value, originalIni.getKeyValue(key), translateIni.getKeyValue(key), args)
                    if version and (key in versionAddKeys):
                        writeValue = writeValue + versionFormat.format(version)
                        print(f'Info: Added version to key: {key}')
                    outputIni.putKeyValue(key, writeValue)
        else:
            for key, value in originalIni.getItems():
                writeValue = value
                if translateIni.isContainKey(key) and isTranslatableKey(key, args):
                    writeValue = translateIni.getKeyValue(key)
                if version and (key in versionAddKeys):
                    writeValue = writeValue + versionFormat.format(version)
                    print(f'Info: Added version to key: {key}')
                outputIni.putKeyValue(key, writeValue)
        outputIni.saveToIniFile(args.output)
    except KeyboardInterrupt:
        print('Interrupted')
        return 1
    except Exception as err:
        print('Error: {0}'.format(err))
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert multi language translation documents to global.ini with reference global_ref.ini.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('files', nargs='+', help='Input multi language translation document (XLSX, XLIFF) or 2 INI files - original & translate')
    parser.add_argument('-o', '--output', metavar='OUT_FILENAME', default='global.ini', help='Directs the output to a file name of your choice')
    parser.add_argument('-r', '--ref', metavar='REF_FILENAME', default='global_ref.ini', help='Reference game global.ini')
    parser.add_argument('-v', '--version', default=None, help='Add localization version (displayed before main menu)')
    parser.add_argument('-c', '--check', default=True, help='Check for simple mistakes (missing variables, , ect.)')
    parser.add_argument('-a', '--allowed-codepoints', metavar='CODEPOINT_FILENAME', default='allowed_codepoints.txt', help='File with all allowed codepoints for translation file check')
    parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Run interactive and allow specify version from keyboard')
    parser.add_argument('--no-ref', action='store_true', default=False, help='Do not use reference global_ref.ini')
    parser.add_argument('--no-outdated-translation', action='store_true', default=False, help='Do not allow outdated translation based on global_ref.ini')
    parser.add_argument('--no-inner-thought', action='store_true', default=False, help='Do not translate known Inner Thought keys (3D font)')
    parser.add_argument('--no-errors', action='store_true', default=False, help='Do not allow errors and break after first error')
    parser.add_argument('--build-import', action='store_true', default=False, help='Build import INI with only translation that match global_ref.ini')
    sys.exit(main(parser.parse_args()))

