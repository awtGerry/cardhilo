import cv2
import os

# Path to the images and labels
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

def draw_bounding_box(image, class_id, center_x, center_y, width, height, img_width, img_height):
    # Convert normalized coordinates to pixel values
    box_width = width * img_width
    box_height = height * img_height
    x_min = int((center_x * img_width) - (box_width / 2))
    y_min = int((center_y * img_height) - (box_height / 2))
    x_max = int((center_x * img_width) + (box_width / 2))
    y_max = int((center_y * img_height) + (box_height / 2))
    
    # Draw the bounding box
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    class_name = class_names[class_id] if class_id < len(class_names) else str(class_id)
    cv2.putText(image, class_name, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

for label_file in os.listdir(label_dir):
    if label_file.endswith('.txt'):
        image_file = label_file.replace('.txt', '.jpg')
        image_path = os.path.join(image_dir, image_file)
        label_path = os.path.join(label_dir, label_file)
        
        # Load image
        image = cv2.imread(image_path)
        img_height, img_width = image.shape[:2]
        
        # Read label file
        with open(label_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split()
                class_id = int(parts[0])
                center_x = float(parts[1])
                center_y = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Draw bounding box on the image
                draw_bounding_box(image, class_id, center_x, center_y, width, height, img_width, img_height)
        
        # Display the image with bounding boxes
        cv2.imshow('Image with Bounding Boxes', image)
        cv2.waitKey(0)

cv2.destroyAllWindows()
