#!/usr/bin/python

# Please install deps before usage:
#
# python -m pip install pandas
# python -m pip install xlrd
# python -m pip install xlsxwriter

import os
import sys
try:
    import pandas
except ImportError:
    pass
import pathlib
import codecs
import math
import re
import collections
import xml.etree.cElementTree as ET

class splitConfig:
    @staticmethod
    def __ReadConfigKey(config, key_name):
        if not key_name in config:
            raise Exception(f"Missing key '{key_name}' in smartCAT config")
        key_value = config[key_name].strip()
        if len(key_value) == 0:
            raise Exception(f"Empty key '{key_name}' value in smartCAT config")
        return key_value

    @staticmethod
    def __ReadConfigKeyArray(config, key_name):
        key_value = splitConfig.__ReadConfigKey(config, key_name)
        return [x.strip() for x in key_value.split(',')]

    def __init__(self, config):
        self.files = []
        self.prefixMap = {}
        for file in config.keys():
            self.files.append(file)
            for prefix in [x.strip() for x in config[file].split(',')]:
                self.prefixMap[prefix] = file

    def searchKeyFile(self, key):
        for prefix in self.prefixMap:
            if key.startswith(prefix):
                return self.prefixMap[prefix]
        return None

class IniParseError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        lineNumber -- number of line which can't be parsed
    """

    def __init__(self, message, lineNumber):
        self.message = message
        self.lineNumber = lineNumber

    def __str__(self):
        return f'{self.message} at line: {self.lineNumber}'

class XlsxParseError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        lineNumber -- number of line which can't be parsed
    """

    def __init__(self, message, lineNumber):
        self.message = message
        self.lineNumber = lineNumber

    def __str__(self):
        return f'{self.message} at line: {self.lineNumber}'

