# Merge multi-language localization documents into INI
Merge multi-language localization documents with reference INI

## Usage

```
name: Merge multi-language localization
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
	- name: Merge with latest version
      uses: defterai/StarCitizen-LocalizationScripts/multilang-to-ini@main
      with:
        documents: global.ini.xlsx
        split_documents: names.ini subtitles.ini garbage.ini
        reference: global_ref.ini
        version: 1.05
```

## Arguments
| Argument | Description | Required | Default Value |
|---|---|---|---|
| filename | Output localization INI file name | - | global.ini |
| reference | Reference localization INI | - | global_ref.ini |
| version | Version name of localization | - | none |
| document | Input main document file name | + | |
| split_documents | Input split document file name list | - | |
