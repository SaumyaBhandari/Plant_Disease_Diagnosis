from dataloader import get_dataloader
from network import EfficientNet

import os
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import random
from PIL import Image, ImageDraw
from PIL import Image
from torchvision.transforms import transforms
from tensorboardX import SummaryWriter
import csv
import matplotlib.pyplot as plt


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# DEVICE = "cpu"
BATCH_SIZE = 16
MODEL_NAME = "TOMATO_LEAF_PLANTVILLAGE_EFFICIENTNET_10CLASSES_V1_6"



class Model():

    def __init__(self, trained=False):
        self.model = EfficientNet().to(DEVICE)
        # self.model.load_state_dict(torch.load('saved_model/TOMATO_LEAF_PLANTVILLAGE_EFFICIENTNET_10CLASSES_V1_5_140.pth', map_location=torch.device(DEVICE)))
        if trained: self.model.load_state_dict(torch.load('saved_model/TOMATO_LEAF_PLANTVILLAGE_EFFICIENTNET_10CLASSES_V1_6_10.pth', map_location=torch.device(DEVICE)))

        self.classes = {
            0: "Tomato Bacterial Spot", 
            1: "Tomato Early Blight", 
            2: "Tomato Healthy", 
            3: "Tomato Late Blight", 
            4: "Tomato Leaf Mold", 
            5: "Tomato Septoria Leaf Spot", 
            6: "Tomato Spider Mites", 
            7: "Tomato Target Spot", 
            8: "Tomato Mosaic Virus",
            9: "Tomato Yellow Leaf Curl Virus",
        }



    def train(self, dataset, loss_func, optimizer):

        self.model.train()
        running_loss = 0.0
        running_correct = 0.0
        counter = 0

        for i, (img, label) in tqdm(enumerate(dataset), total=len(dataset)):

            counter += 1
            optimizer.zero_grad()
            image, label = img.to(DEVICE), label.to(DEVICE)
            outputs = self.model(image)
            loss = loss_func(outputs, label)
            running_loss += loss.item()

            loss.backward()
            optimizer.step()

            # calculate accuracy
            pred = outputs.argmax(1)
            # print(label, pred)
            correct = pred == label
            running_correct += correct.sum().item()

        # loss and accuracy for a complete epoch
        epoch_loss = running_loss / (counter*BATCH_SIZE)
        epoch_acc = 100. * (running_correct / (counter*BATCH_SIZE))

        return epoch_loss, epoch_acc



    def validate(self, dataset):

        self.model.eval()
        running_correct = 0.0
        counter = 0

        with torch.no_grad():
            for i, (img, label) in tqdm(enumerate(dataset), total=len(dataset)):
                counter += 1
                img, label = img.to(DEVICE), label.to(DEVICE)
                outputs = self.model(img)

                #calculate accuracy
                pred = outputs.argmax(1)
                correct = pred == label
                running_correct += correct.sum().item()

        # loss and accuracy for a complete epoch
        epoch_acc = 100. * (running_correct / (counter*BATCH_SIZE))
        return epoch_acc



    def test(self, dataset):

        # self.model.load_state_dict(torch.load('saved_model/TOMATO_LEAF_PLANTVILLAGE_EFFICIENTNET_10CLASSES_V1_3_200.pth'))
        running_correct = 0.0
        counter = 0

        # num = random.randint(0, len(dataset)-1)
        self.model.eval()
        with torch.no_grad():
            for i, (img, label) in tqdm(enumerate(dataset), total=len(dataset)):
                counter += 1
                img, label = img.to(DEVICE), label.to(DEVICE)
                outputs = self.model(img)
                #calculate accuracy
                pred = outputs.argmax(1)
                correct = pred == label
                running_correct += correct.sum().item()
                
                # if i == num:
                #     try:
                #         os.makedirs(f"saved_samples/{MODEL_NAME}", exist_ok=True)
                #     except:
                #         pass
                #     sample = random.randint(0, BATCH_SIZE//2)
                #     image = img[sample, :, :, :].cpu().numpy().transpose((1, 2, 0))
                #     image = (image * 255).astype('uint8')
                #     image = Image.fromarray(image)
                #     draw = ImageDraw.Draw(image)
                #     real_label = self.classes[label[sample].item()]
                #     pred_label = self.classes[pred[sample].item()]
                #     draw.text((image.width - 200, 0), f"Real: {real_label}", fill='red')
                #     draw.text((image.width - 200, 20), f"Predicted: {pred_label}", fill='blue')
                #     image.save(f"saved_samples/{MODEL_NAME}/{num}.jpg")

        # loss and accuracy for a complete epoch
        epoch_acc = 100. * (running_correct / (counter))
    
        return epoch_acc


 
    def fit(self, epochs, lr):

        print(f"Using {DEVICE} device...")
        print("Loading Datasets...")
        train_data, val_data, test_data = get_dataloader("Dataset/Plant_Village/", BATCH_SIZE)
        print(f"Training Samples: {len(train_data)*BATCH_SIZE}\nValidation Samples: {len(val_data)*BATCH_SIZE}\nTesting Samples: {len(test_data)*BATCH_SIZE}")
        print("Dataset Loaded.")
        print("Initializing Parameters...")
        self.model = self.model.to(DEVICE)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"The total parameters of the model are: {total_params}")
        print(f"Initializing the Optimizer")
        optimizer = optim.AdamW(self.model.parameters(), lr)
        print(f"Beginning to train...")

        crossEntropyLoss = nn.CrossEntropyLoss()
        train_loss_epochs, val_acc_epochs, test_acc_epochs = [], [], []
        writer = SummaryWriter(f'runs/{MODEL_NAME}/')
        os.makedirs("checkpoints/", exist_ok=True)
        os.makedirs("saved_model/", exist_ok=True)


        for epoch in range(1, epochs+1):

            print(f"Epoch No: {epoch}")
            train_loss, train_acc = self.train(dataset=train_data, loss_func=crossEntropyLoss, optimizer=optimizer)
            val_acc = self.validate(dataset=val_data)
            test_acc = self.test(dataset=test_data)
            train_loss_epochs.append(train_loss)
            val_acc_epochs.append(val_acc)
            test_acc_epochs.append(test_acc)
            print(f"Train Loss:{train_loss}, Train Accuracy:{train_acc}, Validation Accuracy:{val_acc}, Test Accuracy: {test_acc}")
            print(f"Test Accuracy: {test_acc}")

            if max(test_acc_epochs) == test_acc:
                torch.save({
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': train_loss,
                }, f"checkpoints/{MODEL_NAME}.tar")

            writer.add_scalar("Loss/train", train_loss, epoch)
            writer.add_scalar("Accuracy/train", train_acc, epoch)
            writer.add_scalar("Accuracy/val", val_acc, epoch)
            writer.add_scalar("Accuracy/Test", test_acc, epoch)
            
            
            print("Saving model")
            torch.save(self.model.state_dict(), f"saved_model/{MODEL_NAME}_{epoch}.pth")
            print("Model Saved")
    
            print("Epoch Completed. Proceeding to next epoch...")


        print(f"Training Completed for {epochs} epochs.")


    def infer_a_random_sample(self):
        
        try:
            os.makedirs(f"test_samples/{MODEL_NAME}", exist_ok=True)
        except:
            pass
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        with open('Dataset/Plant_Village/test.csv', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            rows = list(csvreader)
            random_row = random.choice(rows)
            path = random_row[0]
            label = random_row[1]

            image = Image.open(path)
            imageT = transform(image).unsqueeze(0).to(DEVICE)
            outputs = self.model(imageT)
            pred = outputs.argmax(1)
            pred_label = self.classes[pred.item()]
            print(pred_label)
            print(label)


            draw = ImageDraw.Draw(image)
            draw.text((image.width - 200, 0), f"Real: {label}", fill='red')
            draw.text((image.width - 200, 20), f"Predicted: {pred_label}", fill='blue')
            image.save(f"test_samples/{MODEL_NAME}/{label} -> {pred_label}.jpg")
            print("Saved a sample")




    def infer_a_sample(self, image):

        image = image.to(DEVICE)
        self.model.eval()
        # Forward pass the image through the model.
        prediction = nn.Softmax(dim=1)(self.model(image)).max(1)
        class_prob, class_index = round(prediction.values.item(), 3), prediction.indices.item()
        class_name = self.classes[class_index]
        return f'{class_name}: {class_prob*100}%'





# model = Model()
# model.fit(250, 1e-5)
 

# for i in range(10):
#     model.infer_a_random_sample()