# Chatbot Project

This project is a chatbot built using **PyTorch** and other dependencies. Follow the steps below to set up and run the project.

---

## 🚀 Setup Instructions

### 1. Create & Activate Conda Environment with PyTorch
Make sure you have **Anaconda/Miniconda** installed.

```bash
# Create a new conda environment with Python 3.8 (recommended)
conda create -n chatbot python=3.8 -y

# Activate the environment
conda activate chatbot

# Install PyTorch (CPU version, change if GPU available)
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

---

### 2. Install Dependencies
Install the required Python libraries listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

---

### 3. Run the Project
After installing dependencies, you can run the chatbot.

```bash
python train.py    # To train the chatbot model
python chat.py     # To start chatting with the bot
```

---

## 📂 Project Structure
- `train.py` → Script to train the chatbot model  
- `chat.py` → Script to interact with the trained chatbot  
- `model.py` → Defines the neural network model  
- `nltk_utils.py` → Helper functions for tokenization & stemming  
- `data/` → Dataset for training  
- `requirements.txt` → List of dependencies  

---

## ✅ Notes
- Make sure Python ≥ 3.8 is installed.  
- If you face issues with PyTorch installation, check [PyTorch official site](https://pytorch.org/get-started/locally/).  
- GPU installation requires CUDA.  
