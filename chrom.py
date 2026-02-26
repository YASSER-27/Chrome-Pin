import sys
import os
import subprocess
import pygetwindow as gw
import win32gui
import win32con
import win32api
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFrame, QHBoxLayout, QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QColor, QCursor, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint

# --- التصميم العصري (Mac Style) ---
MODERN_STYLE = """
    QMainWindow {
        background-color: #0F0F0F;
        border-radius: 20px;
    }
    QWidget#MainContent {
        background-color: #0F0F0F;
        border-radius: 20px;
    }
    QFrame#Card {
        background-color: #1A1A1A;
        border-radius: 15px;
        border: 1px solid #333333;
    }
    QLabel#Title {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: bold;
        font-family: 'Segoe UI';
    }
    QLabel#Subtitle {
        color: #888888;
        font-size: 12px;
    }
    QPushButton {
        background-color: #252525;
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-size: 14px;
        border: 1px solid #333;
    }
    QPushButton:hover {
        background-color: #333333;
        border: 1px solid #4285F4;
    }
    QPushButton#PrimaryBtn {
        background-color: #4285F4;
        font-weight: bold;
        border: none;
    }
    QPushButton#PrimaryBtn:hover {
        background-color: #357ABD;
    }
    QPushButton#ExitBtn {
        background-color: #CC0000;
        border: none;
    }
"""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModernWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # إعدادات النافذة (Frameless & Transparent)
        self.setWindowTitle("Control Panel")
        self.setFixedSize(380, 520)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MODERN_STYLE)
        
        # دعم سحب النافذة
        self.old_pos = None

        # المحتوى الرئيسي
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainContent")
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(25, 30, 25, 25)
        self.layout.setSpacing(20)

        # العناوين
        self.header_layout = QVBoxLayout()
        self.title_lbl = QLabel("Window Manager")
        self.title_lbl.setObjectName("Title")
        
        self.status_lbl = QLabel("● System Active")
        self.status_lbl.setObjectName("Subtitle")
        self.status_lbl.setStyleSheet("color: #00FF7F;") 
        
        self.header_layout.addWidget(self.title_lbl)
        self.header_layout.addWidget(self.status_lbl)
        self.layout.addLayout(self.header_layout)

        # بطاقة التحكم (Card)
        self.card = QFrame()
        self.card.setObjectName("Card")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(15, 20, 15, 20)
        self.card_layout.setSpacing(15)

        self.card_title = QLabel("Quick Actions")
        self.card_title.setStyleSheet("color: #BBB; font-weight: bold;")
        self.card_layout.addWidget(self.card_title)

        # الأزرار
        self.btn_transform = QPushButton("Transform Chrome")
        self.btn_transform.setObjectName("PrimaryBtn")
        self.btn_transform.clicked.connect(self.controller.ensure_chrome_running)
        
        self.btn_reset = QPushButton("Reset Windows")
        self.btn_reset.clicked.connect(self.controller.cleanup_and_clear)
        
        self.btn_hide = QPushButton("Hide to Tray")
        self.btn_hide.clicked.connect(self.hide)
        
        self.card_layout.addWidget(self.btn_transform)
        self.card_layout.addWidget(self.btn_reset)
        self.card_layout.addWidget(self.btn_hide)
        
        self.layout.addWidget(self.card)

        # التذييل (Footer)
        self.footer_lbl = QLabel("Shortcut: CTRL + G")
        self.footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_lbl.setStyleSheet("color: #444; font-size: 10px; margin-top: 10px;")
        self.layout.addWidget(self.footer_lbl)

        # زر الخروج النهائي
        self.exit_btn = QPushButton("Shut Down")
        self.exit_btn.setObjectName("ExitBtn")
        self.exit_btn.clicked.connect(QApplication.instance().quit)
        self.layout.addWidget(self.exit_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class ChromeController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.transformed_hwnds = set()
        
        self.window = ModernWindow(self)
        
        # إنشاء الأيقونة بجانب الساعة
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.create_icon())
        self.tray.setToolTip("Chrome Controller (CTRL+G)")
        
        self.tray_menu = QMenu()
        show_act = QAction("إظهار لوحة التحكم", self.tray_menu)
        show_act.triggered.connect(self.show_window_at_cursor)
        self.tray_menu.addAction(show_act)
        
        self.tray_menu.addSeparator()
        exit_act = QAction("إغلاق البرنامج", self.tray_menu)
        exit_act.triggered.connect(QApplication.instance().quit)
        self.tray_menu.addAction(exit_act)
        
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()
        self.tray.setVisible(True)
        
        # إعداد التنظيف عند الخروج
        QApplication.instance().aboutToQuit.connect(self.cleanup)
        
        # التأكد من تشغيل كروم عند البدء
        self.chrome_check_attempts = 0
        QTimer.singleShot(500, self.window.show)
        
        # إعداد الاختصار العالمي Ctrl + G
        self.hotkey_timer = QTimer()
        self.hotkey_timer.timeout.connect(self.check_hotkey)
        self.hotkey_timer.start(100) # فحص كل 100 ملي ثانية
        self.hotkey_active = False

    def show_window_at_cursor(self):
        pos = QCursor.pos()
        # محاذاة النافذة لتظهر منتصف الماوس تقريباً
        self.window.move(pos.x() - self.window.width() // 2, pos.y() - self.window.height() // 2)
        self.window.show()
        self.window.activateWindow()

    def check_hotkey(self):
        # 0x11 = VK_CONTROL, 0x47 = 'G'
        ctrl_pressed = win32api.GetAsyncKeyState(0x11) & 0x8000
        g_pressed = win32api.GetAsyncKeyState(0x47) & 0x8000
        
        if ctrl_pressed and g_pressed:
            if not self.hotkey_active:
                self.hotkey_active = True
                if self.window.isVisible():
                    self.window.hide()
                else:
                    self.show_window_at_cursor()
        else:
            self.hotkey_active = False

    def cleanup_and_clear(self):
        self.cleanup()
        self.transformed_hwnds.clear()

    def cleanup(self):
        """إعادة النوافذ لحالتها الطبيعية عند إغلاق البرنامج"""
        print(f"Cleaning up {len(self.transformed_hwnds)} windows...")
        for hwnd in self.transformed_hwnds:
            try:
                if win32gui.IsWindow(hwnd):
                    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            except Exception:
                pass

    def ensure_chrome_running(self):
        # البحث عن نوافذ كروم
        chrome_windows = gw.getWindowsWithTitle('Google Chrome')
        
        if not chrome_windows:
            subprocess.Popen(['start', 'chrome', '--new-window'], shell=True)
            self.chrome_check_attempts = 0
            self.poll_chrome_window()
        else:
            # تحويل أول نافذة يتم العثور عليها تلقائياً
            self.transform_window(chrome_windows[0])

    def poll_chrome_window(self):
        chrome_windows = gw.getWindowsWithTitle('Google Chrome')
        if chrome_windows:
            self.transform_window(chrome_windows[0])
        elif self.chrome_check_attempts < 20:
            self.chrome_check_attempts += 1
            QTimer.singleShot(500, self.poll_chrome_window)

    def create_icon(self):
        icon_path = resource_path("high.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            pix = QPixmap(64, 64)
            pix.fill(QColor("#4285F4"))
            return QIcon(pix)

    def transform_window(self, window):
        # 1. جلب "مقبض" النافذة (HWND)
        hwnd = window._hWnd
        self.transformed_hwnds.add(hwnd)
        
        # 2. جعل النافذة "فوق كل شيء" (Always on Top)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
        # 3. تغيير حجم النافذة لتصبح مثل "الشات" (طولية)
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)
        width, height = 400, 900
        
        # تحريكها لزاوية التنبيهات
        win32gui.MoveWindow(hwnd, screen_width - width - 10, screen_height - height - 50, width, height, True)
        
        # 4. اختيار اختياري: إزالة إطار النافذة
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_CAPTION
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

if __name__ == "__main__":
    controller = ChromeController()
    sys.exit(controller.app.exec())
