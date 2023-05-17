#!/usr/bin/env python
# coding: utf-8

"""
学習データを準備する
"""

import glob
import os
import tarfile

import boto3
import fiftyone as fo
import fiftyone.zoo as foz

DATASET_NAME = "open-images-v6-cat-dog"
DATASET_TYPE = fo.types.YOLOv5Dataset
CLASSES = ["Cat", "Dog"]
OUTPUT_DIR = "training_data"
TARFILE_NAME = "inputs.tgz"
S3_BUCKET = os.environ.get("S3_BUCKET")


def download():
    """
    データセットをダウンロードする
    """

    if DATASET_NAME in fo.list_datasets():
        return fo.load_dataset(DATASET_NAME)

    dataset = foz.load_zoo_dataset(
        "open-images-v6",
        split="validation",
        label_types=["detections"],
        classes=CLASSES,
        max_samples=2000,
    )
    # 名前を付けて永続化する
    dataset.name = DATASET_NAME
    dataset.persistent = True

    return dataset


def export(dataset):
    """
    データセットをエクスポートする
    """

    train_dataset = dataset[:1500]
    val_dataset = dataset[1600:1800]
    test_dataset = dataset[1800:]

    # YOLO V5 形式でエクスポート
    train_dataset.export(
        export_dir=f"{OUTPUT_DIR}",
        dataset_type=DATASET_TYPE,
        split="train",
        classes=CLASSES,
    )
    val_dataset.export(
        export_dir=f"{OUTPUT_DIR}",
        dataset_type=DATASET_TYPE,
        split="val",
        classes=CLASSES,
    )
    test_dataset.export(
        export_dir=f"{OUTPUT_DIR}",
        dataset_type=DATASET_TYPE,
        split="test",
        classes=CLASSES,
    )


def write_list_file(split):
    """
    リストファイルを書き出す
    """

    files = glob.glob(f"{OUTPUT_DIR}/images/{split}/*.jpg")
    files = [line.replace("training_data", ".") + "\n" for line in files]
    with open(f"{OUTPUT_DIR}/{split}.txt", mode="w", encoding="utf-8") as list_file:
        list_file.writelines(files)


def compose():
    """
    ファイルを圧縮する
    """

    with tarfile.open(TARFILE_NAME, "w:gz") as tar:
        tar.add(OUTPUT_DIR, arcname=".")


def upload():
    """
    S3 にファイルをアップロードする
    """

    s3_client = boto3.client("s3")
    s3_client.upload_file(TARFILE_NAME, S3_BUCKET, f"yolov7_sample/{TARFILE_NAME}")


def main():
    """
    メイン処理
    """

    if not os.path.exists(OUTPUT_DIR):
        dataset = download()
        export(dataset)
        write_list_file("train")
        write_list_file("val")
        write_list_file("test")

    if not os.path.exists(TARFILE_NAME):
        compose()

    upload()


if __name__ == "__main__":
    main()
