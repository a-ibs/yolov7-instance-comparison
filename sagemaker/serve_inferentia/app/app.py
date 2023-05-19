# coding: utf-8

"""
メインモジュール
"""

import logging
import traceback
from datetime import datetime

import connexion
import model_loader
import numpy as np
import torch
import torch.neuron
from flask import Flask, jsonify, request
from PIL import Image
from utils.datasets import letterbox  # pylint: disable=no-name-in-module
from utils.general import non_max_suppression  # pylint: disable=no-name-in-module
from waitress import serve

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

MODEL_DIR = "/opt/ml/model"

JSON_HEADER = {"ContentType": "application/json"}

logger.info("Loading model.")

MODEL_NEURON = model_loader.load(MODEL_DIR)  # pylint: disable=no-value-for-parameter

logger.info("Model loaded.")


def format_predictions(predictions, class_map, score_threshold):
    """推論結果整形"""

    formed = []
    for detection in predictions.tolist():
        box = detection[:4]
        box = [float(x) / 640 for x in box]
        prob = float(detection[4])
        class_id = int(detection[5])

        if score_threshold > prob:
            continue

        if class_id not in class_map:
            continue

        formed.append(
            {
                "class_label": class_map[class_id],
                "prob": prob,
                "box": [box[1], box[0], box[3], box[2]],
            }
        )

    return formed


def ping():
    """死活監視応答"""
    return jsonify({"success": True}), 200, JSON_HEADER


def detect_by_model(image, score_threshold, nms_threshold):
    """モデルによる検出"""

    vehicle_map = {0: "cat", 1: "dog"}

    begin_time = datetime.now()

    predictions = MODEL_NEURON(image)

    logger.info("Elapsed time: %s", datetime.now() - begin_time)

    if isinstance(predictions, (list, tuple)):
        predictions = predictions[0]

    nms_begin_time = datetime.now()

    predictions = non_max_suppression(predictions, score_threshold, nms_threshold)[0]

    logger.info("NMS elapsed time: %s", datetime.now() - nms_begin_time)

    format_begin_time = datetime.now()

    formed_predictions = format_predictions(predictions, vehicle_map, score_threshold)

    logger.info("Format elapsed time: %s", datetime.now() - format_begin_time)

    logger.info("Predictions: %s", formed_predictions)

    return formed_predictions


def detect():
    """物体検出応答"""

    whole_begin_time = datetime.now()

    content_type = request.headers.get("Content-Type", None)

    if content_type != "image/jpeg":
        logger.warning("Invalid Content-Type: %s", content_type)
        return f"Invalid Content-Type: {content_type}", 400

    params = request.headers.get("X-Amzn-Sagemaker-Custom-Attributes", "").split(",")
    if len(params) > 1:
        params = {param.split("=")[0]: param.split("=")[1] for param in params}
    else:
        params = {}

    logger.info(params)

    score_threshold = float(params.get("score_threshold", 0.3))
    nms_threshold = float(params.get("nms_threshold", 0.6))

    logger.info("Request received.")

    try:
        image = Image.open(request.stream).convert("RGB")

        image = np.array(image, dtype=np.uint8)
        image = letterbox(image, auto=False, scaleFill=True)[0]
        image = np.ascontiguousarray(image)
        image = np.transpose(image, (2, 0, 1))
        image = torch.from_numpy(image)
        image = image.float()
        image /= 255.0
        image = image.unsqueeze(0)

        predictions = detect_by_model(image, score_threshold, nms_threshold)

        response = jsonify(
            {
                "success": True,
                "predictions": predictions,
            }
        )

        logger.info("Whole elapsed time: %s", datetime.now() - whole_begin_time)

        return response, 200, JSON_HEADER

    except Exception:  # pylint: disable=broad-except
        logger.error(traceback.print_exc())
        return jsonify({"success": False}), 500, JSON_HEADER


if __name__ == "__main__":
    app = connexion.FlaskApp(__name__, specification_dir=".")
    app.add_api("openapi.yml", arguments={"title": "Detection API"})
    serve(app.app, host="0.0.0.0", port=8080, threads=1)
