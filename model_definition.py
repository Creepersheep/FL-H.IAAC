import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, MaxPool2D, Dense, InputLayer, BatchNormalization, Dropout

#from sklearn.linear_model import LogisticRegression
import numpy as np

import logging
logging.getLogger("tensorflow").setLevel(logging.ERROR)

class ModelCreation():

	def create_DNN(self, input_shape, num_classes):
		model = tf.keras.models.Sequential()
		model.add(tf.keras.layers.Flatten(input_shape=(input_shape[1:])))
		model.add(Dense(512, activation='relu'))
		model.add(Dense(256, activation='relu'))
		model.add(Dense(32,  activation='relu'))
		model.add(Dense(num_classes, activation='softmax'))

		model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

		return model, None

	def create_DNN_base_model(self, input_shape):
		base_model = tf.keras.models.Sequential()
		base_model.add(tf.keras.layers.Flatten(input_shape=(input_shape[1:])))
		base_model.add(Dense(512, activation='relu'))
		base_model.add(Dense(256, activation='relu'))
		base_model.add(Dense(32, activation='relu'))

		return base_model, None

	def create_DNN_transfer_learning(self, input_shape, num_classes):

		base_model = self.create_DNN_base_model(input_shape)

		model = tf.keras.models.Sequential()
		model.add(tf.keras.layers.Input(shape=(input_shape[1:])))
		model.add(base_model)
		model.add(Dense(num_classes, activation='softmax'))

		model.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

		return model, base_model

	def create_CNN(self, input_shape, num_classes):

		deep_cnn = Sequential()

		if len(input_shape) == 3:
			deep_cnn.add(InputLayer(input_shape=(input_shape[1], input_shape[2], 1)))
		else:
			deep_cnn.add(InputLayer(input_shape=(input_shape[1:])))

		deep_cnn.add(Conv2D(128, (5, 5), activation='relu', strides=(1, 1), padding='same'))
		deep_cnn.add(MaxPool2D(pool_size=(2, 2)))

		deep_cnn.add(Conv2D(64, (5, 5), activation='relu', strides=(2, 2), padding='same'))
		deep_cnn.add(MaxPool2D(pool_size=(2, 2)))
		deep_cnn.add(BatchNormalization())

		deep_cnn.add(Conv2D(32, (3, 3), activation='relu', strides=(2, 2), padding='same'))
		deep_cnn.add(MaxPool2D(pool_size=(2, 2)))
		deep_cnn.add(BatchNormalization())

		deep_cnn.add(Flatten())

		deep_cnn.add(Dense(100, activation='relu'))
		deep_cnn.add(Dense(100, activation='relu'))
		deep_cnn.add(Dropout(0.25))

		deep_cnn.add(Dense(num_classes, activation='softmax'))

		deep_cnn.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

		return deep_cnn, None


	def create_LogisticRegression(self, input_shape, num_classes):

		logistic_regression = Sequential()

		if len(input_shape) == 3:
			logistic_regression.add(Flatten(input_shape=(input_shape[1], input_shape[2], 1)))
		else:
			logistic_regression.add(Flatten(input_shape=(input_shape[1:])))

		logistic_regression.add(Dense(num_classes, activation='sigmoid'))
		logistic_regression.compile(optimizer='sgd', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

		return logistic_regression, None





