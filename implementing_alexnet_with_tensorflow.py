# -*- coding: utf-8 -*-
"""Implementing AlexNet with Tensorflow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o0KAViL4WAl6sa6tTBxPVZ4gybYiqw57

AlexNet was published in 2012 by Alex Krizhevsky et al. and let to the popularity of deep learning, in particular the use of CNNs.


In 2009, Imagenet data was released. It has more than 15 million images that are labelled in more than 20,000 classes.
GPUs become more popular in deep learning.

Here i will be implementing AlexNet on the MNIST dataset. MNIST has been used instead of ImageNet because of it's simplicity.
Nonetheless, this model can be used for any dataset with little to no variations in code.

**Importing Libraries and Dependencies**
"""

import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import datasets, layers, models, losses

"""**Loading the data**

One important notice is that the original AlexNet model receives images with the size 224 x 224 x 3 however, MNIST images are 28 x 28. The third axis is expanded and repeated 3 times to make image sizes 28 x 28 x 3. It will be then resized at the first layer of the model to 224 x 224 x 3.

"""

(x_train,y_train),(x_test,y_test) = datasets.mnist.load_data()

x_train = tf.pad(x_train, [[0, 0], [2,2], [2, 2]]) / 255
x_test = tf.pad(x_test, [[0, 0], [2,2], [2,2]])/255

x_train = tf.expand_dims(x_train, axis = 3, name = None)
x_test = tf.expand_dims(x_test, axis =3, name = None)

x_train = tf.repeat(x_train, 3, axis = 3)
x_test = tf.repeat(x_test, 3, axis = 3)

x_val = x_train[-2000:,:,:,:]
y_val = y_train[-2000:]
x_train = x_train[:-2000,:,:,:]
y_train = y_train[:-2000]

"""
AlexNet is one of the first examples of deep convolutional neural networks and it swept the competitions thanks to its high complexity (at the time) and the training procedure that is performed on GPUs. However, it was still not easy to train large networks due to vanishing or exploding gradient problems and long training times. In general, gradient-based deep neural networks are inclined to face unstable gradient updates. AlexNet is large enough to learn the patterns in the ImageNet dataset but very shallow compared to today???s models. Why AlexNet could not be designed deeper becomes clearer after understanding the residual connections in ResNet.

The first layer (resizing layer) of the model does not exist in the original implementation since the data were already compatible with the model in terms of image size. For a compatible representation, MNIST images were interpolated bilinearly such that the new sizes are 224 x 224 (also one more dimension for 3 channels corresponding to RGB channels in ImageNet).

The first five layers are similar to LeNet layers in a sense. The layers consist of 96 filters with the sizes of 11 x 11, 256 layers with the sizes of 5 x 5, 384 layers with the sizes of 3 x 3, 384 layers with the sizes of 3 x 3, and finally 256 filters with the sizes of 3 x 3, respectively. 




Unlike LeNet,AlexNet uses ReLU[5] activation function. ReLU does not involve exponentiation operation, which is computationally expensive, thus ReLU is very cheap to calculate. It also reduces the effects of vanishing gradient and resembles the mechanism of biological cells. Yet, ReLU sometimes leads to dying neurons and it is advised to keep track of the activations during the first few epochs of the training.


Another new concept is local response normalization, which is a novel trick to make training go smooth and stable. Unlike sigmoid and tanh activations, ReLU has an unbounded response in the positive edge. Thus, activations can blow up and hurt the training procedure as the training continues. This is why some kind of normalization is required. Local response normalization attempts to balance the activation values in a pixel among neighboring channels. Each activation is divided by the sum of the squares of neighboring channels??? activations in the same pixel location. This idea is borrowed from the neurobiological term lateral inhibition and first described in the original AlexNet paper[1] in detail. Nowadays batch normalization is much more pervasive in the literature and it is faster than LRN but it was not available back in 2012.


After the convolutional layers, the resulting tensor (1 x 1 x 256) is flattened and fed into fully connected layers. After passing two hidden layers having the sizes of 4096, final class scores (for 10 classes) are obtained by softmax operation. Here, dropout is a measure to prevent overfitting. In the model below, half of the neurons in hidden fully connected layers are shut down randomly. During each forward passing of the training samples, a specified fraction of the activations in a layer is set to 0, and in order to keep the mean activation level of the layer the same, the remaining activations are divided by dropout probability (in this case divided by 0.5 or simply multiplied by 2). During test time, dropout is not performed."""



model = models.Sequential()
model.add(layers.experimental.preprocessing.Resizing(224, 224, interpolation="bilinear", input_shape=x_train.shape[1:]))

model.add(layers.Conv2D(96, 11, strides=4, padding='same'))
model.add(layers.Lambda(tf.nn.local_response_normalization))
model.add(layers.Activation('relu'))
model.add(layers.MaxPooling2D(3, strides=2))

model.add(layers.Conv2D(256, 5, strides=4, padding='same'))
model.add(layers.Lambda(tf.nn.local_response_normalization))
model.add(layers.Activation('relu'))
model.add(layers.MaxPooling2D(3, strides=2))

model.add(layers.Conv2D(384, 3, strides=4, padding='same'))
model.add(layers.Activation('relu'))
model.add(layers.Conv2D(384, 3, strides=4, padding='same'))
model.add(layers.Activation('relu'))

model.add(layers.Conv2D(256, 3, strides=4, padding='same'))
model.add(layers.Activation('relu'))

model.add(layers.Flatten())

model.add(layers.Dense(4096, activation='relu'))
model.add(layers.Dropout(0.5))

model.add(layers.Dense(4096, activation='relu'))
model.add(layers.Dropout(0.5))

model.add(layers.Dense(10, activation='softmax'))

"""The model summary is as follows:"""

model.summary()

"""Adam is the most common choice among the deep learning community for adaptively updating the learning rate."""

model.compile(optimizer='adam', loss=losses.sparse_categorical_crossentropy, metrics=['accuracy'])

history = model.fit(x_train, y_train, batch_size=64, epochs=40, validation_data=(x_val, y_val))

"""The accuracy rises up very quickly in the validation set and fluctuates above 98% throughout the training, which means that only one epoch was already enough for the relatively small validation test. Training loss decreases consistently as expected. Using LRN instead of batch normalization slows down the training while not really contributing to the final accuracy."""

fig, axs = plt.subplots(2, 1, figsize=(15,15))
axs[0].plot(history.history['loss'])
axs[0].plot(history.history['val_loss'])
axs[0].title.set_text('Training Loss vs Validation Loss')
axs[0].set_xlabel('Epochs')
axs[0].set_ylabel('Loss')
axs[0].legend(['Train', 'Val'])
axs[1].plot(history.history['accuracy'])
axs[1].plot(history.history['val_accuracy'])
axs[1].title.set_text('Training Accuracy vs Validation Accuracy')
axs[1].set_xlabel('Epochs')
axs[1].set_ylabel('Accuracy')
axs[1].legend(['Train', 'Val'])

"""The test accuracy came out at 98.79%"""



"""AlexNet started a revolution in Computer Vision and paved the road for many other deep learning models. 

The winner models in the ILSRVC Competition continue to reach higher and higher accuries over the years as it became more competitive.

The use of GPUs, ReLU activations and local response normalization layers abd drop-out mechanism were all new compared to the predecessor model, LetNet.

In this implementation, a relatively light MNIST dataset is used for fast training and simplicity, for which AlexNet is an overkill. The original model is trained and evaluated on ImageNet in 2012.
"""



"""The reference is from this article: https://medium.com/swlh/alexnet-with-tensorflow-46f366559ce8"""