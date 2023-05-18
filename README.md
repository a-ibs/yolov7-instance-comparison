# yolov7-instance-comparison

YOLOv7 を SageMaker の複数のインスタンスで実行し、速度を比較する

2023年5月10日 から 2023年5月15日 に実施したもの

## 必要なソフトウェア

* [asdf]
* [Docker]
* [jq]

## ローカル環境構築

プラグインを追加する

    $ asdf plugin-add aws-sam-cli \
        ; asdf plugin-add direnv \
        ; asdf plugin-add hadolint \
        ; asdf plugin-add nodejs \
        ; asdf plugin-add python

必要なソフトウェアをインストールする

    $ asdf install

開発用依存モジュールをインストールする

    $ npm install \
        && pip install --requirement requirements.txt

## 環境変数の準備

.exports.sample をコピーして .exports を作成する

    $ cp .exports.sample .exports

.exports を編集し、環境変数 S3_BUCKET にバケット名を設定する

変更後の環境変数が適用されるように許可する

    $ direnv allow

## AWSインフラ準備

    $ ./prepare_infra.sh

## トレーニング用イメージのデプロイ

    $ ./deploy_sagemaker_train_image.sh

## トレーニング用データの準備

Open Images Dataset V6 から犬と猫の画像をダウンロードし、圧縮して S3 にアップロードする

    $ python prepare_sample_data.py

## SageMaker によるトレーニング

    $ python train_on_sagemaker.py

## 推論用イメージのデプロイ

各種推論用イメージを ECR にデプロイする

    $ ./deploy_sagemaker_serve_cpu_image.sh \
        && ./deploy_sagemaker_serve_graviton_image.sh \
        && ./deploy_sagemaker_serve_image.sh \
        && ./deploy_sagemaker_serve_inference_image.sh

## モデルのダウンロード、変換、デプロイ

トレーニング結果のモデルファイルをダウンロードし、展開する

    $ export JOB_NAME=<ジョブ名>

    $ cd conversion/models

    $ aws s3 cp s3://${S3_BUCKET}/yolov7_sample/${JOB_NAME}/output/model.tar.gz ./model.tar.gz \
        && tar -zxvf model.tar.gz \
        && cp model/weights/best.pt ./yolov7x.pt

モデルファイルを推論用に圧縮し、 S3 にアップロードする

    $ tar -zcvf model.tar.gz ./yolov7x.pt \
        && aws s3 cp ./model.tar.gz s3://${S3_BUCKET}/yolov7_sample/serve/model.tar.gz

モデルファイルを inferentia 用に変換する

    $ cd ..

    $ docker-compose up

inferentia 用のモデルファイルを推論用に圧縮し、 S3 にアップロードする

    $ cd models

    $ tar -zcvf model.tar.gz ./yolov7x_neuron.pt \
        && aws s3 cp ./model.tar.gz s3://${S3_BUCKET}/yolov7_sample/serve_inferentia/model.tar.gz

各種 SageMaker エンドポイントをデプロイする

    $ cd .. \
        && ./deploy_sagemaker_serve_cpu_model.sh \
        && ./deploy_sagemaker_serve_graviton_model.sh \
        && ./deploy_sagemaker_serve_model.sh \
        && ./deploy_sagemaker_serve_inference_model.sh

## 推論の実行

    $ python detect_on_sagemaker.py \
        -e <エンドポイント名> \
        -i <入力画像ディレクトリーパス> \
        -o <出力先ディレクトリーパス>

## AWSインフラ削除

    $ export REGION="us-west-2"

    $ ./delete_sagemaker_serve_model.sh \
        -r "${REGION}" \
        -n sagemaker-yolov7-serve-cpu

    $ ./delete_sagemaker_serve_model.sh \
        -r "${REGION}" \
        -n sagemaker-yolov7-serve-graviton

    $ ./delete_sagemaker_serve_model.sh \
        -r "${REGION}" \
        -n sagemaker-yolov7-serve

    $ ./delete_sagemaker_serve_model.sh \
        -r "${REGION}" \
        -n sagemaker-yolov7-serve-inferentia

    $ ./destroy_infra.sh

[asdf]: https://asdf-vm.com
[docker]: https://docs.docker.com/get-docker/
[jq]: https://stedolan.github.io/jq/
