from app.models.recommender import train_model
import os

def auto_train(data):
    result = train_model(epochs=10, lr=0.01)
    return result
