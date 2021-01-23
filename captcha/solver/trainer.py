import os
import pickle

import tensorflow.keras as ker

input_dir = "train_data/letters"
model_file = "model.hdf5"
label_file = "labels.dat"

w = h = 20
labels = sorted(os.listdir(input_dir))

# Define model
model = ker.Sequential([
    ker.layers.experimental.preprocessing.Rescaling(1. / 255),
    ker.layers.Flatten(),
    ker.layers.Dense(128, activation="relu"),
    ker.layers.Dense(len(labels), activation="softmax")
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Fetch training set
training_set = ker.preprocessing.image_dataset_from_directory(input_dir, image_size=(w, h), label_mode="categorical", color_mode="grayscale", shuffle=True)

# Train the network and save it
model.fit(training_set, epochs=10)
model.save(model_file)

# Save labels
with open(label_file, "wb") as file:
    pickle.dump(labels, file)
