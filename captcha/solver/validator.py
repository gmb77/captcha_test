import tensorflow.keras as ker

input_dir = "validation_data/letters"
model_file = "model.hdf5"
w = h = 20

# Fetch validating set and load model
validating_set = ker.preprocessing.image_dataset_from_directory(input_dir, image_size=(w, h), label_mode="categorical", color_mode="grayscale", shuffle=True)
model = ker.models.load_model(model_file)

model.evaluate(validating_set)
