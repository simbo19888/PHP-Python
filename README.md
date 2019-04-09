Speech-to-Text PHP-Python
---
## Описание
Программа позволяет распознавать текст из mp3 файла (speech_recognize_continuous_from_file)

## Настройка и необходимое ПО

### Ключ
Необходимо указать ключ подписки azure speech SDK в файле python/Speech_to_text.py(32 строка)
Программа использует ключ подписки azure speech SDK. Для тестов можно использовать бесплатную подписку. Ключ записывается вместе с регионом, к которому он относится в переменные speech_key и service_region соответственно.

### Подключение БД
Необходимо настроить подключение к базе данный в файле config/db.php, и файле python/Speech_to_text.py(39,40 строка)
Программа использует PostgreSQL 9.6. Единственная таблица имеет название file_hash. 
Таблица имеет следующие поля:

| поле | тип | длина | Не NULL? | Первичный ключ |
| :---: | :---: | :---: | :---: | :---: |
| id     | integer           |       | Да       | Да             |
| hash   | character varying | 32    | Да       | Нет            |
| status | character varying | 10    | Нет      | Нет            |
| result | text              |       | Нет      | Нет            |

Код создания таблицы:


      CREATE TABLE public.file_hash
      (
          id integer NOT NULL DEFAULT nextval('table_id_seq'::regclass),
          hash character varying(32) COLLATE pg_catalog."default" NOT NULL,
          status character varying(10) COLLATE pg_catalog."default",
          result text COLLATE pg_catalog."default",
          CONSTRAINT file_hash_pkey PRIMARY KEY (id)
      )
      WITH (
          OIDS = FALSE
      )
      TABLESPACE pg_default;
      
      ALTER TABLE public.file_hash
          OWNER to postgres;


Код автоинкрементации id:

      CREATE SEQUENCE public.table_id_seq;
      
      ALTER SEQUENCE public.table_id_seq
          OWNER TO postgres;

### Программы
Для работы необходим Python версии 3.5+ со следующими установленными библиотеками <br>
- requests 
  (pip install requests)
- speech SDK 
  (pip install azure-cognitiveservices-speech)
- psycopg2
  (pip install psycopg2)

Для конвертации mp3 в wav программа использует sox с двумя dll (Необходимо поместить в папку с sox)(https://yadi.sk/d/hzrCNfzbO-fhcw)
Также необходимо указать путь к sox в файле python/Speech_to_text.py(68) строка, (73) строка для linux)

## Запуск
Для начала работы надо отправить POST запрос на host/speech в котором атрибутом file будет являться mp3 файл для обработки.
При отправки GET запроса на host/speech без параметров будет выведен список всех файлов, при отправке GET запроса с параметром id будет выведен результат обработки данного файла.