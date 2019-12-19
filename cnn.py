import itertools
import numpy as np
import plotly.graph_objs as go
import plotly.offline as py

from keras.utils.np_utils import to_categorical # convert to one-hot-encoding
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D, Activation
from keras.optimizers import RMSprop
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau


def print_data_info():
    print("CNN DATA INFO".center(80, "#"))
    print("Train".center(40, "_"))
    print("Shape: ", x_train_cnn.shape)
    print("Test".center(40, "_"))
    print("Shape: ", x_test_cnn.shape)
    print("Val".center(40, "_"))
    print("Shape: ", x_val_cnn.shape)


def train_cnn(x_train, y_train, x_val, y_val, batch_size, epochs, hidden_units):

    y_train_cnn = to_categorical(y_train, num_classes=10)  # To [0,0,0,0,0,1,0,0,0,0]
    y_val_cnn = to_categorical(y_val, num_classes=10)
    x_train_cnn = x_train.values.reshape(-1, 28, 28, 1)  # Extra dimention for rgb channels
    x_val_cnn = x_val.values.reshape(-1, 28, 28, 1)
    x_test_cnn = x_test.values.reshape(-1, 28, 28, 1)

    model = Sequential()

    model.add(Dense(10, input_dim=784))
    model.add(Activation('relu'))

    optimizer = RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"])


    # Set a learning rate annealer
    learning_rate_reduction = ReduceLROnPlateau(monitor='val_acc',
                                                patience=3,
                                                verbose=1,
                                                factor=0.5,
                                                min_lr=0.00001)

    epochs = 200
    batch_size = 250

    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # dimesion reduction
        rotation_range=10,  # randomly rotate images in the range 0 to 10 degrees
        zoom_range=0.1,  # Randomly zoom image 10%
        width_shift_range=0.1,  # randomly shift images horizontally 1%
        height_shift_range=0.1,  # randomly shift images vertically 1%
        horizontal_flip=False,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    datagen.fit(x_train_cnn)

    history = model.fit_generator(datagen.flow(x_train_cnn, y_train_cnn, batch_size=batch_size),
                                  epochs=epochs, validation_data=(x_val_cnn, y_val_cnn),
                                  steps_per_epoch=x_train_cnn.shape[0] // batch_size)

    val_accuracy = history.history['val_acc']
    CNN_accuracy = round(max(val_accuracy) * 100, 2)
    print("CNN accuracy is ", CNN_accuracy)


def train_nn(x_train, y_train, x_val, y_val, batch_size, epochs, hidden_units):

    y_train_cnn = to_categorical(y_train, num_classes=10)  # To [0,0,0,0,0,1,0,0,0,0]
    y_val_cnn = to_categorical(y_val, num_classes=10)
    x_train_cnn = x_train.values.reshape(-1, 784)
    x_val_cnn = x_val.values.reshape(-1, 784)

    model = Sequential()

    model.add(Dense(10, input_dim=784, activation='relu'))
    model.add(Dense(hidden_units, activation='relu'))
    model.add(Dense(hidden_units, activation='relu'))
    model.add(Dense(10, activation='softmax'))

    model.compile(optimizer='rmsprop',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(x_train_cnn,
                        y_train_cnn,
                        batch_size=batch_size,
                        epochs=epochs,
                        validation_data=(x_val_cnn, y_val_cnn),
                        verbose=2)

    val_accuracy = history.history['val_accuracy']
    CNN_accuracy = round(max(val_accuracy) * 100, 2)
    print("CNN accuracy is ", CNN_accuracy)

    accuracy = []
    num_of_epochs = []
    for i in range(1, epochs, 5):
        accuracy.append(round(100 * val_accuracy[i], 3))
        num_of_epochs.append(i)
    trace1 = go.Scatter(y=accuracy, x=num_of_epochs, mode="lines")
    data = [trace1]
    layout = dict(title='CNN Accuracy',
                  autosize=False,
                  width=800,
                  height=500,
                  yaxis=dict(title='Accuracy (%)', gridwidth=2, gridcolor='#bdbdbd'),
                  xaxis=dict(title='Number of Epochs', gridwidth=2, gridcolor='#bdbdbd'),
                  font=dict(size=14)
                  )
    fig = dict(data=data, layout=layout)
    py.plot(fig)
