# 👁️ AIEyeCare

**AIEyeCare** is an open-source, AI-powered desktop application designed to protect your eyes and prevent digital eye strain and dry eyes during long hours of working or studying on your laptop.

---

## 🚀 What It Does
* **Real-Time Blink Monitoring:** Tracks your eye blinking behavior using advanced computer vision (`MediaPipe FaceLandmarker`) to detect low blink rates or extended periods without blinking[cite: 3].
* **Smart Notifications:** Sends system alerts when your eyes are fatigued or when your blink rate drops below healthy thresholds, reminding you to blink and rest[cite: 3].
* **Automated Screen Brightness:** Dynamically adjusts your laptop screen brightness based on your environment's lighting conditions to reduce glare and eye strain.
* **Lightweight & Clean UI:** Built with Python, featuring a modern graphical interface for easy control.

---

## 🛠️ Tech Stack
* **Python** (Core Logic)
* **MediaPipe** (Face & Eye Landmark Detection)
* **OpenCV** (Video Capture & Processing)
* **CustomTkinter / GUI** (User Interface)
* **Screen Brightness Control** (Environment-aware Lighting)

---

## ⚙️ Installation & Usage

### 1. Clone the Repository
```bash
git clone [https://github.com/ziadelalfy74/AIEyeCare.git](https://github.com/ziadelalfy74/AIEyeCare.git)
cd AIEyeCare


2. Install Dependencies
Make sure you have Python installed, then run:

pip install -r requirements.txt

3. Run the Application
python gui.py

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a pull request.