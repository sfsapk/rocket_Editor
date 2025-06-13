
"""
Редактор деталей ракеты с пользовательской клавиатурой
Версия для Pydroid 3 с полностью отключенной системной клавиатурой

Добавлены новые возможности:
- Фоновые изображения для всех модальных окон
- Закругленные углы у всех кнопок
- Увеличенный в 1.5 раза шрифт кнопок
- Продвинутые кнопки деталей с иконками 100x100
- Подробные комментарии к коду
- ИСПРАВЛЕНО: Центрирование иконок в боксах
- ИСПРАВЛЕНО: Загрузка иконок из папки icons
"""
import os
import json
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from functools import partial

# Устанавливаем рабочую директорию проекта (для Android)
project_directory = ''
if os.path.exists(project_directory):
    os.chdir(project_directory)

# Принудительно используем свою клавиатуру вместо системной
# ОБЯЗАТЕЛЬНО УСТАНОВИТЬ ПЕРЕД ИМПОРТОМ Config
os.environ['KIVY_USE_ANDROID_KEYBOARD'] = '0'
os.environ['KIVY_NO_NATIVE_KEYBOARD'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'

# Теперь можно импортировать Config
from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'dock')
Config.set('graphics', 'resizable', '0')

# Переменная для проверки Android-платформы
IS_ANDROID = os.path.exists('/data/data')

# Функция загрузки иконок деталей из папки icons (ИСПРАВЛЕНА)
def load_detail_icon(detail_name):
    """
    Загружает иконку детали из папки icons по имени детали.
    Поддерживает формат JPEG/JPG и возвращает путь к иконке или None если не найдена.
    
    Args:
        detail_name (str): Название детали для поиска соответствующей иконки
        
    Returns:
        str or None: Путь к файлу иконки или None если иконка не найдена
    """
    # Определяем путь к папке с иконками
    icons_dir = os.path.join(os.getcwd(), "icons")
    
    # Создаем папку icons если её нет
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir, exist_ok=True)
        print(f"Создана папка для иконок: {icons_dir}")
        return None
    
    # Выводим информацию о поиске иконки
    print(f"Ищем иконку для детали: '{detail_name}' в папке: {icons_dir}")
    
    # Формируем возможные имена файлов иконок (расширенный список вариантов)
    possible_names = [
        f"{detail_name}.jpeg",
        f"{detail_name}.jpg",
        f"{detail_name}.png",
        f"{detail_name.lower()}.jpeg",
        f"{detail_name.lower()}.jpg", 
        f"{detail_name.lower()}.png",
        f"{detail_name.replace(' ', '_')}.jpeg",
        f"{detail_name.replace(' ', '_')}.jpg",
        f"{detail_name.replace(' ', '_')}.png",
        f"{detail_name.replace(' ', '_').lower()}.jpeg",
        f"{detail_name.replace(' ', '_').lower()}.jpg",
        f"{detail_name.replace(' ', '_').lower()}.png",
        # Дополнительные варианты для русских названий
        f"{detail_name.replace(' ', '')}.jpeg",
        f"{detail_name.replace(' ', '')}.jpg",
        f"{detail_name.replace(' ', '')}.png",
        f"{detail_name.replace(' ', '').lower()}.jpeg",
        f"{detail_name.replace(' ', '').lower()}.jpg",
        f"{detail_name.replace(' ', '').lower()}.png"
    ]
    
    # Выводим список файлов в папке icons для отладки
    try:
        files_in_icons = os.listdir(icons_dir)
        print(f"Файлы в папке icons: {files_in_icons}")
    except Exception as e:
        print(f"Ошибка при чтении папки icons: {e}")
        return None
    
    # Ищем иконку среди возможных вариантов имен
    for icon_name in possible_names:
        icon_path = os.path.join(icons_dir, icon_name)
        print(f"Проверяем файл: {icon_path}")
        if os.path.exists(icon_path):
            print(f"✓ НАЙДЕНА иконка для детали '{detail_name}': {icon_path}")
            return icon_path
    
    # Если иконка не найдена, возвращаем None
    print(f"✗ Иконка для детали '{detail_name}' НЕ НАЙДЕНА в папке {icons_dir}")
    print(f"Искали файлы с именами: {possible_names[:5]}... (и другие)")
    return None

# Универсальный стиль для кнопок с закругленными углами
class RoundedButton(Button):
    """
    Кастомная кнопка с закругленными углами и настраиваемым дизайном.
    Автоматически применяет стиль ко всем кнопкам в приложении.
    """
    def __init__(self, **kwargs):
        # Устанавливаем увеличенный размер шрифта (в 1.5 раза больше стандартного)
        if 'font_size' not in kwargs:
            kwargs['font_size'] = dp(21)  # Стандартный 14dp * 1.5 = 21dp
        else:
            # Если размер шрифта указан явно, увеличиваем его в 1.5 раза
            kwargs['font_size'] = kwargs['font_size'] * 1.5
            
        super(RoundedButton, self).__init__(**kwargs)
        
        # Убираем стандартный фон кнопки
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон
        
        # Привязываем перерисовку к изменению размера и позиции
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    
    def update_graphics(self, *args):
        """
        Обновляет графическое представление кнопки с закругленными углами.
        Вызывается при изменении размера или позиции кнопки.
        """
        self.canvas.before.clear()
        with self.canvas.before:
            # Устанавливаем цвет фона кнопки
            if hasattr(self, 'button_color'):
                Color(*self.button_color)
            else:
                # Стандартный серо-голубой цвет
                Color(0.7, 0.8, 0.9, 1)
            
            # Рисуем закругленный прямоугольник
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]  # Радиус закругления углов
            )
            
            # Добавляем тонкую рамку
            Color(0.4, 0.5, 0.6, 1)  # Темнее основного цвета
            Line(
                rounded_rectangle=[
                    self.x, self.y, self.width, self.height, dp(10)
                ],
                width=1.2
            )

