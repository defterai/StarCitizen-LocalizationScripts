# SmartCAT Export
Export SmartCAT multi-language documents to files

## Usage

```
name: Export Document
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: defterai/smartcat-export@master
      name: Export SmartCat documents
      with:
        account_id: ${{ secrets.SMARTCAT_ACCOUNT_ID }}
        auth_key: ${{ secrets.SMARTCAT_API_KEY }}
        language_id: 1058
		documents: file.xlsx b2274ec73fedfdb987bb3170
```

## Arguments
| Argument | Description | Required |
|---|---|---|
| account_id | SmartCAT account identifier | + |
| auth_key | SmartCAT auth API key | + |
| language_id | Export document language identifier | + |
| documents | Export documents pair (name, identifier) | + |
