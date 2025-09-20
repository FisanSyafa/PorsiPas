# PorsiPas AI
[Click Here to Try PorsiPas Chatbot](https://porsipas-ai.streamlit.app)

AI chatbot using NLP, LLM, and RAG to analyze food nutrition intake and recommend the next meal for balanced nutrition.

**PorsiPas AI** is an intelligent chatbot designed to be your personal nutrition assistant. This application can analyze the foods you consume (from both text and images), provide detailed nutrition information, and recommend the next meal to help balance your daily nutrition.

The project is built with **Streamlit** for the user interface and powered by the **Google Gemini API** with a **RAG (Retrieval-Augmented Generation)** keyword-based architecture.

---

## ✨ Key Features

* **Natural Language Input**: Enter your daily meals in plain sentences (example: "I had soto for breakfast and rendang for lunch").
* **Food Recognition from Images**: Upload a photo of your food, and the AI will attempt to identify it.
* **Comprehensive Nutrition Database**: Combines multiple CSV files covering raw ingredients, local ready-to-eat foods, and fast food.
* **Smart Analysis & Recommendations**: Provides nutrition breakdowns and actionable menu suggestions to balance your diet.
* **Smart Search (Fallback)**: If a specific dish cannot be found (e.g., "soto ayam"), the system will attempt to find a more general version ("soto").

---

## 🛠️ Architecture & Technology

The app uses a **keyword-based RAG (Retrieval-Augmented Generation)** architecture to provide relevant answers based on the supplied database.

**Workflow:**
1. **User Input**: Accepts text or image input.
2. **Entity Extraction**: The Gemini model extracts food names from the input.
3. **Retrieval**: The system performs keyword-based searches in the combined CSV databases to find relevant nutrition data.
4. **Augmentation**: The retrieved nutrition data is merged into a custom prompt.
5. **Generation**: The enriched prompt is sent to Gemini to generate a structured response with analysis and recommendations.

**Core Technologies:**
* **Python**: Primary programming language.
* **Streamlit**: To build the interactive web interface.
* **Google Gemini API (1.5 Flash)**: Large Language Model (LLM) for language processing, image recognition, and response generation.
* **Pandas**: For handling and querying CSV data.

---

## 🚀 Installation & Usage

Follow the steps below to run this project on your local machine.

### 1. Prerequisites
* Python.
* miniconda/anaconda
* Git.

### 2. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/FisanSyafa/PorsiPas.git
```

### 3. Create a Conda Environment
```bash
conda create -n chatbot-env python=3.9
conda activate chatbot-env
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Once everything is set up, run the Streamlit app:
```bash
streamlit run healthcare_assistant.py
```

The app will open in your browser. Enter and confirm your GEMINI API Key in the sidebar to get started!
