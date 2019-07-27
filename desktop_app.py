import sys
import time
from functools import partial

import serial
import re
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QHBoxLayout, QFormLayout, QComboBox, QDesktopWidget, QListWidget, QFrame

# PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

# globals for the max size so we can pad all values to work with c code
MAX_CHAR_SIZE: int = 180
MAX_NUM_SIZE: int = 7


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PHATCAT Desktop Application")
        # self.setMinimumSize(1000, 500)

        self.pixmap = QtGui.QPixmap('PHATCAT.png').scaledToWidth(150).scaledToHeight(75)
        # self.pixmap.scalled()

        # TODO make the menu appear in the right location
        # self.main_frame = QtWidgets.QFrame()
        # self.main_layout = QtWidgets.QGridLayout()
        # self.main_frame.setLayout(self.main_layout)

        # create the menu at the top of the GUI
        self.menu = QtWidgets.QMenuBar()
        self.action_new = QtWidgets.QAction()
        self.action_save = QtWidgets.QAction()
        self.action_load = QtWidgets.QAction()
        self.action_exit = QtWidgets.QAction()

        # add the actions to the menu
        self.menu.addAction(self.action_new)
        self.menu.addAction(self.action_save)
        self.menu.addAction(self.action_load)
        self.menu.addAction(self.action_exit)

        # TODO make tabs for each settings page
        self.tabs = QtWidgets.QTabWidget()
        self.eq_data_tab = QtWidgets.QWidget()
        self.led_ind_tab = QtWidgets.QWidget()
        self.output_contacts_tab = QtWidgets.QWidget()
        self.current_differential_tab = QtWidgets.QWidget()
        self.w_winding_tab = QtWidgets.QWidget()
        self.x_winding_tab = QtWidgets.QWidget()
        self.volts_hertz_tab = QtWidgets.QWidget()

        # # TODO make the list widget show up in the right location
        self.v_spacer = QtWidgets.QSpacerItem(0, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # # create a list widget to hold all the menu settings
        # self.menu_list = QListWidget()
        # self.eq_data = QtWidgets.QListWidgetItem("Equipment Data")
        # self.led_indicator = QtWidgets.QListWidgetItem("LED Indicators")
        # self.output_contacts = QtWidgets.QListWidgetItem("Output Contacts")
        # self.current_diff = QtWidgets.QListWidgetItem("Current Differential")
        # self.w_winding_over = QtWidgets.QListWidgetItem("W-Winding Overcurrent")
        # self.x_winding_over = QtWidgets.QListWidgetItem("X-Winding Overcurrent")
        # self.volts_hz = QtWidgets.QListWidgetItem("Volts/Hz Element")
        # self.menu_list.setMinimumHeight(250)
        # self.menu_list.setMinimumWidth(350)
        # self.menu_list.setMaximumHeight(270)
        # self.menu_list.setMaximumWidth(350)
        # # self.menu_list.
        #
        # # add the menu lists to the list widget
        # self.menu_list.addItem(self.eq_data)
        # self.menu_list.addItem(self.led_indicator)
        # self.menu_list.addItem(self.output_contacts)
        # self.menu_list.addItem(self.current_diff)
        # self.menu_list.addItem(self.w_winding_over)
        # self.menu_list.addItem(self.x_winding_over)
        # self.menu_list.addItem(self.volts_hz)
        # # self.menu_list.setMinimumSize(500, 500)
        #
        # # TODO make different settings based off which menu item is clicked
        # if self.menu_list.itemClicked(self.eq_data):
        #     pass

        # def setup_equipment_data(self):
        # set up the GUI for the desktop application
        self.relay_name = QtWidgets.QLabel("Relay Name (40 Characters)")
        self.relay_name_entry = QtWidgets.QLineEdit()

        self.trans_nameplate = QtWidgets.QLabel("Transformer Nameplate Max MVA Rating (float 0.2 - 5000)")
        self.trans_nameplate_entry = QtWidgets.QLineEdit()

        self.sys_nom_freq = QtWidgets.QLabel("System Nominal Frequency (float 45 - 65)")
        self.sys_nom_freq_entry = QtWidgets.QLineEdit()

        self.source_side_winding = QtWidgets.QLabel("Source Side Winding")
        self.source_side_winding_cb = QComboBox()
        self.source_side_winding_cb.setMinimumHeight(20)
        self.source_side_winding_cb.addItem("W-Winding")
        self.source_side_winding_cb.addItem("X-Winding")

        self.trans_connect_type = QtWidgets.QLabel("Transformer Connection Type")
        self.trans_connect_type_cb = QComboBox()
        self.trans_connect_type_cb.setMinimumHeight(20)
        self.trans_connect_type_cb.addItem("Y-Y")
        self.trans_connect_type_cb.addItem("YDAC")
        self.trans_connect_type_cb.addItem("DACDAC")

        self.w_winding_group = QtWidgets.QGroupBox()
        self.w_winding_group.setTitle("W-Winding")
        self.w_winding_layout = QtWidgets.QVBoxLayout()

        self.w_winding_volt_rate = QtWidgets.QLabel("Line-to-Line Voltage Rating(in kV) of W-Winding (float 1-1000)")
        self.w_winding_volt_rate_entry = QtWidgets.QLineEdit()
        self.w_winding_volt_rate_entry.setMaximumHeight(50)
        self.w_winding_phase_ct = QtWidgets.QLabel("W-Winding Phase CT Ratio Wye-Connection (float 1-5000)")
        self.w_winding_phase_ct_entry = QtWidgets.QLineEdit()
        self.w_winding_phase_ct_entry.setMaximumHeight(50)
        self.w_winding_neutral = QtWidgets.QLabel("W-Winding Neutral CT Ratio (float 1-5000)")
        self.w_winding_neutral_entry = QtWidgets.QLineEdit()
        self.w_winding_neutral_entry.setMaximumHeight(50)
        self.w_winding_phase_pt = QtWidgets.QLabel("W-Winding Phase PT Ratio Wye-Connection (float 1-5000)")
        self.w_winding_phase_pt_entry = QtWidgets.QLineEdit()
        self.w_winding_phase_pt_entry.setMaximumHeight(50)

        # add the components to the layout
        self.w_winding_layout.addWidget(self.w_winding_volt_rate)
        self.w_winding_layout.addWidget(self.w_winding_volt_rate_entry)
        self.w_winding_layout.addWidget(self.w_winding_phase_ct)
        self.w_winding_layout.addWidget(self.w_winding_phase_ct_entry)
        self.w_winding_layout.addWidget(self.w_winding_neutral)
        self.w_winding_layout.addWidget(self.w_winding_neutral_entry)
        self.w_winding_layout.addWidget(self.w_winding_phase_pt)
        self.w_winding_layout.addWidget(self.w_winding_phase_pt_entry)
        self.w_winding_group.setLayout(self.w_winding_layout)

        self.x_winding_group = QtWidgets.QGroupBox()
        self.x_winding_group.setTitle("X-Winding")
        self.x_winding_layout = QtWidgets.QVBoxLayout()

        self.x_winding_volt_rate = QtWidgets.QLabel("Line-to-Line Voltage Rating(in kV) of X-Winding (float 1-1000)")
        self.x_winding_volt_rate_entry = QtWidgets.QLineEdit()
        self.x_winding_volt_rate_entry.setMaximumHeight(50)
        self.x_winding_phase_ct = QtWidgets.QLabel("X-Winding Phase CT Ratio Wye-Connection (float 1-5000)")
        self.x_winding_phase_ct_entry = QtWidgets.QLineEdit()
        self.x_winding_phase_ct_entry.setMaximumHeight(50)
        self.x_winding_neutral = QtWidgets.QLabel("X-Winding Neutral CT Ratio (float 1-5000)")
        self.x_winding_neutral_entry = QtWidgets.QLineEdit()
        self.x_winding_neutral_entry.setMaximumHeight(50)
        self.x_winding_phase_pt = QtWidgets.QLabel("X-Winding Phase PT Ratio Wye-Connection (float 1-5000)")
        self.x_winding_phase_pt_entry = QtWidgets.QLineEdit()
        self.x_winding_phase_pt_entry.setMaximumHeight(50)

        # add the components to the layout
        self.x_winding_layout.addWidget(self.x_winding_volt_rate)
        self.x_winding_layout.addWidget(self.x_winding_volt_rate_entry)
        self.x_winding_layout.addWidget(self.x_winding_phase_ct)
        self.x_winding_layout.addWidget(self.x_winding_phase_ct_entry)
        self.x_winding_layout.addWidget(self.x_winding_neutral)
        self.x_winding_layout.addWidget(self.x_winding_neutral_entry)
        self.x_winding_layout.addWidget(self.x_winding_phase_pt)
        self.x_winding_layout.addWidget(self.x_winding_phase_pt_entry)
        self.x_winding_group.setLayout(self.x_winding_layout)

        self.nom_phase_volt = QtWidgets.QLabel("Nominal Phase Voltage (L-N, Secondary Volts)(float 25-100)")
        self.nom_phase_volt_entry = QtWidgets.QLineEdit()
        self.nom_phase_volt_entry.setMaximumHeight(50)

        # create a scroll area to put everything in
        # TODO make it so the scroll area has the scroll bar
        self.eq_data_tab = QtWidgets.QScrollArea()
        self.eq_data_tab.setWidgetResizable(True)
        self.eq_data_tab.setGeometry(10, 10, 200, 200)
        self.scroll_layout = QtWidgets.QFormLayout()
        self.scroll_layout.addWidget(self.relay_name)
        self.scroll_layout.addWidget(self.relay_name_entry)
        self.scroll_layout.addWidget(self.trans_nameplate)
        self.scroll_layout.addWidget(self.trans_nameplate_entry)
        self.scroll_layout.addWidget(self.sys_nom_freq)
        self.scroll_layout.addWidget(self.sys_nom_freq_entry)

        self.scroll_layout.addWidget(self.source_side_winding)
        self.scroll_layout.addWidget(self.source_side_winding_cb)

        self.scroll_layout.addWidget(self.trans_connect_type)
        self.scroll_layout.addWidget(self.trans_connect_type_cb)

        self.scroll_layout.addWidget(self.w_winding_group)

        self.scroll_layout.addWidget(self.x_winding_group)

        self.scroll_layout.addWidget(self.nom_phase_volt)
        self.scroll_layout.addWidget(self.nom_phase_volt_entry)

        self.eq_data_tab.setLayout(self.scroll_layout)

        # TODO make LED settings
        self.led_tab = QtWidgets.QScrollArea()
        self.led_tab.setWidgetResizable(True)
        self.led_layout = QtWidgets.QFormLayout()
        self.led1_status = QtWidgets.QLabel("User-Defined Logic Expression for LED1 Status")
        self.led1_entry = QtWidgets.QLineEdit()

        self.led2_status = QtWidgets.QLabel("User-Defined Logic Expression for LED2 Status")
        self.led2_entry = QtWidgets.QLineEdit()

        self.led3_status = QtWidgets.QLabel("User-Defined Logic Expression for LED3 Status")
        self.led3_entry = QtWidgets.QLineEdit()

        self.led4_status = QtWidgets.QLabel("User-Defined Logic Expression for LED4 Status")
        self.led4_entry = QtWidgets.QLineEdit()

        # make the check boxes
        self.checkbox_led1_window = QtWidgets.QScrollArea()
        self.checkbox_led1_window.setMinimumHeight(150)
        self.checkbox_led1_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_led1 = QtWidgets.QCheckBox("Trip")
        # self.trip_checkbox_led1.setMaximumSize(1, 1)

        self.pb3_checkbox_led1 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_led1 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_led1 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_led1 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_led1 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_led1 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_led1 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_led1 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_led1 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_led1 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_led1 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_led1 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_led1 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_led1 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_led1 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_led1 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_led1 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_led1 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_led1 = QtWidgets.QCheckBox("NOTIN3")

        # self.v_spacer = QtWidgets.QSpacerItem(0, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.checkbox_led1_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_led1_button.clicked.connect(partial(self.select_checkbox_button_clicked_led1, selected_str))

        self.checkbox_led1_layout.addWidget(self.trip_checkbox_led1, 0, 0)

        self.checkbox_led1_layout.addWidget(self.pb3_checkbox_led1, 0, 1)
        self.checkbox_led1_layout.addWidget(self.pb4_checkbox_led1, 1, 1)
        self.checkbox_led1_layout.addWidget(self.pb5_checkbox_led1, 2, 1)
        self.checkbox_led1_layout.addWidget(self.pb6_checkbox_led1, 3, 1)
        # self.checkbox_led1_layout.addItem(self.v_spacer, 4, 1)

        self.checkbox_led1_layout.addWidget(self.p50_checkbox_led1, 0, 2)
        self.checkbox_led1_layout.addWidget(self.n50_checkbox_led1, 1, 2)
        self.checkbox_led1_layout.addWidget(self.g50_checkbox_led1, 2, 2)

        self.checkbox_led1_layout.addWidget(self.p51_checkbox_led1, 0, 3)
        self.checkbox_led1_layout.addWidget(self.g51_checkbox_led1, 1, 3)

        self.checkbox_led1_layout.addWidget(self.r87_checkbox_led1, 0, 4)
        self.checkbox_led1_layout.addWidget(self.u87_checkbox_led1, 1, 4)

        self.checkbox_led1_layout.addWidget(self.v1_24_checkbox_led1, 0, 5)
        self.checkbox_led1_layout.addWidget(self.v2_24_checkbox_led1, 1, 5)

        self.checkbox_led1_layout.addWidget(self.in1_checkbox_led1, 0, 6)
        self.checkbox_led1_layout.addWidget(self.in2_checkbox_led1, 1, 6)
        self.checkbox_led1_layout.addWidget(self.in3_checkbox_led1, 2, 6)

        self.checkbox_led1_layout.addWidget(self.notin1_checkbox_led1, 0, 7)
        self.checkbox_led1_layout.addWidget(self.notin2_checkbox_led1, 1, 7)
        self.checkbox_led1_layout.addWidget(self.notin3_checkbox_led1, 2, 7)

        self.checkbox_led1_layout.addItem(self.v_spacer, 5, 8)
        self.checkbox_led1_layout.addWidget(self.checkbox_led1_button, 5, 9)

        self.checkbox_led1_window.setLayout(self.checkbox_led1_layout)

        # make the check boxes
        self.checkbox_led2_window = QtWidgets.QScrollArea()
        self.checkbox_led2_window.setMinimumHeight(150)
        self.checkbox_led2_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_led2 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_led2 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_led2 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_led2 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_led2 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_led2 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_led2 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_led2 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_led2 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_led2 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_led2 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_led2 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_led2 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_led2 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_led2 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_led2 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_led2 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_led2 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_led2 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_led2 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_led2_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_led2_button.clicked.connect(partial(self.select_checkbox_button_clicked_led2, selected_str))

        self.checkbox_led2_layout.addWidget(self.trip_checkbox_led2, 0, 0)

        self.checkbox_led2_layout.addWidget(self.pb3_checkbox_led2, 0, 1)
        self.checkbox_led2_layout.addWidget(self.pb4_checkbox_led2, 1, 1)
        self.checkbox_led2_layout.addWidget(self.pb5_checkbox_led2, 2, 1)
        self.checkbox_led2_layout.addWidget(self.pb6_checkbox_led2, 3, 1)

        self.checkbox_led2_layout.addWidget(self.p50_checkbox_led2, 0, 2)
        self.checkbox_led2_layout.addWidget(self.n50_checkbox_led2, 1, 2)
        self.checkbox_led2_layout.addWidget(self.g50_checkbox_led2, 2, 2)

        self.checkbox_led2_layout.addWidget(self.p51_checkbox_led2, 0, 3)
        self.checkbox_led2_layout.addWidget(self.g51_checkbox_led2, 1, 3)

        self.checkbox_led2_layout.addWidget(self.r87_checkbox_led2, 0, 4)
        self.checkbox_led2_layout.addWidget(self.u87_checkbox_led2, 1, 4)

        self.checkbox_led2_layout.addWidget(self.v1_24_checkbox_led2, 0, 5)
        self.checkbox_led2_layout.addWidget(self.v2_24_checkbox_led2, 1, 5)

        self.checkbox_led2_layout.addWidget(self.in1_checkbox_led2, 0, 6)
        self.checkbox_led2_layout.addWidget(self.in2_checkbox_led2, 1, 6)
        self.checkbox_led2_layout.addWidget(self.in3_checkbox_led2, 2, 6)

        self.checkbox_led2_layout.addWidget(self.notin1_checkbox_led2, 0, 7)
        self.checkbox_led2_layout.addWidget(self.notin2_checkbox_led2, 1, 7)
        self.checkbox_led2_layout.addWidget(self.notin3_checkbox_led2, 2, 7)

        self.checkbox_led2_layout.addItem(self.v_spacer, 5, 8)
        self.checkbox_led2_layout.addWidget(self.checkbox_led2_button, 5, 9)

        self.checkbox_led2_window.setLayout(self.checkbox_led2_layout)

        # make the check boxes
        self.checkbox_led3_window = QtWidgets.QScrollArea()
        self.checkbox_led3_window.setMinimumHeight(150)
        self.checkbox_led3_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_led3 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_led3 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_led3 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_led3 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_led3 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_led3 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_led3 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_led3 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_led3 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_led3 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_led3 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_led3 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_led3 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_led3 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_led3 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_led3 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_led3 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_led3 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_led3 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_led3 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_led3_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_led3_button.clicked.connect(partial(self.select_checkbox_button_clicked_led3, selected_str))

        self.checkbox_led3_layout.addWidget(self.trip_checkbox_led3, 0, 0)

        self.checkbox_led3_layout.addWidget(self.pb3_checkbox_led3, 0, 1)
        self.checkbox_led3_layout.addWidget(self.pb4_checkbox_led3, 1, 1)
        self.checkbox_led3_layout.addWidget(self.pb5_checkbox_led3, 2, 1)
        self.checkbox_led3_layout.addWidget(self.pb6_checkbox_led3, 3, 1)

        self.checkbox_led3_layout.addWidget(self.p50_checkbox_led3, 0, 2)
        self.checkbox_led3_layout.addWidget(self.n50_checkbox_led3, 1, 2)
        self.checkbox_led3_layout.addWidget(self.g50_checkbox_led3, 2, 2)

        self.checkbox_led3_layout.addWidget(self.p51_checkbox_led3, 0, 3)
        self.checkbox_led3_layout.addWidget(self.g51_checkbox_led3, 1, 3)

        self.checkbox_led3_layout.addWidget(self.r87_checkbox_led3, 0, 4)
        self.checkbox_led3_layout.addWidget(self.u87_checkbox_led3, 1, 4)

        self.checkbox_led3_layout.addWidget(self.v1_24_checkbox_led3, 0, 5)
        self.checkbox_led3_layout.addWidget(self.v2_24_checkbox_led3, 1, 5)

        self.checkbox_led3_layout.addWidget(self.in1_checkbox_led3, 0, 6)
        self.checkbox_led3_layout.addWidget(self.in2_checkbox_led3, 1, 6)
        self.checkbox_led3_layout.addWidget(self.in3_checkbox_led3, 2, 6)

        self.checkbox_led3_layout.addWidget(self.notin1_checkbox_led3, 0, 7)
        self.checkbox_led3_layout.addWidget(self.notin2_checkbox_led3, 1, 7)
        self.checkbox_led3_layout.addWidget(self.notin3_checkbox_led3, 2, 7)

        self.checkbox_led3_layout.addItem(self.v_spacer, 5, 8)
        self.checkbox_led3_layout.addWidget(self.checkbox_led3_button, 5, 9)

        self.checkbox_led3_window.setLayout(self.checkbox_led3_layout)

        # make the check boxes
        self.checkbox_led4_window = QtWidgets.QScrollArea()
        self.checkbox_led4_window.setMinimumHeight(150)
        self.checkbox_led4_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_led4 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_led4 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_led4 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_led4 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_led4 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_led4 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_led4 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_led4 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_led4 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_led4 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_led4 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_led4 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_led4 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_led4 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_led4 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_led4 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_led4 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_led4 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_led4 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_led4 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_led4_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_led4_button.clicked.connect(partial(self.select_checkbox_button_clicked_led4, selected_str))

        self.checkbox_led4_layout.addWidget(self.trip_checkbox_led4, 0, 0)

        self.checkbox_led4_layout.addWidget(self.pb3_checkbox_led4, 0, 1)
        self.checkbox_led4_layout.addWidget(self.pb4_checkbox_led4, 1, 1)
        self.checkbox_led4_layout.addWidget(self.pb5_checkbox_led4, 2, 1)
        self.checkbox_led4_layout.addWidget(self.pb6_checkbox_led4, 3, 1)

        self.checkbox_led4_layout.addWidget(self.p50_checkbox_led4, 0, 2)
        self.checkbox_led4_layout.addWidget(self.n50_checkbox_led4, 1, 2)
        self.checkbox_led4_layout.addWidget(self.g50_checkbox_led4, 2, 2)

        self.checkbox_led4_layout.addWidget(self.p51_checkbox_led4, 0, 3)
        self.checkbox_led4_layout.addWidget(self.g51_checkbox_led4, 1, 3)

        self.checkbox_led4_layout.addWidget(self.r87_checkbox_led4, 0, 4)
        self.checkbox_led4_layout.addWidget(self.u87_checkbox_led4, 1, 4)

        self.checkbox_led4_layout.addWidget(self.v1_24_checkbox_led4, 0, 5)
        self.checkbox_led4_layout.addWidget(self.v2_24_checkbox_led4, 1, 5)

        self.checkbox_led4_layout.addWidget(self.in1_checkbox_led4, 0, 6)
        self.checkbox_led4_layout.addWidget(self.in2_checkbox_led4, 1, 6)
        self.checkbox_led4_layout.addWidget(self.in3_checkbox_led4, 2, 6)

        self.checkbox_led4_layout.addWidget(self.notin1_checkbox_led4, 0, 7)
        self.checkbox_led4_layout.addWidget(self.notin2_checkbox_led4, 1, 7)
        self.checkbox_led4_layout.addWidget(self.notin3_checkbox_led4, 2, 7)

        self.checkbox_led4_layout.addItem(self.v_spacer, 5, 8)

        self.checkbox_led4_layout.addWidget(self.checkbox_led4_button, 5, 9)

        self.checkbox_led4_window.setLayout(self.checkbox_led4_layout)
        
        ########
        self.led_layout.addWidget(self.led1_status)
        self.led_layout.addWidget(self.checkbox_led1_window)
        # self.led_layout.addWidget(self.led1_entry)

        self.led_layout.addWidget(self.led2_status)
        self.led_layout.addWidget(self.checkbox_led2_window)
        # self.led_layout.addWidget(self.led2_entry)

        self.led_layout.addWidget(self.led3_status)
        self.led_layout.addWidget(self.checkbox_led3_window)
        # self.led_layout.addWidget(self.led3_entry)

        self.led_layout.addWidget(self.led4_status)
        self.led_layout.addWidget(self.checkbox_led4_window)
        # self.led_layout.addWidget(self.led4_entry)
        self.led_tab.setLayout(self.led_layout)

        # TODO make OC settings
        self.output_contacts_tab = QtWidgets.QScrollArea()
        self.output_contacts_tab.setWidgetResizable(True)
        self.oc_layout = QtWidgets.QFormLayout()

        self.oc_1 = QtWidgets.QLabel("User Defined Logic Expression for Output Contact 1 (NO) Status")
        self.oc_1_entry = QtWidgets.QLineEdit()

        self.oc_2 = QtWidgets.QLabel("User Defined Logic Expression for Output Contact 2 (NO) Status")
        self.oc_2_entry = QtWidgets.QLineEdit()

        self.oc_3 = QtWidgets.QLabel("User Defined Logic Expression for Output Contact 3 (NO) Status")
        self.oc_3_entry = QtWidgets.QLineEdit()

        # make the check boxes
        self.checkbox_oc1_window = QtWidgets.QScrollArea()
        self.checkbox_oc1_window.setMinimumHeight(150)
        self.checkbox_oc1_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_oc1 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_oc1 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_oc1 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_oc1 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_oc1 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_oc1 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_oc1 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_oc1 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_oc1 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_oc1 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_oc1 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_oc1 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_oc1 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_oc1 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_oc1 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_oc1 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_oc1 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_oc1 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_oc1 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_oc1 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_oc1_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_oc1_button.clicked.connect(partial(self.select_checkbox_button_clicked_oc1, selected_str))

        self.checkbox_oc1_layout.addWidget(self.trip_checkbox_oc1, 0, 0)

        self.checkbox_oc1_layout.addWidget(self.pb3_checkbox_oc1, 0, 1)
        self.checkbox_oc1_layout.addWidget(self.pb4_checkbox_oc1, 1, 1)
        self.checkbox_oc1_layout.addWidget(self.pb5_checkbox_oc1, 2, 1)
        self.checkbox_oc1_layout.addWidget(self.pb6_checkbox_oc1, 3, 1)

        self.checkbox_oc1_layout.addWidget(self.p50_checkbox_oc1, 0, 2)
        self.checkbox_oc1_layout.addWidget(self.n50_checkbox_oc1, 1, 2)
        self.checkbox_oc1_layout.addWidget(self.g50_checkbox_oc1, 2, 2)

        self.checkbox_oc1_layout.addWidget(self.p51_checkbox_oc1, 0, 3)
        self.checkbox_oc1_layout.addWidget(self.g51_checkbox_oc1, 1, 3)

        self.checkbox_oc1_layout.addWidget(self.r87_checkbox_oc1, 0, 4)
        self.checkbox_oc1_layout.addWidget(self.u87_checkbox_oc1, 1, 4)

        self.checkbox_oc1_layout.addWidget(self.v1_24_checkbox_oc1, 0, 5)
        self.checkbox_oc1_layout.addWidget(self.v2_24_checkbox_oc1, 1, 5)

        self.checkbox_oc1_layout.addWidget(self.in1_checkbox_oc1, 0, 6)
        self.checkbox_oc1_layout.addWidget(self.in2_checkbox_oc1, 1, 6)
        self.checkbox_oc1_layout.addWidget(self.in3_checkbox_oc1, 2, 6)

        self.checkbox_oc1_layout.addWidget(self.notin1_checkbox_oc1, 0, 7)
        self.checkbox_oc1_layout.addWidget(self.notin2_checkbox_oc1, 1, 7)
        self.checkbox_oc1_layout.addWidget(self.notin3_checkbox_oc1, 2, 7)

        self.checkbox_oc1_layout.addItem(self.v_spacer, 5, 8)

        self.checkbox_oc1_layout.addWidget(self.checkbox_oc1_button, 5, 9)

        self.checkbox_oc1_window.setLayout(self.checkbox_oc1_layout)

        # make the check boxes
        self.checkbox_oc2_window = QtWidgets.QScrollArea()
        self.checkbox_oc2_window.setMinimumHeight(150)
        self.checkbox_oc2_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_oc2 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_oc2 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_oc2 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_oc2 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_oc2 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_oc2 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_oc2 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_oc2 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_oc2 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_oc2 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_oc2 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_oc2 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_oc2 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_oc2 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_oc2 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_oc2 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_oc2 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_oc2 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_oc2 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_oc2 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_oc2_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_oc2_button.clicked.connect(partial(self.select_checkbox_button_clicked_oc2, selected_str))

        self.checkbox_oc2_layout.addWidget(self.trip_checkbox_oc2, 0, 0)

        self.checkbox_oc2_layout.addWidget(self.pb3_checkbox_oc2, 0, 1)
        self.checkbox_oc2_layout.addWidget(self.pb4_checkbox_oc2, 1, 1)
        self.checkbox_oc2_layout.addWidget(self.pb5_checkbox_oc2, 2, 1)
        self.checkbox_oc2_layout.addWidget(self.pb6_checkbox_oc2, 3, 1)

        self.checkbox_oc2_layout.addWidget(self.p50_checkbox_oc2, 0, 2)
        self.checkbox_oc2_layout.addWidget(self.n50_checkbox_oc2, 1, 2)
        self.checkbox_oc2_layout.addWidget(self.g50_checkbox_oc2, 2, 2)

        self.checkbox_oc2_layout.addWidget(self.p51_checkbox_oc2, 0, 3)
        self.checkbox_oc2_layout.addWidget(self.g51_checkbox_oc2, 1, 3)

        self.checkbox_oc2_layout.addWidget(self.r87_checkbox_oc2, 0, 4)
        self.checkbox_oc2_layout.addWidget(self.u87_checkbox_oc2, 1, 4)

        self.checkbox_oc2_layout.addWidget(self.v1_24_checkbox_oc2, 0, 5)
        self.checkbox_oc2_layout.addWidget(self.v2_24_checkbox_oc2, 1, 5)

        self.checkbox_oc2_layout.addWidget(self.in1_checkbox_oc2, 0, 6)
        self.checkbox_oc2_layout.addWidget(self.in2_checkbox_oc2, 1, 6)
        self.checkbox_oc2_layout.addWidget(self.in3_checkbox_oc2, 2, 6)

        self.checkbox_oc2_layout.addWidget(self.notin1_checkbox_oc2, 0, 7)
        self.checkbox_oc2_layout.addWidget(self.notin2_checkbox_oc2, 1, 7)
        self.checkbox_oc2_layout.addWidget(self.notin3_checkbox_oc2, 2, 7)

        self.checkbox_oc2_layout.addItem(self.v_spacer, 5, 8)

        self.checkbox_oc2_layout.addWidget(self.checkbox_oc2_button, 5, 9)

        self.checkbox_oc2_window.setLayout(self.checkbox_oc2_layout)

        # make the check boxes
        self.checkbox_oc3_window = QtWidgets.QScrollArea()
        self.checkbox_oc3_window.setMinimumHeight(150)
        self.checkbox_oc3_layout = QtWidgets.QGridLayout()

        self.trip_checkbox_oc3 = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_oc3 = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_oc3 = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_oc3 = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_oc3 = QtWidgets.QCheckBox("PB6")

        self.p50_checkbox_oc3 = QtWidgets.QCheckBox("50P")
        self.n50_checkbox_oc3 = QtWidgets.QCheckBox("50N")
        self.g50_checkbox_oc3 = QtWidgets.QCheckBox("50G")

        self.p51_checkbox_oc3 = QtWidgets.QCheckBox("51P")
        self.g51_checkbox_oc3 = QtWidgets.QCheckBox("51G")

        self.r87_checkbox_oc3 = QtWidgets.QCheckBox("87R")
        self.u87_checkbox_oc3 = QtWidgets.QCheckBox("87U")

        self.v1_24_checkbox_oc3 = QtWidgets.QCheckBox("24V1")
        self.v2_24_checkbox_oc3 = QtWidgets.QCheckBox("24V2")

        self.in1_checkbox_oc3 = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_oc3 = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_oc3 = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_oc3 = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_oc3 = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_oc3 = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_oc3_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_oc3_button.clicked.connect(partial(self.select_checkbox_button_clicked_oc3, selected_str))

        self.checkbox_oc3_layout.addWidget(self.trip_checkbox_oc3, 0, 0)

        self.checkbox_oc3_layout.addWidget(self.pb3_checkbox_oc3, 0, 1)
        self.checkbox_oc3_layout.addWidget(self.pb4_checkbox_oc3, 1, 1)
        self.checkbox_oc3_layout.addWidget(self.pb5_checkbox_oc3, 2, 1)
        self.checkbox_oc3_layout.addWidget(self.pb6_checkbox_oc3, 3, 1)

        self.checkbox_oc3_layout.addWidget(self.p50_checkbox_oc3, 0, 2)
        self.checkbox_oc3_layout.addWidget(self.n50_checkbox_oc3, 1, 2)
        self.checkbox_oc3_layout.addWidget(self.g50_checkbox_oc3, 2, 2)

        self.checkbox_oc3_layout.addWidget(self.p51_checkbox_oc3, 0, 3)
        self.checkbox_oc3_layout.addWidget(self.g51_checkbox_oc3, 1, 3)

        self.checkbox_oc3_layout.addWidget(self.r87_checkbox_oc3, 0, 4)
        self.checkbox_oc3_layout.addWidget(self.u87_checkbox_oc3, 1, 4)

        self.checkbox_oc3_layout.addWidget(self.v1_24_checkbox_oc3, 0, 5)
        self.checkbox_oc3_layout.addWidget(self.v2_24_checkbox_oc3, 1, 5)

        self.checkbox_oc3_layout.addWidget(self.in1_checkbox_oc3, 0, 6)
        self.checkbox_oc3_layout.addWidget(self.in2_checkbox_oc3, 1, 6)
        self.checkbox_oc3_layout.addWidget(self.in3_checkbox_oc3, 2, 6)

        self.checkbox_oc3_layout.addWidget(self.notin1_checkbox_oc3, 0, 7)
        self.checkbox_oc3_layout.addWidget(self.notin2_checkbox_oc3, 1, 7)
        self.checkbox_oc3_layout.addWidget(self.notin3_checkbox_oc3, 2, 7)

        self.checkbox_oc3_layout.addItem(self.v_spacer, 5, 8)
        self.checkbox_oc3_layout.addWidget(self.checkbox_oc3_button, 5, 9)

        self.checkbox_oc3_window.setLayout(self.checkbox_oc3_layout)

        self.oc_layout.addWidget(self.oc_1)
        self.oc_layout.addWidget(self.checkbox_oc1_window)
        # self.oc_layout.addWidget(self.oc_1_entry)

        self.oc_layout.addWidget(self.oc_2)
        self.oc_layout.addWidget(self.checkbox_oc2_window)
        # self.oc_layout.addWidget(self.oc_2_entry)

        self.oc_layout.addWidget(self.oc_3)
        self.oc_layout.addWidget(self.checkbox_oc3_window)
        # self.oc_layout.addWidget(self.oc_3_entry)

        self.output_contacts_tab.setLayout(self.oc_layout)

        # TODO make Current Diff settings
        self.current_differential_tab = QtWidgets.QScrollArea()
        self.current_differential_tab.setWidgetResizable(True)
        self.cd_layout = QtWidgets.QFormLayout()

        self.rest_diff_current = QtWidgets.QLabel("Restrained Differential Pickup Current (Multiple of TAP)"
                                                  "(float 0.2-1.0)")
        self.rest_diff_current_entry = QtWidgets.QLineEdit()

        self.rest_diff_fir_slope = QtWidgets.QLabel("Restrained Differential First Slope (%) (float 5-100)")
        self.rest_diff_fir_slope_entry = QtWidgets.QLineEdit()

        self.rest_diff_scd_slope = QtWidgets.QLabel("Restrained Differential Second Slope (%) (float 10-200)")
        self.rest_diff_scd_slope_entry = QtWidgets.QLineEdit()

        self.rest_diff_slope_intersect = QtWidgets.QLabel("Restrained Differential, First and Second Slope "
                                                          "Intersection (Multiple of TAP) (float 1-16)")
        self.rest_diff_slope_intersect_entry = QtWidgets.QLineEdit()

        self.thresh_to_scd_harmonic = QtWidgets.QLabel("Threshold for Blocking due to 2nd Harmonic Content (%) (float "
                                                       "5-100 & OFF)")
        self.thresh_to_scd_harmonic_entry = QtWidgets.QLineEdit()

        self.thresh_to_fourth_harmonic = QtWidgets.QLabel("Threshold for Blocking due to 4th Harmonic Content (%) ("
                                                          "float 5-100 & OFF)")
        self.thresh_to_fourth_harmonic_entry = QtWidgets.QLineEdit()

        self.thresh_to_fifth_harmonic = QtWidgets.QLabel("Threshold for Blocking due to 5th Harmonic Content (%) ("
                                                         "float 5-100 & OFF)")
        self.thresh_to_fifth_harmonic_entry = QtWidgets.QLineEdit()

        self.unrest_diff_pickup_current = QtWidgets.QLabel("Unrestrained Differential Pickup Current (Multiple of "
                                                           "TAP) (float 1.0-16.0)")
        self.unrest_diff_pickup_current_entry = QtWidgets.QLineEdit()

        self.current_diff_enable = QtWidgets.QLabel("Current Differential Enable Equation")
        self.current_diff_enable_entry = QtWidgets.QLineEdit()

        # make the check boxes
        self.checkbox_curr_diff_enable_eq_window = QtWidgets.QScrollArea()
        self.checkbox_curr_diff_enable_eq_window.setMinimumHeight(150)
        self.checkbox_curr_diff_enable_eq_layout = QtWidgets.QGridLayout()

        # self.trip_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("Trip")

        self.pb3_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("PB3")
        self.pb4_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("PB4")
        self.pb5_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("PB5")
        self.pb6_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("PB6")


        self.in1_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("IN1")
        self.in2_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("IN2")
        self.in3_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("IN3")

        self.notin1_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("NOTIN1")
        self.notin2_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("NOTIN2")
        self.notin3_checkbox_curr_diff_enable_eq = QtWidgets.QCheckBox("NOTIN3")

        self.checkbox_curr_diff_enable_eq_button = QtWidgets.QPushButton("Select Checkboxes...")

        selected_str = ""
        self.checkbox_curr_diff_enable_eq_button.clicked.connect(partial(self.select_checkbox_button_clicked_curr_diff_enable_eq, selected_str))

        # self.checkbox_curr_diff_enable_eq_layout.addWidget(self.trip_checkbox_curr_diff_enable_eq, 0, 0)

        # self.v_spacer = QtWidgets.QSpacerItem(0, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.pb3_checkbox_curr_diff_enable_eq, 0, 0)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.pb4_checkbox_curr_diff_enable_eq, 1, 0)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.pb5_checkbox_curr_diff_enable_eq, 2, 0)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.pb6_checkbox_curr_diff_enable_eq, 3, 0)

        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.in1_checkbox_curr_diff_enable_eq, 0, 1)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.in2_checkbox_curr_diff_enable_eq, 1, 1)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.in3_checkbox_curr_diff_enable_eq, 2, 1)

        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.notin1_checkbox_curr_diff_enable_eq, 0, 2)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.notin2_checkbox_curr_diff_enable_eq, 1, 2)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.notin3_checkbox_curr_diff_enable_eq, 2, 2)

        self.checkbox_curr_diff_enable_eq_layout.addItem(self.v_spacer, 4, 3)
        self.checkbox_curr_diff_enable_eq_layout.addWidget(self.checkbox_curr_diff_enable_eq_button, 4, 4)

        self.checkbox_curr_diff_enable_eq_window.setLayout(self.checkbox_curr_diff_enable_eq_layout)

        self.cd_layout.addWidget(self.rest_diff_current)
        self.cd_layout.addWidget(self.rest_diff_current_entry)

        self.cd_layout.addWidget(self.rest_diff_fir_slope)
        self.cd_layout.addWidget(self.rest_diff_fir_slope_entry)

        self.cd_layout.addWidget(self.rest_diff_scd_slope)
        self.cd_layout.addWidget(self.rest_diff_scd_slope_entry)

        self.cd_layout.addWidget(self.rest_diff_slope_intersect)
        self.cd_layout.addWidget(self.rest_diff_slope_intersect_entry)

        self.cd_layout.addWidget(self.thresh_to_scd_harmonic)
        self.cd_layout.addWidget(self.thresh_to_scd_harmonic_entry)

        self.cd_layout.addWidget(self.thresh_to_fourth_harmonic)
        self.cd_layout.addWidget(self.thresh_to_fourth_harmonic_entry)

        self.cd_layout.addWidget(self.thresh_to_fifth_harmonic)
        self.cd_layout.addWidget(self.thresh_to_fifth_harmonic_entry)

        self.cd_layout.addWidget(self.unrest_diff_pickup_current)
        self.cd_layout.addWidget(self.unrest_diff_pickup_current_entry)

        self.cd_layout.addWidget(self.current_diff_enable)
        self.cd_layout.addWidget(self.checkbox_curr_diff_enable_eq_window)
        # self.cd_layout.addWidget(self.current_diff_enable_entry)

        self.current_differential_tab.setLayout(self.cd_layout)

        # TODO make w_winding settings
        self.w_winding_tab = QtWidgets.QScrollArea()
        self.w_winding_tab.setWidgetResizable(True)
        self.w_winding_tab.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ww_layout = QtWidgets.QVBoxLayout()

        # phase setup
        self.w_winding_group1 = QtWidgets.QGroupBox()
        self.w_winding_group1.setTitle("Phase")
        self.w_winding_group1_layout = QtWidgets.QVBoxLayout()

        self.w_winding_group1_oc_pickup = QtWidgets.QLabel(
            "W-Winding, Instantaneous Phase Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.w_winding_group1_oc_pickup_entry = QtWidgets.QLineEdit()

        self.w_winding_group1_oc_delay = QtWidgets.QLabel(
            "W-Winding, Instantaneous Phase Overcurrent Delay (Cycles)(float 0-16000)")
        self.w_winding_group1_oc_delay_entry = QtWidgets.QLineEdit()

        self.w_winding_group1_oc_time_inverse = QtWidgets.QLabel(
            "W-Winding, Time Inverse Phase Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        self.w_winding_group1_oc_time_inverse_entry = QtWidgets.QLineEdit()

        self.w_winding_group1_curve_style = QtWidgets.QLabel(
            "W-Winding, Time Inverse Phase Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        self.w_winding_group1_curve_style_cb = QComboBox()
        self.w_winding_group1_curve_style_cb.setMinimumHeight(20)
        self.w_winding_group1_curve_style_cb.addItem("U1")
        self.w_winding_group1_curve_style_cb.addItem("U2")
        self.w_winding_group1_curve_style_cb.addItem("U3")
        self.w_winding_group1_curve_style_cb.addItem("U4")
        self.w_winding_group1_curve_style_cb.addItem("U5")

        self.w_winding_group1_time_dial = QtWidgets.QLabel(
            "W-Winding, Time Inverse Phase Overcurrent Time Dial (float 0.5-15.0)")
        self.w_winding_group1_time_dial_entry = QtWidgets.QLineEdit()

        self.w_winding_group1_electro_reset = QtWidgets.QLabel(
            "W-Winding, Time Inverse Phase Overcurrent Electromechanical Reset (YES, NO)")
        self.w_winding_group1_electro_reset_cb = QComboBox()
        self.w_winding_group1_electro_reset_cb.setMinimumHeight(20)
        self.w_winding_group1_electro_reset_cb.addItem("YES")
        self.w_winding_group1_electro_reset_cb.addItem("NO")

        # self.w_winding_group1_neutral_enable_eq = QtWidgets.QLabel(
        #     "W_Winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.w_winding_group1_neutral_enable_eq_entry = QtWidgets.QLineEdit()

        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_pickup)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_pickup_entry)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_delay)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_delay_entry)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_time_inverse)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_oc_time_inverse_entry)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_curve_style)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_curve_style_cb)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_time_dial)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_time_dial_entry)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_electro_reset)
        self.w_winding_group1_layout.addWidget(self.w_winding_group1_electro_reset_cb)
        # self.w_winding_group1_layout.addWidget(self.w_winding_group1_neutral_enable_eq)
        # self.w_winding_group1_layout.addWidget(self.w_winding_group1_neutral_enable_eq_entry)

        # # group 2 setup
        self.w_winding_group2 = QtWidgets.QGroupBox()
        self.w_winding_group2.setTitle("Neutral")
        self.w_winding_group2_layout = QtWidgets.QVBoxLayout()

        self.w_winding_group2_oc_pickup = QtWidgets.QLabel(
            "W-Winding, Instantaneous Neutral Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.w_winding_group2_oc_pickup_entry = QtWidgets.QLineEdit()

        self.w_winding_group2_oc_delay = QtWidgets.QLabel(
            "W-Winding, Instantaneous Neutral Overcurrent Delay (Cycles)(float 0-16000)")
        self.w_winding_group2_oc_delay_entry = QtWidgets.QLineEdit()

        # self.w_winding_group2_oc_time_inverse = QtWidgets.QLabel(
        #     "W-Winding, Time Inverse Neutral Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        # self.w_winding_group2_oc_time_inverse_entry = QtWidgets.QLineEdit()
        #
        # self.w_winding_group2_curve_style = QtWidgets.QLabel(
        #     "W-Winding, Time Inverse Neutral Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        # self.w_winding_group2_curve_style_cb = QComboBox()
        # self.w_winding_group2_curve_style_cb.setMinimumHeight(40)
        # self.w_winding_group2_curve_style_cb.addItem("U1")
        # self.w_winding_group2_curve_style_cb.addItem("U2")
        # self.w_winding_group2_curve_style_cb.addItem("U3")
        # self.w_winding_group2_curve_style_cb.addItem("U4")
        # self.w_winding_group2_curve_style_cb.addItem("U5")

        # self.w_winding_group2_time_dial = QtWidgets.QLabel(
        #     "W-Winding, Time Inverse Neutral Overcurrent Time Dial (float 0.5-15.0)")
        # self.w_winding_group2_time_dial_entry = QtWidgets.QLineEdit()
        # #
        # self.w_winding_group2_electro_reset = QtWidgets.QLabel(
        #     "W-Winding, Time Inverse Neutral Overcurrent Electromechanical Reset (YES, NO)")
        # self.w_winding_group2_electro_reset_cb = QComboBox()
        # self.w_winding_group2_electro_reset_cb.setMinimumHeight(40)
        # self.w_winding_group2_electro_reset_cb.addItem("YES")
        # self.w_winding_group2_electro_reset_cb.addItem("NO")
        # #
        # self.w_winding_group2_neutral_enable_eq = QtWidgets.QLabel(
        #     "W_Winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.w_winding_group2_neutral_enable_eq_entry = QtWidgets.QLineEdit()
        #
        self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_pickup)
        self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_pickup_entry)
        self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_delay)
        self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_delay_entry)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_time_inverse)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_oc_time_inverse_entry)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_curve_style)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_curve_style_cb)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_time_dial)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_time_dial_entry)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_electro_reset)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_electro_reset_cb)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_neutral_enable_eq)
        # self.w_winding_group2_layout.addWidget(self.w_winding_group2_neutral_enable_eq_entry)

        # # group 3 setup
        self.w_winding_group3 = QtWidgets.QGroupBox()
        self.w_winding_group3.setTitle("Ground")
        self.w_winding_group3_layout = QtWidgets.QVBoxLayout()

        self.w_winding_group3_oc_pickup = QtWidgets.QLabel(
            "W-Winding, Instantaneous Ground Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.w_winding_group3_oc_pickup_entry = QtWidgets.QLineEdit()

        self.w_winding_group3_oc_delay = QtWidgets.QLabel(
            "W-Winding, Instantaneous Ground Overcurrent Delay (Cycles)(float 0-16000)")
        self.w_winding_group3_oc_delay_entry = QtWidgets.QLineEdit()

        self.w_winding_group3_oc_time_inverse = QtWidgets.QLabel(
            "W-Winding, Time Inverse Ground Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        self.w_winding_group3_oc_time_inverse_entry = QtWidgets.QLineEdit()

        self.w_winding_group3_curve_style = QtWidgets.QLabel(
            "W-Winding, Time Inverse Ground Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        self.w_winding_group3_curve_style_cb = QComboBox()
        self.w_winding_group3_curve_style_cb.setMinimumHeight(20)
        self.w_winding_group3_curve_style_cb.addItem("U1")
        self.w_winding_group3_curve_style_cb.addItem("U2")
        self.w_winding_group3_curve_style_cb.addItem("U3")
        self.w_winding_group3_curve_style_cb.addItem("U4")
        self.w_winding_group3_curve_style_cb.addItem("U5")

        self.w_winding_group3_time_dial = QtWidgets.QLabel(
            "W-Winding, Time Inverse Ground Overcurrent Time Dial (float 0.5-15.0)")
        self.w_winding_group3_time_dial_entry = QtWidgets.QLineEdit()

        self.w_winding_group3_electro_reset = QtWidgets.QLabel(
            "W-Winding, Time Inverse Ground Overcurrent Electromechanical Reset (YES, NO)")
        self.w_winding_group3_electro_reset_cb = QComboBox()
        self.w_winding_group3_electro_reset_cb.setMinimumHeight(20)
        self.w_winding_group3_electro_reset_cb.addItem("YES")
        self.w_winding_group3_electro_reset_cb.addItem("NO")
        #
        # self.w_winding_group3_neutral_enable_eq = QtWidgets.QLabel(
        #     "W_Winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.w_winding_group3_neutral_enable_eq_entry = QtWidgets.QLineEdit()
        #
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_pickup)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_pickup_entry)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_delay)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_delay_entry)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_time_inverse)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_oc_time_inverse_entry)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_curve_style)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_curve_style_cb)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_time_dial)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_time_dial_entry)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_electro_reset)
        self.w_winding_group3_layout.addWidget(self.w_winding_group3_electro_reset_cb)
        # self.w_winding_group3_layout.addWidget(self.w_winding_group3_neutral_enable_eq)
        # self.w_winding_group3_layout.addWidget(self.w_winding_group3_neutral_enable_eq_entry)

        # set up all the layouts for each group and add to the scroll frame
        self.w_winding_group1.setLayout(self.w_winding_group1_layout)
        self.w_winding_group2.setLayout(self.w_winding_group2_layout)
        self.w_winding_group3.setLayout(self.w_winding_group3_layout)
        self.ww_layout.addWidget(self.w_winding_group1)
        self.ww_layout.addWidget(self.w_winding_group2)
        self.ww_layout.addWidget(self.w_winding_group3)

        self.w_winding_tab.setLayout(self.ww_layout)

        # TODO make x_winding settings
        self.x_winding_tab = QtWidgets.QScrollArea()
        self.x_winding_tab.setWidgetResizable(True)
        self.x_winding_tab.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.xw_layout = QtWidgets.QVBoxLayout()

        # phase setup
        self.x_winding_group1 = QtWidgets.QGroupBox()
        self.x_winding_group1.setTitle("Phase")
        self.x_winding_group1_layout = QtWidgets.QVBoxLayout()

        self.x_winding_group1_oc_pickup = QtWidgets.QLabel(
            "X-Winding, Instantaneous Phase Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.x_winding_group1_oc_pickup_entry = QtWidgets.QLineEdit()

        self.x_winding_group1_oc_delay = QtWidgets.QLabel(
            "X-Winding, Instantaneous Phase Overcurrent Delay (Cycles)(float 0-16000)")
        self.x_winding_group1_oc_delay_entry = QtWidgets.QLineEdit()

        self.x_winding_group1_oc_time_inverse = QtWidgets.QLabel(
            "X-Winding, Time Inverse Phase Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        self.x_winding_group1_oc_time_inverse_entry = QtWidgets.QLineEdit()

        self.x_winding_group1_curve_style = QtWidgets.QLabel(
            "X-Winding, Time Inverse Phase Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        self.x_winding_group1_curve_style_cb = QComboBox()
        self.x_winding_group1_curve_style_cb.setMinimumHeight(20)
        self.x_winding_group1_curve_style_cb.addItem("U1")
        self.x_winding_group1_curve_style_cb.addItem("U2")
        self.x_winding_group1_curve_style_cb.addItem("U3")
        self.x_winding_group1_curve_style_cb.addItem("U4")
        self.x_winding_group1_curve_style_cb.addItem("U5")

        self.x_winding_group1_time_dial = QtWidgets.QLabel(
            "X-Winding, Time Inverse Phase Overcurrent Time Dial (float 0.5-15.0)")
        self.x_winding_group1_time_dial_entry = QtWidgets.QLineEdit()

        self.x_winding_group1_electro_reset = QtWidgets.QLabel(
            "X-Winding, Time Inverse Phase Overcurrent Electromechanical Reset (YES, NO)")
        self.x_winding_group1_electro_reset_cb = QComboBox()
        self.x_winding_group1_electro_reset_cb.setMinimumHeight(20)
        self.x_winding_group1_electro_reset_cb.addItem("YES")
        self.x_winding_group1_electro_reset_cb.addItem("NO")

        # self.x_winding_group1_neutral_enable_eq = QtWidgets.QLabel(
        #     "x_winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.x_winding_group1_neutral_enable_eq_entry = QtWidgets.QLineEdit()

        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_pickup)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_pickup_entry)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_delay)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_delay_entry)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_time_inverse)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_oc_time_inverse_entry)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_curve_style)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_curve_style_cb)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_time_dial)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_time_dial_entry)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_electro_reset)
        self.x_winding_group1_layout.addWidget(self.x_winding_group1_electro_reset_cb)
        # self.x_winding_group1_layout.addWidget(self.x_winding_group1_neutral_enable_eq)
        # self.x_winding_group1_layout.addWidget(self.x_winding_group1_neutral_enable_eq_entry)

        # # group 2 setup
        self.x_winding_group2 = QtWidgets.QGroupBox()
        self.x_winding_group2.setTitle("Neutral")
        self.x_winding_group2_layout = QtWidgets.QVBoxLayout()

        self.x_winding_group2_oc_pickup = QtWidgets.QLabel(
            "X-Winding, Instantaneous Neutral Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.x_winding_group2_oc_pickup_entry = QtWidgets.QLineEdit()

        self.x_winding_group2_oc_delay = QtWidgets.QLabel(
            "X-Winding, Instantaneous Neutral Overcurrent Delay (Cycles)(float 0-16000)")
        self.x_winding_group2_oc_delay_entry = QtWidgets.QLineEdit()

        # self.x_winding_group2_oc_time_inverse = QtWidgets.QLabel(
        #     "X-Winding, Time Inverse Neutral Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        # self.x_winding_group2_oc_time_inverse_entry = QtWidgets.QLineEdit()
        #
        # self.x_winding_group2_curve_style = QtWidgets.QLabel(
        #     "X-Winding, Time Inverse Neutral Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        # self.x_winding_group2_curve_style_cb = QComboBox()
        # self.x_winding_group2_curve_style_cb.setMinimumHeight(40)
        # self.x_winding_group2_curve_style_cb.addItem("U1")
        # self.x_winding_group2_curve_style_cb.addItem("U2")
        # self.x_winding_group2_curve_style_cb.addItem("U3")
        # self.x_winding_group2_curve_style_cb.addItem("U4")
        # self.x_winding_group2_curve_style_cb.addItem("U5")

        # self.x_winding_group2_time_dial = QtWidgets.QLabel(
        #     "X-Winding, Time Inverse Neutral Overcurrent Time Dial (float 0.5-15.0)")
        # self.x_winding_group2_time_dial_entry = QtWidgets.QLineEdit()
        # #
        # self.x_winding_group2_electro_reset = QtWidgets.QLabel(
        #     "X-Winding, Time Inverse Neutral Overcurrent Electromechanical Reset (YES, NO)")
        # self.x_winding_group2_electro_reset_cb = QComboBox()
        # self.x_winding_group2_electro_reset_cb.setMinimumHeight(40)
        # self.x_winding_group2_electro_reset_cb.addItem("YES")
        # self.x_winding_group2_electro_reset_cb.addItem("NO")
        # #
        # self.x_winding_group2_neutral_enable_eq = QtWidgets.QLabel(
        #     "x_winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.x_winding_group2_neutral_enable_eq_entry = QtWidgets.QLineEdit()
        #
        self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_pickup)
        self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_pickup_entry)
        self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_delay)
        self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_delay_entry)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_time_inverse)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_oc_time_inverse_entry)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_curve_style)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_curve_style_cb)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_time_dial)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_time_dial_entry)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_electro_reset)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_electro_reset_cb)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_neutral_enable_eq)
        # self.x_winding_group2_layout.addWidget(self.x_winding_group2_neutral_enable_eq_entry)

        # # group 3 setup
        self.x_winding_group3 = QtWidgets.QGroupBox()
        self.x_winding_group3.setTitle("Ground")
        self.x_winding_group3_layout = QtWidgets.QVBoxLayout()

        self.x_winding_group3_oc_pickup = QtWidgets.QLabel(
            "X-Winding, Instantaneous Ground Overcurrent Pickup (Secondary Amps)(float 0.5-80)")
        self.x_winding_group3_oc_pickup_entry = QtWidgets.QLineEdit()

        self.x_winding_group3_oc_delay = QtWidgets.QLabel(
            "X-Winding, Instantaneous Ground Overcurrent Delay (Cycles)(float 0-16000)")
        self.x_winding_group3_oc_delay_entry = QtWidgets.QLineEdit()

        self.x_winding_group3_oc_time_inverse = QtWidgets.QLabel(
            "X-Winding, Time Inverse Ground Overcurrent Pickup (Secondary Amps)(float 0.5-16)")
        self.x_winding_group3_oc_time_inverse_entry = QtWidgets.QLineEdit()

        self.x_winding_group3_curve_style = QtWidgets.QLabel(
            "X-Winding, Time Inverse Ground Overcurrent Curve Style (U.S. Curves)(U1, U2, U3, U4, U5)")
        self.x_winding_group3_curve_style_cb = QComboBox()
        self.x_winding_group3_curve_style_cb.setMinimumHeight(20)
        self.x_winding_group3_curve_style_cb.addItem("U1")
        self.x_winding_group3_curve_style_cb.addItem("U2")
        self.x_winding_group3_curve_style_cb.addItem("U3")
        self.x_winding_group3_curve_style_cb.addItem("U4")
        self.x_winding_group3_curve_style_cb.addItem("U5")

        self.x_winding_group3_time_dial = QtWidgets.QLabel(
            "X-Winding, Time Inverse Ground Overcurrent Time Dial (float 0.5-15.0)")
        self.x_winding_group3_time_dial_entry = QtWidgets.QLineEdit()

        self.x_winding_group3_electro_reset = QtWidgets.QLabel(
            "X-Winding, Time Inverse Ground Overcurrent Electromechanical Reset (YES, NO)")
        self.x_winding_group3_electro_reset_cb = QComboBox()
        self.x_winding_group3_electro_reset_cb.setMinimumHeight(20)
        self.x_winding_group3_electro_reset_cb.addItem("YES")
        self.x_winding_group3_electro_reset_cb.addItem("NO")
        #
        # self.x_winding_group3_neutral_enable_eq = QtWidgets.QLabel(
        #     "x_winding, Time Inverse Neutral Overcurrent Enable Equation ")
        # self.x_winding_group3_neutral_enable_eq_entry = QtWidgets.QLineEdit()
        #
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_pickup)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_pickup_entry)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_delay)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_delay_entry)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_time_inverse)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_oc_time_inverse_entry)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_curve_style)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_curve_style_cb)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_time_dial)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_time_dial_entry)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_electro_reset)
        self.x_winding_group3_layout.addWidget(self.x_winding_group3_electro_reset_cb)
        # self.x_winding_group3_layout.addWidget(self.x_winding_group3_neutral_enable_eq)
        # self.x_winding_group3_layout.addWidget(self.x_winding_group3_neutral_enable_eq_entry)

        # set up all the layouts for each group and add to the scroll frame
        self.x_winding_group1.setLayout(self.x_winding_group1_layout)
        self.x_winding_group2.setLayout(self.x_winding_group2_layout)
        self.x_winding_group3.setLayout(self.x_winding_group3_layout)
        self.xw_layout.addWidget(self.x_winding_group1)
        self.xw_layout.addWidget(self.x_winding_group2)
        self.xw_layout.addWidget(self.x_winding_group3)

        self.x_winding_tab.setLayout(self.xw_layout)

        # TODO make volts/hz settings
        self.volts_hertz_tab = QtWidgets.QScrollArea()
        self.volts_hertz_tab.setWidgetResizable(True)
        self.volts_hz_layout = QtWidgets.QFormLayout()

        self.volts_hz_level1_pickup = QtWidgets.QLabel("Volts/Hz Level 1 Pickup (%) (float 100-200)")
        self.volts_hz_level1_pickup_entry = QtWidgets.QLineEdit()

        self.volts_hz_level1_time_delay = QtWidgets.QLabel("Volts/Hz Level 1 Time Delay (Cycles) (float 0.04-400)")
        self.volts_hz_level1_time_delay_entry = QtWidgets.QLineEdit()

        self.volts_hz_level2_pickup = QtWidgets.QLabel("Volts/Hz Level 2 Pickup (%) (float 100-200)")
        self.volts_hz_level2_pickup_entry = QtWidgets.QLineEdit()

        self.volts_hz_level2_time_delay = QtWidgets.QLabel("Volts/Hz Level 2 Time Delay (Cycles) (float 0.04-400)")
        self.volts_hz_level2_time_delay_entry = QtWidgets.QLineEdit()

        self.volts_hz_layout.addWidget(self.volts_hz_level1_pickup)
        self.volts_hz_layout.addWidget(self.volts_hz_level1_pickup_entry)
        self.volts_hz_layout.addWidget(self.volts_hz_level1_time_delay)
        self.volts_hz_layout.addWidget(self.volts_hz_level1_time_delay_entry)
        self.volts_hz_layout.addWidget(self.volts_hz_level2_pickup)
        self.volts_hz_layout.addWidget(self.volts_hz_level2_pickup_entry)
        self.volts_hz_layout.addWidget(self.volts_hz_level2_time_delay)
        self.volts_hz_layout.addWidget(self.volts_hz_level2_time_delay_entry)

        self.volts_hertz_tab.setLayout(self.volts_hz_layout)

        # TODO create buttons to save and load settings and push to phatcat
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout2 = QtWidgets.QHBoxLayout()
        # save_file = QtGui.QActionEvent("Save File")

        self.set_port_entry = QtWidgets.QLineEdit()
        # self.set_port_entry.setGeometry(7, 10, 10, 7)
        self.set_port_entry.setMaximumWidth(100)
        # self.set_port_button = QtWidgets.QPushButton("Set Com Port")
        self.set_port_button_label = QtWidgets.QLabel("Set Com Port")
        # self.set_port_button.clicked.connect(self.on_set_port_button_clicked)

        self.save_button = QtWidgets.QPushButton("Save File")
        self.save_button.clicked.connect(self.on_save_button_clicked)

        self.load_button = QtWidgets.QPushButton("Load File")
        self.load_button.clicked.connect(self.on_load_button_clicked)

        self.push_settings_button = QtWidgets.QPushButton("Push Settings to PHATCAT")
        self.push_settings_button.clicked.connect(self.on_push_button_clicked)

        self.pull_settings_button = QtWidgets.QPushButton("Pull Settings from PHATCAT")
        self.pull_settings_button.clicked.connect(self.on_pull_settings_button_clicked)

        self.h_spacer = QtWidgets.QSpacerItem(50, 50, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.button_layout.addItem(self.h_spacer)

        self.h2_spacer = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.PHATCAT_pic = QtWidgets.QLabel()
        self.PHATCAT_pic.setPixmap(self.pixmap)

        # self.button_layout.addWidget(self.set_port_button)
        self.button_layout.addWidget(self.PHATCAT_pic)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.load_button)
        # self.button_layout2.addWidget(self.PHATCAT_pic)
        self.button_layout2.addItem(self.h2_spacer)
        self.button_layout2.addWidget(self.set_port_button_label)
        self.button_layout2.addWidget(self.set_port_entry)
        self.button_layout2.addWidget(self.push_settings_button)
        self.button_layout2.addWidget(self.pull_settings_button)

        self.tabs.addTab(self.eq_data_tab, "Equipment Data")
        self.tabs.addTab(self.led_tab, "LED Indicators")
        self.tabs.addTab(self.output_contacts_tab, "Output Contacts")
        self.tabs.addTab(self.current_differential_tab, "Current Differential")
        self.tabs.addTab(self.w_winding_tab, "W-Winding Overcurrent")
        self.tabs.addTab(self.x_winding_tab, "X-Winding Overcurrent")
        self.tabs.addTab(self.volts_hertz_tab, "Volts/Hz Element")

        # set the layout and add all the widgets to it
        self.layout = QtWidgets.QVBoxLayout()
        self.tab1_layout = QtWidgets.QGridLayout()
        # self.tab1_layout.addWidget(self.eq_data_tab)
        # self.tab1_layout.addWidget(self.eq_data_tab, 0, 1)
        # self.anchor = QtWidgets.QGraphicsAnchorLayout.addAnchor(self.layout, self.menu_list, Qt.AnchorLeft, self.eq_data_tab, Qt.Anchor)
        # self.layout.addWidget(self.menu_list, 0, 0, alignment=QtCore.Qt.AlignTop)
        self.layout.addWidget(self.tabs)
        self.layout.addLayout(self.button_layout)
        self.layout.addLayout(self.button_layout2)

        self.setLayout(self.layout)

    def select_checkbox_button_clicked_led1(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_led1.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_led1.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_led1.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_led1.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_led1.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_led1.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_led1.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_led1.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_led1.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_led1.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_led1.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_led1.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_led1.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_led1.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_led1.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_led1.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_led1.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_led1.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_led1.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_led1.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.led1_entry.setText(sent_str)

    def select_checkbox_button_clicked_led2(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_led2.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_led2.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_led2.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_led2.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_led2.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_led2.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_led2.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_led2.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_led2.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_led2.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_led2.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_led2.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_led2.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_led2.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_led2.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_led2.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_led2.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_led2.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_led2.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_led2.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.led2_entry.setText(sent_str)

    def select_checkbox_button_clicked_led3(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_led3.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_led3.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_led3.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_led3.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_led3.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_led3.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_led3.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_led3.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_led3.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_led3.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_led3.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_led3.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_led3.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_led3.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_led3.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_led3.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_led3.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_led3.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_led3.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_led3.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.led3_entry.setText(sent_str)

    def select_checkbox_button_clicked_led4(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_led4.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_led4.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_led4.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_led4.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_led4.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_led4.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_led4.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_led4.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_led4.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_led4.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_led4.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_led4.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_led4.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_led4.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_led4.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_led4.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_led4.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_led4.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_led4.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_led4.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.led4_entry.setText(sent_str)

    def select_checkbox_button_clicked_oc1(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_oc1.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_oc1.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_oc1.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_oc1.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_oc1.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_oc1.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_oc1.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_oc1.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_oc1.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_oc1.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_oc1.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_oc1.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_oc1.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_oc1.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_oc1.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_oc1.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_oc1.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_oc1.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_oc1.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_oc1.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.oc_1_entry.setText(sent_str)

    def select_checkbox_button_clicked_oc2(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_oc2.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_oc2.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_oc2.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_oc2.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_oc2.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_oc2.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_oc2.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_oc2.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_oc2.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_oc2.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_oc2.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_oc2.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_oc2.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_oc2.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_oc2.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_oc2.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_oc2.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_oc2.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_oc2.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_oc2.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.oc_2_entry.setText(sent_str)

    def select_checkbox_button_clicked_oc3(self, sent_str):

        sent_str = ""
        if self.trip_checkbox_oc3.checkState():
            sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_oc3.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_oc3.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_oc3.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_oc3.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        if self.p50_checkbox_oc3.checkState():
            sent_str = sent_str + "FIFTYP" + ":"

        if self.n50_checkbox_oc3.checkState():
            sent_str = sent_str + "FIFTYN" + ":"

        if self.g50_checkbox_oc3.checkState():
            sent_str = sent_str + "FIFTYG" + ":"

        if self.p51_checkbox_oc3.checkState():
            sent_str = sent_str + "PFIFTYONE" + ":"

        if self.g51_checkbox_oc3.checkState():
            sent_str = sent_str + "FIFTYONEG" + ":"

        if self.r87_checkbox_oc3.checkState():
            sent_str = sent_str + "EIGHTYSEVENR" + ":"

        if self.u87_checkbox_oc3.checkState():
            sent_str = sent_str + "EIGHTYSEVENU" + ":"

        if self.v1_24_checkbox_oc3.checkState():
            sent_str = sent_str + "TWENTYFOURVONE" + ":"

        if self.v2_24_checkbox_oc3.checkState():
            sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_oc3.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_oc3.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_oc3.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_oc3.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_oc3.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_oc3.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.oc_3_entry.setText(sent_str)

    def select_checkbox_button_clicked_curr_diff_enable_eq(self, sent_str):

        sent_str = ""
        # if self.trip_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "TRIP" + ":"

        if self.pb3_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "PBTHREE" + ":"

        if self.pb4_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "PBFOUR" + ":"

        if self.pb5_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "PBFIVE" + ":"

        if self.pb6_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "PBSIX" + ":"

        # if self.p50_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "FIFTYP" + ":"
        #
        # if self.n50_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "FIFTYN" + ":"
        #
        # if self.g50_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "FIFTYG" + ":"
        #
        # if self.p51_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "PFIFTYONE" + ":"
        #
        # if self.g51_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "FIFTYONEG" + ":"
        #
        # if self.r87_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "EIGHTYSEVENR" + ":"
        #
        # if self.u87_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "EIGHTYSEVENU" + ":"
        #
        # if self.v1_24_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "TWENTYFOURVONE" + ":"
        #
        # if self.v2_24_checkbox_curr_diff_enable_eq.checkState():
        #     sent_str = sent_str + "TWENTYFOURVTWO" + ":"

        if self.in1_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "INONE" + ":"

        if self.in2_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "INTWO" + ":"

        if self.in3_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "INTHREE" + ":"

        if self.notin1_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "NOTINONE" + ":"

        if self.notin2_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "NOTINTWO" + ":"

        if self.notin3_checkbox_curr_diff_enable_eq.checkState():
            sent_str = sent_str + "NOTINTHREE" + ":"

        # print(self.selected_str)
        self.current_diff_enable_entry.setText(sent_str)

    # pad strings with # so I can have exact size
    def pad_with_hash(self, input_str):
        length: int = len(input_str)
        padded_str = ""
        padding = MAX_CHAR_SIZE - length
        if input_str is '':
            input_str = "Empty"
        if length < MAX_CHAR_SIZE:
            padded_str = input_str.ljust(padding + len(input_str), '#')
        # print(len(padded_str))
        return padded_str

    # method to pad numbers with a zero before them so I can have exact size
    def pad_dat_number(self, input_num):
        length: int = len(input_num)
        padded_num = ""
        padding = MAX_NUM_SIZE - length
        if length < MAX_NUM_SIZE:
            padded_num = input_num.rjust(padding + len(input_num), '0')
        else:
            padded_num = input_num
        return padded_num

    # TODO make method to get the information housed in the various text boxes
    # eq data settings
    def get_relay_name(self):
        relay_name_str = self.pad_with_hash(self.relay_name_entry.text())
        return relay_name_str

    def get_trans_nameplate(self):
        trans_nameplate_str = self.pad_dat_number(self.trans_nameplate_entry.text())
        return trans_nameplate_str

    def get_sys_nom_freq(self):
        sys_nom_str = self.pad_dat_number(self.sys_nom_freq_entry.text())
        return sys_nom_str

    def get_winding(self):
        winding_str = self.pad_with_hash(str(self.source_side_winding_cb.currentText()))
        return winding_str

    def get_trans_connect_type(self):
        connection_type_str = self.pad_with_hash((str(self.trans_connect_type_cb.currentText())))
        return connection_type_str

    def get_w_winding_volt_rate(self):
        w_wind_volt_rate_str = self.pad_dat_number(self.w_winding_volt_rate_entry.text())
        return w_wind_volt_rate_str

    def get_w_winding_phase_ct(self):
        w_wind_phase_ct = self.pad_dat_number(self.w_winding_phase_ct_entry.text())
        return w_wind_phase_ct

    def get_w_winding_neutral(self):
        w_wind_neutral_str = self.pad_dat_number(self.w_winding_neutral_entry.text())
        return w_wind_neutral_str

    def get_w_winding_phase_pt(self):
        w_wind_phase_pt_str = self.pad_dat_number(self.w_winding_phase_pt_entry.text())
        return w_wind_phase_pt_str

    def get_x_winding_volt_rate(self):
        x_wind_volt_rate_str = self.pad_dat_number(self.x_winding_volt_rate_entry.text())
        return x_wind_volt_rate_str

    def get_x_winding_phase_ct(self):
        x_wind_phase_ct_str = self.pad_dat_number(self.x_winding_phase_ct_entry.text())
        return x_wind_phase_ct_str

    def get_x_winding_neutral(self):
        x_wind_neutral_str = self.pad_dat_number(self.x_winding_neutral_entry.text())
        return x_wind_neutral_str

    def get_x_winding_phase_pt(self):
        x_wind_phase_pt_str = self.pad_dat_number(self.x_winding_phase_pt_entry.text())
        return x_wind_phase_pt_str

    def get_nom_phase_volt(self):
        nom_phase_volt_str = self.pad_dat_number(self.nom_phase_volt_entry.text())
        return nom_phase_volt_str

    # LED settings
    def get_led1_status(self):
        led1_str = self.pad_with_hash(self.led1_entry.text())
        return led1_str

    def get_led2_status(self):
        led2_str = self.pad_with_hash(self.led2_entry.text())
        return led2_str

    def get_led3_status(self):
        led3_str = self.pad_with_hash(self.led3_entry.text())
        return led3_str

    def get_led4_status(self):
        led4_str = self.pad_with_hash(self.led4_entry.text())
        return led4_str

    # output contacts settings
    def get_oc1(self):
        oc_str = self.pad_with_hash(self.oc_1_entry.text())
        return oc_str

    def get_oc2(self):
        oc_str = self.pad_with_hash(self.oc_2_entry.text())
        return oc_str

    def get_oc3(self):
        oc_str = self.pad_with_hash(self.oc_3_entry.text())
        return oc_str

    # current differential settings
    def get_current_differential(self):
        curr_diff_str = self.pad_dat_number(self.rest_diff_current_entry.text())
        return curr_diff_str

    def get_current_differential_first(self):
        curr_diff_fir_str = self.pad_dat_number(self.rest_diff_fir_slope_entry.text())
        return curr_diff_fir_str

    def get_current_differential_second(self):
        cur_diff_scd_str = self.pad_dat_number(self.rest_diff_scd_slope_entry.text())
        return cur_diff_scd_str

    def get_current_differential_slope_intersect(self):
        curr_diff_slope_inter_str = self.pad_dat_number(self.rest_diff_slope_intersect_entry.text())
        return curr_diff_slope_inter_str

    def get_second_harmonic(self):
        scd_har_str = self.pad_dat_number(self.thresh_to_scd_harmonic_entry.text())
        return scd_har_str

    def get_fourth_harmonic(self):
        for_har_str = self.pad_dat_number(self.thresh_to_fourth_harmonic_entry.text())
        return for_har_str

    def get_fifth_harmonic(self):
        fif_har_str = self.pad_dat_number(self.thresh_to_fifth_harmonic_entry.text())
        return fif_har_str

    def get_unrest_differential_pickup_current(self):
        unrest_diff_str = self.pad_dat_number(self.unrest_diff_pickup_current_entry.text())
        return unrest_diff_str

    def get_current_differential_enable(self):
        enable_str = self.pad_with_hash(self.current_diff_enable_entry.text())
        return enable_str

    # w_winding settings
    # group 1
    def get_group1_w_wind_oc_pickup(self):
        w_wind_oc_pu_str = self.pad_dat_number(self.w_winding_group1_oc_pickup_entry.text())
        return w_wind_oc_pu_str

    def get_group1_w_wind_oc_delay(self):
        w_wind_delay_str = self.pad_dat_number(self.w_winding_group1_oc_delay_entry.text())
        return w_wind_delay_str

    def get_group1_w_wind_oc_time_inverse(self):
        w_wind_oc_inv_str = self.pad_dat_number(self.w_winding_group1_oc_time_inverse_entry.text())
        return w_wind_oc_inv_str

    def get_group1_w_wind_curve_style(self):
        curve_style_str = self.w_winding_group1_curve_style_cb.currentText()
        return curve_style_str[1:]

    def get_group1_w_wind_time_dial(self):
        w_wind_time_dial_str = self.pad_dat_number(self.w_winding_group1_time_dial_entry.text())
        return w_wind_time_dial_str

    def get_group1_w_wind_electro_reset(self):
        electro_str = self.pad_with_hash(str(self.w_winding_group1_electro_reset_cb.currentText()))
        return electro_str

    #
    # def get_group1_w_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.w_winding_group1_neutral_enable_eq_entry.text())
    #     return enable_eq_str

    #     # group 2

    def get_group2_w_wind_oc_pickup(self):
        line_str = self.pad_dat_number(self.w_winding_group2_oc_pickup_entry.text())
        return line_str

    def get_group2_w_wind_oc_delay(self):
        line_str = self.pad_dat_number(self.w_winding_group2_oc_delay_entry.text())
        return line_str

    #
    # def get_group2_w_wind_oc_time_inverse(self):
    #     return self.w_winding_group2_oc_time_inverse_entry.text()
    #
    # def get_group2_w_wind_curve_style(self):
    #     curve_style_str = self.w_winding_group2_curve_style_cb.currentText()
    #     return curve_style_str[1:]
    #
    # def get_group2_w_wind_time_dial(self):
    #     return self.w_winding_group2_time_dial_entry.text()
    #
    # def get_group2_w_wind_electro_reset(self):
    #     electro_str = self.pad_with_hash(str(self.w_winding_group2_electro_reset_cb.currentText()))
    #     return electro_str
    #
    # def get_group2_w_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.w_winding_group2_neutral_enable_eq_entry.text())
    #     return enable_eq_str
    #
    #     # group 3

    def get_group3_w_wind_oc_pickup(self):
        line_str = self.pad_dat_number(self.w_winding_group3_oc_pickup_entry.text())
        return line_str

    def get_group3_w_wind_oc_delay(self):
        line_str = self.pad_dat_number(self.w_winding_group3_oc_delay_entry.text())
        return line_str

    def get_group3_w_wind_oc_time_inverse(self):
        line_str = self.pad_dat_number(self.w_winding_group3_oc_time_inverse_entry.text())
        return line_str

    def get_group3_w_wind_curve_style(self):
        curve_style_str = self.w_winding_group3_curve_style_cb.currentText()
        return curve_style_str[1:]

    def get_group3_w_wind_time_dial(self):
        line_str = self.pad_dat_number(self.w_winding_group3_time_dial_entry.text())
        return line_str

    def get_group3_w_wind_electro_reset(self):
        electro_str = self.pad_with_hash(str(self.w_winding_group3_electro_reset_cb.currentText()))
        return electro_str

    #
    # def get_group3_w_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.w_winding_group3_neutral_enable_eq_entry.text())
    #     return enable_eq_str

    # x_winding settings

    # group 1
    def get_group1_x_wind_oc_pickup(self):
        x_wind_oc_pu_str = self.pad_dat_number(self.x_winding_group1_oc_pickup_entry.text())
        return x_wind_oc_pu_str

    def get_group1_x_wind_oc_delay(self):
        x_wind_delay_str = self.pad_dat_number(self.x_winding_group1_oc_delay_entry.text())
        return x_wind_delay_str

    def get_group1_x_wind_oc_time_inverse(self):
        x_wind_oc_inv_str = self.pad_dat_number(self.x_winding_group1_oc_time_inverse_entry.text())
        return x_wind_oc_inv_str

    def get_group1_x_wind_curve_style(self):
        curve_style_str = self.x_winding_group1_curve_style_cb.currentText()
        return curve_style_str[1:]

    def get_group1_x_wind_time_dial(self):
        x_wind_time_dial_str = self.pad_dat_number(self.x_winding_group1_time_dial_entry.text())
        return x_wind_time_dial_str

    def get_group1_x_wind_electro_reset(self):
        electro_str = self.pad_with_hash(str(self.x_winding_group1_electro_reset_cb.currentText()))
        return electro_str

    #
    # def get_group1_x_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.x_winding_group1_neutral_enable_eq_entry.text())
    #     return enable_eq_str

    #     # group 2

    def get_group2_x_wind_oc_pickup(self):
        line_str = self.pad_dat_number(self.x_winding_group2_oc_pickup_entry.text())
        return line_str

    def get_group2_x_wind_oc_delay(self):
        line_str = self.pad_dat_number(self.x_winding_group2_oc_delay_entry.text())
        return line_str

    # def get_group2_x_wind_oc_time_inverse(self):
    #     return self.x_winding_group2_oc_time_inverse_entry.text()
    #
    # def get_group2_x_wind_curve_style(self):
    #     curve_style_str = self.w_winding_group2_curve_style_cb.currentText()
    #     return curve_style_str[1:]
    #
    # def get_group2_x_wind_time_dial(self):
    #     return self.x_winding_group2_time_dial_entry.text()
    #
    # def get_group2_x_wind_electro_reset(self):
    #     electro_str = self.pad_with_hash(str(self.x_winding_group2_electro_reset_cb.currentText()))
    #     return electro_str
    #
    # def get_group2_x_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.x_winding_group2_neutral_enable_eq_entry.text())
    #     return enable_eq_str
    #
    #     # group 3

    def get_group3_x_wind_oc_pickup(self):
        line_str = self.pad_dat_number(self.x_winding_group3_oc_pickup_entry.text())
        return line_str

    def get_group3_x_wind_oc_delay(self):
        line_str = self.pad_dat_number(self.x_winding_group3_oc_delay_entry.text())
        return line_str

    def get_group3_x_wind_oc_time_inverse(self):
        line_str = self.pad_dat_number(self.x_winding_group3_oc_time_inverse_entry.text())
        return line_str

    def get_group3_x_wind_curve_style(self):
        curve_style_str = self.w_winding_group3_curve_style_cb.currentText()
        return curve_style_str[1:]

    def get_group3_x_wind_time_dial(self):
        line_str = self.pad_dat_number(self.x_winding_group3_time_dial_entry.text())
        return line_str

    def get_group3_x_wind_electro_reset(self):
        electro_str = self.pad_with_hash(str(self.x_winding_group3_electro_reset_cb.currentText()))
        return electro_str

    #
    # def get_group3_x_wind_neutral_enable_eq(self):
    #     enable_eq_str = self.pad_with_hash(self.x_winding_group3_neutral_enable_eq_entry.text())
    #     return enable_eq_str

    # volts/hz settings

    def get_hz_level1_pickup(self):
        hz_level1_pickup_str = self.pad_dat_number(self.volts_hz_level1_pickup_entry.text())
        return hz_level1_pickup_str

    def get_hz_level1_time_delay(self):
        hz_level1_time_delay_str = self.pad_dat_number(self.volts_hz_level1_time_delay_entry.text())
        return hz_level1_time_delay_str

    def get_hz_level2_pickup(self):
        hz_level2_pickup_str = self.pad_dat_number(self.volts_hz_level2_pickup_entry.text())
        return hz_level2_pickup_str

    def get_hz_level2_time_delay(self):
        hz_level2_time_delay_str = self.pad_dat_number(self.volts_hz_level2_time_delay_entry.text())
        return hz_level2_time_delay_str

    # method to get the port to use for uart com
    def get_com_port(self):
        return self.set_port_entry.text()

    # TODO make methods to set the settings windows from a file
    # set eq data settings
    def set_relay_name(self, data):
        line = re.sub('[!@#$]', '', data[0])
        self.relay_name_entry.setText(line)

    def set_trans_nameplate(self, data):
        line = data[1].lstrip("0")
        self.trans_nameplate_entry.setText(line)

    def set_sys_nom_freq(self, data):
        line = data[2].lstrip("0")
        self.sys_nom_freq_entry.setText(line)

    def set_winding(self, data):
        line = re.sub('[!@#$]', '', data[3])
        self.source_side_winding_cb.setCurrentText(line)

    def set_trans_connect_type(self, data):
        line = re.sub('[!@#$]', '', data[4])
        self.trans_connect_type_cb.setCurrentText(line)

    def set_w_winding_volt_rate(self, data):
        line = data[5].lstrip("0")
        self.w_winding_volt_rate_entry.setText(line)

    def set_w_winding_phase_ct(self, data):
        line = data[6].lstrip("0")
        self.w_winding_phase_ct_entry.setText(line)

    def set_w_winding_neutral(self, data):
        line = data[7].lstrip("0")
        self.w_winding_neutral_entry.setText(line)

    def set_w_winding_phase_pt(self, data):
        line = data[8].lstrip("0")
        self.w_winding_phase_pt_entry.setText(line)

    def set_x_winding_volt_rate(self, data):
        line = data[9].lstrip("0")
        self.x_winding_volt_rate_entry.setText(line)

    def set_x_winding_phase_ct(self, data):
        line = data[10].lstrip("0")
        self.x_winding_phase_ct_entry.setText(line)

    def set_x_winding_neutral(self, data):
        line = data[11].lstrip("0")
        self.x_winding_neutral_entry.setText(line)

    def set_x_winding_phase_pt(self, data):
        line = data[12].lstrip("0")
        self.x_winding_phase_pt_entry.setText(line)

    def set_nom_phase_volt(self, data):
        line = data[13].lstrip("0")
        self.nom_phase_volt_entry.setText(line)

    # set led settings
    def set_led1_status(self, data):
        line = re.sub('[!@#$]', '', data[14])
        self.led1_entry.setText(line)

    def set_led2_status(self, data):
        line = re.sub('[!@#$]', '', data[15])
        self.led2_entry.setText(line)

    def set_led3_status(self, data):
        line = re.sub('[!@#$]', '', data[16])
        self.led3_entry.setText(line)

    def set_led4_status(self, data):
        line = re.sub('[!@#$]', '', data[17])
        self.led4_entry.setText(line)

    # set oc settings
    def set_oc1_status(self, data):
        line = re.sub('[!@#$]', '', data[18])
        self.oc_1_entry.setText(line)

    def set_oc2_status(self, data):
        line = re.sub('[!@#$]', '', data[19])
        self.oc_2_entry.setText(line)

    def set_oc3_status(self, data):
        line = re.sub('[!@#$]', '', data[20])
        self.oc_3_entry.setText(line)

    # set current differential settings
    def set_rest_diff_pickup_current(self, data):
        line = data[21].lstrip("0")
        self.rest_diff_current_entry.setText(line)

    def set_rest_diff_first_slope(self, data):
        line = data[22].lstrip("0")
        self.rest_diff_fir_slope_entry.setText(line)

    def set_rest_diff_second_slope(self, data):
        line = data[23].lstrip("0")
        self.rest_diff_scd_slope_entry.setText(line)

    def set_rest_diff_slope_intersect(self, data):
        line = data[24].lstrip("0")
        self.rest_diff_slope_intersect_entry.setText(line)

    def set_thresh_blocking_2nd_harmonic(self, data):
        line = data[25].lstrip("0")
        self.thresh_to_scd_harmonic_entry.setText(line)

    def set_thresh_blocking_4th_harmonic(self, data):
        line = data[26].lstrip("0")
        self.thresh_to_fourth_harmonic_entry.setText(line)

    def set_thresh_blocking_5th_harmonic(self, data):
        line = data[27].lstrip("0")
        self.thresh_to_fifth_harmonic_entry.setText(line)

    def set_unrest_diff_pickup_current(self, data):
        line = data[28].lstrip("0")
        self.unrest_diff_pickup_current_entry.setText(line)

    def set_curr_diff_enable_eq(self, data):
        line = re.sub('[!@#$]', '', data[29])
        self.current_diff_enable_entry.setText(line)

    # set w_winding settings
    # group 1
    def set_w_wind_group1_phase_oc_pickup(self, data):
        line = data[30].lstrip("0")
        self.w_winding_group1_oc_pickup_entry.setText(line)

    def set_w_wind_group1_phase_oc_delay(self, data):
        line = data[31].lstrip("0")
        self.w_winding_group1_oc_delay_entry.setText(line)

    def set_w_wind_group1_time_inverse(self, data):
        line = data[32].lstrip("0")
        self.w_winding_group1_oc_time_inverse_entry.setText(line)

    def set_w_wind_group1_curve_style(self, data):
        line = 'U' + str(data[33])
        self.w_winding_group1_curve_style_cb.setCurrentText(line)

    def set_w_wind_group1_time_dial(self, data):
        line = data[34].lstrip("0")
        self.w_winding_group1_time_dial_entry.setText(line)

    def set_w_wind_group1_electro_reset(self, data):
        line = re.sub('[!@#$]', '', data[35])
        self.w_winding_group1_electro_reset_cb.setCurrentText(line)

    #
    # def set_w_wind_group1_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[36])
    #     self.w_winding_group1_neutral_enable_eq_entry.setText(line)

    # # group 2
    def set_w_wind_group2_phase_oc_pickup(self, data):
        line = data[36].lstrip("0")
        self.w_winding_group2_oc_pickup_entry.setText(line)

    def set_w_wind_group2_phase_oc_delay(self, data):
        line = data[37].lstrip("0")
        self.w_winding_group2_oc_delay_entry.setText(line)

    #
    # def set_w_wind_group2_time_inverse(self, data):
    #     self.w_winding_group2_oc_time_inverse_entry.setText(data[39])
    #
    # def set_w_wind_group2_curve_style(self, data):
    #     line = 'U' + str(data[40])
    #     self.w_winding_group2_curve_style_cb.setCurrentText(line)
    #
    # def set_w_wind_group2_time_dial(self, data):
    #     self.w_winding_group2_time_dial_entry.setText(data[41])
    #
    # def set_w_wind_group2_electro_reset(self, data):
    #     line = re.sub('[!@#$]', '', data[42])
    #     self.w_winding_group2_electro_reset_cb.setCurrentText(line)
    #
    # def set_w_wind_group2_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[43])
    #     self.w_winding_group2_neutral_enable_eq_entry.setText(line)
    #
    # # group 3
    def set_w_wind_group3_phase_oc_pickup(self, data):
        line = data[38].lstrip("0")
        self.w_winding_group3_oc_pickup_entry.setText(line)

    def set_w_wind_group3_phase_oc_delay(self, data):
        line = data[39].lstrip("0")
        self.w_winding_group3_oc_delay_entry.setText(line)

    def set_w_wind_group3_time_inverse(self, data):
        line = data[40].lstrip("0")
        self.w_winding_group3_oc_time_inverse_entry.setText(line)

    def set_w_wind_group3_curve_style(self, data):
        line = 'U' + str(data[41])
        self.w_winding_group3_curve_style_cb.setCurrentText(line)

    def set_w_wind_group3_time_dial(self, data):
        line = data[42].lstrip("0")
        self.w_winding_group3_time_dial_entry.setText(line)

    def set_w_wind_group3_electro_reset(self, data):
        line = re.sub('[!@#$]', '', data[43])
        self.w_winding_group3_electro_reset_cb.setCurrentText(line)

    #
    # def set_w_wind_group3_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[50])
    #     self.w_winding_group3_neutral_enable_eq_entry.setText(line)

    # set x_winding settings
    # group 1
    def set_x_wind_group1_phase_oc_pickup(self, data):
        line = data[44].lstrip("0")
        self.x_winding_group1_oc_pickup_entry.setText(line)

    def set_x_wind_group1_phase_oc_delay(self, data):
        line = data[45].lstrip("0")
        self.x_winding_group1_oc_delay_entry.setText(line)

    def set_x_wind_group1_time_inverse(self, data):
        line = data[46].lstrip("0")
        self.x_winding_group1_oc_time_inverse_entry.setText(line)

    def set_x_wind_group1_curve_style(self, data):
        line = 'U' + str(data[47])
        self.x_winding_group1_curve_style_cb.setCurrentText(line)

    def set_x_wind_group1_time_dial(self, data):
        line = data[48].lstrip("0")
        self.x_winding_group1_time_dial_entry.setText(line)

    def set_x_wind_group1_electro_reset(self, data):
        line = re.sub('[!@#$]', '', data[49])
        self.x_winding_group1_electro_reset_cb.setCurrentText(line)

    #
    # def set_x_wind_group1_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[57])
    #     self.x_winding_group1_neutral_enable_eq_entry.setText(line)

    # # group 2
    def set_x_wind_group2_phase_oc_pickup(self, data):
        line = data[50].lstrip("0")
        self.x_winding_group2_oc_pickup_entry.setText(line)

    def set_x_wind_group2_phase_oc_delay(self, data):
        line = data[51].lstrip("0")
        self.x_winding_group2_oc_delay_entry.setText(line)

    #
    # def set_x_wind_group2_time_inverse(self, data):
    #     self.x_winding_group2_oc_time_inverse_entry.setText(data[60])
    #
    # def set_x_wind_group2_curve_style(self, data):
    #     line = 'U' + str(data[61])
    #     self.x_winding_group2_curve_style_cb.setCurrentText(line)
    #
    # def set_x_wind_group2_time_dial(self, data):
    #     self.x_winding_group2_time_dial_entry.setText(data[62])
    #
    # def set_x_wind_group2_electro_reset(self, data):
    #     line = re.sub('[!@#$]', '', data[63])
    #     self.x_winding_group2_electro_reset_cb.setCurrentText(line)
    #
    # def set_x_wind_group2_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[64])
    #     self.x_winding_group2_neutral_enable_eq_entry.setText(line)
    #
    # # group 3
    def set_x_wind_group3_phase_oc_pickup(self, data):
        line = data[52].lstrip("0")
        self.x_winding_group3_oc_pickup_entry.setText(line)

    def set_x_wind_group3_phase_oc_delay(self, data):
        line = data[53].lstrip("0")
        self.x_winding_group3_oc_delay_entry.setText(line)

    def set_x_wind_group3_time_inverse(self, data):
        line = data[54].lstrip("0")
        self.x_winding_group3_oc_time_inverse_entry.setText(line)

    def set_x_wind_group3_curve_style(self, data):
        line = 'U' + str(data[55])
        self.x_winding_group3_curve_style_cb.setCurrentText(line)

    def set_x_wind_group3_time_dial(self, data):
        line = data[56].lstrip("0")
        self.x_winding_group3_time_dial_entry.setText(line)

    def set_x_wind_group3_electro_reset(self, data):
        line = re.sub('[!@#$]', '', data[57])
        self.x_winding_group3_electro_reset_cb.setCurrentText(line)

    # def set_x_wind_group3_neu_enable_eq(self, data):
    #     line = re.sub('[!@#$]', '', data[71])
    #     self.x_winding_group3_neutral_enable_eq_entry.setText(line)

    # set volts/hz settings
    def set_level1_pickup(self, data):
        line = data[58].lstrip("0")
        self.volts_hz_level1_pickup_entry.setText(line)

    def set_level1_time_delay(self, data):
        line = data[59].lstrip("0")
        self.volts_hz_level1_time_delay_entry.setText(line)

    def set_level2_pickup(self, data):
        line = data[60].lstrip("0")
        self.volts_hz_level2_pickup_entry.setText(line)

    def set_level2_time_delay(self, data):
        line = data[61].lstrip("0")
        self.volts_hz_level2_time_delay_entry.setText(line)

    # TODO call back to be used when button pressed to select folder
    def on_input_file_button_clicked(self):
        pass

    # have a method to make the data to go into the settings file
    def make_data(self, **kwargs):
        pass

    # TODO make a method to save the settings into a file
    def on_save_button_clicked(self):
        # file to store the settings adding the date and time to make each file save unique
        file_name = "settings.txt"
        data = self.get_relay_name() + ";" + self.get_trans_nameplate() + ";" \
               + self.get_sys_nom_freq() + ";" + self.get_winding() + ";" \
               + self.get_trans_connect_type() + ";" + self.get_w_winding_volt_rate() + ";" \
               + self.get_w_winding_phase_ct() + ";" + self.get_w_winding_neutral() + ";" \
               + self.get_w_winding_phase_pt() + ";" + self.get_x_winding_volt_rate() + ";" \
               + self.get_x_winding_phase_ct() + ";" + self.get_x_winding_neutral() + ";" \
               + self.get_x_winding_phase_pt() + ";" + self.get_nom_phase_volt() + ";" \
               + self.get_led1_status() + ";" + self.get_led2_status() + ";" \
               + self.get_led3_status() + ";" + self.get_led4_status() + ";" \
               + self.get_oc1() + ";" + self.get_oc2() + ";" \
               + self.get_oc3() + ";" + self.get_current_differential() + ";" \
               + self.get_current_differential_first() + ";" + self.get_current_differential_second() + ";" \
               + self.get_current_differential_slope_intersect() + ";" + self.get_second_harmonic() + ";" \
               + self.get_fourth_harmonic() + ";" + self.get_fifth_harmonic() + ";" \
               + self.get_unrest_differential_pickup_current() + ";" + self.get_current_differential_enable() + ";" \
               + self.get_group1_w_wind_oc_pickup() + ";" + self.get_group1_w_wind_oc_delay() + ";" \
               + self.get_group1_w_wind_oc_time_inverse() + ";" + self.get_group1_w_wind_curve_style() + ";" \
               + self.get_group1_w_wind_time_dial() + ";" + self.get_group1_w_wind_electro_reset() + ";" \
               + self.get_group2_w_wind_oc_pickup() + ";" + self.get_group2_w_wind_oc_delay() + ";" \
               + self.get_group3_w_wind_oc_pickup() + ";" + self.get_group3_w_wind_oc_delay() + ";" \
               + self.get_group3_w_wind_oc_time_inverse() + ";" + self.get_group3_w_wind_curve_style() + ";" \
               + self.get_group3_w_wind_time_dial() + ";" + self.get_group3_w_wind_electro_reset() + ";" \
               + self.get_group1_x_wind_oc_pickup() + ";" + self.get_group1_x_wind_oc_delay() + ";" \
               + self.get_group1_x_wind_oc_time_inverse() + ";" + self.get_group1_x_wind_curve_style() + ";" \
               + self.get_group1_x_wind_time_dial() + ";" + self.get_group1_x_wind_electro_reset() + ";" \
               + self.get_group2_x_wind_oc_pickup() + ";" + self.get_group2_x_wind_oc_delay() + ";"\
               + self.get_group3_x_wind_oc_pickup() + ";" + self.get_group3_x_wind_oc_delay() + ";" \
               + self.get_group3_x_wind_oc_time_inverse() + ";" + self.get_group3_x_wind_curve_style() + ";" \
               + self.get_group3_x_wind_time_dial() + ";" + self.get_group3_x_wind_electro_reset() + ";" \
               + self.get_hz_level1_pickup() + ";" + self.get_hz_level1_time_delay() + ";" \
               + self.get_hz_level2_pickup() + ";" + self.get_hz_level2_time_delay() + ";"

        settings_file = open(file_name, "w")
        settings_file.write(data)
        settings_file.close()
    # reply = QtGui.QMessageBox.question(parent=self, title='Attention',
    #                                    text='File will be overwritten.\nDo you still want to proceed?',
    #                                    buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
    #                                    defaultButton=QtGui.QMessageBox.No)
    # if the user chooses to overwite the file we will save it
    # if reply == QtGui.QMessageBox.Yes:
    #     name = self.get_relay_name()
    # file_name = self.inputFileLineEdit.text()
    # data = QFile("settings.txt")
    # if data.open(QFile.WriteOnly | QFile.Truncate):
    #     out = QTextStream(data)
    # data_stream = QTextStream()

    # settings_file = open("settings.txt", "w")
    # settings_file.write(name)

    # TODO make a method to load the settings from a file
    def on_load_button_clicked(self):
        file_name = "settings_load.txt"
        settings_file = open(file_name, "r")
        # check to make sure the file is open to read
        if settings_file.mode == "r":
            data = settings_file.read().split(";")
            # print (data)

        # set the settings from the file
        # lead eq data
        self.set_relay_name(data)
        self.set_trans_nameplate(data)
        self.set_sys_nom_freq(data)
        self.set_winding(data)
        self.set_trans_connect_type(data)
        self.set_w_winding_volt_rate(data)
        self.set_w_winding_phase_ct(data)
        self.set_w_winding_neutral(data)
        self.set_w_winding_phase_pt(data)
        self.set_x_winding_volt_rate(data)
        self.set_x_winding_phase_ct(data)
        self.set_x_winding_neutral(data)
        self.set_x_winding_phase_pt(data)
        self.set_nom_phase_volt(data)
        # load led data
        self.set_led1_status(data)
        self.set_led2_status(data)
        self.set_led3_status(data)
        self.set_led4_status(data)
        # load oc data
        self.set_oc1_status(data)
        self.set_oc2_status(data)
        self.set_oc3_status(data)
        # load curr diff data
        self.set_rest_diff_pickup_current(data)
        self.set_rest_diff_first_slope(data)
        self.set_rest_diff_second_slope(data)
        self.set_rest_diff_slope_intersect(data)
        self.set_thresh_blocking_2nd_harmonic(data)
        self.set_thresh_blocking_4th_harmonic(data)
        self.set_thresh_blocking_5th_harmonic(data)
        self.set_unrest_diff_pickup_current(data)
        self.set_curr_diff_enable_eq(data)
        # load w_wind data
        # group 1
        self.set_w_wind_group1_phase_oc_pickup(data)
        self.set_w_wind_group1_phase_oc_delay(data)
        self.set_w_wind_group1_time_inverse(data)
        self.set_w_wind_group1_curve_style(data)
        self.set_w_wind_group1_time_dial(data)
        self.set_w_wind_group1_electro_reset(data)
        # self.set_w_wind_group1_neu_enable_eq(data)
        # # group 2
        self.set_w_wind_group2_phase_oc_pickup(data)
        self.set_w_wind_group2_phase_oc_delay(data)
        # self.set_w_wind_group2_time_inverse(data)
        # self.set_w_wind_group2_curve_style(data)
        # self.set_w_wind_group2_time_dial(data)
        # self.set_w_wind_group2_electro_reset(data)
        # self.set_w_wind_group2_neu_enable_eq(data)
        # # group 3
        self.set_w_wind_group3_phase_oc_pickup(data)
        self.set_w_wind_group3_phase_oc_delay(data)
        self.set_w_wind_group3_time_inverse(data)
        self.set_w_wind_group3_curve_style(data)
        self.set_w_wind_group3_time_dial(data)
        self.set_w_wind_group3_electro_reset(data)
        # self.set_w_wind_group3_neu_enable_eq(data)
        # load x_wind data
        # group 1
        self.set_x_wind_group1_phase_oc_pickup(data)
        self.set_x_wind_group1_phase_oc_delay(data)
        self.set_x_wind_group1_time_inverse(data)
        self.set_x_wind_group1_curve_style(data)
        self.set_x_wind_group1_time_dial(data)
        # self.set_x_wind_group1_electro_reset(data)
        # self.set_x_wind_group1_neu_enable_eq(data)
        # # group 2
        self.set_x_wind_group2_phase_oc_pickup(data)
        self.set_x_wind_group2_phase_oc_delay(data)
        # self.set_x_wind_group2_time_inverse(data)
        # self.set_x_wind_group2_curve_style(data)
        # self.set_x_wind_group2_time_dial(data)
        # self.set_x_wind_group2_electro_reset(data)
        # self.set_x_wind_group2_neu_enable_eq(data)
        # # group 3
        self.set_x_wind_group3_phase_oc_pickup(data)
        self.set_x_wind_group3_phase_oc_delay(data)
        self.set_x_wind_group3_time_inverse(data)
        self.set_x_wind_group3_curve_style(data)
        self.set_x_wind_group3_time_dial(data)
        self.set_x_wind_group3_electro_reset(data)
        # self.set_x_wind_group3_neu_enable_eq(data)
        # load volts/hz data
        self.set_level1_pickup(data)
        self.set_level1_time_delay(data)
        self.set_level2_pickup(data)
        self.set_level2_time_delay(data)

    def load_stored_relay_settings(self):
        file_name = "pulled_settings.txt"
        settings_file = open(file_name, "r")
        # check to make sure the file is open to read
        if settings_file.mode == "r":
            data = settings_file.read().split(";")
            # print (data)

        # set the settings from the file
        # lead eq data
        self.set_relay_name(data)
        self.set_trans_nameplate(data)
        self.set_sys_nom_freq(data)
        self.set_winding(data)
        self.set_trans_connect_type(data)
        self.set_w_winding_volt_rate(data)
        self.set_w_winding_phase_ct(data)
        self.set_w_winding_neutral(data)
        self.set_w_winding_phase_pt(data)
        self.set_x_winding_volt_rate(data)
        self.set_x_winding_phase_ct(data)
        self.set_x_winding_neutral(data)
        self.set_x_winding_phase_pt(data)
        self.set_nom_phase_volt(data)
        # load led data
        self.set_led1_status(data)
        self.set_led2_status(data)
        self.set_led3_status(data)
        self.set_led4_status(data)
        # load oc data
        self.set_oc1_status(data)
        self.set_oc2_status(data)
        self.set_oc3_status(data)
        # load curr diff data
        self.set_rest_diff_pickup_current(data)
        self.set_rest_diff_first_slope(data)
        self.set_rest_diff_second_slope(data)
        self.set_rest_diff_slope_intersect(data)
        self.set_thresh_blocking_2nd_harmonic(data)
        self.set_thresh_blocking_4th_harmonic(data)
        self.set_thresh_blocking_5th_harmonic(data)
        self.set_unrest_diff_pickup_current(data)
        self.set_curr_diff_enable_eq(data)
        # load w_wind data
        # group 1
        self.set_w_wind_group1_phase_oc_pickup(data)
        self.set_w_wind_group1_phase_oc_delay(data)
        self.set_w_wind_group1_time_inverse(data)
        self.set_w_wind_group1_curve_style(data)
        self.set_w_wind_group1_time_dial(data)
        self.set_w_wind_group1_electro_reset(data)
        # self.set_w_wind_group1_neu_enable_eq(data)
        # # group 2
        self.set_w_wind_group2_phase_oc_pickup(data)
        self.set_w_wind_group2_phase_oc_delay(data)
        # self.set_w_wind_group2_time_inverse(data)
        # self.set_w_wind_group2_curve_style(data)
        # self.set_w_wind_group2_time_dial(data)
        # self.set_w_wind_group2_electro_reset(data)
        # self.set_w_wind_group2_neu_enable_eq(data)
        # # group 3
        self.set_w_wind_group3_phase_oc_pickup(data)
        self.set_w_wind_group3_phase_oc_delay(data)
        self.set_w_wind_group3_time_inverse(data)
        self.set_w_wind_group3_curve_style(data)
        self.set_w_wind_group3_time_dial(data)
        self.set_w_wind_group3_electro_reset(data)
        # self.set_w_wind_group3_neu_enable_eq(data)
        # load x_wind data
        # group 1
        self.set_x_wind_group1_phase_oc_pickup(data)
        self.set_x_wind_group1_phase_oc_delay(data)
        self.set_x_wind_group1_time_inverse(data)
        self.set_x_wind_group1_curve_style(data)
        self.set_x_wind_group1_time_dial(data)
        # self.set_x_wind_group1_electro_reset(data)
        # self.set_x_wind_group1_neu_enable_eq(data)
        # # group 2
        self.set_x_wind_group2_phase_oc_pickup(data)
        self.set_x_wind_group2_phase_oc_delay(data)
        # self.set_x_wind_group2_time_inverse(data)
        # self.set_x_wind_group2_curve_style(data)
        # self.set_x_wind_group2_time_dial(data)
        # self.set_x_wind_group2_electro_reset(data)
        # self.set_x_wind_group2_neu_enable_eq(data)
        # # group 3
        self.set_x_wind_group3_phase_oc_pickup(data)
        self.set_x_wind_group3_phase_oc_delay(data)
        self.set_x_wind_group3_time_inverse(data)
        self.set_x_wind_group3_curve_style(data)
        self.set_x_wind_group3_time_dial(data)
        self.set_x_wind_group3_electro_reset(data)
        # self.set_x_wind_group3_neu_enable_eq(data)
        # load volts/hz data
        self.set_level1_pickup(data)
        self.set_level1_time_delay(data)
        self.set_level2_pickup(data)
        self.set_level2_time_delay(data)

    # def setup_comm_connection(self):
    #     file_name = "settings.txt"
    #     # time_end = time.time() + 5 * 1
    #     with open(file_name) as infile:
    #         lines = 0
    #         words = 0
    #         characters = 0
    #         for line in infile:
    #             wordslist = line.split(";")
    #             lines = lines + 1
    #             words = words + len(wordslist)
    #             characters += sum(len(word) for word in wordslist)
    #
    #     with open(file_name) as f1:
    #         content1 = f1.readlines()
    #     content1 = [x.strip() for x in content1]
    #     return content1

    def do_read(self, ser):
        # matcher = re.compile(term)  # gives you the ability to search for anything
        # tic = time.time()
        ser.flush()
        buff = ser.readlines(460)
        # buff = ser.read_until(terminator='*')
        # you can use if not ('\n' in buff) too if you don't like re
        # while ((time.time() - tic) < tout) and (not matcher.search(buff)):
        #     buff += ser.read(128)
        return buff

    def setup_serial(self):
        if self.get_com_port() is not ' ':
            user_port = self.get_com_port()
        else:
            user_port = 5
        # content = self.setup_comm_connection()

        # setup the com port
        port = "\\\\.\\COM" + user_port
        # print(port)
        baud = 9600
        bytesize = serial.EIGHTBITS
        stop_bit = serial.STOPBITS_ONE
        parity = serial.PARITY_NONE

        ser = serial.Serial(port=port, baudrate=baud, bytesize=bytesize, stopbits=stop_bit, timeout=2 , parity=parity)
        return ser

    # TODO make a method for when push settings button is clicked
    def on_push_button_clicked(self):
        send_file_name = "settings.txt"
        time_end = time.time() + 2 * 1
        # if self.get_com_port() is not ' ':
        #     user_port = self.get_com_port()
        # else:
        #     user_port = 5
        self.on_save_button_clicked()
        # self.push_button_clicks += 1
        # content = self.setup_comm_connection()
        with open(send_file_name) as infile:
            lines = 0
            words = 0
            characters = 0

            for line in infile:
                wordslist = line.split(";")
                lines = lines + 1
                words = words + len(wordslist)
                characters += sum(len(word) for word in wordslist)
        # print(lines)
        # print(words)
        # print(characters)
        with open(send_file_name) as f1:
            content1 = f1.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content1 = [x.strip() for x in content1]

        # setup the com port
        ser = self.setup_serial()
        # port = "\\\\.\\COM" + user_port
        # # print(port)
        # baud = 9600
        # bytesize = serial.EIGHTBITS
        # stop_bit = serial.STOPBITS_ONE
        # parity = serial.PARITY_NONE
        #
        # ser = serial.Serial(port=port, baudrate=baud, bytesize=bytesize, stopbits=stop_bit, timeout=5, parity=parity)
        while time.time() < time_end:
            if not ser.isOpen():
                ser.open()

            # time.sleep(3.0)
            self.send_s(ser)
            # ser.flush()
            # ser.write(send.encode())
            # if self.push_button_clicks is 1:
            #     self.send_s(ser)

            ser.flush()
            for items in content1:
                ser.write(items.encode())
            #     # time.sleep(1)
            #
            # # time.sleep(1)
            # # output = self.do_read(ser, '*')
            # output = self.do_read(ser)
            # print(output)
            # time.sleep(1)
            ser.close()

    def send_r(self, ser):
        read = "r"
        ser.flush()
        ser.write(read.encode())
        ser.flush()

    def send_s(self, ser):
        read = "s"
        ser.flush()
        ser.write(read.encode())
        ser.flush()

    def on_pull_settings_button_clicked(self):
        read_file_name = "pulled_settings.txt"
        time_end = time.time() + 2 * 1

        # self.pull_button_clicks += 1
        # if self.get_com_port() is not ' ':
        #     user_port = self.get_com_port()
        # else:
        #     user_port = 5
        # setup the com port

        ser = self.setup_serial()
        # port = "\\\\.\\COM" + user_port
        # # print(port)
        # baud = 9600
        # bytesize = serial.EIGHTBITS
        # stop_bit = serial.STOPBITS_ONE
        # parity = serial.PARITY_NONE
        #
        # ser = serial.Serial(port=port, baudrate=baud, bytesize=bytesize, stopbits=stop_bit, timeout=5, parity=parity)
        while time.time() < time_end:
            if not ser.isOpen():
                ser.open()

            # ser.flush()
            # read = "read"
            # ser.write(read.encode())
            # ser.flush()
            self.send_r(ser)
            # if self.pull_button_clicks is 1:
            #     self.send_r(ser)
            output = self.do_read(ser)


            # print(output)
            # time.sleep(1)
            ser.close()

        read_settings_file = open(read_file_name, "w")
        for item in output:
            read_settings_file.write(item.decode())
        read_settings_file.close()
        self.load_stored_relay_settings()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    # widget.resize(QDesktopWidget().availableGeometry().size() * 1.0)
    widget.showMaximized()
    widget.show()

    sys.exit(app.exec_())