class LocalizationIni:
    __utf8_bom = u'\ufeff'
    __delimiter = '='
    __whitespaces = "\r\n\t\ufeff"
    __namedFormatExpr = re.compile(r'\~([a-z]+)\(([^\)]*)\)')
    __unnamedFormatExpr = re.compile(r'<[^-=< ][^>]*>|%ls|%s|%S|%i|%I|%u|%d|%[0-9.]*f|%\.\*f')
    __englishWordsExpr = re.compile(r'[A-Za-z]+')
    __languageWordsExpr = re.compile(r'[\w-]+', re.UNICODE)
    __parseExceptions = False
    __interactiveMode = False

    @staticmethod
    def __RaiseException(exception):
        if LocalizationIni.__parseExceptions:
            raise exception
        else:
            print("Error: {0}".format(exception))
            if LocalizationIni.__interactiveMode:
                input()

    @staticmethod
    def __ParseKeyValue(line):
        if line:
            strippedLine = line.strip(LocalizationIni.__whitespaces)
            if strippedLine:
                return strippedLine.split(LocalizationIni.__delimiter, 1)
        return None

    @staticmethod
    def __ParseXlsxCellValue(line):
        try:
            if math.isnan(line):
                return None
            else:
                return LocalizationIni.__ParseKeyValue(line)
        except Exception as e:
            return LocalizationIni.__ParseKeyValue(line)

    @staticmethod
    def __LoadFromIniFile(filename):
        data = collections.OrderedDict()
        with codecs.open(filename, "r", "utf-8") as inputFile:
            lineNumber = 1
            for line in inputFile:
                parts = LocalizationIni.__ParseKeyValue(line)
                if parts:
                    if len(parts) != 2:
                        LocalizationIni.__RaiseException(IniParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                    else:
                        data[parts[0]] = parts[1]
                lineNumber += 1
        return data

    @staticmethod
    def __LoadFromXlsxFileColumn(filename, sheetName, columnIndex):
        data = collections.OrderedDict()
        with pandas.ExcelFile(filename) as inputFile:
            sheet = inputFile.parse(sheet_name=sheetName)
            lineNumber = 1
            for row in sheet.values:
                if columnIndex >= len(row):
                   LocalizationIni.__RaiseException(XlsxParseError("Invalid column index {0} for row".format(columnIndex), lineNumber))
                else:
                    parts = LocalizationIni.__ParseXlsxCellValue(row[columnIndex]);
                    if parts:
                        if len(parts) != 2:
                            LocalizationIni.__RaiseException(XlsxParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                        else:
                            data[parts[0]] = parts[1]
                lineNumber += 1
        return data

    @staticmethod
    def __LoadFromXlsxFileColumns(filename, sheetName, columnsCount):
        data = []
        columnIndex = 0
        while columnIndex < columnsCount:
            data.append(collections.OrderedDict())
            columnIndex += 1
        with pandas.ExcelFile(filename) as inputFile:
            sheet = inputFile.parse(sheet_name=sheetName)
            lineNumber = 1
            for row in sheet.values:
                if len(row) == 0:
                    LocalizationIni.__RaiseException(XlsxParseError("Less than {0} columns found".format(columnsCount), lineNumber))
                    lineNumber += 1
                    continue
                parts = LocalizationIni.__ParseXlsxCellValue(row[0]);
                if parts:
                    if len(parts) != 2:
                        LocalizationIni.__RaiseException(XlsxParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                    else:
                        data[0][parts[0]] = parts[1]
                        columnIndex = 1
                        while (columnIndex < columnsCount) and (columnIndex < len(row)):
                            subParts = LocalizationIni.__ParseXlsxCellValue(row[columnIndex]);
                            if subParts:
                                if len(subParts) != 2:
                                    LocalizationIni.__RaiseException(XlsxParseError("Missing translation key value separator '=': {0}".format(parts[0]), lineNumber))
                                else:
                                    if subParts[0] != parts[0]:
                                        LocalizationIni.__RaiseException(XlsxParseError("Translation key change found: {0} -> {1}".format(parts[0], subParts[0]), lineNumber))
                                    else:
                                        data[columnIndex][subParts[0]] = subParts[1]
                            columnIndex += 1
                lineNumber += 1
        return data

    @staticmethod
    def Empty():
        return LocalizationIni(collections.OrderedDict())

    @staticmethod
    def FromIniFile(filename):
        return LocalizationIni(LocalizationIni.__LoadFromIniFile(filename))

    @staticmethod
    def FromXlsxFile(filename, sheetName):
        return LocalizationIni(LocalizationIni.__LoadFromXlsxFileColumn(filename, sheetName, 0))

    @staticmethod
    def FromXlsxFileColumns(filename, sheetName, columnsCount):
        result = []
        if columnsCount > 0:
            dataArray = LocalizationIni.__LoadFromXlsxFileColumns(filename, sheetName, columnsCount)
            for data in dataArray:
                result.append(LocalizationIni(data))
        return result

    @staticmethod
    def FromXlsxFiles(filename, sheetName, columnsCount, filenames):
        result = []
        if columnsCount > 0:
            print(f'Loading {filename}')
            outPath = pathlib.Path(filename).parent.absolute()
            dataArray = LocalizationIni.__LoadFromXlsxFileColumns(filename, sheetName, columnsCount)          
            for filename in filenames:
                print(f'Loading {filename}.xlsx')
                additionalDataArray = LocalizationIni.__LoadFromXlsxFileColumns(os.path.join(outPath, filename + ".xlsx"), filename, columnsCount)
                for i in range(0, columnsCount):
                    dataArray[i].update(additionalDataArray[i])
            for data in dataArray:
                result.append(LocalizationIni(data))
        return result

    @staticmethod
    def FromXliffFile(filename):
        source_ini = LocalizationIni.Empty()
        target_ini = LocalizationIni.Empty()
        tree = ET.ElementTree(file=filename)
        root = tree.getroot()
        ns = {'xliff': root.tag.split('}', 1)[0][1:]}
        trans_units = root.findall('.//xliff:trans-unit', namespaces=ns)
        for trans_unit in trans_units:
            key = trans_unit.get('resname')
            translate = trans_unit.get('translate')
            source_value = trans_unit.find('xliff:source', namespaces=ns)
            target_value =  trans_unit.find('xliff:target', namespaces=ns)
            source_ini.putKeyValue(key, '' if source_value.text is None else source_value.text)
            if translate == 'no' or target_value.get('state') == 'final':
                target_ini.putKeyValue(key, '' if target_value.text is None else target_value.text)
        return [ source_ini, target_ini ]

    @staticmethod
    def FromMultilang(filename, splitDocuments):
        if filename.endswith('.xlsx'):
            return LocalizationIni.FromXlsxFiles(filename, 'global.ini', 2, splitDocuments)
        if filename.endswith('.xliff'):
            return LocalizationIni.FromXliffFile(filename)
        raise Exception(f'Error: unknown input file format {filename}')

    def __init__(self, data):
        self.data = data

    def getItems(self):
        return self.data.items()

    def getItemsCount(self):
        return len(self.data)

    def isContainKey(self, key):
        return key in self.data

    def getKeyValue(self, key):
        return self.data.get(key)

    def putKeyValue(self, key, value):
        self.data[key] = value

    def getKeysSet(self):
        return set(self.data)

    def addLocalizationIni(self, localizationIni):
        for key, value in localizationIni.data.items():
            self.data[key] = value

    def saveToIniFile(self, filename):
        with codecs.open(filename, "w", "utf-8") as outputFile:
            outputFile.write(LocalizationIni.__utf8_bom)
            for key, value in self.data.items():
                outputFile.write(key)
                outputFile.write(LocalizationIni.__delimiter)
                outputFile.write(value)
                outputFile.write('\r\n')

    def saveToXlsxFile(self, filename, sheetName):
        outputData = [ 'en' ]
        for key, value in self.data.items():
            line = key + LocalizationIni.__delimiter + value
            outputData.append(line)
        dataFrame = pandas.DataFrame(outputData, columns=[ 'A' ])
        dataFrame.to_excel(filename, sheet_name=sheetName, encoding='utf8', index=False, header=False)

    @staticmethod
    def GetKeyValueText(key, value):
        return key + LocalizationIni.__delimiter + value

    @staticmethod
    def GetNamedFormats(value):
        return set(LocalizationIni.__namedFormatExpr.findall(value))

    @staticmethod
    def IsNamedFormatEquals(origFormat, translateFormat):
        if origFormat == translateFormat:
            return True
        formatDiff = origFormat - translateFormat
        for missingFormat in formatDiff:
            parts = missingFormat[1].split('|')
            if len(parts) != 2 or (missingFormat[0], parts[0]) not in translateFormat:
                return False
        return True

    @staticmethod
    def GetUnnamedFormats(value):
        return LocalizationIni.__unnamedFormatExpr.findall(value)

    @staticmethod
    def GetTextWithoutFormats(value, removeFormats):
        result = value
        for removeFormat in removeFormats:
            if isinstance(removeFormat, str):
                result = result.replace(removeFormat, " ")
            else:
                result = result.replace(f"~{removeFormat[0]}({removeFormat[1]})", " ")
        return result

    @staticmethod
    def GetCleanText(value, *formats):
        result = value.replace("\\n", " ")
        for removeFormat in formats:
            result = LocalizationIni.GetTextWithoutFormats(result, removeFormat)
        return result

    @staticmethod
    def GetEnglishWords(value):
        return set(LocalizationIni.__englishWordsExpr.findall(value.replace("\\n", " ")))

    @staticmethod
    def GetAnyLanguageWords(value):
        return set(LocalizationIni.__languageWordsExpr.findall(value.replace("\\n", " ")))

    @staticmethod
    def SetEnableParseExceptions(enable):
        LocalizationIni.__parseExceptions = enable;

    @staticmethod
    def SetInteractiveMode(enabled):
        LocalizationIni.__interactiveMode = enabled;

class MultiLangXlsx:

    @staticmethod
    def Empty(language):
        return MultiLangXlsx([[ 'en', language ]])

    def __init__(self, data):
        self.data = data
        self.autoMarkEmptyAsTranslated = False

    def setAutoMarkEmptyAsTranslated(self, enabled):
        self.autoMarkEmptyAsTranslated = enabled

    def getItemsCount(self):
        return len(self.data) - 1;

    def append(self, key, value, translate):
        line = LocalizationIni.GetKeyValueText(key, value)
        if translate:
            self.data.append([line, LocalizationIni.GetKeyValueText(key, translate)])
        elif self.autoMarkEmptyAsTranslated and (len(value) == 0):
            self.data.append([line, LocalizationIni.GetKeyValueText(key, '')])
        else:
            self.data.append([line, ''])

    def saveToXlsxFile(self, filename, sheetName):
        dataFrame = pandas.DataFrame(self.data, columns=[ 'A', 'B' ])
        dataFrame.to_excel(filename, sheet_name=sheetName, encoding='utf8', index=False, header=False)

class LocalizationVerifier:
    __lostNewlineExpr = re.compile(r'[^\\]\\[^n\\]')
    __spaceBeforeNewlineExpr = re.compile(r' \\n')
    __truths = set(['True', 'true', 1, '1'])
    __verifyExceptions = False
    __interactiveMode = False

    @staticmethod
    def __RaiseVerifyError(text):
        if LocalizationVerifier.__verifyExceptions:
            raise Exception(f'Error: {text}')
        else:
            print(f'Error: {text}')
            if LocalizationVerifier.__interactiveMode:
                input()

    @staticmethod
    def __NamedFormatToString(formatSet):
        result = ''
        for format in formatSet:
            if result:
                result += ', '
            result += f'~{format[0]}({format[1]})'
        return result

    @staticmethod
    def __ReadCodepointCharactersSet(inputFilename):
        characterSet = set({ ' ', '\t' }); #, '\xa0'
        with codecs.open(inputFilename, "r", "utf-8") as inputFile:
            while True:
                prefix = inputFile.read(2)
                if not prefix:
                    break;
                if prefix != '\\u':
                    LocalizationVerifier.__RaiseVerifyError(f'Found invalid codepoint prefix: {prefix}')
                    return set()
                codepoint = inputFile.read(4)
                if not codepoint:
                    LocalizationVerifier.__RaiseVerifyError('Missing codepoint')
                    return set()
                characterSet.add(chr(int(codepoint, 16)))
        return characterSet

    def __init__(self, options):
        self.lostNewline = ('lost_newline' in options) and options['lost_newline'] in LocalizationVerifier.__truths
        self.spaceBeforeNewline = ('space_before_newline' in options) and options['space_before_newline'] in LocalizationVerifier.__truths
        self.englishWordsMismatch = ('english_words_mismatch' in options) and options['english_words_mismatch'] in LocalizationVerifier.__truths
        self.allowedCharacters = set()
        if 'allowed_characters_file' in options:
            allowedCharactersFile = options['allowed_characters_file']
            if os.path.isfile(allowedCharactersFile):
                print(f"Read allowed characters: {allowedCharactersFile}")
                self.allowedCharacters = LocalizationVerifier.__ReadCodepointCharactersSet(allowedCharactersFile)

    def verify(self, originalIni, translationIni):
        for key, value in originalIni.getItems():
            translateValue = translationIni.getKeyValue(key)
            if translateValue != None:
                if (len(translateValue) == 0) and (len(value) > 0):
                    LocalizationVerifier.__RaiseVerifyError(f'empty translation - {key}')
                    continue
                if len(self.allowedCharacters) > 0:
                    invalidCharacters = set()
                    for translateChar in translateValue:
                        if (translateChar not in self.allowedCharacters) and (translateChar not in value):
                           invalidCharacters.add(translateChar)
                    if len(invalidCharacters) > 0:
                        LocalizationVerifier.__RaiseVerifyError(f'invalid characters in - {key}\nCharacters: {invalidCharacters}')
                if not key.startswith("PU_") and not key.startswith("PH_PU_") and not key.startswith("DXSM_"):
                    origUnnamedFormats = LocalizationIni.GetUnnamedFormats(value)
                    translateUnnamedFormats = LocalizationIni.GetUnnamedFormats(translateValue)
                    if origUnnamedFormats != translateUnnamedFormats:
                        LocalizationVerifier.__RaiseVerifyError(f'unnamed format seq change - {key}\nFormat original : {origUnnamedFormats}\nFormat translate : {translateUnnamedFormats}')
                origNamedFormats = LocalizationIni.GetNamedFormats(value)
                translateNamedFormats = LocalizationIni.GetNamedFormats(translateValue)
                if not LocalizationIni.IsNamedFormatEquals(origNamedFormats, translateNamedFormats):
                    LocalizationVerifier.__RaiseVerifyError(f'named format seq change - {key}\nFormat original : {LocalizationVerifier.__NamedFormatToString(origNamedFormats)}\nFormat translate : {LocalizationVerifier.__NamedFormatToString(translateNamedFormats)}')
                if self.lostNewline:
                    count = len(LocalizationVerifier.__lostNewlineExpr.findall(translateValue))
                    if count > 0:
                        print(f"Note: lost newline \\n [{count}] - {key}")
                if self.spaceBeforeNewline:
                    count = len(LocalizationVerifier.__spaceBeforeNewlineExpr.findall(translateValue))
                    if count > 0:
                        print(f"Note: space before \\n [{count}] - {key}")
                if self.englishWordsMismatch:
                    translateCleanValue = LocalizationIni.GetCleanText(translateValue, translateUnnamedFormats, translateNamedFormats)
                    translateEngWords = LocalizationIni.GetEnglishWords(translateCleanValue)
                    if len(translateEngWords) > 0:
                        cleanValue = LocalizationIni.GetCleanText(value, origUnnamedFormats, origNamedFormats)
                        origEngWords = LocalizationIni.GetEnglishWords(cleanValue)
                        if not translateEngWords.issubset(origEngWords):
                            print(f"Note: use undefined word in - {key}")
                            print("English words original : ", origEngWords)
                            print("English words translate : ", translateEngWords)
                            print("English words diff : ", translateEngWords.difference(origEngWords))

    @staticmethod
    def SetEnableVerifyExceptions(enabled):
        LocalizationVerifier.__verifyExceptions = enabled

    @staticmethod
    def SetInteractiveMode(enabled):
        LocalizationVerifier.__interactiveMode = enabled


