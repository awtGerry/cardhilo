import os
import shutil
import random

# Paths
train_images_dir = 'data/axioma/images/train'
train_labels_dir = 'data/axioma/labels/train'
val_images_dir = 'data/axioma/images/val'
val_labels_dir = 'data/axioma/labels/val'

# Create validation directories if they don't exist
os.makedirs(val_images_dir, exist_ok=True)
os.makedirs(val_labels_dir, exist_ok=True)

# Get list of all training images
train_images = [f for f in os.listdir(train_images_dir) if f.endswith('.jpg')]

# Shuffle and split the images
random.shuffle(train_images)
val_images = train_images[:1001]  # Take first 1001 images for validation
train_images = train_images[1001:]  # Remaining for training

# Move validation images and labels
for img in val_images:
    img_path = os.path.join(train_images_dir, img)
    label_path = os.path.join(train_labels_dir, img.replace('.jpg', '.txt'))
    shutil.move(img_path, os.path.join(val_images_dir, img))
    shutil.move(label_path, os.path.join(val_labels_dir, img.replace('.jpg', '.txt')))

# Print confirmation
print(f"Moved {len(val_images)} images to validation set.")
