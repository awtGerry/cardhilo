# Prepare the Dataset for Training:
#   -> Ensure that the dataset is split into training, validation, and testing sets.
#       This helps in evaluating the performance of your model.
#   -> Verify that the directory structure and labeling format are compatible with the
#       deep learning framework you plan to use (e.g., YOLO, TensorFlow, PyTorch).
# We'll use pytorch to train the model.

# Choose and Set Up a Model Architecture:
#   -> Select a model architecture suitable for object detection. Common choices include YOLO, Faster R-CNN, and SSD.
#   -> Set up the chosen model architecture in your preferred deep learning framework.
# We'll use YOLOv5, a popular object detection model, for this project.

# Configure the Training Parameters:
#   -> Define parameters such as learning rate, batch size, number of epochs, and any data augmentation techniques you plan to use.
# We'll use the default training parameters provided by the YOLOv5 repository.

# Train the Model:
#     -> Train the model using your training dataset and validate it using the validation dataset.
#           Monitor the training process to ensure the model is learning correctly.
#     -> Adjust hyperparameters as needed to improve performance.
# We'll train the YOLOv5 model using the training dataset prepared earlier.

# Dataset in: data/output/axioma/(images,label)/train/

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torchvision import transforms
from dataset import CardDataset
from model import YOLOv5

# Set the random seed for reproducibility
seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)

# Define the paths to the images and labels
image_dir = 'data/output/axioma/images/train/'
label_dir = 'data/output/axioma/labels/train/'

# Mapping class IDs to class names
class_names = [
    'Ac', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc',
    'Ad', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd',
    'Ah', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh',
    'As', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks',
    'joker', 'back', 'PLAYER', 'PLAYER_DD', 'DEALER'
]
