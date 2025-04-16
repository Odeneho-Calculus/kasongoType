"""
KasongoType Desktop Application
Cross-platform desktop app built with PyQt5 WebEngine
"""

import os
import sys
import json
import signal
import threading
import webbrowser
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                           QAction, QToolBar, QStatusBar, QSystemTrayIcon, 
                           QMenu, QDialog, QDialogButtonBox, QMessageBox)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

from web.app import app as flask_app

class KasongoTypeDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.web_app_thread = None
        self.setWindowTitle("KasongoType - Cyberpunk Typing Trainer")
        self.setMinimumSize(1024, 768)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget with WebEngineView
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create WebEngineView
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        
        # Add web view to layout
        layout.addWidget(self.web_view)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Connect signals and slots
        self.web_view.loadFinished.connect(self.on_load_finished)
        
        # Start Flask server in a separate thread
        self.start_web_server()
        
        # Load the local URL
        self.web_view.load(QUrl("http://localhost:5000"))
        
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Navigation")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Add actions
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.web_view.back)
        toolbar.addAction(back_action)
        
        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.web_view.forward)
        toolbar.addAction(forward_action)
        
        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.web_view.reload)
        toolbar.addAction(reload_action)
        
        home_action = QAction("Home", self)
        home_action.triggered.connect(self.go_home)
        toolbar.addAction(home_action)
        
        # Add menu
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        typing_action = QAction("Typing", self)
        typing_action.triggered.connect(lambda: self.web_view.load(QUrl("http://localhost:5000/")))
        view_menu.addAction(typing_action)
        
        exercises_action = QAction("Exercises", self)
        exercises_action.triggered.connect(lambda: self.web_view.load(QUrl("http://localhost:5000/exercises")))
        view_menu.addAction(exercises_action)
        
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.web_view.load(QUrl("http://localhost:5000/dashboard")))
        view_menu.addAction(dashboard_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def create_tray_icon(self):
        """Create system tray icon"""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icon.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        
        # Create tray menu
        tray_menu = QMenu()
        
        open_action = QAction("Open KasongoType", self)
        open_action.triggered.connect(self.show)
        tray_menu.addAction(open_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close_application)
        tray_menu.addAction(quit_action)
        
        # Set the tray's menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect signals
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Minimize to tray instead of closing
        if self.tray_icon.isVisible():
            QMessageBox.information(self, "KasongoType",
                                   "KasongoType will continue running in the system tray.\n"
                                   "To quit the application, right-click on the tray icon and select Quit.")
            self.hide()
            event.ignore()
        else:
            self.close_application()
            event.accept()
    
    def close_application(self):
        """Close the application completely"""
        # Stop the web server
        self.stop_web_server()
        
        # Close the application
        QApplication.quit()
    
    def go_home(self):
        """Navigate to home page"""
        self.web_view.load(QUrl("http://localhost:5000/"))
        
    def on_load_finished(self, success):
        """Handle page load completion"""
        if success:
            self.statusBar.showMessage("Page loaded successfully")
        else:
            self.statusBar.showMessage("Error loading page")
            
    def show_about_dialog(self):
        """Show about dialog"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About KasongoType")
        msg_box.setText("KasongoType - Cyberpunk Typing Trainer\n\nVersion 1.0.0\n\n© 2025 KasongoType Team")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
    
    def start_web_server(self):
        """Start Flask web server in a separate thread"""
        def run_server():
            flask_app.run(debug=False, use_reloader=False)
        
        self.web_app_thread = threading.Thread(target=run_server)
        self.web_app_thread.daemon = True
        self.web_app_thread.start()
        
        # Allow some time for the server to start
        import time
        time.sleep(0.5)
    
    def stop_web_server(self):
        """Stop the Flask web server"""
        if self.web_app_thread and self.web_app_thread.is_alive():
            # Send signal to stop the server
            os.kill(os.getpid(), signal.SIGTERM)

def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    window = KasongoTypeDesktop()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
