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
import os


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
speech_key, service_region = "81910142c03e4791b01fc12a2d3356f7", "westus" 
fromLanguage = "ru-RU"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = fromLanguage


def connect_db():
    return psycopg2.connect(dbname='postgres', user='postgres', 
        password='qweasdzxc', host='localhost', port='5432')

pid = os.getpid()
f = open('pid.txt','w')
f.write(str(pid))
f.close()

def speech_recognize_continuous_from_file(processing_file):
    """performs continuous speech recognition with input from an audio file"""
    def write_db(status, result, id):
        try:
            conn = connect_db()
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

    baseAudioPath = "../uploads/"
    filePath = processing_file[1]
    id = processing_file[0]
    write_db('processing', '', id)
    convert_fail = subprocess.call(["C:\Program Files (x86)\sox-14-4-2\sox.exe",
    baseAudioPath + 'mp3/' + filePath + ".mp3", '--norm', "-V1",
    baseAudioPath + 'wav/' + filePath + ".wav"])
    if(convert_fail):
        write_db('error', "Ошибка при конвертации файла.", id)
        os.remove(baseAudioPath + "mp3/" + processing_file[1] + ".mp3") 
        return 0
    audio_config = speechsdk.audio.AudioConfig(filename = baseAudioPath+'wav/'+filePath+'.wav')
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    done = False
    result = ''
    

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        speech_recognizer.stop_continuous_recognition()
        nonlocal result
        nonlocal id
        nonlocal done
        done = True
        write_db('succes', result, id)


    def canceled_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        nonlocal result
        if(result == ''):
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            nonlocal id
            done = True
            write_db('error', evt.result.reason, id)



    def add_result(evt):
        nonlocal result
        result += evt.result.text + ' '
        
        
    # Connect callbacks to the events fired by the speech recognizer
    #speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt))) #Вывод промежуточных результатов
    speech_recognizer.recognized.connect(add_result)
    #speech_recognizer.session_started.connect(lambda evt: print('processing...'))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(canceled_cb)
    #speech_recognizer.speech_end_detected.connect(lambda evt: print('end'))

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)
    del(speech_recognizer)
    return True


def remove_file(path):
    try:
        os.remove(path)
    except Exception as error:
        f = open('file.txt', 'a')
        f.write(str(error)+'\n')
        f.close()

while True:
    try:
        conn = connect_db()
        with conn.cursor() as cursor:
            sql_select_query = """select * from file_hash where status = 'waiting' or status = 'processing' limit 10"""
            cursor.execute(sql_select_query)
            turn = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        f = open('error.txt', 'a')
        f.write(str(datetime.datetime.now())+':')
        f.write(str(error))
        f.close()
        break
    finally:
        if (conn):
            conn.cursor().close()
            conn.close()
    if(turn==[]):
        break
    for processing_file in turn:
        if(speech_recognize_continuous_from_file(processing_file)):
                remove_file("../uploads/mp3/" + processing_file[1] + ".mp3")
                remove_file("../uploads/wav/" + processing_file[1] + ".wav")

    undelitedfiles = ''
    if(os.path.exists('file.txt')):
        f = open('file.txt', 'r') 
        undelitedfiles = f.read()
        f.close()
        os.remove('file.txt')
    undelitedfiles = undelitedfiles.split('\n')[:-1]
    for line in undelitedfiles:
        path = line.split('\'')
        remove_file(path[1])