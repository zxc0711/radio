import customtkinter as ctk
import pygame
import requests
from tkinter import messagebox, Listbox, Menu
from datetime import datetime, timedelta
import threading

class RadioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Радио Приложение")
        self.geometry("600x600")

        self.radio_station_url = None
        self.radio_stations = self.load_radio_stations()
        self.favorites = []
        self.current_station = None
        self.stop_timer = None

        self.init_ui()
        self.init_pygame()

    def load_radio_stations(self):
        # Загружаем или создаем список радиостанций
        return [
            {"name": "Station 1", "url": "http://example.com/stream1", "genre": "Rock", "language": "English", "country": "USA", "quality": "High"},
            {"name": "Station 2", "url": "http://example.com/stream2", "genre": "Pop", "language": "Spanish", "country": "Spain", "quality": "Medium"},
            # Добавьте больше станций здесь
        ]

    def init_ui(self):
        # Поле ввода URL и кнопки
        self.url_label = ctk.CTkLabel(self, text="Введите URL радио станции:")
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(self, width=300)
        self.url_entry.pack(pady=10)
        self.create_context_menu(self.url_entry)

        self.play_button = ctk.CTkButton(self, text="Играть", command=self.play_radio)
        self.play_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self, text="Стоп", command=self.stop_radio)
        self.stop_button.pack(pady=10)

        self.add_favorite_button = ctk.CTkButton(self, text="Добавить в избранное", command=self.add_favorite)
        self.add_favorite_button.pack(pady=10)

        # Таймер отключения
        self.timer_label = ctk.CTkLabel(self, text="Таймер отключения (в минутах):")
        self.timer_label.pack(pady=10)

        self.timer_entry = ctk.CTkEntry(self, width=100)
        self.timer_entry.pack(pady=10)
        self.create_context_menu(self.timer_entry)

        self.set_timer_button = ctk.CTkButton(self, text="Установить таймер", command=self.set_timer)
        self.set_timer_button.pack(pady=10)

        # Сортировка и фильтры
        self.sort_label = ctk.CTkLabel(self, text="Сортировать по:")
        self.sort_label.pack(pady=5)

        self.sort_options = ["Жанр", "Язык", "Страна", "Качество"]
        self.sort_combobox = ctk.CTkComboBox(self, values=self.sort_options, command=self.sort_stations)
        self.sort_combobox.pack(pady=5)

        self.search_label = ctk.CTkLabel(self, text="Поиск по исполнителю:")
        self.search_label.pack(pady=5)

        self.search_entry = ctk.CTkEntry(self, width=200)
        self.search_entry.pack(pady=5)
        self.create_context_menu(self.search_entry)

        self.search_button = ctk.CTkButton(self, text="Искать", command=self.search_artist)
        self.search_button.pack(pady=5)

        # Выбор качества
        self.quality_label = ctk.CTkLabel(self, text="Выбор качества:")
        self.quality_label.pack(pady=5)

        self.quality_options = ["Low", "Medium", "High"]
        self.quality_combobox = ctk.CTkComboBox(self, values=self.quality_options, command=self.update_quality)
        self.quality_combobox.pack(pady=5)

        # Кнопка для просмотра плейлиста
        self.playlist_button = ctk.CTkButton(self, text="Просмотреть плейлист", command=self.view_playlist)
        self.playlist_button.pack(pady=5)

        # Список радиостанций
        self.station_list_label = ctk.CTkLabel(self, text="Список радиостанций:")
        self.station_list_label.pack(pady=10)

        self.station_listbox = Listbox(self)
        self.station_listbox.pack(pady=10)
        self.update_station_list()

    def create_context_menu(self, widget):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="Копировать", command=lambda: self.copy(widget))
        context_menu.add_command(label="Вставить", command=lambda: self.paste(widget))

        widget.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu))

    def show_context_menu(self, event, menu):
        menu.tk_popup(event.x_root, event.y_root)

    def copy(self, widget):
        self.clipboard_clear()
        self.clipboard_append(widget.selection_get())

    def paste(self, widget):
        try:
            widget.insert(ctk.INSERT, self.clipboard_get())
        except:
            pass

    def init_pygame(self):
        pygame.init()
        pygame.mixer.init()

    def play_radio(self):
        self.radio_station_url = self.url_entry.get()
        if not self.radio_station_url and self.station_listbox.curselection():
            index = self.station_listbox.curselection()[0]
            self.radio_station_url = self.radio_stations[index]["url"]

        if self.radio_station_url:
            quality = self.quality_combobox.get()
            # Измените URL станции в зависимости от выбранного качества
            if quality == "Low":
                self.radio_station_url = self.radio_station_url.replace("high", "low")
            elif quality == "Medium":
                self.radio_station_url = self.radio_station_url.replace("high", "medium")

            try:
                response = requests.get(self.radio_station_url, stream=True)
                if response.status_code == 200:
                    pygame.mixer.music.load(self.radio_station_url)
                    pygame.mixer.music.play()
                    self.current_station = self.radio_station_url
                else:
                    messagebox.showerror("Ошибка", "Невозможно подключиться к радио станции.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")

    def stop_radio(self):
        pygame.mixer.music.stop()
        self.current_station = None

    def add_favorite(self):
        if self.current_station:
            self.favorites.append(self.current_station)
            messagebox.showinfo("Информация", "Радиостанция добавлена в избранное.")

    def set_timer(self):
        minutes = self.timer_entry.get()
        if minutes.isdigit():
            self.stop_timer = threading.Timer(int(minutes) * 60, self.stop_radio)
            self.stop_timer.start()
            messagebox.showinfo("Информация", f"Таймер установлен на {minutes} минут.")
        else:
            messagebox.showerror("Ошибка", "Введите корректное количество минут.")

    def sort_stations(self, sort_option):
        if sort_option == "Жанр":
            self.radio_stations.sort(key=lambda x: x["genre"])
        elif sort_option == "Язык":
            self.radio_stations.sort(key=lambda x: x["language"])
        elif sort_option == "Страна":
            self.radio_stations.sort(key=lambda x: x["country"])
        elif sort_option == "Качество":
            self.radio_stations.sort(key=lambda x: x["quality"])
        self.update_station_list()

    def search_artist(self):
        search_query = self.search_entry.get().lower()
        filtered_stations = [station for station in self.radio_stations if search_query in station["name"].lower()]
        self.station_listbox.delete(0, ctk.END)
        for station in filtered_stations:
            self.station_listbox.insert(ctk.END, station["name"])

    def update_station_list(self):
        self.station_listbox.delete(0, ctk.END)
        for station in self.radio_stations:
            self.station_listbox.insert(ctk.END, station["name"])

    def update_quality(self, quality):
        # Реализуйте логику обновления качества трансляции
        pass

    def view_playlist(self):
        if self.current_station:
            # Реализуйте логику получения и отображения плейлиста
            playlist_url = self.radio_station_url + "/playlist"  # Пример
            try:
                response = requests.get(playlist_url)
                if response.status_code == 200:
                    playlist = response.text
                    messagebox.showinfo("Плейлист", playlist)
                else:
                    messagebox.showerror("Ошибка", "Невозможно получить плейлист.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")
        else:
            messagebox.showinfo("Информация", "Нет активной радиостанции.")

if __name__ == "__main__":
    app = RadioApp()
    app.mainloop()
