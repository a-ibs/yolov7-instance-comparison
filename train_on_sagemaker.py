#!/usr/bin/env python
# coding: utf-8

"""
SageMaker で学習を実行する
"""

import json
import os
from argparse import ArgumentParser

import boto3

import sagemaker

ROLE_ID = "sagemaker-yolov7-train-role"
S3_BUCKET = os.environ.get("S3_BUCKET")
TARFILE_NAME = "inputs.tgz"
REPOSITORY_NAME = "sagemaker-yolov7-train"


def parse_args(default_instance_type):
    """
    引数をパースする
    """

    argparser = ArgumentParser()
    argparser.add_argument(
        "-i",
        "--input-path",
        required=False,
        default=f"yolov7_sample/{TARFILE_NAME}",
        help="Input S3 path",
    )
    argparser.add_argument(
        "-o",
        "--output-path",
        required=False,
        default="yolov7_sample/models",
        help="Output S3 path",
    )
    argparser.add_argument(
        "-r",
        "--region",
        required=False,
        default="us-west-2",
        help="SageMaker region",
    )
    argparser.add_argument(
        "-j",
        "--job-name",
        required=False,
        default="yolov7-training",
        help="SageMaker job name prefix",
    )
    argparser.add_argument(
        "-t",
        "--instance-type",
        required=False,
        default=default_instance_type,
        help="SageMaker instance type",
    )
    return argparser.parse_args()


def generate_estimator(parsed_args):
    """
    estimator を生成する
    """

    client = boto3.client(service_name="sagemaker", region_name=parsed_args.region)
    boto_session = boto3.session.Session(region_name=parsed_args.region)
    sagemaker_session = (
        sagemaker.session.Session(  # pylint: disable=c-extension-no-member
            boto_session=boto_session, sagemaker_client=client
        )
    )

    caller_identity = boto3.client("sts").get_caller_identity()
    account_id = caller_identity["Account"]
    container = (
        f"{account_id}.dkr.ecr.{parsed_args.region}.amazonaws.com/{REPOSITORY_NAME}"
    )
    role = f"arn:aws:iam::{account_id}:role/{ROLE_ID}"
    s3_output_path = f"s3://{S3_BUCKET}/{parsed_args.output_path}"

    estimator = sagemaker.estimator.Estimator(  # pylint: disable=c-extension-no-member
        container,
        role,
        instance_count=1,
        instance_type=parsed_args.instance_type,
        max_run=(24 * 60 * 60),
        volume_size=5,
        output_path=s3_output_path,
        base_job_name=parsed_args.job_name,
        sagemaker_session=sagemaker_session,
    )

    return estimator


def train(parsed_args):
    """
    学習の実行
    """

    estimator = generate_estimator(parsed_args)

    with open(
        "sagemaker/train/app/cfg/hyperparameters.json", mode="r", encoding="utf-8"
    ) as file:
        hyperparameters = json.load(file)

    estimator.set_hyperparameters(
        name=hyperparameters.get("name", "yolov7x-sample"),
        data=hyperparameters.get("data", "data/sample.yaml"),
        size=hyperparameters.get("size", "640"),
        cfg=hyperparameters.get("cfg", "cfg/yolov7x.yaml"),
        weights=hyperparameters.get("weights", "yolov7x_training.pt"),
        hyp=hyperparameters.get("hyp", "data/hyp.sample.yaml"),
        device=hyperparameters.get("device", "0"),
        batch=hyperparameters.get("batch", "8"),
        workers=hyperparameters.get("workers", "4"),
        epochs=hyperparameters.get("epochs", "200"),
    )

    s3_input_path = f"s3://{S3_BUCKET}/{parsed_args.input_path}"
    estimator.fit({"main": s3_input_path})


if __name__ == "__main__":
    train(parse_args("ml.g4dn.xlarge"))
