
.PHONY: all ui

all: ui
	python logician.py

ui:
	pyside-uic ./ui/MainWindow.ui -o./ui/main_window.py
	pyside-uic ./ui/AnalyzerDialog.ui -o./ui/analyzer_dialog.py