# Продвинутая кнопка детали с иконкой (ИСПРАВЛЕНА)
class DetailButton(BoxLayout):
    """
    Продвинутая кнопка для отображения детали с иконкой и названием.
    Включает область 100x100 для иконки и текстовую область для названия.
    ИСПРАВЛЕНО: Правильное центрирование иконки в контейнере.
    """
    def __init__(self, detail_name, callback, **kwargs):
        super(DetailButton, self).__init__(orientation='horizontal', size_hint_y=None, height=dp(100), spacing=dp(10), **kwargs)
        
        self.detail_name = detail_name
        self.callback = callback
        
        # Контейнер для иконки (фиксированный размер 100x100) - ИСПРАВЛЕН
        icon_container = BoxLayout(
            size_hint=(None, None), 
            size=(dp(110), dp(100)),
            
            # Убираем pos_hint, так как BoxLayout автоматически центрирует содержимое
        )
        
        # Загружаем иконку детали
        icon_path = load_detail_icon(detail_name)
        
        if icon_path and os.path.exists(icon_path):
            # Если иконка найдена, отображаем её - ИСПРАВЛЕНО ЦЕНТРИРОВАНИЕ
            print(f"Загружаем иконку: {icon_path}")
            self.icon_image = Image(
                source=icon_path,
                size_hint=(None, None),
                size=(dp(107), dp(90)),
                
                # Центрируем иконку в контейнере
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                allow_stretch=True,  # Разрешаем растягивание для подгонки размера
                keep_ratio=True      # Сохраняем пропорции
            )
        else:
            # Если иконка не найдена, создаем заглушку с цветным фоном
            print(f"Создаем заглушку для детали: {detail_name}")
            self.icon_image = Widget(
                size_hint=(None, None), 
                size=(dp(110), dp(100))
            )
            
            # Рисуем цветную заглушку для иконки
            with self.icon_image.canvas:
                Color(0.3, 0.4, 0.6, 1)  # Серо-синий цвет заглушки
                self.placeholder_rect = RoundedRectangle(
                    pos=self.icon_image.pos,
                    size=self.icon_image.size,
                    radius=[dp(10)]
                )
            
            # Привязываем обновление заглушки к изменению позиции
            self.icon_image.bind(pos=self.update_placeholder, size=self.update_placeholder)
        
        # Добавляем иконку в центр контейнера
        icon_container.add_widget(self.icon_image)
        self.add_widget(icon_container)
        
        # Создаем основную кнопку с названием детали
        self.main_button = RoundedButton(
            text=detail_name,
            font_size=dp(10),  # Размер шрифта для названия детали
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        # Устанавливаем цвет кнопки в зависимости от типа детали
        self.main_button.button_color = self.get_detail_color(detail_name)
        self.main_button.bind(on_release=self.on_button_press)
        
        self.add_widget(self.main_button)
        
        # Добавляем общий фон для всей кнопки детали
        with self.canvas.before:
            Color(0.2, 0.25, 0.35, 0.8)  # Полупрозрачный темный фон
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )
        
        # Привязываем обновление фона к изменению размера
        self.bind(pos=self.update_background, size=self.update_background)
    
    def update_placeholder(self, *args):
        """Обновляет заглушку иконки при изменении позиции - ИСПРАВЛЕНО"""
        if hasattr(self, 'placeholder_rect'):
            self.placeholder_rect.pos = self.icon_image.pos
            self.placeholder_rect.size = self.icon_image.size
    
    def update_background(self, *args):
        """Обновляет фон кнопки детали при изменении размера"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def get_detail_color(self, detail_name):
        """
        Определяет цвет кнопки на основе названия детали.
        Возвращает цвет в формате RGBA для разных типов деталей.
        """
        name_lower = detail_name.lower()
        
        # Цветовая схема для разных типов деталей
        if any(word in name_lower for word in ['двигатель', 'мотор', 'engine', 'hawk', 'kolibr', 'valia']):
            return (0.8, 0.3, 0.2, 1)  # Красноватый для двигателей
        elif any(word in name_lower for word in ['бак', 'топливо', 'tank', 'fuel', 'топливный']):
            return (0.2, 0.6, 0.8, 1)  # Голубой для топливных баков
        elif any(word in name_lower for word in ['команд', 'кабина', 'pod', 'command', 'капсула']):
            return (0.3, 0.7, 0.3, 1)  # Зеленый для командных модулей
        elif any(word in name_lower for word in ['крыло', 'стабилизатор', 'wing', 'боковая']):
            return (0.7, 0.7, 0.2, 1)  # Желтый для аэродинамических элементов
        elif any(word in name_lower for word in ['солнечная', 'батарея', 'solar']):
            return (1.0, 0.8, 0.2, 1)  # Золотистый для солнечных батарей
        elif any(word in name_lower for word in ['парашют', 'parachute']):
            return (0.9, 0.5, 0.1, 1)  # Оранжевый для парашютов
        else:
            return (0.5, 0.5, 0.7, 1)  # Фиолетовый для остальных деталей
    
    def on_button_press(self, instance):
        """Обрабатывает нажатие на кнопку детали"""
        if self.callback:
            self.callback(self.detail_name)

# Заменяем стандартную кнопку на кастомную во всем приложении
Button = RoundedButton

# Базовый класс для модальных окон с фоном
class StyledModalView(ModalView):
    """
    Базовый класс для всех модальных окон с красивым фоном.
    Добавляет градиентный фон и улучшенный внешний вид.
    """
    def __init__(self, **kwargs):
        super(StyledModalView, self).__init__(**kwargs)
        
        # Привязываем перерисовку фона к изменению размера
        self.bind(size=self.update_background, pos=self.update_background)
    
    def update_background(self, *args):
        '''
        #Создает красивый градиентный фон для модального окна.
        #Использует несколько слоев для создания эффекта глубины.
        
        #МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
        #Здесь можно добавить загрузку фонового изображения в формате JPEG:
        background_image_path = "backgrounds/modal_background.jpeg"
         if os.path.exists(background_image_path):
            # Код для установки фонового изображения
        '''
        self.canvas.before.clear()
        with self.canvas.before:
            # Основной фон - темно-синий градиент
            Color(0.1, 0.2, 0.4, 0.95)  # Полупрозрачный темно-синий
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )
            
            # Добавляем более светлый слой сверху для эффекта градиента
            Color(0.2, 0.3, 0.5, 0.3)  # Светлее и более прозрачный
            RoundedRectangle(
                pos=(self.x, self.y + self.height * 0.6),
                size=(self.width, self.height * 0.4),
                radius=[dp(15), dp(15), 0, 0]  # Закругление только сверху
            )
            
            # Добавляем рамку
            Color(0.3, 0.4, 0.6, 0.8)
            Line(
                rounded_rectangle=[
                    self.x, self.y, self.width, self.height, dp(15)
                ],
                width=2
            )

# Класс встроенной клавиатуры для модальных окон
class ModalKeyboard(BoxLayout):
    """
    Встроенная клавиатура с поддержкой русского и английского языков.
    Включает функции переключения регистра, языка и специальные клавиши.
    """
    def __init__(self, textinput, **kwargs):
        super(ModalKeyboard, self).__init__(orientation='vertical', size_hint=(1, None), height=dp(200), **kwargs)
        self.textinput = textinput  # Ссылка на поле ввода
        self.is_caps = False        # Состояние Caps Lock
        self.is_russian = True      # Текущий язык (True = русский, False = английский)
        
        # Русская раскладка клавиатуры (ЙЦУКЕН)
        self.russian_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '.'],
            ['й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х'],
            ['ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э'],
            ['я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', ',']
        ]
        
        # Английская раскладка клавиатуры (QWERTY)
        self.english_layout = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '.'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.']
        ]
        
        # Создаем контейнер для клавиатуры
        self.keyboard_layout = GridLayout(cols=1)
        self.add_widget(self.keyboard_layout)
        self.build_keyboard()
        
    def build_keyboard(self):
        """
        Строит клавиатуру на основе текущих настроек (язык, регистр).
        Очищает предыдущую клавиатуру и создает новую.
        """
        # Очищаем предыдущую клавиатуру
        self.keyboard_layout.clear_widgets()
        
        # Выбираем текущую раскладку в зависимости от языка
        current_layout = self.russian_layout if self.is_russian else self.english_layout
        
        # Создаем строки клавиатуры
        for row in current_layout:
            row_layout = BoxLayout(size_hint_y=None, height=dp(40))
            
            # Добавляем кнопки в строку
            for key in row:
                # Применяем регистр к буквам
                displayed_key = key.upper() if self.is_caps else key
                btn = Button(text=displayed_key)
                btn.button_color = (0.8, 0.9, 1.0, 1)  # Светло-голубой для клавиш
                btn.bind(on_press=lambda x, k=displayed_key: self.key_pressed(k))
                row_layout.add_widget(btn)
                
            self.keyboard_layout.add_widget(row_layout)
        
        # Добавляем специальные кнопки (язык, caps, пробел, backspace)
        special_row = BoxLayout(size_hint_y=None, height=dp(40))
        
        # Кнопка переключения языка
        lang_btn = Button(text="RU/EN" if self.is_russian else "EN/RU", size_hint_x=0.2)
        lang_btn.button_color = (1.0, 0.8, 0.6, 1)  # Оранжевый для специальных кнопок
        lang_btn.bind(on_press=self.switch_language)
        
        # Кнопка Caps Lock
        caps_btn = Button(text="CAPS", size_hint_x=0.2)
        caps_btn.button_color = (0.8, 1.0, 0.6, 1) if self.is_caps else (0.6, 0.8, 1.0, 1)
        caps_btn.bind(on_press=self.toggle_caps)
        
        # Кнопка пробела
        space_btn = Button(text="ПРОБЕЛ", size_hint_x=0.4)
        space_btn.button_color = (0.9, 0.9, 0.9, 1)  # Серый для пробела
        space_btn.bind(on_press=lambda x: self.key_pressed(" "))
        
        # Кнопка удаления
        backspace_btn = Button(text="Del", size_hint_x=0.2)
        backspace_btn.button_color = (1.0, 0.6, 0.6, 1)  # Красноватый для удаления
        backspace_btn.bind(on_press=self.backspace)
        
        special_row.add_widget(lang_btn)
        special_row.add_widget(caps_btn)
        special_row.add_widget(space_btn)
        special_row.add_widget(backspace_btn)
        
        self.keyboard_layout.add_widget(special_row)
    
    def key_pressed(self, key):
        """
        Обрабатывает нажатие на клавишу клавиатуры.
        Добавляет символ к тексту в поле ввода.
        """
        if self.textinput:
            self.textinput.text += key
    
    def backspace(self, instance):
        """
        Обрабатывает нажатие на клавишу backspace.
        Удаляет последний символ из поля ввода.
        """
        if self.textinput and self.textinput.text:
            self.textinput.text = self.textinput.text[:-1]
    
    def toggle_caps(self, instance):
        """
        Переключает режим Caps Lock (верхний/нижний регистр).
        Перестраивает клавиатуру с новым регистром.
        """
        self.is_caps = not self.is_caps
        self.build_keyboard()
    
    def switch_language(self, instance):
        """
        Переключает язык клавиатуры между русским и английским.
        Перестраивает клавиатуру с новой раскладкой.
        """
        self.is_russian = not self.is_russian
        self.build_keyboard()

# Всплывающее окно выбора папки для сохранения
class FolderSelectionModal(StyledModalView):
    """
    Модальное окно для ввода имени папки для сохранения файлов.
    Включает встроенную клавиатуру для ввода текста.
    
    МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
    Для установки фона этого модального окна, раскомментируйте и измените:
    background_image_path = "backgrounds/folder_selection_background.jpeg"
    """
    def __init__(self, parent_modal, **kwargs):
        super(FolderSelectionModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.parent_modal = parent_modal  # Ссылка на родительское модальное окно
        
        # Создаем основной макет с отступами
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок окна
        title_label = Label(
            text="Укажите имя новой папки:", 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)  # Белый текст для контраста с темным фоном
        )
        main_layout.add_widget(title_label)
        
        # Поле для ввода имени папки
        self.folder_input = TextInput(
            hint_text="Имя папки", 
            multiline=False, 
            size_hint_y=None, 
            height=70,
            font_size=dp(20),
            readonly=True,  # Предотвращаем показ системной клавиатуры
            background_color=(1, 1, 1, 0.9),  # Полупрозрачный белый фон
            foreground_color=(0, 0, 0, 1)     # Черный текст
        )
        self.folder_input.bind(focus=self.on_focus)
        main_layout.add_widget(self.folder_input)
        
        # Кнопки действий
        button_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        confirm_button = Button(text="Подтвердить")
        confirm_button.button_color = (0.2, 0.8, 0.2, 1)  # Зеленый для подтверждения
        confirm_button.bind(on_release=self.confirm_selection)
        
        cancel_button = Button(text="Отменить")
        cancel_button.button_color = (0.8, 0.2, 0.2, 1)  # Красный для отмены
        cancel_button.bind(on_release=self.dismiss)
        
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Встроенная клавиатура
        self.keyboard = ModalKeyboard(self.folder_input)
        main_layout.add_widget(self.keyboard)
        
        self.add_widget(main_layout)
    
    def on_focus(self, instance, value):
        """
        Обрабатывает получение фокуса полем ввода.
        Предотвращает появление системной клавиатуры.
        """
        pass
    
    def confirm_selection(self, instance):
        """
        Подтверждает выбор имени папки и запускает сохранение.
        Проверяет, что имя папки не пустое.
        """
        folder_name = self.folder_input.text.strip()
        if folder_name:
            self.parent_modal.save_to_folder(folder_name)
        else:
            print("Необходимо указать имя папки.")
        self.dismiss()

# Класс для ввода числовых значений
class NumberInputModal(StyledModalView):
    """
    Модальное окно для ввода числовых значений.
    Включает специальную числовую клавиатуру и валидацию ввода.
    
    МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
    Для установки фона этого модального окна, раскомментируйте и измените:
    background_image_path = "backgrounds/number_input_background.jpeg"
    """
    def __init__(self, title, initial_value, callback, **kwargs):
        super(NumberInputModal, self).__init__(size_hint=(0.9, 0.8), auto_dismiss=True, **kwargs)
        self.callback = callback              # Функция обратного вызова для результата
        self.initial_value = str(initial_value)  # Начальное значение
        
        # Основной макет
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title_label = Label(
            text=title, 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title_label)
        
        # Поле ввода числа
        self.value_input = TextInput(
            text=self.initial_value, 
            multiline=False, 
            readonly=True,  # Предотвращаем системную клавиатуру
            font_size=dp(28),
            size_hint_y=None, 
            height=100,
            background_color=(1, 1, 1, 0.9),
            foreground_color=(0, 0, 0, 1),
            halign='center'  # Центрируем текст
        )
        self.value_input.bind(focus=self.on_focus)
        main_layout.add_widget(self.value_input)
        
        # Кнопки подтверждения и отмены
        button_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        confirm_button = Button(text="Подтвердить")
        confirm_button.button_color = (0.2, 0.8, 0.2, 1)
        confirm_button.bind(on_release=self.confirm_selection)
        
        cancel_button = Button(text="Отменить")
        cancel_button.button_color = (0.8, 0.2, 0.2, 1)
        cancel_button.bind(on_release=self.dismiss)
        
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Числовая клавиатура
        num_keyboard = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(220))
        
        # Создаем ряды с числами (как на калькуляторе)
        rows = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', '-']
        ]
        
        for row in rows:
            row_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=5)
            for key in row:
                btn = Button(text=key)
                btn.button_color = (0.9, 0.9, 1.0, 1)  # Светло-голубой для цифр
                btn.bind(on_press=lambda x, k=key: self.key_pressed(k))
                row_layout.add_widget(btn)
            num_keyboard.add_widget(row_layout)
        
        # Специальные кнопки (очистить и удалить)
        special_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=5)
        
        clear_btn = Button(text="Очистить", size_hint_x=0.5)
        clear_btn.button_color = (1.0, 0.8, 0.2, 1)  # Желтый для очистки
        clear_btn.bind(on_press=self.clear_input)
        
        backspace_btn = Button(text="←", size_hint_x=0.5)
        backspace_btn.button_color = (1.0, 0.6, 0.6, 1)  # Красноватый для удаления
        backspace_btn.bind(on_press=self.backspace)
        
        special_row.add_widget(clear_btn)
        special_row.add_widget(backspace_btn)
        num_keyboard.add_widget(special_row)
        
        main_layout.add_widget(num_keyboard)
        
        self.add_widget(main_layout)
    
    def on_focus(self, instance, value):
        """Предотвращает появление системной клавиатуры"""
        pass
    
    def key_pressed(self, key):
        """
        Обрабатывает нажатие на числовую клавишу.
        Включает специальную логику для десятичной точки и знака минус.
        """
        # Специальная обработка для чисел с плавающей точкой
        if key == '.' and '.' in self.value_input.text:
            return  # Предотвращаем добавление второй точки
        elif key == '-' and self.value_input.text:
            # Переключаем знак числа
            if self.value_input.text[0] == '-':
                self.value_input.text = self.value_input.text[1:]  # Убираем минус
            else:
                self.value_input.text = '-' + self.value_input.text  # Добавляем минус
            return
        
        self.value_input.text += key
    
    def backspace(self, instance):
        """Удаляет последний символ из поля ввода"""
        if self.value_input.text:
            self.value_input.text = self.value_input.text[:-1]
    
    def clear_input(self, instance):
        """Полностью очищает поле ввода"""
        self.value_input.text = ""
    
    def confirm_selection(self, instance):
        """
        Подтверждает введенное число и вызывает callback.
        Включает валидацию числа и обработку ошибок.
        """
        try:
            value = float(self.value_input.text) if self.value_input.text else 0
            self.callback(value)
            self.dismiss()
        except ValueError:
            # Показываем сообщение об ошибке при неверном формате числа
            error_popup = StyledModalView(size_hint=(0.8, 0.3))
            error_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            
            error_label = Label(
                text="Введите корректное число",
                font_size=dp(21),
                color=(1, 1, 1, 1)
            )
            error_layout.add_widget(error_label)
            
            close_btn = Button(text="OK", size_hint_y=None, height=60)
            close_btn.button_color = (0.2, 0.8, 0.2, 1)
            close_btn.bind(on_release=error_popup.dismiss)
            error_layout.add_widget(close_btn)
            
            error_popup.add_widget(error_layout)
            error_popup.open()

# Класс для выбора значения из списка доступных опций
class SelectionModal(StyledModalView):
    """
    Модальное окно для выбора одного значения из списка опций.
    Используется для небольших списков (до 10 элементов).
    
    МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
    Для установки фона этого модального окна, раскомментируйте и измените:
    background_image_path = "backgrounds/selection_background.jpeg"
    """
    def __init__(self, title, options, callback, current_value=None, **kwargs):
        super(SelectionModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.callback = callback      # Функция обратного вызова
        self.options = options        # Список опций для выбора
        
        # Основной макет
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title_label = Label(
            text=title, 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title_label)
        
        # Скроллируемый список опций
        scroll_view = ScrollView(do_scroll_x=False)
        options_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        options_layout.bind(minimum_height=options_layout.setter('height'))
        
        # Создаем кнопки для каждой опции
        for option in options:
            btn = Button(
                text=str(option),
                size_hint_y=None,
                height=70,
                text_size=(None, None),  # Автоматический размер текста
                halign='center'
            )
            # Выделяем текущее значение другим цветом
            if str(option) == str(current_value):
                btn.button_color = (0.3, 0.6, 0.9, 1)  # Синий для выбранного
            else:
                btn.button_color = (0.8, 0.8, 0.8, 1)  # Серый для остальных
            
            btn.bind(on_release=lambda x, opt=option: self.select_option(opt))
            options_layout.add_widget(btn)
        
        scroll_view.add_widget(options_layout)
        main_layout.add_widget(scroll_view)
        
        # Кнопка отмены
        cancel_button = Button(text="Отмена", size_hint_y=None, height=70)
        cancel_button.button_color = (0.8, 0.2, 0.2, 1)
        cancel_button.bind(on_release=self.dismiss)
        main_layout.add_widget(cancel_button)
        
        self.add_widget(main_layout)
    
    def select_option(self, option):
        """
        Выбирает опцию и закрывает модальное окно.
        Вызывает callback с выбранным значением.
        """
        self.callback(option)
        self.dismiss()

# Класс для выбора опции из списка с поиском
class SearchableSelectionModal(StyledModalView):
    """
    Модальное окно для выбора значения из большого списка с возможностью поиска.
    Используется для списков с более чем 10 элементами.
    
    МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
    Для установки фона этого модального окна, раскомментируйте и измените:
    background_image_path = "backgrounds/searchable_selection_background.jpeg"
    """
    def __init__(self, title, options, callback, current_value=None, **kwargs):
        super(SearchableSelectionModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.callback = callback                    # Функция обратного вызова
        self.options = options                      # Полный список опций
        self.filtered_options = options.copy()      # Отфильтрованный список
        
        # Основной макет
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title_label = Label(
            text=title, 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        main_layout.add_widget(title_label)
        
        # Поле поиска с кнопкой очистки
        search_box = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        self.search_input = TextInput(
            hint_text="Поиск...",
            multiline=False,
            readonly=True,  # Используем встроенную клавиатуру
            font_size=dp(20),
            background_color=(1, 1, 1, 0.9),
            foreground_color=(0, 0, 0, 1)
        )
        search_box.add_widget(self.search_input)
        
        # Кнопка очистки поиска
        clear_btn = Button(text="Очистить", size_hint_x=0.3)
        clear_btn.button_color = (1.0, 0.8, 0.2, 1)
        clear_btn.bind(on_release=self.clear_search)
        search_box.add_widget(clear_btn)
        
        main_layout.add_widget(search_box)
        
        # Встроенная клавиатура для поиска
        self.keyboard = ModalKeyboard(self.search_input)
        self.search_input.bind(text=self.filter_options)
        
        # Скроллируемый список опций
        self.scroll_view = ScrollView(do_scroll_x=False)
        self.options_layout = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.options_layout.bind(minimum_height=self.options_layout.setter('height'))
        
        self.update_options_display(current_value)
        
        self.scroll_view.add_widget(self.options_layout)
        main_layout.add_widget(self.scroll_view)
        
        # Кнопка отмены
        button_layout = BoxLayout(size_hint_y=None, height=70)
        cancel_button = Button(text="Отмена")
        cancel_button.button_color = (0.8, 0.2, 0.2, 1)
        cancel_button.bind(on_release=self.dismiss)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Добавляем клавиатуру внизу
        main_layout.add_widget(self.keyboard)
        
        self.add_widget(main_layout)
    
    def update_options_display(self, current_value=None):
        """
        Обновляет отображаемые опции на основе текущего фильтра поиска.
        Выделяет текущее выбранное значение.
        """
        self.options_layout.clear_widgets()
        
        for option in self.filtered_options:
            btn = Button(
                text=str(option),
                size_hint_y=None,
                height=70,
                text_size=(None, None),
                halign='center'
            )
            # Выделяем текущее значение
            if str(option) == str(current_value):
                btn.button_color = (0.3, 0.6, 0.9, 1)
            else:
                btn.button_color = (0.8, 0.8, 0.8, 1)
            
            btn.bind(on_release=lambda x, opt=option: self.select_option(opt))
            self.options_layout.add_widget(btn)
    
    def filter_options(self, instance, value):
        """
        Фильтрует опции на основе введенного в поиск текста.
        Обновляет отображение списка.
        """
        search_text = value.lower()
        self.filtered_options = [opt for opt in self.options if search_text in str(opt).lower()]
        self.update_options_display()
    
    def clear_search(self, instance):
        """
        Очищает поле поиска и восстанавливает полный список опций.
        """
        self.search_input.text = ""
        self.filtered_options = self.options.copy()
        self.update_options_display()
    
    def select_option(self, option):
        """Выбирает опцию и закрывает модальное окно"""
        self.callback(option)
        self.dismiss()

# Класс для редактирования текстовых значений
class TextInputModal(StyledModalView):
    """
    Модальное окно для ввода и редактирования текстовых значений.
    Включает встроенную клавиатуру с поддержкой русского и английского языков.
    
    МЕСТО ДЛЯ УКАЗАНИЯ ПУТИ К ФОНОВОМУ ИЗОБРАЖЕНИЮ:
    Для установки фона этого модального окна, раскомментируйте и измените:
    background_image_path = "backgrounds/text_input_background.jpeg"
    """
    def __init__(self, title, initial_text, callback, **kwargs):
        super(TextInputModal, self).__init__(size_hint=(0.9, 0.9), auto_dismiss=True, **kwargs)
        self.callback = callback  # Функция обратного вызова
        
        # Основной макет
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        title_label = Label(
            text=title, 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title_label)
        
        # Поле ввода текста
        self.text_input = TextInput(
            text=initial_text,
            multiline=False,
            readonly=True,  # Предотвращаем системную клавиатуру
            font_size=dp(15),  # ИЗМЕНЕН РАЗМЕР ШРИФТА НА 15
            size_hint_y=None,
            height=100,
            background_color=(1, 1, 1, 0.9),
            foreground_color=(0, 0, 0, 1)
        )
        layout.add_widget(self.text_input)
        
        # Кнопки подтверждения и отмены
        button_layout = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        confirm_button = Button(text="Подтвердить")
        confirm_button.button_color = (0.2, 0.8, 0.2, 1)
        confirm_button.bind(on_release=self.confirm_text)
        
        cancel_button = Button(text="Отмена")
        cancel_button.button_color = (0.8, 0.2, 0.2, 1)
        cancel_button.bind(on_release=self.dismiss)
        
        button_layout.add_widget(confirm_button)
        button_layout.add_widget(cancel_button)
        layout.add_widget(button_layout)
        
        # Встроенная клавиатура
        self.keyboard = ModalKeyboard(self.text_input)
        layout.add_widget(self.keyboard)
        
        self.add_widget(layout)
    
    def confirm_text(self, instance):
        """
        Подтверждает введенный текст и вызывает callback.
        Закрывает модальное окно.
        """
        self.callback(self.text_input.text)
        self.dismiss()

# Главное модальное окно редактирования деталей
class EditDetailModal(StyledModalView):
   
   
    background_image_path = "ROCKET_EDITOR_SFS.V1/backgrounds/edit_detail_background.jpeg"
    
    def __init__(self, detail_name, part_data, callback, **kwargs):
        super(EditDetailModal, self).__init__(size_hint=(1, 1), auto_dismiss=True, **kwargs)
        self.detail_name = detail_name    # Название редактируемой детали
        self.part_data = part_data        # Исходные данные детали
        self.callback = callback          # Функция обратного вызова
        self.updated_data = dict(part_data)  # Копия данных для изменений
        
        # Основной макет
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.layout = layout
        
        # Заголовок с кнопкой закрытия
        header = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        close_button = Button(text='Закрыть', size_hint_x=0.3)
        close_button.button_color = (0.8, 0.2, 0.2, 1)
        close_button.bind(on_release=self.dismiss)
        
        title_label = Label(
            text=f"{detail_name}", 
            font_size=dp(20),
            color=(1, 1, 1, 1)
        )
        
        header.add_widget(close_button)
        header.add_widget(title_label)
        layout.add_widget(header)
        
        # Контейнер для параметров с прокруткой
        self.param_layout = GridLayout(cols=1, spacing=12, size_hint_y=None)
        self.param_layout.bind(minimum_height=self.param_layout.setter('height'))
        
        scroll_view = ScrollView(do_scroll_x=False)
        scroll_view.add_widget(self.param_layout)
        layout.add_widget(scroll_view)
        
        # Создаем поля ввода для параметров
        self.create_param_inputs(part_data)
        
        # Кнопки действий (сохранить/отмена)
        button_layout = BoxLayout(size_hint_y=None, height=80, spacing=15)
        
        save_btn = Button(text="Сохранить", size_hint_y=None, height=80)
        save_btn.button_color = (0.2, 0.8, 0.2, 1)
        save_btn.bind(on_press=lambda x: self.prepare_to_save())
        
        cancel_btn = Button(text="Отмена", size_hint_y=None, height=80)
        cancel_btn.button_color = (0.8, 0.2, 0.2, 1)
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def create_param_inputs(self, part_data):
        """
        Создает поля ввода для всех параметров детали.
        Обрабатывает различные типы данных: строки, числа, булевы значения,
        списки, словари и специальные структуры.
        """
        # Секция: Название детали
        name_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
        name_label = Label(
            text="Название:", 
            font_size=dp(15),  # ИЗМЕНЕН РАЗМЕР ШРИФТА НА 15
            size_hint_x=0.4,
            color=(1, 1, 1, 1)
        )
        name_group.add_widget(name_label)
        
        # Кнопка для редактирования названия (вместо TextInput)
        self.name_button = Button(
            text=part_data.get("n", ""),
            font_size=dp(15),  # ИЗМЕНЕН РАЗМЕР ШРИФТА НА 15
            background_color=(1, 1, 1, 0.8)
        )
        self.name_button.button_color = (0.9, 0.9, 1.0, 1)
        self.name_button.bind(on_release=self.show_name_input)
        name_group.add_widget(self.name_button)
        self.param_layout.add_widget(name_group)
        
        # Секция: Позиция (если есть параметр 'p')
        if 'p' in part_data:
            # Заголовок секции позиции
            position_title = Label(
                text="Позиция:", 
                font_size=dp(15), 
                size_hint_y=None, 
                height=40,
                color=(0.8, 1.0, 0.8, 1)  # Светло-зеленый для заголовков секций
            )
            self.param_layout.add_widget(position_title)
            
            # X координата
            pos_x_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
            pos_x_group.add_widget(Label(
                text="X:", 
                font_size=dp(15), 
                size_hint_x=0.4,
                color=(1, 1, 1, 1)
            ))
            self.pos_x_button = Button(
                text=str(part_data['p'].get('x', 0)),
                font_size=dp(15)
            )
            self.pos_x_button.button_color = (1.0, 0.9, 0.8, 1)  # Персиковый для числовых полей
            self.pos_x_button.bind(on_release=lambda x: self.show_number_input(
                "Позиция X", part_data['p'].get('x', 0), self.set_pos_x))
            pos_x_group.add_widget(self.pos_x_button)
            self.param_layout.add_widget(pos_x_group)
            
            # Y координата
            pos_y_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
            pos_y_group.add_widget(Label(
                text="Y:", 
                font_size=dp(15), 
                size_hint_x=0.4,
                color=(1, 1, 1, 1)
            ))
            self.pos_y_button = Button(
                text=str(part_data['p'].get('y', 0)),
                font_size=dp(15)
            )
            self.pos_y_button.button_color = (1.0, 0.9, 0.8, 1)
            self.pos_y_button.bind(on_release=lambda x: self.show_number_input(
                "Позиция Y", part_data['p'].get('y', 0), self.set_pos_y))
            pos_y_group.add_widget(self.pos_y_button)
            self.param_layout.add_widget(pos_y_group)
            
        # Секция: Ориентация (если есть параметр 'o')
        if 'o' in part_data:
            # Заголовок секции ориентации
            orientation_title = Label(
                text="Ориентация:", 
                font_size=dp(15), 
                size_hint_y=None, 
                height=40,
                color=(0.8, 1.0, 0.8, 1)
            )
            self.param_layout.add_widget(orientation_title)
            
            # X ориентация
            orient_x_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
            orient_x_group.add_widget(Label(
                text="X:", 
                font_size=dp(15), 
                size_hint_x=0.4,
                color=(1, 1, 1, 1)
            ))
            self.orient_x_button = Button(
                text=str(part_data['o'].get('x', 0)),
                font_size=dp(15)
            )
            self.orient_x_button.button_color = (0.8, 0.9, 1.0, 1)  # Голубой для ориентации
            self.orient_x_button.bind(on_release=lambda x: self.show_number_input(
                "Ориентация X", part_data['o'].get('x', 0), self.set_orient_x))
            orient_x_group.add_widget(self.orient_x_button)
            self.param_layout.add_widget(orient_x_group)
            
            # Y ориентация
            orient_y_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
            orient_y_group.add_widget(Label(
                text="Y:", 
                font_size=dp(15), 
                size_hint_x=0.4,
                color=(1, 1, 1, 1)
            ))
            self.orient_y_button = Button(
                text=str(part_data['o'].get('y', 0)),
                font_size=dp(15)
            )
            self.orient_y_button.button_color = (0.8, 0.9, 1.0, 1)
            self.orient_y_button.bind(on_release=lambda x: self.show_number_input(
                "Ориентация Y", part_data['o'].get('y', 0), self.set_orient_y))
            orient_y_group.add_widget(self.orient_y_button)
            self.param_layout.add_widget(orient_y_group)
            
            # Z ориентация
            orient_z_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
            orient_z_group.add_widget(Label(
                text="Z:", 
                font_size=dp(15), 
                size_hint_x=0.4,
                color=(1, 1, 1, 1)
            ))
            self.orient_z_button = Button(
                text=str(part_data['o'].get('z', 0)),
                font_size=dp(15)
            )
            self.orient_z_button.button_color = (0.8, 0.9, 1.0, 1)
            self.orient_z_button.bind(on_release=lambda x: self.show_number_input(
                "Ориентация Z", part_data['o'].get('z', 0), self.set_orient_z))
            orient_z_group.add_widget(self.orient_z_button)
            self.param_layout.add_widget(orient_z_group)
        
        # Секция: Специальные параметры N (если есть)
        if 'N' in part_data:
            # Заголовок секции специальных параметров
            n_params_title = Label(
                text="Специальные параметры (N):", 
                font_size=dp(15), 
                size_hint_y=None, 
                height=40,
                color=(1.0, 0.8, 0.8, 1)  # Розоватый для специальных параметров
            )
            self.param_layout.add_widget(n_params_title)
            
            # Словарь для хранения ссылок на кнопки параметров N
            self.n_params = {}
            
            # Обрабатываем каждый параметр в секции N
            for key, value in part_data['N'].items():
                param_group = BoxLayout(size_hint_y=None, height=70, spacing=10)
                param_group.add_widget(Label(
                    text=f"{key}:", 
                    font_size=dp(15), 
                    size_hint_x=0.4,
                    color=(1, 1, 1, 1)
                ))
                
                # Создаем кнопку для параметра
                param_button = Button(
                    text=str(value),
                    font_size=dp(15)
                )
                
                # Обработка в зависимости от типа значения
                if isinstance(value, (int, float)):
                    # Числовые значения - показываем числовой ввод
                    param_button.button_color = (1.0, 0.9, 0.8, 1)  # Персиковый
                    param_button.bind(on_release=lambda x, k=key, v=value: 
                                     self.show_number_input(f"Параметр {k}", v, 
                                                          lambda val, param=k: self.set_n_param(param, val)))
                elif isinstance(value, bool):
                    # Булевы значения - переключаем состояние
                    param_button.button_color = (0.2, 0.8, 0.2, 1) if value else (0.8, 0.2, 0.2, 1)
                    param_button.bind(on_release=lambda x, k=key, v=value: 
                                     self.toggle_n_param_bool(k))
                elif isinstance(value, str):
                    # Строковые значения - текстовый ввод или выбор из списка
                    param_button.button_color = (0.9, 0.9, 1.0, 1)  # Светло-голубой
                    # Проверяем, является ли это enum-параметром
                    if key in ["type", "engine_type", "category", "mode"]:
                        # Предопределенный список значений
                        options = self.get_enum_options(key)
                        param_button.bind(on_release=lambda x, k=key, v=value, opts=options: 
                                         self.show_selection_input(f"Выберите {k}", opts, v,
                                                                lambda val, param=k: self.set_n_param(param, val)))
                    else:
                        # Обычный текстовый ввод
                        param_button.bind(on_release=lambda x, k=key, v=value: 
                                         self.show_text_input(f"Параметр {k}", v, 
                                                            lambda val, param=k: self.set_n_param(param, val)))
                elif isinstance(value, list):
                    # Списки значений - специальный редактор
                    param_button.text = f"{len(value)} элементов"
                    param_button.button_color = (1.0, 0.8, 1.0, 1)  # Фиолетовый для списков
                    param_button.bind(on_release=lambda x, k=key, v=value: 
                                     self.show_list_editor(f"Редактирование списка {k}", v, 
                                                         lambda val, param=k: self.set_n_param(param, val)))
                elif isinstance(value, dict):
                    # Словари - специальный редактор
                    param_button.text = f"{len(value)} параметров"
                    param_button.button_color = (0.8, 1.0, 1.0, 1)  # Циан для словарей
                    param_button.bind(on_release=lambda x, k=key, v=value: 
                                     self.show_dict_editor(f"Редактирование словаря {k}", v, 
                                                         lambda val, param=k: self.set_n_param(param, val)))
                
                # Сохраняем ссылку на кнопку для последующего обновления
                self.n_params[key] = param_button
                param_group.add_widget(param_button)
                self.param_layout.add_widget(param_group)
                
        # Секция: Булевы параметры B (если есть)
        if 'B' in part_data:
            # Заголовок секции булевых параметров
            bool_params_title = Label(
                text="Параметры:", 
                font_size=dp(15), 
                size_hint_y=None, 
                height=40,
                color=(1.0, 1.0, 0.8, 1)  # Желтоватый для булевых параметров
            )
            self.param_layout.add_widget(bool_params_title)
            
            # Словарь для хранения чекбоксов
            self.checkboxes = {}
            
            # Создаем чекбоксы для каждого булева параметра
            for key, value in part_data['B'].items():
                chk_row = BoxLayout(size_hint_y=None, height=70, spacing=10)
                
                chk_label = Label(
                    text=key, 
                    font_size=dp(15), 
                    size_hint_x=0.7,
                    color=(1, 1, 1, 1)
                )
                chk_row.add_widget(chk_label)
                
                # Создаем чекбокс с увеличенным размером
                checkbox = CheckBox(
                    active=value, 
                    size_hint_x=0.3,
                    size_hint_y=None,
                    height=50
                )
                self.checkboxes[key] = checkbox
                chk_row.add_widget(checkbox)
                self.param_layout.add_widget(chk_row)
    
    def get_enum_options(self, param_key):
        """
        Возвращает список возможных значений для enum-параметров.
        Используется для параметров с предопределенными значениями.
        """
        # Предопределенные списки для различных типов параметров
        options_map = {
            "type": ["engine", "fuel_tank", "command_pod", "structural", "aerodynamic", "utility", "science"],
            "engine_type": ["liquid", "solid", "ion", "nuclear", "hybrid"],
            "category": ["propulsion", "control", "resources", "scientific", "electrical", "thermal", "structural"],
            "mode": ["normal", "boost", "economic", "precise", "advanced"]
        }
        return options_map.get(param_key, ["option1", "option2", "option3"])
    
    def show_name_input(self, instance):
        """
        Показывает модальное окно для редактирования названия детали.
        Создает временное модальное окно с встроенной клавиатурой.
        """
        name_modal = StyledModalView(size_hint=(0.9, 0.8))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Заголовок
        layout.add_widget(Label(
            text="Введите название детали:", 
            size_hint_y=None, 
            height=50,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        ))
        
        # Поле ввода
        name_input = TextInput(
            text=self.name_button.text,
            multiline=False,
            readonly=True,
            font_size=dp(28),
            size_hint_y=None,
            height=90,
            background_color=(1, 1, 1, 0.9),
            foreground_color=(0, 0, 0, 1)
        )
        layout.add_widget(name_input)
        
        # Кнопки действий
        buttons = BoxLayout(size_hint_y=None, height=70, spacing=10)
        
        confirm_btn = Button(text="Применить")
        confirm_btn.button_color = (0.2, 0.8, 0.2, 1)
        confirm_btn.bind(on_release=lambda x: self.set_name(name_input.text, name_modal))
        
        cancel_btn = Button(text="Отмена")
        cancel_btn.button_color = (0.8, 0.2, 0.2, 1)
        cancel_btn.bind(on_release=name_modal.dismiss)
        
        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)
        layout.add_widget(buttons)
        
        # Встроенная клавиатура
        keyboard = ModalKeyboard(name_input)
        layout.add_widget(keyboard)
        
        name_modal.add_widget(layout)
        name_modal.open()
    
    def set_name(self, name, modal):
        """
        Устанавливает новое имя детали и закрывает модальное окно.
        """
        self.name_button.text = name
        modal.dismiss()
    
    def show_number_input(self, title, initial_value, callback):
        """
        Показывает модальное окно для ввода числового значения.
        Использует специализированное окно с числовой клавиатурой.
        """
        number_modal = NumberInputModal(title, initial_value, callback)
        number_modal.open()
    
    def show_text_input(self, title, initial_text, callback):
        """
        Показывает модальное окно для ввода текстового значения.
        Использует окно с полной клавиатурой.
        """
        text_modal = TextInputModal(title, initial_text, callback)
        text_modal.open()
    
    def show_selection_input(self, title, options, current_value, callback):
        """
        Показывает модальное окно для выбора из списка опций.
        Выбирает тип окна в зависимости от количества опций.
        """
        # Если опций много, используем окно с поиском
        if len(options) > 10:
            selection_modal = SearchableSelectionModal(title, options, callback, current_value)
        else:
            selection_modal = SelectionModal(title, options, callback, current_value)
        selection_modal.open()
    
    def show_list_editor(self, title, list_values, callback):
        """
        Показывает упрощенный редактор для списков значений.
        В данной реализации позволяет редактировать только первый элемент.
        """
        if len(list_values) > 0:
            # Определяем тип первого элемента и показываем соответствующий редактор
            if isinstance(list_values[0], (int, float)):
                self.show_number_input(f"{title} (элемент 1)", list_values[0], 
                                      lambda val: self.update_list_value(list_values, 0, val, callback))
            elif isinstance(list_values[0], str):
                self.show_text_input(f"{title} (элемент 1)", list_values[0], 
                                    lambda val: self.update_list_value(list_values, 0, val, callback))
        else:
            # Если список пустой, показываем информационное сообщение
            self.show_info_message("Список пуст")
    
    def show_dict_editor(self, title, dict_values, callback):
        """
        Показывает упрощенный редактор для словарей.
        В данной реализации позволяет редактировать только первый ключ.
        """
        if dict_values:
            # Получаем первый ключ для демонстрации
            first_key = next(iter(dict_values))
            value = dict_values[first_key]
            
            # Показываем соответствующий редактор в зависимости от типа значения
            if isinstance(value, (int, float)):
                self.show_number_input(f"{title} ({first_key})", value, 
                                      lambda val: self.update_dict_value(dict_values, first_key, val, callback))
            elif isinstance(value, str):
                self.show_text_input(f"{title} ({first_key})", value, 
                                    lambda val: self.update_dict_value(dict_values, first_key, val, callback))
            elif isinstance(value, bool):
                # Для булевых значений сразу переключаем и применяем
                dict_values[first_key] = not value
                callback(dict_values)
        else:
            # Если словарь пустой, показываем информационное сообщение
            self.show_info_message("Словарь пуст")
    
    def show_info_message(self, message):
        """
        Показывает информационное сообщение пользователю.
        Используется для уведомлений о пустых списках/словарях.
        """
        info_modal = StyledModalView(size_hint=(0.8, 0.3))
        info_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        info_layout.add_widget(Label(
            text=message,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        ))
        
        close_btn = Button(text="OK", size_hint_y=None, height=60)
        close_btn.button_color = (0.2, 0.8, 0.2, 1)
        close_btn.bind(on_release=info_modal.dismiss)
        info_layout.add_widget(close_btn)
        
        info_modal.add_widget(info_layout)
        info_modal.open()
    
    def update_list_value(self, list_values, index, new_value, callback):
        """
        Обновляет значение в списке по индексу и вызывает callback.
        """
        list_values[index] = new_value
        callback(list_values)
    
    def update_dict_value(self, dict_values, key, new_value, callback):
        """
        Обновляет значение в словаре по ключу и вызывает callback.
        """
        dict_values[key] = new_value
        callback(dict_values)
    
    # Методы для обновления конкретных полей позиции
    def set_pos_x(self, value):
        """Устанавливает значение позиции X"""
        self.pos_x_button.text = str(value)
    
    def set_pos_y(self, value):
        """Устанавливает значение позиции Y"""
        self.pos_y_button.text = str(value)
    
    # Методы для обновления полей ориентации
    def set_orient_x(self, value):
        """Устанавливает значение ориентации X"""
        self.orient_x_button.text = str(value)
    
    def set_orient_y(self, value):
        """Устанавливает значение ориентации Y"""
        self.orient_y_button.text = str(value)
    
    def set_orient_z(self, value):
        """Устанавливает значение ориентации Z"""
        self.orient_z_button.text = str(value)
    
    def set_n_param(self, param_key, value):
        """
        Устанавливает значение для параметра N и обновляет пользовательский интерфейс.
        Обрабатывает различные типы данных соответствующим образом.
        """
        # Обновляем отображение кнопки с новым значением
        if param_key in self.n_params:
            # Для сложных типов показываем количество элементов
            if isinstance(value, dict):
                self.n_params[param_key].text = f"{len(value)} параметров"
            elif isinstance(value, list):
                self.n_params[param_key].text = f"{len(value)} элементов"
            else:
                self.n_params[param_key].text = str(value)
            
            # Обновляем значение в структуре данных
            if 'N' not in self.updated_data:
                self.updated_data['N'] = {}
            self.updated_data['N'][param_key] = value
    
    def toggle_n_param_bool(self, param_key):
        """
        Переключает булево значение для параметра N.
        Обновляет как данные, так и визуальное представление кнопки.
        """
        if param_key in self.n_params:
            # Создаем секцию N, если её еще нет
            if 'N' not in self.updated_data:
                self.updated_data['N'] = {}
                
            # Получаем текущее значение и переключаем его
            current_value = self.updated_data['N'].get(param_key, False) if 'N' in self.updated_data else False
            new_value = not current_value
            
            # Обновляем данные
            self.updated_data['N'][param_key] = new_value
            
            # Обновляем внешний вид кнопки
            button = self.n_params[param_key]
            button.text = str(new_value)
            button.button_color = (0.2, 0.8, 0.2, 1) if new_value else (0.8, 0.2, 0.2, 1)
    
    def prepare_to_save(self):
        """
        Подготавливает данные для сохранения.
        Собирает все изменения из полей ввода и проверяет их корректность.
        """
        # Создаем копию исходных данных
        self.updated_data = dict(self.part_data)
        
        # Обновляем название детали
        self.updated_data["n"] = self.name_button.text
        
        # Обновляем позицию, если она была в исходных данных
        if 'p' in self.part_data:
            try:
                self.updated_data['p'] = {
                    'x': float(self.pos_x_button.text),
                    'y': float(self.pos_y_button.text)
                }
            except ValueError:
                print("Ошибка: значения координат должны быть числами")
                return
            
        # Обновляем ориентацию, если она была в исходных данных
        if 'o' in self.part_data:
            try:
                self.updated_data['o'] = {
                    'x': float(self.orient_x_button.text),
                    'y': float(self.orient_y_button.text),
                    'z': float(self.orient_z_button.text)
                }
            except ValueError:
                print("Ошибка: значения ориентации должны быть числами")
                return
            
        # Переносим обновленные параметры N
        if 'N' in self.part_data:
            # Если параметров N еще нет в updated_data, создаем их
            if 'N' not in self.updated_data:
                self.updated_data['N'] = {}
                
            # Проверяем, что все изменения параметров N сохранены
            for key, value in self.part_data['N'].items():
                if key not in self.updated_data['N']:
                    self.updated_data['N'][key] = value
            
        # Обновляем булевы параметры из чекбоксов
        if 'B' in self.part_data:
            self.updated_data['B'] = {}
            for key, checkbox in self.checkboxes.items():
                self.updated_data['B'][key] = checkbox.active
                
        # Показываем диалог выбора папки для сохранения
        folder_dialog = FolderSelectionModal(parent_modal=self)
        folder_dialog.open()
    
    def save_to_folder(self, folder_name):
        """
        Сохраняет обновленные данные детали в указанную папку.
        Создает файлы Blueprint.txt и Version.txt.
        """
        # Определяем путь для сохранения в зависимости от платформы
        if IS_ANDROID:
            # Для Android используем внешнее хранилище
            base_output_dir = 'Details_Output'
        else:
            # Для других платформ используем локальную папку
            base_output_dir = os.path.join(os.getcwd(), "Details_Output")
        
        output_folder = os.path.join(base_output_dir, folder_name)
        
        try:
            # Создаем директорию, если её нет
            os.makedirs(output_folder, exist_ok=True)
            
            # Создаем структуру данных для Blueprint.txt
            blueprint_data = {
                "center": 10.0,
                "parts": [self.updated_data]
            }
            
            # Определяем пути к файлам
            blueprint_path = os.path.join(output_folder, "Blueprint.txt")
            version_path = os.path.join(output_folder, "Version.txt")
            
            # Сохраняем Blueprint.txt с отформатированными данными
            with open(blueprint_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint_data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем Version.txt с номером версии
            with open(version_path, 'w') as f:
                f.write("1.59.15")
                
            print(f"Файл сохранен в папку: {output_folder}")
            
            # Показываем сообщение об успешном сохранении
            self.show_success_message(f"Файл сохранен в папку:\n{output_folder}")
            
        except Exception as e:
            # Показываем сообщение об ошибке при сохранении
            self.show_error_message(f"Ошибка при сохранении:\n{str(e)}")
            print(f"Произошла ошибка при сохранении файлов: {e}")
    
    def show_success_message(self, message):
        """Показывает сообщение об успешном выполнении операции"""
        success_modal = StyledModalView(size_hint=(0.8, 0.4))
        success_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        success_layout.add_widget(Label(
            text=message,
            halign='center',
            font_size=dp(15),
            color=(1, 1, 1, 1)
        ))
        
        close_btn = Button(text="OK", size_hint_y=None, height=60)
        close_btn.button_color = (0.2, 0.8, 0.2, 1)
        close_btn.bind(on_release=success_modal.dismiss)
        success_layout.add_widget(close_btn)
        
        success_modal.add_widget(success_layout)
        success_modal.open()
    
    def show_error_message(self, message):
        """Показывает сообщение об ошибке"""
        error_modal = StyledModalView(size_hint=(0.8, 0.4))
        error_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        error_layout.add_widget(Label(
            text=message,
            halign='center',
            font_size=dp(21),
            color=(1, 1, 1, 1)
        ))
        
        close_btn = Button(text="OK", size_hint_y=None, height=60)
        close_btn.button_color = (0.8, 0.2, 0.2, 1)
        close_btn.bind(on_release=error_modal.dismiss)
        error_layout.add_widget(close_btn)
        
        error_modal.add_widget(error_layout)
        error_modal.open()

# Главный класс приложения
class RocketEditorApp(App):
    
   
    
   
    main_background_image_path = "backgrounds/main_background.jpeg"
   
    def __init__(self, **kwargs):
        super(RocketEditorApp, self).__init__(**kwargs)
        
    def build(self):
        """
        Создает и возвращает корневой виджет приложения.
        Настраивает пути к данным и создает основной интерфейс.
        """
        # Выводим информацию о запуске
        print("Запуск приложения Редактор деталей ракеты")
        print(f"Работаем на Android: {IS_ANDROID}")
        
        # Определяем путь к папке с деталями в зависимости от платформы
        if IS_ANDROID:
            # Проверяем различные возможные пути для Android
            if os.path.exists('Details'):
                self.details_dir = 'Details'
                print(f"Используем путь: {self.details_dir}")
            elif os.path.exists('Details'):
                self.details_dir = 'Details'
                print(f"Используем путь: {self.details_dir}")
            else:
                # Если стандартные пути не найдены, используем локальный путь
                self.details_dir = os.path.join(os.getcwd(), 'Details')
                os.makedirs(self.details_dir, exist_ok=True)
                print(f"Используем локальный путь: {self.details_dir}")
                self._create_test_data_if_needed()
        else:
            # Для не-Android платформ используем локальную директорию
            self.details_dir = os.path.join(os.getcwd(), 'Details')
            os.makedirs(self.details_dir, exist_ok=True)
            print(f"Используем локальный путь: {self.details_dir}")
            # Создаем демо-файлы для тестирования
            self._create_test_data_if_needed()
            
        self.current_detail = None  # Текущая выбранная деталь
        
        # Создаем корневой макет приложения
        self.root_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Добавляем фон для главного окна
        with self.root_layout.canvas.before:
            Color(0.05, 0.1, 0.2, 1)  # Темно-синий фон
            self.bg_rect = RoundedRectangle(pos=self.root_layout.pos, size=self.root_layout.size, radius=[dp(10)])
        
        # Привязываем обновление фона к изменению размера
        self.root_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Заголовок приложения
        title_label = Label(
            text="Редактор деталей ракеты", 
            font_size=dp(20), 
            size_hint_y=None, 
            height=80,
            color=(1, 1, 1, 1),
            bold=True
        )
        self.root_layout.add_widget(title_label)
        
        # Информация о текущем пути к данным
        path_label = Label(
            text=f"Путь к данным: {self.details_dir}", 
            font_size=dp(9), 
            size_hint_y=None, 
            height=40,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.root_layout.add_widget(path_label)
        
        # Создаем скроллируемый список продвинутых кнопок деталей
        scroll_view = ScrollView(do_scroll_x=False)
        self.details_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10, 0])
        self.details_layout.bind(minimum_height=self.details_layout.setter('height'))
        
        # Заполняем список деталей
        self.populate_details_list()
        
        scroll_view.add_widget(self.details_layout)
        self.root_layout.add_widget(scroll_view)
        
        return self.root_layout
    
    def populate_details_list(self):
        """
        Заполняет список продвинутых кнопок деталей.
        Создает DetailButton для каждой найденной детали.
        """
        details_list = self.get_details_list()
        
        if not details_list:
            # Если деталей нет, показываем сообщение
            no_details_label = Label(
                text="Детали не найдены.\nПроверьте путь к папке с деталями.",
                font_size=dp(18),
                color=(0.8, 0.8, 0.8, 1),
                halign='center',
                size_hint_y=None,
                height=100
            )
            self.details_layout.add_widget(no_details_label)
        else:
            # Создаем продвинутые кнопки для каждой детали
            for detail_name in details_list:
                detail_button = DetailButton(
                    detail_name=detail_name,
                    callback=self.on_detail_select
                )
                self.details_layout.add_widget(detail_button)
    
    def update_bg(self, *args):
        """Обновляет фон главного окна при изменении размера"""
        self.bg_rect.pos = self.root_layout.pos
        self.bg_rect.size = self.root_layout.size
    
    def _create_test_data_if_needed(self):
        """
        Создает демонстрационные данные для тестирования приложения.
        Создает несколько примеров деталей с различными типами параметров.
        """
        # Первый пример: двигатель с комплексными параметрами N
        example_dir = os.path.join(self.details_dir, "Солнечная батарея 3")
        os.makedirs(example_dir, exist_ok=True)
        
        test_data = {
            "size": {"x": 1, "y": 1},
            "parts": [
                {
                    "n": "Солнечная батарея 3",
                    "p": {"x": 0, "y": 0},
                    "o": {"x": 0, "y": 0, "z": 0},
                    "B": {"Активен": True, "Основной": False},
                    "N": {
                        "engine_type": "liquid",
                        "thrust": 250.0,
                        "isp": 320.5,
                        "fuel_consumption": 12.8,
                        "enabled": True,
                        "stages": [1, 2],
                        "properties": {
                            "restart": True,
                            "throttleable": True,
                            "gimbal": 5.0
                        }
                    }
                }
            ]
        }
        
        # Второй пример: топливный бак
        example_dir2 = os.path.join(self.details_dir, "Топливный бак")
        os.makedirs(example_dir2, exist_ok=True)
        
        tank_data = {
            "size": {"x": 1, "y": 2},
            "parts": [
                {
                    "n": "Топливный бак",
                    "p": {"x": 0, "y": 0},
                    "o": {"x": 0, "y": 0, "z": 0},
                    "B": {"Отсоединяемый": True},
                    "N": {
                        "type": "fuel_tank",
                        "capacity": 800.0,
                        "mass": 120.0,
                        "contents": ["Керосин", "Жидкий кислород"],
                        "ratios": {
                            "Керосин": 0.4,
                            "Жидкий кислород": 0.6
                        }
                    }
                }
            ]
        }
        
        # Сохраняем первый пример
        test_file = os.path.join(example_dir, "Blueprint.txt")
        if not os.path.exists(test_file):
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
                
            # Создаем также файл Version.txt
            version_file = os.path.join(example_dir, "Version.txt")
            with open(version_file, 'w') as f:
                f.write("1.59.15")
        
        # Сохраняем второй пример
        test_file2 = os.path.join(example_dir2, "Blueprint.txt")
        if not os.path.exists(test_file2):
            with open(test_file2, 'w', encoding='utf-8') as f:
                json.dump(tank_data, f, indent=2, ensure_ascii=False)
                
            # Создаем файл Version.txt для второго примера
            version_file2 = os.path.join(example_dir2, "Version.txt")
            with open(version_file2, 'w') as f:
                f.write("1.59.15")
    
    def on_detail_select(self, detail_name):
        """
        Обрабатывает выбор детали из списка продвинутых кнопок.
        Загружает данные детали и открывает окно редактирования.
        """
        self.current_detail = detail_name
        detail_path = os.path.join(self.details_dir, detail_name, 'Blueprint.txt')
        
        try:
            # Загружаем данные детали из файла
            with open(detail_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Открываем модальное окно редактирования
            modal = EditDetailModal(detail_name, data["parts"][0], self.update_detail_callback)
            modal.open()
        except Exception as e:
            # Показываем сообщение об ошибке загрузки
            self.show_error_dialog(f"Ошибка загрузки детали {detail_name}:\n{str(e)}\n\nПуть: {detail_path}")
            print(f"Ошибка загрузки детали: {e}")
    
    def show_error_dialog(self, message):
        """Показывает диалог с сообщением об ошибке"""
        error_modal = StyledModalView(size_hint=(0.8, 0.5))
        error_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        error_layout.add_widget(Label(
            text=message,
            halign='center',
            font_size=dp(21),
            color=(1, 1, 1, 1)
        ))
        
        close_btn = Button(text="OK", size_hint_y=None, height=60)
        close_btn.button_color = (0.8, 0.2, 0.2, 1)
        close_btn.bind(on_release=error_modal.dismiss)
        error_layout.add_widget(close_btn)
        
        error_modal.add_widget(error_layout)
        error_modal.open()
    
    def update_detail_callback(self, detail_name, updated_data):
        """
        Callback-функция, вызываемая после обновления детали.
        В данной реализации не выполняет дополнительных действий.
        """
        pass
    
    def get_details_list(self):
        """
        Получает список доступных деталей из директории.
        Возвращает отсортированный список имен папок.
        """
        try:
            details = sorted([d for d in os.listdir(self.details_dir) 
                             if os.path.isdir(os.path.join(self.details_dir, d))])
            if not details:
                print(f"В папке {self.details_dir} не найдено деталей.")
                return []
            return details
        except Exception as e:
            print(f"Ошибка при получении списка деталей: {e}")
            return []

# Точка входа в приложение
if __name__ == "__main__":
    app = RocketEditorApp()
    try:
        app.run()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
