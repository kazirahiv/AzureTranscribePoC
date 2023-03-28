# Azure batch transcription PoC

![](https://github.com/kazirahiv/AzureTranscribePoC/blob/main/workflow.png?raw=true)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Configurations
Grab your Azure Client id, Client secret, Tenant id, Service region, subscription key (Azure Speech),Azure storage container connection string from portal and put them into .env file accordingly.

Set your folder containing audio files in TRANSCRIPTION_DIRECTORY variable from .env
Set VERBOSE variable to True if you want to see every step in CLI 

## Usage

```
python main.py

```
