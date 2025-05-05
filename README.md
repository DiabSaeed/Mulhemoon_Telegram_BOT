# 🧠 Mulhemoon Telegram Bot
A Telegram bot that quizzes veterinary students on pathology slides. Users receive slide images, enter their answers (name, organ, and description), and get personalized feedback including a PDF report.

## 🚀 Features
- Sends one slide at a time (image or description)

- Accepts answers from users (name + organ + description)

- Uses AI to compare answers with correct annotations

- Provides personalized feedback after 10 slides

- Generates a PDF report summarizing performance

## 🛠️ Technologies Used
- Python

- `python-telegram-bot`

- OpenAI API (for evaluating answers) or Ollama in case of not response

- ReportLab / FPDF (for PDF generation)

- SQLite (for storing slide data)

## 📦 Installation
1. Clone the repo:
`git clone https://github.com/DiabSaeed/Mulhemoon_Telegram_BOT.git
cd Mulhemoon_Telegram_BOT.git
`
2. Create a virtual environment:
`python -m venv venv
source venv/bin/activate  # On Windows use "venv\Scripts\activate"
`
3. Install dependencies:
`pip install -r requirements.txt`
4. Set up your environment variables (.env file):
`TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key
`

## 🧪 Usage
1. Run the bot:
`python bot.py`
2. Interact with the bot on Telegram.

## 🧠 Quiz Flow

1. Bot sends an image from the slide database

2. User responds with the slide name and description

3. Bot evaluates response using AI

4. After 10 slides, a performance summary is generated as a PDF

## ✨ Future Improvements

1. Add multi-language support
2. Make it survices different topics like parasitology and histology
3. Web dashboard for teachers and students' history

## 📽️ Testing of this bot
[[Watch the demo](https://youtu.be/v5kKhXOvHFo)

## 📫 Contact
For any questions or suggestions, feel free to reach out at:
📧 diab.saeed.2020@vet.usc.edu.eg
📬 Telegram: @Khedawy123
