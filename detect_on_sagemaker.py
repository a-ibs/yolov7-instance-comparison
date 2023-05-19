# coding: utf-8

"""
SageMaker動作確認用
"""

import glob
import json
import logging
import os
from argparse import ArgumentParser
from datetime import datetime

import boto3
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

CLIENT = boto3.client("sagemaker-runtime", region_name="us-west-2")


def load_image(path):
    """
    画像読込
    """

    return Image.open(path).convert("RGB")


def draw_results(
    img,
    dst_path,
    results,
    color=(255, 255, 0),
    font_path="DejaVuSans.ttf",
):  # pylint: disable=too-many-locals
    """
    検出結果を描画する
    """

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 24)
    width, height = img.size

    for result in results:
        rect = result["box"]
        ymin, xmin, ymax, xmax = rect
        min_x = float(xmin) * width
        min_y = float(ymin) * height
        max_x = float(xmax) * width
        max_y = float(ymax) * height
        draw.rectangle([(min_x, min_y), (max_x, max_y)], outline=color, width=8)
        text = result["class_label"]
        if "prob" in result:
            text += " " + str(int(round(result["prob"], 2) * 100))
        draw.text(
            (min_x, min_y),
            text,
            font=font,
            fill=(255, 0, 0),
        )

    img.save(dst_path)

    return img


def parse_args():
    """引数をパースする

    Returns:
        dict: パース結果
    """

    argparser = ArgumentParser()
    argparser.add_argument(
        "-e",
        "--endpoint",
        required=False,
        type=str,
        default="sagemaker-yolov7-serve-endpoint",
        help="SageMaker endpoint name",
    )
    argparser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input image or directory path",
    )
    argparser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory",
    )
    argparser.add_argument(
        "-c",
        "--confidence",
        required=False,
        type=float,
        default=0.3,
        help="Detection confidence threshold",
    )
    argparser.add_argument(
        "-n",
        "--nms",
        required=False,
        type=float,
        default=0.6,
        help="NMS threshold",
    )
    return argparser.parse_args()


def detect_from_image(args):
    """
    画像から検出する
    """

    img_path = args.input

    with open(img_path, "rb") as image_file:
        payload = image_file.read()

    attributes = ""
    attributes += f"score_threshold={args.confidence}"
    attributes += f",nms_threshold={args.nms}"

    begin_time = datetime.now()

    response = CLIENT.invoke_endpoint(
        EndpointName=args.endpoint,
        Body=payload,
        CustomAttributes=attributes,
        ContentType="image/jpeg",
        Accept="application/json",
    )

    logger.info("%s Response time: %s", img_path, datetime.now() - begin_time)

    result = json.loads(response["Body"].read().decode())

    basename = os.path.basename(img_path)
    output_path = os.path.join(args.output, basename)

    predictions = []
    for prediction in result["predictions"]:
        box = prediction["box"]
        predictions.append(
            {
                "box": [box[0], box[1], box[2], box[3]],
                "prob": prediction["prob"],
                "class_label": prediction["class_label"],
            }
        )

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    with open(
        output_path.replace(".jpg", ".json"), mode="w", encoding="utf-8"
    ) as json_file:
        json.dump(predictions, json_file, indent=2)

    img = load_image(img_path)
    draw_results(
        img, output_path, predictions, font_path="/System/Library/Fonts/Keyboard.ttf"
    )


def detect_from_directory(args):
    """
    ディレクトリー内の画像から検出する
    """

    os.makedirs(args.output, exist_ok=True)

    img_list = sorted(glob.iglob(args.input + "/**/*.jpg", recursive=True))
    for img_path in img_list:
        args.input = img_path
        detect_from_image(args)


def main(args):
    """メイン処理

    Returns:
        args: 引数
    """

    if args.input.endswith(".jpg"):
        detect_from_image(args)

    else:
        detect_from_directory(args)


if __name__ == "__main__":
    main(parse_args())
