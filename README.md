# KasongoType - Cyberpunk Typing Trainer

![KasongoType Logo](desktop/assets/icon.ico)

**KasongoType** is a next-generation typing trainer with a sleek cyberpunk aesthetic. It helps users improve typing speed and accuracy through an immersive neon-on-black interface. Whether on the web or desktop, KasongoType delivers a consistent, futuristic typing experience.


## 🚀 Features

- **Cyberpunk Design** – Neon green on black for a futuristic terminal vibe.
- **Cross-Platform** – Use in your browser or as a standalone desktop app.
- **Real-Time Feedback** – WPM, accuracy, and error tracking as you type.
- **Progress Tracking** – Visual charts that show your improvement.
- **Multiple Difficulty Levels** – From beginner warm-ups to expert drills.
- **Consistent UI** – Unified experience across web and desktop.


## 📁 Project Structure

<pre>
KasongoType/
├── web/                   ← Web app using Flask
│   ├── static/            ← CSS, JS, and assets
│   ├── templates/         ← HTML templates
│   └── app.py             ← Flask entry point
├── desktop/               ← PyQt5 desktop version
│   ├── main.py            ← Desktop app entry
│   └── assets/            ← App icons & desktop resources
├── common/                ← Shared backend logic
│   ├── data/              ← Typing exercises & user data
│   ├── typing_engine.py   ← Core typing logic
│   └── analytics.py       ← User performance tracking
└── tests/                 ← Unit tests
</pre>


## 🧰 Requirements

### Web Version
- Python 3.8+
- Flask
- Modern browser (JavaScript enabled)

### Desktop Version
- Python 3.8+
- PyQt5
- PyQtWebEngine


## 📦 Installation

```bash
git clone https://github.com/Odeneho-Calculus/KasongoType.git
cd KasongoType
pip install -r desktop/requirements.txt
```


## 🖥️ Running the App

### Web Version

```bash
python web/app.py
```

Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Desktop Version

```bash
python desktop/main.py
```


## 🧪 Running Tests

```bash
python -m unittest discover tests
```


## 🛠️ Development Guide

### ➕ Adding New Exercises

Update the `common/data/exercises.json` file with this structure:

```json
{
  "levels": {
    "easy": [
      {
        "id": "exercise1",
        "title": "Getting Started",
        "text": "The quick brown fox jumps over the lazy dog."
      }
    ]
  }
}
```

### 🎨 Customizing the Theme

You can change the cyberpunk look by editing:

```plaintext
web/static/css/style.css
```


## 📄 License

This project is licensed under the [MIT License](LICENSE).


## 🙏 Credits

- Created for cyberpunk typing enthusiasts.
- Inspired by classic typing trainers and futuristic UIs.

