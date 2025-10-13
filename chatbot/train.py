import json
from nltk_utils import tokenize, stem, bag_of_words
import numpy as np
from model import NeuralNet

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
with open("intents.json", "r")as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w,tag)) 


ignore_words = ["?", "!", ",", "."]
all_words = [stem(w)for w in all_words if w not in ignore_words]    
all_words = sorted(set(all_words))
tags = sorted(set(tags))



x_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    x_train.append(bag)


    label = tags.index(tag)
    y_train.append(label)

x_train = np.array(x_train)
y_train = np.array(y_train)  

class chatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(x_train)
        self.x_data = x_train
        self.y_data = y_train

    # dataset[idx]
    def __getitem__(self,index):
        return self.x_data[index], self.y_data[index]        
    

    def __len__(self):
        return self.n_samples
    
batch_size = 16
hidden_size = 32
output_size = len(tags)
input_size = len(x_train[0])
learning_rate = 5e-3
num_epochs = 600

# simple train/val split for monitoring
num_samples = len(x_train)
val_size = max(1, int(0.15 * num_samples))
train_size = num_samples - val_size

indices = np.random.permutation(num_samples)
train_idx, val_idx = indices[:train_size], indices[train_size:]

x_train_t = torch.tensor(x_train[train_idx], dtype=torch.float32)
y_train_t = torch.tensor(y_train[train_idx], dtype=torch.long)
x_val_t = torch.tensor(x_train[val_idx], dtype=torch.float32)
y_val_t = torch.tensor(y_train[val_idx], dtype=torch.long)

class TensorDataset(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __len__(self):
        return self.x.shape[0]
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

dataset = TensorDataset(x_train_t, y_train_t)
val_dataset = TensorDataset(x_val_t, y_val_t)
train_loader = DataLoader(dataset = dataset, batch_size = batch_size, shuffle = True, num_workers = 0)
val_loader = DataLoader(dataset = val_dataset, batch_size = batch_size, shuffle = False, num_workers = 0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu' )      
model = NeuralNet(input_size, hidden_size, output_size).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)

best_val_acc = 0.0
patience = 15
epochs_no_improve = 0

for epoch in range(num_epochs):
    model.train()
    for(words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long, device=device)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for words, labels in val_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long, device=device)
            outputs = model(words)
            _, predicted = torch.max(outputs, dim=1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    val_acc = correct / max(1, total)

    if (epoch + 1) % 50 == 0:
        print(f'epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}, val_acc={val_acc:.3f}')

    if val_acc > best_val_acc + 1e-4:
        best_val_acc = val_acc
        epochs_no_improve = 0
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= patience:
            print(f'No improvement for {patience} epochs, continuing training but consider stopping early.')

print(f'final loss, loss={loss.item():.4f}, best_val_acc={best_val_acc:.3f}')        

data = {
     "model_state": model.state_dict(),
     "input_size": input_size,
     "output_size": output_size,
     "hidden_size": hidden_size,
     "all_words": all_words,
     "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)
