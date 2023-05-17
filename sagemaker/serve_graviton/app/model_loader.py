# coding: utf-8

"""
モデルローダー
"""

import torch
from models.experimental import attempt_load  # pylint: disable=no-name-in-module


def load(model_dir):
    """モデル読み込み"""

    model = attempt_load(model_dir + "/yolov7x.pt")

    model_compiled = torch.compile(model)

    dry_run_input = torch.zeros([1, 3, 640, 640])

    model_compiled(dry_run_input)

    return model_compiled
