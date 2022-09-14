# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import paddle

sys.path.append("../../")
from ppfleetx.utils.tensor_fusion_helper import fused_parameters
from paddle.optimizer import Adam, AdamW, Momentum

__all__ = [
    'Adam',
    'AdamW',
    'Momentum',
    'FusedAdamW',
]


class FusedAdamW(paddle.optimizer.AdamW):
    def __init__(self, learning_rate, parameters, grad_clip, **config):
        tensor_fusion = config.pop("tensor_fusion", False)

        if tensor_fusion:
            self.decay_fused_tensors, self.all_fused_tensors = fused_parameters(
                parameters)
            decay_params = [p.name for p in self.decay_fused_tensors]
        else:
            decay_params = [
                p.name for p in parameters
                if not any(nd in p.name for nd in ["bias", "norm"])
            ]

        apply_decay_param_fun = lambda x: x in decay_params

        super().__init__(
            learning_rate=learning_rate,
            parameters=self.all_fused_tensors if tensor_fusion else parameters,
            grad_clip=grad_clip,
            apply_decay_param_fun=apply_decay_param_fun,
            **config)