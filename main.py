import os
import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.utils import platform

# Set sleek dark palette
Window.clearcolor = (0.08, 0.10, 0.16, 1)

API_BASE_URL = "http://studyapi4all.42web.io/api/pdf/notes"

# ----------------- Screen 1: Notes & PDF Downloader -----------------
class NotesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title Header
        title = Label(
            text="CBSE Class X Study Hub",
            font_size='24sp',
            bold=True,
            size_hint=(1, 0.12),
            color=(0.2, 0.8, 0.9, 1)
        )
        self.layout.add_widget(title)

        # Subject Selector Mapping
        self.subject_map = {
            "Science": "sc",
            "Mathematics": "ma",
            "Social Science": "so",
            "English": "en",
            "Hindi": "hi"
        }

        # Subject Dropdown
        self.sub_spinner = Spinner(
            text="Select Subject",
            values=list(self.subject_map.keys()),
            size_hint=(1, 0.1),
            background_color=(0.18, 0.24, 0.38, 1)
        )
        self.layout.add_widget(self.sub_spinner)

        # Chapter Dropdown (1 to 16)
        self.chap_spinner = Spinner(
            text="Select Chapter",
            values=[f"Chapter {i}" for i in range(1, 17)],
            size_hint=(1, 0.1),
            background_color=(0.18, 0.24, 0.38, 1)
        )
        self.layout.add_widget(self.chap_spinner)

        # Download / Fetch Button
        self.fetch_btn = Button(
            text="📥 Fetch Notes PDF",
            font_size='18sp',
            bold=True,
            size_hint=(1, 0.12),
            background_color=(0.15, 0.65, 0.45, 1)
        )
        self.fetch_btn.bind(on_press=self.start_download)
        self.layout.add_widget(self.fetch_btn)

        # Status Label & Progress Bar
        self.status_label = Label(
            text="Choose your subject and chapter to download notes.",
            font_size='14sp',
            size_hint=(1, 0.1),
            color=(0.8, 0.8, 0.8, 1)
        )
        self.layout.add_widget(self.status_label)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, 0.05))
        self.layout.add_widget(self.progress)

        # Navigation to Interactive Quiz Mode
        quiz_nav_btn = Button(
            text="🧠 Switch to Interactive Quiz Mode",
            font_size='16sp',
            size_hint=(1, 0.12),
            background_color=(0.35, 0.45, 0.95, 1)
        )
        quiz_nav_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'quiz_screen'))
        self.layout.add_widget(quiz_nav_btn)

        self.add_widget(self.layout)

    def start_download(self, instance):
        sub_name = self.sub_spinner.text
        chap_text = self.chap_spinner.text

        if sub_name == "Select Subject" or chap_text == "Select Chapter":
            self.status_label.text = "⚠️ Please select both Subject and Chapter first."
            self.status_label.color = (1, 0.3, 0.3, 1)
            return

        sub_code = self.subject_map[sub_name]
        chap_num = chap_text.replace("Chapter ", "").strip()
        target_url = f"{API_BASE_URL}/{sub_code}/{chap_num}"

        self.status_label.text = f"Connecting to: {target_url} ..."
        self.status_label.color = (1, 0.8, 0.2, 1)
        self.progress.value = 25
        self.fetch_btn.disabled = True

        # Run fetch in a separate thread so UI does not stutter
        threading.Thread(target=self._download_worker, args=(target_url, sub_code, chap_num), daemon=True).start()

    def _download_worker(self, url, sub_code, chap_num):
        try:
            response = requests.get(url, timeout=15, stream=True)
            if response.status_code == 200:
                filename = f"Class10_{sub_code}_Ch{chap_num}.pdf"

                # Save locally in app storage
                save_path = os.path.join(App.get_running_app().user_data_dir, filename)
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                self.progress.value = 100
                self.status_label.text = f"✅ Downloaded: {filename}"
                self.status_label.color = (0.2, 1, 0.4, 1)
                self.open_pdf(save_path)
            else:
                self.status_label.text = f"❌ Server returned status {response.status_code}"
                self.status_label.color = (1, 0.3, 0.3, 1)
                self.progress.value = 0
        except Exception as e:
            self.status_label.text = f"⚠️ Connection Error: {str(e)[:45]}..."
            self.status_label.color = (1, 0.3, 0.3, 1)
            self.progress.value = 0
        finally:
            self.fetch_btn.disabled = False

    def open_pdf(self, file_path):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')

                intent = Intent(Intent.ACTION_VIEW)
                file_obj = File(file_path)
                uri = Uri.fromFile(file_obj)
                intent.setDataAndType(uri, "application/pdf")
                intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK)

                currentActivity = PythonActivity.mActivity
                currentActivity.startActivity(intent)
            except Exception:
                pass


