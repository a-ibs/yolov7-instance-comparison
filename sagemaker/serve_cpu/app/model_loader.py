# coding: utf-8

"""
モデルローダー
"""

import torch
from models.common import Conv  # pylint: disable=no-name-in-module
from models.experimental import attempt_load  # pylint: disable=no-name-in-module
from torch import nn
from utils.activations import Hardswish, SiLU  # pylint: disable=no-name-in-module


def load(model_dir):
    """モデル読み込み"""

    model = attempt_load(model_dir + "/yolov7x.pt", map_location=torch.device("cpu"))

    # Update model
    for _, module in model.named_modules():
        module._non_persistent_buffers_set = set()  # pylint: disable=protected-access
        if isinstance(module, Conv):
            if isinstance(module.act, nn.Hardswish):
                module.act = Hardswish()
            elif isinstance(module.act, nn.SiLU):
                module.act = SiLU()

    dry_run_input = torch.zeros([1, 3, 640, 640])

    model(dry_run_input)

    model_jit = torch.jit.trace(model, dry_run_input, strict=False)

    model_jit(dry_run_input)

    return model_jit
