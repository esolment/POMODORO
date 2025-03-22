import time
import threading
import tkinter as tk
from tkinter import Label
import pyttsx3
import keyboard
from ctypes import windll

# Конфигурация в секундах
CONFIG = {
    "Работа": 1500,
    "маленький перерыв": 300,
    "большой перерыв": 1200,
    "количество помидорок": 12,
    "количество больших перерывов": 1
}

paused = False  # Глобальная переменная для паузы


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def block_inputs(block=True):
    """ Блокировка/разблокировка клавиатуры и мыши """
    windll.user32.BlockInput(1 if block else 0)


def is_system_locked():
    """ Проверяет, заблокирован ли экран """
    return windll.user32.GetForegroundWindow() == 0  # Если нет активного окна, система заблокирована


class PomodoroTimer:
    def __init__(self):
        self.work_time = CONFIG["Работа"]
        self.short_break = CONFIG["маленький перерыв"]
        self.long_break = CONFIG["большой перерыв"]
        self.total_pomodoros = CONFIG["количество помидорок"]
        self.long_breaks = CONFIG["количество больших перерывов"]
        self.current_pomodoro = 0
        self.schedule_long_breaks()
        self.running = True
        keyboard.add_hotkey("ctrl+q", self.stop)
        keyboard.add_hotkey("ctrl+0", self.announce_time_left)
        keyboard.add_hotkey("ctrl+`", self.toggle_pause)

    def schedule_long_breaks(self):
        intervals = self.total_pomodoros // (self.long_breaks + 1)
        self.long_break_points = [(i + 1) * intervals for i in range(self.long_breaks)]

    def show_break_screen(self, duration):
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.configure(bg="blue")
        root.attributes("-topmost", True)
        label = Label(root, text=f"Перерыв! Осталось {duration} сек\n{self.current_pomodoro} из {self.total_pomodoros}",
                      fg="white", bg="blue", font=("Arial", 40))
        label.pack(expand=True)
        root.update()

        for i in range(duration, 0, -1):
            if paused or is_system_locked():
                break

            minutes = i // 60
            seconds = i % 60
            label.config(text=f"Перерыв! Осталось {minutes} мин {seconds} сек\n{self.current_pomodoro} из {self.total_pomodoros}")
            root.update()
            time.sleep(1)
        root.destroy()

    def announce_time_left(self):
        if paused:
            speak("Таймер на паузе")
        else:
            remaining = self.work_time - (time.time() - self.start_time)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            speak(f"Осталось {minutes} минут {seconds} секунд")

    def stop(self):
        print("Остановка таймера...")
        block_inputs(False)
        exit(0)

    def toggle_pause(self):
        global paused
        paused = not paused
        speak("Таймер поставлен на паузу." if paused else "Таймер возобновлен.")

    def start(self):
        while self.current_pomodoro < self.total_pomodoros:
            self.start_time = time.time()

            while paused or is_system_locked():  # Ожидание, если пауза или экран заблокирован
                time.sleep(1)

            time.sleep(self.work_time)
            self.current_pomodoro += 1

            if self.current_pomodoro in self.long_break_points:
                block_inputs(True)
                self.show_break_screen(self.long_break)
                block_inputs(False)
            else:
                block_inputs(True)
                self.show_break_screen(self.short_break)
                block_inputs(False)


if __name__ == "__main__":
    timer = PomodoroTimer()
    threading.Thread(target=timer.start, daemon=True).start()

    while True:
        time.sleep(1)