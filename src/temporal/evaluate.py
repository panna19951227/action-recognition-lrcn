import sys; sys.path.append('/home/binghao/workspace/mxnet/python')
import mxnet as mx
import cPickle as pickle
import os
import numpy as np
from collections import namedtuple
from iterator import TemporalIter
from kth import KTH
import time

# load data
batch_size = 16
Batch = namedtuple('Batch', ['data'])
filepath = os.path.dirname(os.path.realpath(__file__))
inputvec_path = os.path.join(filepath, '../cache/test/inputvec')
name = 'test_walking_person10_d4_4_78'
input_vec0 = pickle.load(open(os.path.join(inputvec_path, name + '.p'), 'rb'))
input_vec = input_vec0[0:1]

imdb = KTH('../cache/test')
data_names = ['data']
data_shapes = (100, 100)
label_names = ['softmax_label']
data_batch = TemporalIter(imdb, data_shapes, batch_size, shuffle=True, is_train=True)
input_vec = data_batch._data['data']
labels = data_batch._label['softmax_label']
# input_vec = data.next().data[0]

# load model
sym, arg_params, aux_params = mx.model.load_checkpoint('resnet-50-kth', 20)
mod = mx.mod.Module(symbol=sym, context=mx.gpu(0))
mod.bind(for_training=False, data_shapes=[('data', (batch_size, 20, 100, 100))])
mod.set_params(arg_params, aux_params)

# predict
count = 0
error = 0
# mod.forward(Batch([mx.nd.array(input_vec)]))
for batch_inx in range(200):
    if batch_inx % 10 == 0:
        print('evaluating on batch {}'.format(batch_inx))
    mod.forward(Batch([input_vec]))
    prob = mod.get_outputs()[0].asnumpy()
    prob = np.squeeze(prob)
    outputs = np.argsort(prob)
    predicts = np.empty(batch_size)
    for inx, output in enumerate(outputs):
        predicts[inx] = output[-1]
    labels = labels.asnumpy()

    for i in range(batch_size):
        count += 1
        if not predicts[i] == labels[i]:
            error += 1

    data_batch.next()
    input_vec = data_batch._data['data']
    labels = data_batch._label['softmax_label']

print 'total: {}, error: {}, precision: {}'.format(int(count), int(error), float(count-error) / count)
# actionnames = ['boxing', 'handclapping', 'handwaving', 'jogging', 'running', 'walking']
# for i in a[0:6]:
#     print('probability=%f, class=%s' % (prob[i], actionnames[i]))
# print a

