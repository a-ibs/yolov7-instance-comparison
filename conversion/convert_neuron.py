# coding: utf-8

"""
Yolov7xモデル変換
"""

import torch
import torch_neuron  # noqa: F401 pylint: disable=unused-import
from models.common import Conv  # pylint: disable=no-name-in-module
from models.experimental import attempt_load  # pylint: disable=no-name-in-module
from torch import nn
from utils.activations import Hardswish, SiLU  # pylint: disable=no-name-in-module

model = attempt_load("/tmp/models/yolov7x.pt", map_location=torch.device("cpu"))

# Checks
image = torch.zeros([1, 3, 640, 640], dtype=torch.float32)

# Update model
for k, m in model.named_modules():
    m._non_persistent_buffers_set = (  # pylint: disable=protected-access
        set()
    )  # pytorch 1.6.0 compatibility
    if isinstance(m, Conv):  # assign export-friendly activations
        if isinstance(m.act, nn.Hardswish):
            m.act = Hardswish()
        elif isinstance(m.act, nn.SiLU):
            m.act = SiLU()

model.model[-1].end2end = True

model(image)  # dry run

model_neuron_for_inspection = torch.neuron.trace(model, image, skip_compiler=True)
print(model_neuron_for_inspection)


def subgraph_builder_function(node):
    """サブグラフ"""
    return "Detect" not in node.name


model_neuron = torch.neuron.trace(
    model, image, subgraph_builder_function=subgraph_builder_function
)
model_neuron.save("/tmp/models/yolov7x_neuron.pt")
