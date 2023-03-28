# Azure batch transcription PoC

![](https://github.com/kazirahiv/AzureTranscribePoC/blob/main/workflow.png?raw=true)

This CLI tool is a working version of Azure Cognitive Speech Service with batch transcription. It can be a perfect example of call center transcription. It detects the language, timestamp, and speaker recognition/diarization.
Just store your audio files in a directory and the tool will correct the audio file's bitness and change the audio channel to mono (if it's stereo), then it'll upload the verified audio files in a storage container and collect the blob links and submit those links for batch transcription. When the job is done, it'll create an output directory containing your transcriptions as txt files.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## Configurations
Grab your Azure Client id, Client secret, Tenant id, Service region, subscription key (Azure Speech), and Azure storage container connection string from the portal and put them into the .env file accordingly.

Set your folder containing audio files in the TRANSCRIPTION_DIRECTORY variable from .env
Set the VERBOSE variable to True if you want to see every step in CLI 

## Usage

```
python main.py

```
