# StarCitizen-LocalizationScripts
Star Citizen localization scripts for automate download localization from CAT and merge with latest global.ini

# Requirements

- Python 3 (version 3.7 or higher)
- PIP (Python package manager)
- git (optional)

# Prepare scripts envirovement

- Install requirements  
  ```
  pip install -r requirements.txt
  ```
- Generate CAT config by python script  
  ```
  gen_smartcat_config.py global.ini.xlsx <document_id> --account-id <id> --auth-key <key>
  ```
- Generate convert config by python script  
  ```
  gen_convert_config.py global.ini
  ```
