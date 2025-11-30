# Craft Today!

A Streamlit web application that helps users discover and explore craft projects from Instructables. Browse projects by category, popularity, and get AI-powered step-by-step instructions.

## Installation

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Install Playwright browser**
   ```
   python -m playwright install chromium
   ```

3. **Set up OpenAI API key**
   - Create a `keys.py` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY = "your-api-key-here"`

## Running the App

```
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Select your preferences** - Choose category, number of projects, and sort method
2. **Click "Show Projects"** - View filtered results table
3. **Select a project** - Choose from the dropdown list
4. **Click "Get Instructions"** - Get AI-analyzed materials and step-by-step instructions

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping and AI analysis