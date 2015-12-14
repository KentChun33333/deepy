#!/usr/bin/env python
# -*- coding: utf-8 -*-

from deepy import *
import theano.tensor as T

class AggregationLayer(NeuralLayer):
    """
    Aggregation layer.
    """

    def __init__(self, size, activation='relu', init=None, layers=3):
        super(AggregationLayer, self).__init__("aggregation")
        self.size = size
        self.activation = activation
        self.init = init
        self.layers = layers

    def prepare(self):
        self.output_dim = self.size
        self._act = build_activation(self.activation)
        self._inner_layers = [Dense(self.size, self.activation, init=self.init).connect(self.input_dim)]
        for _ in range(self.layers - 1):
            self._inner_layers.append(Dense(self.size, self.activation, init=self.init).connect(self.size))
        self.register_inner_layers(*self._inner_layers)

        self._chain2 = Chain(self.input_dim).stack(
            Dense(self.size, self.activation, init=self.init),
            Dense(self.layers, 'linear', init=self.init),
            Softmax()
        )

        self.register_inner_layers(self._chain2)
        self._dropout = Dropout(0.1)

    def _output(self, x, test=False):
        seq = []
        v = x
        for layer in self._inner_layers:
            v = layer.call(v, test)
            v = self._dropout.call(v, test)
            seq.append(v.dimshuffle(0, "x", 1))

        seq_v = T.concatenate(seq, axis=1)

        eva = self._chain2.call(x, test)

        result = seq_v * eva.dimshuffle((0, 1, "x"))
        result = result.sum(axis=1)
        return result

    def output(self, x):
        return self._output(x, False)

    def test_output(self, x):
        return self._output(x, True)



