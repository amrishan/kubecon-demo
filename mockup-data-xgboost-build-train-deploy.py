#!/usr/bin/env python
# coding: utf-8

# # Train and deploy on Kubeflow from Notebooks
# 
# This notebook introduces you to using Kubeflow Fairing to train and deploy a model to Kubeflow on Google Kubernetes Engine (GKE), and Kubeflow Pipeline to build a simple pipeline and deploy on GKE. This notebook demonstrate how to:
#  
# * Train an XGBoost model in a local notebook,
# * Use Kubeflow Fairing to train an XGBoost model remotely on Kubeflow,
#   * For simplicity code-generated syntthetic data is used. If you would like to use actual data please refer to `ames-xgboost-buld-train-deploy` notebook whcih shows how to attach and read data from PVC.  
#   * The append builder is used to rapidly build a docker image
# * Use Kubeflow Fairing to deploy a trained model to Kubeflow, and Call the deployed endpoint for predictions.
# * Use a simple pipeline to train a model in GKE. 
# 
# To learn more about how to run this notebook locally, see the guide to [training and deploying on GCP from a local notebook][gcp-local-notebook].
# 
# [gcp-local-notebook]: https://kubeflow.org/docs/fairing/gcp-local-notebook/

# ## Set up your notebook for training an XGBoost model
# 
# Import the libraries required to train this model.

# fairing:include-cell
import fire
import joblib
import logging
import nbconvert
import os
import pathlib
import sys
from pathlib import Path
import pandas as pd
import pprint
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
from importlib import reload
from sklearn.datasets import make_regression

# fairing:include-cell
def read_synthetic_input(test_size=0.25):
    """generate synthetic data and split it into train and test."""
    # generate regression dataset
    X, y = make_regression(n_samples=200, n_features=5, noise=0.1)
    train_X, test_X, train_y, test_y = train_test_split(X,
                                                      y,
                                                      test_size=test_size,
                                                      shuffle=False)

    imputer = SimpleImputer()
    train_X = imputer.fit_transform(train_X)
    test_X = imputer.transform(test_X)

    return (train_X, train_y), (test_X, test_y)

# fairing:include-cell
def train_model(train_X,
                train_y,
                test_X,
                test_y,
                n_estimators,
                learning_rate):
    """Train the model using XGBRegressor."""
    model = XGBRegressor(n_estimators=n_estimators, learning_rate=learning_rate)

    model.fit(train_X,
            train_y,
            early_stopping_rounds=40,
            eval_set=[(test_X, test_y)])

    print("Best RMSE on eval: %.2f with %d rounds",
               model.best_score,
               model.best_iteration+1)
    return model

def eval_model(model, test_X, test_y):
    """Evaluate the model performance."""
    predictions = model.predict(test_X)
    logging.info("mean_absolute_error=%.2f", mean_absolute_error(predictions, test_y))

def save_model(model, model_file):
    """Save XGBoost model for serving."""
    joblib.dump(model, model_file)
    logging.info("Model export success: %s", model_file)

# Define various constants

# ## Define Train and Predict functions

# fairing:include-cell
class HousingServe(object):
    
    def __init__(self, model_file=None):
        self.n_estimators = 50
        self.learning_rate = 0.1
        if not model_file:
            if "MODEL_FILE" in os.environ:
                print("model_file not supplied; checking environment variable")
                model_file = os.getenv("MODEL_FILE")
            else:
                print("model_file not supplied; using the default")
                model_file = "mockup-model.dat"
        
        self.model_file = model_file
        print("model_file={0}".format(self.model_file))
        
        self.model = None

    def train(self):
        (train_X, train_y), (test_X, test_y) = read_synthetic_input()
        model = train_model(train_X,
                          train_y,
                          test_X,
                          test_y,
                          self.n_estimators,
                          self.learning_rate)

        eval_model(model, test_X, test_y)
        save_model(model, self.model_file)

    def predict(self, X, feature_names):
        """Predict using the model for given ndarray."""
        if not self.model:
            self.model = joblib.load(self.model_file)
        # Do any preprocessing
        prediction = self.model.predict(data=X)
        # Do any postprocessing
        return [[prediction.item(0), prediction.item(0)]]

# ## Train your Model Locally
# 
# * Train your model locally inside your notebook

# ## Predict locally
# 
# * Run prediction inside the notebook using the newly created notebook

# ## Use Fairing to Launch a K8s Job to train your model

# ### Set up Kubeflow Fairing for training and predictions
# 
# Import the `fairing` library and configure the environment that your training or prediction job will run in.

# ## Use fairing to build the docker image
# 
# * This uses the append builder to rapidly build docker images

# ## Launch the K8s Job
# 
# * Use pod mutators to attach a PVC and credentials to the pod

# ## Deploy the trained model to Kubeflow for predictions

# ## Call the prediction endpoint
# 
# Create a test dataset, then call the endpoint on Kubeflow for predictions.

# ## Clean up the prediction endpoint
# 
# Delete the prediction endpoint created by this notebook.

# ## Build a simple 1 step pipeline

# #### Define the pipeline
# Pipeline function has to be decorated with the `@dsl.pipeline` decorator

# #### Compile the pipeline

# #### Submit the pipeline for execution


if __name__ == "__main__":
  import fire
  import logging
  logging.basicConfig(format='%(message)s')
  logging.getLogger().setLevel(logging.INFO)
  fire.Fire(HousingServe)
