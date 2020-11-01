import os
import csv
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

#%%
def get_data(filename):
    # You will need to write code that will read the file passed
    # into this function. The first line contains the column headers
    # so you should ignore it
    # Each successive line contians 785 comma separated values between 0 and 255
    # The first value is the label
    # The rest are the pixel values for that picture
    # The function will return 2 np.array types. One with all the labels
    # One with all the images
    #
    # Tips:
    # If you read a full line (as 'row') then row[0] has the label
    # and row[1:785] has the 784 pixel values
    # Take a look at np.array_split to turn the 784 pixels into 28x28
    # You are reading in strings, but need the values to be floats
    # Check out np.array().astype for a conversion
    with open(filename) as training_file:
        # Your code starts here
        labels_tmp, images_tmp = [], []
        # read file lines
        csv_reader = csv.reader(training_file, delimiter=',')
        next(csv_reader)
        for line in csv_reader:
            labels_tmp.append(line[0])
            image_vector = line[1:785]
            images_tmp.append(np.array_split(image_vector, 28)) # faster than tensor.reshape(28,28)
        images = np.array(images_tmp).astype('float')
        labels = np.array(labels_tmp).astype('float')
    # Your code ends here
    return images, labels


fname_train = os.path.join('D:\\PycharmProjects\\TFD_Exam\\data', 'kaggle_sign_language',
                           'sign_mnist_train.csv')
fname_test = os.path.join('D:\\PycharmProjects\\TFD_Exam\\data', 'kaggle_sign_language', 'sign_mnist_test.csv')

training_images, training_labels = get_data(fname_train)
testing_images, testing_labels = get_data(fname_test)

# Keep these
print(training_images.shape)
print(training_labels.shape)
print(testing_images.shape)
print(testing_labels.shape)

# Their output should be:
# (27455, 28, 28)
# (27455,)
# (7172, 28, 28)
# (7172,)
# %%
# In this section you will have to add another dimension to the data
# So, for example, if your array is (10000, 28, 28)
# You will need to make it (10000, 28, 28, 1)
# Hint: np.expand_dims

training_images = np.expand_dims(training_images, axis=-1)
testing_images = np.expand_dims(testing_images, axis=-1)

# Keep These
print(training_images.shape)
print(testing_images.shape)

# Their output should be:
# (27455, 28, 28, 1)
# (7172, 28, 28, 1)

# %%
# Create an ImageDataGenerator and do Image Augmentation
train_datagen = ImageDataGenerator(rescale=1.0 / 255.0,
                                   shear_range=0.2,
                                   horizontal_flip=True,
                                   height_shift_range=0.2,
                                   width_shift_range=0.2,
                                   zoom_range=0.2,
                                   rotation_range=40,
                                   fill_mode='nearest'
                                   )

validation_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

# %%
# Define the model
# Use no more than 2 Conv2D and 2 MaxPooling2D
labels_count = len(np.unique(training_labels))
print('training labels:', np.unique(training_labels))
print('testing labels:', np.unique(testing_labels))
print(labels_count) # it will be 24! two classes exist in the original dataset but not in our training/testing files
# %%

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    # tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(labels_count + 2, activation='softmax')
    # based on the dataset documentation it has 26 classes
])

model.compile(optimizer=tf.optimizers.RMSprop(lr=0.01),
              metrics=['accuracy'],
              loss=tf.keras.losses.SparseCategoricalCrossentropy())
# model.summary()

# *************************************************************************
# *************************************************************************
# Train the Model
batchSize = 100
history = model.fit(
    train_datagen.flow(training_images, training_labels, batch_size=batchSize),
    epochs=2,
    steps_per_epoch=len(training_images) // batchSize,
    validation_data=validation_datagen.flow(testing_images, testing_labels, batch_size=batchSize // 2),
    validation_steps=len(testing_images) // batchSize
)
print('*****************************')
model.evaluate(testing_images, testing_labels)
# The output from model.evaluate should be close to:
# [6.92426086682151, 0.56609035]

# %%
# Plot the chart for accuracy and loss on both training and validation

import matplotlib.pyplot as plt

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(acc))
plt.gcf()
plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()

plt.plot(epochs, loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and validation loss')
plt.legend()
plt.figure()
plt.show()
