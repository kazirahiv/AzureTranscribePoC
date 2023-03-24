import argparse
import datetime
import os
import time


try:
    from pydub import AudioSegment
except ImportError:
    print("""
    Importing pydub for Python failed. Install dependency with: pip install pydub
    """)
    import sys

    sys.exit(1)


try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Azure Speech SDK for Python failed. Install dependency with: pip install azure-cognitiveservices-speech
    """)
    import sys

    sys.exit(1)

# Create an argument parser
parser = argparse.ArgumentParser()

# Add the arguments
parser.add_argument('--speech_key', type=str, required=True, help='speech key for authentication')
parser.add_argument('--service_region', type=str, required=True, help='service region for the speech service')
parser.add_argument('--audiofile', type=str, required=True, help='path to the audio file')

# Parse the arguments
args = parser.parse_args()

# Get the values of the arguments
speech_key = args.speech_key
service_region = args.service_region
audiofile = args.audiofile


def speech_recognize_continuous_from_file():
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.enable_dictation()
    audio_config = speechsdk.audio.AudioConfig(filename=audiofile)

    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=["de-DE", "en-US", "he-IL"])

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config,
                                                   auto_detect_source_language_config=auto_detect_source_language_config)

    done = False
    speaker_set = False
    speeches = []

    def stop_cb(evt: speechsdk.SessionEventArgs):
        nonlocal done
        nonlocal speaker_set
        done = True
        if not speaker_set:
            for i in range(len(speeches)):
                if i % 2 == 0:
                    speeches[i] = "speaker1 " + speeches[i]
                else:
                    speeches[i] = "speaker2 " + speeches[i]
            speaker_set = True

    def recognized(evt: speechsdk.SpeechRecognitionEventArgs):
        auto_detect_source_language_result = speechsdk.AutoDetectSourceLanguageResult(evt.result)
        time_str = (datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=evt.result.offset // 10)).strftime(
            "%M:%S")
        transcribed_speech = str(auto_detect_source_language_result.language) + " " + time_str + " " + str(
            evt.result.text)
        print('Transcribed ---- {}'.format(transcribed_speech))
        nonlocal speeches
        speeches.append(transcribed_speech)

    speech_recognizer.recognized.connect(recognized)
    #speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)

    speech_recognizer.stop_continuous_recognition()

    with open(audiofile + ".txt", "w", encoding="utf-8") as f:
        f.write(audiofile + "\n")
        for speech in speeches:
            f.write(speech + "\n")


# try catch for the speech recognition
try:
    speech_recognize_continuous_from_file()
except Exception as e:
    audiofile = os.path.abspath(audiofile)
    mp3_file = AudioSegment.from_mp3(audiofile)
    file_name = audiofile.split(".")[0]
    mp3_file.export(file_name + ".wav", format="wav")
    audiofile = file_name + ".wav"
    speech_recognize_continuous_from_file()