# ----------------- Screen 2: Interactive Revision Quiz -----------------
class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = [
            {"q": "[Science] Chemical formula for Rust is:", "opts": ["Fe2O3.xH2O", "Fe3O4", "FeO", "FeCO3"], "ans": "Fe2O3.xH2O"},
            {"q": "[Maths] If discriminant D > 0, quadratic equation roots are:", "opts": ["Real & Distinct", "Real & Equal", "Imaginary", "Zero"], "ans": "Real & Distinct"},
            {"q": "[Social] In which year was the Non-Cooperation Movement launched?", "opts": ["1920", "1919", "1930", "1942"], "ans": "1920"},
            {"q": "[Science] The functional unit of Kidney is:", "opts": ["Nephron", "Neuron", "Alveoli", "Glomerulus"], "ans": "Nephron"}
        ]
        self.curr_q = 0
        self.score = 0

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.score_lbl = Label(text=f"Score: {self.score}", font_size='18sp', size_hint=(1, 0.08), color=(0.3, 0.9, 0.5, 1))
        self.layout.add_widget(self.score_lbl)

        self.q_lbl = Label(text="", font_size='20sp', size_hint=(1, 0.25), halign='center', valign='middle')
        self.q_lbl.bind(size=self.q_lbl.setter('text_size'))
        self.layout.add_widget(self.q_lbl)

        self.opts_box = GridLayout(cols=1, spacing=10, size_hint=(1, 0.45))
        self.layout.add_widget(self.opts_box)

        self.feedback_lbl = Label(text="", font_size='16sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.feedback_lbl)

        back_btn = Button(text="⬅ Back to Notes Downloader", size_hint=(1, 0.12), background_color=(0.4, 0.4, 0.5, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'notes_screen'))
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)
        self.load_question()

    def load_question(self):
        if self.curr_q < len(self.questions):
            q_data = self.questions[self.curr_q]
            self.q_lbl.text = f"Q{self.curr_q + 1}: {q_data['q']}"
            self.opts_box.clear_widgets()

            for opt in q_data['opts']:
                btn = Button(text=opt, font_size='16sp', background_color=(0.22, 0.35, 0.55, 1))
                btn.bind(on_press=self.verify_answer)
                self.opts_box.add_widget(btn)
        else:
            self.q_lbl.text = f"🎉 Quiz Complete!\nYour Score: {self.score} / {len(self.questions)}"
            self.opts_box.clear_widgets()
            retry_btn = Button(text="Restart Quiz", background_color=(0.2, 0.7, 0.4, 1))
            retry_btn.bind(on_press=self.reset_quiz)
            self.opts_box.add_widget(retry_btn)

    def verify_answer(self, instance):
        correct = self.questions[self.curr_q]['ans']
        if instance.text == correct:
            self.score += 1
            self.feedback_lbl.text = " Correct!"
            self.feedback_lbl.color = (0.2, 1, 0.4, 1)
        else:
            self.feedback_lbl.text = f" Incorrect! (Correct: {correct})"
            self.feedback_lbl.color = (1, 0.3, 0.3, 1)

        self.score_lbl.text = f"Score: {self.score}"
        self.curr_q += 1
        self.load_question()

    def reset_quiz(self, instance):
        self.curr_q = 0
        self.score = 0
        self.feedback_lbl.text = ""
        self.score_lbl.text = "Score: 0"
        self.load_question()


class CBSEClass10App(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(NotesScreen(name='notes_screen'))
        sm.add_widget(QuizScreen(name='quiz_screen'))
        return sm


if __name__ == '__main__':
    CBSEClass10App().run()
