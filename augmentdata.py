

# ------------------------------------------------------ Code to create the files and append to rows in the dataset -----------------------------------------------------------------------------

import csv
import random
import os
import glob
from PIL import Image
from torchvision import transforms

# Function to apply random augmentations to an image
def apply_augmentations(image):
    # Define a list of transformations to apply
    transformations = [
        transforms.RandomRotation(45),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        # Add more transformations as needed
    ]
    
    # Apply random transformations
    for transform in transformations:
        image = transform(image)
    
    return image

# Set the paths
dataset_path = 'Dataset/Plant_Village'
train_csv_path = 'Dataset/Plant_Village/valid.csv'

# Create a list to store the new rows for train.csv
new_rows = []

# Open train.csv
with open(train_csv_path, 'r') as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        file_path = row[0]
        class_name = row[1]
        
        # Open the image
        image_path = os.path.join(file_path)
        image = Image.open(image_path)
        
        # Apply augmentations
        augmented_image = apply_augmentations(image)
        
        # Generate a new random filename
        new_file_name = f'{random.randint(1, 40000)}.jpg'
        
        # Save the augmented image
        save_path = os.path.join(dataset_path, class_name, new_file_name)
        print(save_path)
        augmented_image.save(save_path)
        
        # Add a new row to train.csv
        new_row = [save_path, class_name]
        new_rows.append(new_row)

# Shuffle the new rows
random.shuffle(new_rows)

# Append the new rows to train.csv
with open(train_csv_path, 'a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(new_rows)

print('Data augmentation and CSV update complete.')





# --------------------------------------- Code to remove the files and rows from csv -------------------------------------------------





# import csv
# import os

# def remove_files_and_rows(csv_file, start_row, end_row):
#     with open(csv_file, 'r') as f:
#         reader = csv.reader(f)
#         rows = list(reader)

#     # Validate start_row and end_row
#     if start_row < 0 or end_row > len(rows) - 1:
#         print("Invalid range of rows")
#         return

#     for i in range(start_row, end_row + 1):
#         filepath = f'{dataset_path}/{rows[i][0]}'
#         if os.path.isfile(filepath):
#             os.remove(filepath)
#             # print(f"Removed file: {filepath}")
#         else:
#             print(f"File not found: {filepath}")

#     del rows[start_row:end_row + 1]

#     with open(csv_file, 'w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerows(rows)

#     print("Removed rows from the CSV file.")

# # Usage example
# csv_file = 'Dataset/Plant_Village/train.csv'
# start_row = 12569
# end_row = 25137
# remove_files_and_rows(csv_file, start_row, end_row)








# Just removes the generated files 


# import os

# base_dir = "Dataset/Plant_Village/"

# def remove_numerical_files(folder_path):
#     files = os.listdir(folder_path)
#     for file in files:
#         file_path = os.path.join(folder_path, file)
#         if os.path.isfile(file_path) and file[:-4].isdigit():
#             os.remove(file_path)
#             print(f"Removed file: {file_path}")

# def remove_numerical_files_in_folders():
#     folders = os.listdir(base_dir)
#     for folder in folders:
#         folder_path = os.path.join(base_dir, folder)
#         if os.path.isdir(folder_path):
#             remove_numerical_files(folder_path)

# # Usage example
# remove_numerical_files_in_folders()