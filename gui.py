import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

import cv2
import threading
import customtkinter as ctk
from PIL import Image, ImageTk
from engine import EyeCareEngine

ctk.set_appearance_mode("Dark")

class ModernEyeCareGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Eye Care - Cybernetic Health Engine")
        self.geometry("1000x650")
        self.configure(fg_color="#0F111A")
        self.resizable(False, False)
        self.iconbitmap(resource_path("icon.ico"))

        self.engine = EyeCareEngine(model_path=resource_path('face_landmarker.task'))
        self.is_running = False
        self.cap = None
        self.thread = None

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color="#1A1D24", corner_radius=20, border_width=1, border_color="#2A2E3D")
        self.sidebar.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="👁️ EYE CARE AI", 
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#00E5FF"
        )
        self.logo_label.pack(padx=20, pady=(25, 2))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar, 
            text="Vision & Brightness Guard", 
            font=ctk.CTkFont(size=11),
            text_color="#6C7289"
        )
        self.subtitle_label.pack(padx=20, pady=(0, 20))

        self.btn_toggle = ctk.CTkButton(
            self.sidebar, 
            text="START MONITOR", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00E5FF", 
            text_color="#0F111A",
            hover_color="#00B0FF",
            height=48,
            corner_radius=12,
            command=self.toggle_engine
        )
        self.btn_toggle.pack(padx=20, pady=10, fill="x")

        self.status_card = ctk.CTkFrame(self.sidebar, fg_color="#12141C", corner_radius=14, border_width=1, border_color="#252936")
        self.status_card.pack(padx=20, pady=15, fill="x")

        self.status_title = ctk.CTkLabel(self.status_card, text="LIVE METRICS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#6C7289")
        self.status_title.pack(padx=15, pady=(12, 2), anchor="w")

        self.lbl_blinks = ctk.CTkLabel(self.status_card, text="Blinks: 0", font=ctk.CTkFont(family="Consolas", size=14), text_color="#00E5FF")
        self.lbl_blinks.pack(padx=15, pady=2, anchor="w")

        self.lbl_rate = ctk.CTkLabel(self.status_card, text="Rate/Min: 0", font=ctk.CTkFont(family="Consolas", size=14), text_color="#00FF66")
        self.lbl_rate.pack(padx=15, pady=2, anchor="w")

        self.lbl_light = ctk.CTkLabel(self.status_card, text="Room Light: --", font=ctk.CTkFont(family="Consolas", size=14), text_color="#FFD600")
        self.lbl_light.pack(padx=15, pady=(2, 12), anchor="w")

        self.guide_frame = ctk.CTkFrame(self.sidebar, fg_color="#12141C", corner_radius=14)
        self.guide_frame.pack(padx=20, pady=(5, 20), fill="both", expand=True)

        guide_text = (
            "🛡️ SYSTEM FEATURES\n\n"
            "• Auto Brightness:\n"
            "  Adapts screen levels based\n"
            "  on room illumination.\n\n"
            "• Blink Protection:\n"
            "  Detects eye fatigue &\n"
            "  low blink rates safely.\n\n"
            "• Smart Notifications:\n"
            "  Sends system toasts above\n"
            "  any active window."
        )
        
        self.guide_label = ctk.CTkLabel(
            self.guide_frame, 
            text=guide_text, 
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#A0A5B5",
            justify="left"
        )
        self.guide_label.pack(padx=12, pady=12, anchor="nw")

        self.video_frame = ctk.CTkFrame(self, fg_color="#1A1D24", corner_radius=20, border_width=1, border_color="#2A2E3D")
        self.video_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        self.video_label = ctk.CTkLabel(
            self.video_frame, 
            text="📷 CAMERA OFFLINE\n\nClick START MONITOR to initialize system", 
            font=ctk.CTkFont(size=14),
            text_color="#52586B"
        )
        self.video_label.pack(expand=True, fill="both", padx=15, pady=15)

    def toggle_engine(self):
        if not self.is_running:
            self.is_running = True
            self.btn_toggle.configure(text="STOP MONITOR", fg_color="#FF3366", hover_color="#D81B60", text_color="#FFFFFF")
            
            self.thread = threading.Thread(target=self.run_monitor_loop, daemon=True)
            self.thread.start()
        else:
            self.is_running = False
            self.btn_toggle.configure(text="START MONITOR", fg_color="#00E5FF", hover_color="#00B0FF", text_color="#0F111A")
            self.video_label.configure(image="", text="📷 CAMERA OFFLINE\n\nClick START MONITOR to initialize system")
            self.lbl_blinks.configure(text="Blinks: 0")
            self.lbl_rate.configure(text="Rate/Min: 0")
            self.lbl_light.configure(text="Room Light: --")

    def update_gui_state(self, img_tk, blinks, rate, light):
        if self.is_running:
            self.video_label.configure(image=img_tk, text="")
            self.video_label.image = img_tk
            
            self.lbl_blinks.configure(text=f"Blinks: {blinks}")
            self.lbl_rate.configure(text=f"Rate/Min: {rate}")
            self.lbl_light.configure(text=f"Room Light: {light}")

    def run_monitor_loop(self):
        self.cap = cv2.VideoCapture(0)

        try:
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                
                processed_frame, blinks, rate, light = self.engine.process_frame(frame)

                rgb_image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_image)
                img = img.resize((520, 420))
                img_tk = ImageTk.PhotoImage(image=img)

                self.after(0, self.update_gui_state, img_tk, blinks, rate, light)
        except Exception as e:
            print(f"Error in monitor loop: {e}")
        finally:
            if self.cap and self.cap.isOpened():
                self.cap.release()

if __name__ == "__main__":
    app = ModernEyeCareGUI()
    app.mainloop()