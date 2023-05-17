# yolov7-instance-comparison

YOLOv7 を SageMaker の複数のインスタンスで実行し、速度を比較する

2023年5月10日 から 2023年5月15日 に実施したもの

## 必要なソフトウェア

* [asdf]
* [Docker]

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

## AWSインフラ準備

    $ ./prepare_infra.sh

## コンテナデプロイ

    $ ./deploy_sagemaker_train_image.sh

## SageMaker による学習

    $ python train_on_sagemaker.py

## 推論用イメージのデプロイ

各種推論用イメージを ECR にデプロイする

    $ ./deploy_sagemaker_serve_cpu_image.sh

    $ ./deploy_sagemaker_serve_graviton_image.sh

    $ ./deploy_sagemaker_serve_image.sh

    $ ./deploy_sagemaker_serve_inference_image.sh

## モデルのダウンロード、変換、デプロイ

学習結果のモデルファイルをダウンロードし、展開する

    $ cd conversion/models

    $ aws s3 cp s3://${S3_BUCKET}/yolov7_sample/<ジョブ名>/output/model.tar.gz ./model.tar.gz \
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

    $ cd ..

    $ ./deploy_sagemaker_serve_cpu_model.sh

    $ ./deploy_sagemaker_serve_graviton_model.sh

    $ ./deploy_sagemaker_serve_model.sh

    $ ./deploy_sagemaker_serve_inference_model.sh

## 推論の実行

    $ python detect_on_sagemaker.py \
        -e <エンドポイント名> \
        -i <入力画像ディレクトリパス> \
        -o <出力先ディレクトリパス>

## AWSインフラ削除

    $ ./delete_sagemaker_serve_model.sh \
        -r us-west-2 \
        -n sagemaker-yolov7-serve-cpu

    $ ./delete_sagemaker_serve_model.sh \
        -r us-west-2 \
        -n sagemaker-yolov7-serve-graviton

    $ ./delete_sagemaker_serve_model.sh \
        -r us-west-2 \
        -n sagemaker-yolov7-serve

    $ ./delete_sagemaker_serve_model.sh \
        -r us-west-2 \
        -n sagemaker-yolov7-serve-inferentia

    $ ./destroy_infra.sh

[asdf]: https://asdf-vm.com/#/core-manage-asdf-vm
[docker]: https://docs.docker.com/get-docker/
