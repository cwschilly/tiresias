from preprocessing.preprocess import read_and_clean
from preprocessing.tensors import get_training_tensors

from network.train import train_model
from network.export import export_model, write_pipeline

## Load the data
ratings = read_and_clean()

## Build and train the model
X, y, scaler, pca = get_training_tensors(ratings)
model = train_model(X, y)

## Export the model and pipeline params
export_model(model)
write_pipeline(scaler, pca)
