# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/MainWindow.ui'
#
# Created: Wed Nov 13 21:22:29 2013
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(911, 657)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.topRowLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.topRowLayoutWidget.setObjectName("topRowLayoutWidget")
        self.topRowLayout = QtGui.QHBoxLayout(self.topRowLayoutWidget)
        self.topRowLayout.setContentsMargins(12, 12, -1, -1)
        self.topRowLayout.setObjectName("topRowLayout")
        self.label_2 = QtGui.QLabel(self.topRowLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.topRowLayout.addWidget(self.label_2)
        self.sampleRateComboBox = QtGui.QComboBox(self.topRowLayoutWidget)
        font = QtGui.QFont()
        self.sampleRateComboBox.setFont(font)
        self.sampleRateComboBox.setObjectName("sampleRateComboBox")
        self.topRowLayout.addWidget(self.sampleRateComboBox)
        self.label = QtGui.QLabel(self.topRowLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.topRowLayout.addWidget(self.label)
        self.sampleCountComboBox = QtGui.QComboBox(self.topRowLayoutWidget)
        self.sampleCountComboBox.setObjectName("sampleCountComboBox")
        self.topRowLayout.addWidget(self.sampleCountComboBox)
        self.label_3 = QtGui.QLabel(self.topRowLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.topRowLayout.addWidget(self.label_3)
        self.triggerChannelComboBox = QtGui.QComboBox(self.topRowLayoutWidget)
        self.triggerChannelComboBox.setObjectName("triggerChannelComboBox")
        self.triggerChannelComboBox.addItem("")
        self.triggerChannelComboBox.addItem("")
        self.triggerChannelComboBox.addItem("")
        self.triggerChannelComboBox.addItem("")
        self.topRowLayout.addWidget(self.triggerChannelComboBox)
        self.triggerSlopeComboBox = QtGui.QComboBox(self.topRowLayoutWidget)
        self.triggerSlopeComboBox.setObjectName("triggerSlopeComboBox")
        self.triggerSlopeComboBox.addItem("")
        self.triggerSlopeComboBox.addItem("")
        self.topRowLayout.addWidget(self.triggerSlopeComboBox)
        self.startButton = QtGui.QPushButton(self.topRowLayoutWidget)
        self.startButton.setObjectName("startButton")
        self.topRowLayout.addWidget(self.startButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.topRowLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.topRowLayoutWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.analyzerWidget = AnalyzerWidget(self.centralwidget)
        self.analyzerWidget.setProperty("cursor", QtCore.Qt.CrossCursor)
        self.analyzerWidget.setMouseTracking(True)
        self.analyzerWidget.setFrameShape(QtGui.QFrame.NoFrame)
        self.analyzerWidget.setFrameShadow(QtGui.QFrame.Plain)
        self.analyzerWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.analyzerWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.analyzerWidget.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.analyzerWidget.setRenderHints(QtGui.QPainter.TextAntialiasing)
        self.analyzerWidget.setObjectName("analyzerWidget")
        self.horizontalLayout.addWidget(self.analyzerWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.protocolComboBox = QtGui.QComboBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.protocolComboBox.sizePolicy().hasHeightForWidth())
        self.protocolComboBox.setSizePolicy(sizePolicy)
        self.protocolComboBox.setObjectName("protocolComboBox")
        self.protocolComboBox.addItem("")
        self.protocolComboBox.addItem("")
        self.protocolComboBox.addItem("")
        self.protocolComboBox.addItem("")
        self.verticalLayout.addWidget(self.protocolComboBox)
        self.displayTypeComboBox = QtGui.QComboBox(self.centralwidget)
        self.displayTypeComboBox.setObjectName("displayTypeComboBox")
        self.displayTypeComboBox.addItem("")
        self.displayTypeComboBox.addItem("")
        self.displayTypeComboBox.addItem("")
        self.verticalLayout.addWidget(self.displayTypeComboBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 911, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuTheme = QtGui.QMenu(self.menuView)
        self.menuTheme.setObjectName("menuTheme")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.statusBar.setFont(font)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSave_to_Spreadsheet = QtGui.QAction(MainWindow)
        self.actionSave_to_Spreadsheet.setEnabled(False)
        self.actionSave_to_Spreadsheet.setObjectName("actionSave_to_Spreadsheet")
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionDefault = QtGui.QAction(MainWindow)
        self.actionDefault.setObjectName("actionDefault")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave_to_Spreadsheet)
        self.menuView.addAction(self.menuTheme.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Logician Logic Analyzer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Sample Rate", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Sample Count", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerChannelComboBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "Channel 0", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerChannelComboBox.setItemText(1, QtGui.QApplication.translate("MainWindow", "Channel 1", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerChannelComboBox.setItemText(2, QtGui.QApplication.translate("MainWindow", "Channel 2", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerChannelComboBox.setItemText(3, QtGui.QApplication.translate("MainWindow", "Channel 3", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerSlopeComboBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "Rising", None, QtGui.QApplication.UnicodeUTF8))
        self.triggerSlopeComboBox.setItemText(1, QtGui.QApplication.translate("MainWindow", "Falling", None, QtGui.QApplication.UnicodeUTF8))
        self.startButton.setText(QtGui.QApplication.translate("MainWindow", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setToolTip(QtGui.QApplication.translate("MainWindow", "Select a suitable communication protocol.", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "General I/O", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(1, QtGui.QApplication.translate("MainWindow", "I2C", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(2, QtGui.QApplication.translate("MainWindow", "SPI", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(3, QtGui.QApplication.translate("MainWindow", "USART", None, QtGui.QApplication.UnicodeUTF8))
        self.displayTypeComboBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "Ascii", None, QtGui.QApplication.UnicodeUTF8))
        self.displayTypeComboBox.setItemText(1, QtGui.QApplication.translate("MainWindow", "Hex", None, QtGui.QApplication.UnicodeUTF8))
        self.displayTypeComboBox.setItemText(2, QtGui.QApplication.translate("MainWindow", "Decimal", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuView.setTitle(QtGui.QApplication.translate("MainWindow", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.menuTheme.setTitle(QtGui.QApplication.translate("MainWindow", "Theme", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_to_Spreadsheet.setText(QtGui.QApplication.translate("MainWindow", "Save to Spreadsheet...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_to_Spreadsheet.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDefault.setText(QtGui.QApplication.translate("MainWindow", "Default", None, QtGui.QApplication.UnicodeUTF8))

from ui.widgets import AnalyzerWidget
