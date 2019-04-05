<?php

namespace app\controllers;

use yii\web\Response;
use yii\rest\Controller;
use yii\db\Exception;
use yii;


class SpeechController extends Controller
{
    /* Определяет формат возращаемых данных */
    public function behaviors()
    {
        $behaviors = parent::behaviors();
        $behaviors['contentNegotiator']['formats'] = ['application/json' => Response::FORMAT_JSON,];
        return $behaviors;
    }

    /* Отключение всех методов кроме GET */
    protected function verbs()
    {
        return[
            'post' => ['POST'],
            'get' => ['GET'],
        ];
    }


    private function insertHash($hash)
    {

        try {
            Yii::$app->db->createCommand()
                ->insert('file_hash', [
                    'hash' => $hash,
                    'status' => 'waiting'
                ])->execute();
        } catch (Exception $e) {
            return $e;
        }
        $return = [
            'id' => intval(Yii::$app->db->lastInsertID),
            'status' => 'waiting'];
        return $return;
    }

    private function updateHash($id){
        try {
            Yii::$app->db->createCommand()
                ->update('file_hash', [
                    'status' => 'waiting',
                ],
                    ['id'=>$id])
                ->execute();
        } catch (Exception $e) {
            return $e;
        }
        return [
            'id' => $id,
            'status' => 'waiting'
        ];
    }

    private function processingQueryCheck(){
        $query = (new \yii\db\Query())
            ->select(['id', 'status'])
            ->from('file_hash')
            ->where(['or', ['status' => 'processing'], ['status' => 'waiting']])
            ->count();
        return (boolean)$query;
    }

    /* Поиск хеша в базе данных, возвращает id и status если находит, false если не находит */
    private function searchForHash($hash)
    {
        $query = (new \yii\db\Query())
            ->select(['id', 'status', 'result'])
            ->from('file_hash')
            ->where(['hash' => $hash])
            ->one();
        return (boolean)$query ? $query : false;
    }

    public function pythonProcessingStart()
    {
        pclose(popen("start  /B /min ../python/Speech-to-Text.py", "r"));
    }

    /* Вызывается при обращенни к /speech методом GET. Можно указать id. */
    public function actionGet()
    {
        $queryParams = Yii::$app->request->get();
        if (!isset($queryParams['id'])) {
            $query = (new \yii\db\Query())
                ->select(['id', 'status', 'result'])
                ->from('file_hash')
                ->all();
        } else {
            $query = (new \yii\db\Query())
                ->select(['id', 'status', 'result'])
                ->from('file_hash')
                ->where(['id' => $queryParams['id']])
                ->one();
        }
        return $query;
    }

    /* Основная функция, вызывается при обращенни к /log */
    public function actionPost()
    {
        $result=[];
        $uploadDir = '../uploads/mp3/';
        foreach($_FILES["file"]["error"] as $key=>$error) {
            $filePath  = $_FILES['file']['tmp_name'][$key];
            $errorCode = $_FILES['file']['error'][$key];
            $name = basename($_FILES['file']['name'][$key]);
            $hash = md5_file($filePath);
            $hash = microtime();
            if ($errorCode !== UPLOAD_ERR_OK) {

                // Массив с названиями ошибок
                $errorMessages = [
                    UPLOAD_ERR_INI_SIZE   => 'Размер файла превысил значение upload_max_filesize в конфигурации PHP.',
                    UPLOAD_ERR_PARTIAL    => 'Загружаемый файл был получен только частично.',
                    UPLOAD_ERR_FORM_SIZE  => 'Размер загружаемого файла превысил значение MAX_FILE_SIZE в HTML-форме.',
                    UPLOAD_ERR_NO_FILE    => 'Файл не был загружен.',
                    UPLOAD_ERR_NO_TMP_DIR => 'Отсутствует временная папка.',
                    UPLOAD_ERR_CANT_WRITE => 'Не удалось записать файл на диск.',
                    UPLOAD_ERR_EXTENSION  => 'PHP-расширение остановило загрузку файла.',
                ];

                // Зададим неизвестную ошибку
                $unknownMessage = 'При загрузке файла произошла неизвестная ошибка.';

                // Если в массиве нет кода ошибки, скажем, что ошибка неизвестна
                $outputMessage = isset($errorMessages[$errorCode]) ? $errorMessages[$errorCode] : $unknownMessage;

                // Выведем название ошибки
                array_push($result, ['file' => $name,'error' => $outputMessage]);
            } else {
                move_uploaded_file($filePath,$uploadDir . $hash . '.mp3');

                $hashExists = $this->searchForHash($hash);
                $isProcessing = $this->processingQueryCheck();
                if (!$hashExists) {
                    // Кэша не существует
                    $id = $this->insertHash($hash);
                    array_push($result, $id);
                } else if ($hashExists['status']=='error') {
                    // Кэш с ошибкой
                    array_push($result, $this->updateHash($hashExists['id']));
                } else {
                    // Файл обрабатывается/обработан
                    array_push($result, $hashExists);
                    $isProcessing = true;
                }

                if (!$isProcessing) {
                    $this->pythonProcessingStart();
                }
            }
        }
        return $result;
    }
}
