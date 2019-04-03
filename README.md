Speech-to-Text PHP-Python
---
## Описание
Программа позволяет преобразовывать речь из различных источников в текст.

## Настройка
Необходимо настроить подключение к базе данный в файле config/db.php, и файле python/Speech_to_text.py(47,48 строка)
В базе данных надо создать таблицу file_hash со следующей структурой
<img src="https://downloader.disk.yandex.ru/preview/c3cc5d3e2821998c0e79666841a3d8f7ba47293ce7f3835f216d918ac23cb534/5ca4a4eb/V43Y9xPPPrg2jcyjKbNNngD2cIYuTk68sc7l7GYKV1qQMmbPNY1oa5ubntLtVD35qIiVNCT81iC5HTG_cC_rtg%3D%3D?uid=0&filename=bd.bmp&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&tknv=v2&size=2048x2048">
Необходимо указать ключ подписки azure speech SDK в файле python/Speech_to_text.py(31 строка)
Необходимо указать путь к sox в файле python/Speech_to_text.py(40 строка)
## Функционал
Программа позволяет производить следующие действия:
- Распознавать длинные тексты из файла.
  (speech_recognize_continuous_from_file)


## Запуск
Для начала работы надо отправить POST запрос на host/speech в котором атрибутом file будет являться mp3 файл для обработки.
При отправки GET запроса на host/speech без параметров будет выведен список всех файлов, при отправке GET запроса с параметром id будет выведен результат обработки данного файла.
### Ключ
Программа использует ключ подписки azure speech SDK. Для тестов можно использовать бесплатную подписку. Ключ записывается вместе с регионом, к которому он относится в переменные speech_key и service_region соответственно.

### Python
Для работы необходим Python версии 3.5+ <br>

###  Библиотеки
Программа использует следующие библиотеки:
- requests 
  (pip install requests)
- speech SDK 
  (pip install azure-cognitiveservices-speech)
- psycopg2
  (pip install psycopg2)
  
### Программы
Для конвертации mp3 в wav программа использует sox с двумя dll (Необходимо поместить в папку с sox)(https://yadi.sk/d/hzrCNfzbO-fhcw)