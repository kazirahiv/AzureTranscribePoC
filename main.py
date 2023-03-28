import json
import time
import datetime
import requests
from azure.storage.blob import BlobServiceClient, ContainerClient
import os

from dotenv import load_dotenv

load_dotenv(".env")
(service_region, subscription_key, storage_connection_string, directory_name, verbose) = (
    os.environ.get("AZURE_SERVICE_REGION"),
    os.environ.get("AZURE_SUBSCRIPTION_KEY"),
    os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
    os.environ.get("TRANSCRIPTION_DIRECTORY"),
    os.environ.get("VERBOSE"))


# function to print log if verbose is true
def print_log(message):
    if verbose == "True":
        print(message)


try:
    from pydub import AudioSegment
except ImportError:
    print_log("""
    Importing pydub for Python failed. Install dependency with: pip install pydub
    """)
    import sys

    sys.exit(1)

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print_log("""
    Importing the Azure Speech SDK for Python failed. Install dependency with: pip install azure-cognitiveservices-speech
    """)
    import sys

    sys.exit(1)

files_to_transcribe = []


# function create container if not exists by directory name and upload files from directory
def create_container_and_upload_files(directory_name):
    container_name = directory_name
    blob_service_client = BlobServiceClient.from_connection_string(f"{storage_connection_string}")

    # check if container exists by name otherwise create container
    if not container_name in [container.name for container in blob_service_client.list_containers()]:
        blob_service_client.create_container(container_name, public_access="blob")

    # get container
    container_client: ContainerClient = blob_service_client.get_container_client(container_name)

    for filename in os.listdir(directory_name):
        # check if blob exists by name otherwise upload file
        if not filename in [blob.name for blob in container_client.list_blobs()]:
            with open(os.path.join(directory_name, filename), "rb") as data:
                container_client.upload_blob(name=filename, data=data)
                print_log(f"Uploaded {filename} to Azure container for transcription")
    # list blobs in container and their URL
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        files_to_transcribe.append(f"{container_client.url}/{blob.name}")


# scan directory for audio files and check if audio file is mono or stereo, if stereo convert to mono
def check_if_mono(directory_name):
    for filename in os.listdir(directory_name):
        if filename.endswith(".mp3"):
            audiofile = os.path.join(directory_name, filename)
            mp3_file = AudioSegment.from_mp3(audiofile)
            file_name = audiofile.split(".")[0]
            if mp3_file.channels != 1:
                # convert to mono
                print_log(f"Converting {file_name} to mono")
                mp3_file = mp3_file.set_channels(1)
                mp3_file.export(f"{file_name}.mp3", format="mp3")


def parse_transcribed_json(directory, filename, content_url):
    # get content from content url
    request = requests.get(content_url)
    if request.status_code == 200:
        json_data = request.json()
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(json_data['source'] + '\n')
            for phrase in json_data['recognizedPhrases']:
                time_str = (datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=phrase['offsetInTicks'] // 10)).strftime("%M:%S")
                f.write(f"{phrase['locale']}-{time_str}-{phrase['speaker']}-{phrase['nBest'][0]['display']}\n")
    else:
        print_log(f"Error getting transcribed JSON : {request.status_code}")


# function to send files in directory to azure for batch transcription
def send_files_to_azure_for_transcription() -> []:
    if not files_to_transcribe:
        print_log("No files to transcribe")
        return
    print_log(f"Sending files in directory {directory_name} to Azure for transcription")
    url = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions"
    payload = json.dumps({
        "contentUrls": files_to_transcribe,
        "locale": "en-US",
        "displayName": f"{directory_name} Transcription",
        "model": None,
        "properties": {
            "diarizationEnabled": True,
            "diarization": {
                "speakers": {
                    "minCount": 1,
                    "maxCount": 2
                }
            },
            "languageIdentification": {
                "candidateLocales": [
                    "en-US",
                    "de-DE",
                    "es-ES",
                    "he-IL"
                ]
            }
        }
    })
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # check if transcription was successful
    if response.status_code == 201:
        print_log(f"Transcription started successfully: {directory_name} Transcription")

    transcription_id = response.json()['self'].split("/")[-1]

    # check every 10 seconds if transcription is successful
    while True:
        # check transcription status
        url = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions/{transcription_id}"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers)

        # check if transcription is completed
        if response.json()['status'] == "Succeeded":
            print_log(f"Transcription completed successfully")
            break
        else:
            print_log(f"Transcription status: {response.json()['status']}")
        # delay 4 seconds
        time.sleep(10)

    # download transcription result
    url = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions/{transcription_id}/files"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers)

    transcribed_json_urls = []

    # print_log name and contentUrl of transcription result
    for result in response.json()['values']:
        if result['kind'] != "Transcription":
            continue
        print_log(f"Name: {result['name']}")
        print_log(f"ContentUrl: {result['links']['contentUrl']}")
        transcribed_json_urls.append({
            "name": result['name'],
            "contentUrl": result['links']['contentUrl']
        })

    return transcribed_json_urls


# function to delete container if exists
def delete_container(container_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(f"{storage_connection_string}")
        container_client = blob_service_client.get_container_client(container_name)
        container_client.delete_container()
        print_log(f"Deleted container {container_name}")
    except:
        pass


try:
    print("Starting transcription ....")
    check_if_mono(directory_name)
    create_container_and_upload_files(directory_name)
    transcribed_json_urls = send_files_to_azure_for_transcription()
    for content in transcribed_json_urls:
        parse_transcribed_json(f"{directory_name}_output", f"{content['name']}.txt", content['contentUrl'])
    delete_container(directory_name)
    print("Transcription completed successfully")
except Exception as e:
    if verbose:
        print(e)
    print("Error occurred")
    delete_container(directory_name)
