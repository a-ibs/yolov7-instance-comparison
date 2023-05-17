# coding: utf-8

"""
モデルローダー
"""

import torch
import torch_neuron  # noqa: F401 pylint: disable=unused-import


def load(model_dir):
    """モデル読み込み"""

    model_neuron = torch.jit.load(model_dir + "/yolov7x_neuron.pt")

    dry_run_input = torch.zeros([1, 3, 640, 640], dtype=torch.float32)

    model_neuron(dry_run_input)

    return model_neuron
