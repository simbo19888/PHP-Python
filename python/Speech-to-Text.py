#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
import datetime
import time
import wave
import requests
import subprocess
from sys import argv
import psycopg2
from psycopg2 import sql


try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)


# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "aa64dc3f85f54193b774fa22a1e622f5", "westus" 
fromLanguage = "ru-RU"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = fromLanguage


def speech_recognize_continuous_from_file(filePath):
    """performs continuous speech recognition with input from an audio file"""
    filePath = filePath[:-4]
    subprocess.call(["C:\Program Files (x86)\sox-14-4-2\sox.exe", filePath+".mp3", filePath+".wav"])
    audio_config = speechsdk.audio.AudioConfig(filename=filePath+'.wav')
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    done = False
    result = ''
    def write_db(status, result, id):
        try:
            conn = psycopg2.connect(dbname='postgres', user='postgres', 
                            password='qweasdzxc', host='localhost', port='5432')
            with conn.cursor() as cursor:
                sql_update_query = """Update file_hash set status = %s , result = %s where id = %s"""
                cursor.execute(sql_update_query, (status, str(result), id))
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            f = open('error.txt', 'a')
            f.write(str(datetime.datetime.now())+':')
            f.write(str(error))
            f.write(str(result)+'\n')
            f.close()
        finally:
            if (conn):
                conn.cursor().close()
                conn.close()


    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        speech_recognizer.stop_continuous_recognition_async()
        nonlocal result
        nonlocal done
        done = True
        write_db('succes', result, argv[2]) 


    def canceled_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        nonlocal result
        if(result==''):
            speech_recognizer.stop_continuous_recognition_async()
            nonlocal done
            done = True
            write_db('error', evt.result.reason, argv[2])


    def add_result(evt):
        nonlocal result
        result += evt.result.text + ' '
        
        
    # Connect callbacks to the events fired by the speech recognizer
    #speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt))) #Вывод промежуточных результатов
    speech_recognizer.recognized.connect(add_result)
    #speech_recognizer.session_started.connect(lambda evt: print('processing...'))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(canceled_cb)


    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition_async()

    while not done:
        time.sleep(.5)


speech_recognize_continuous_from_file(argv[1])