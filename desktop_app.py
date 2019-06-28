import sys
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QHBoxLayout, QFormLayout, QComboBox, QDesktopWidget, QListWidget, QFrame


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        #TODO make the application have the phatcat title
        self.setObjectName("PHATCAT Desktop Application")
        # self.setMinimumSize(1000, 500)

        # TODO make the menu appear in the right location
        self.main_frame = QtWidgets.QFrame()
        self.main_layout = QtWidgets.QGridLayout()
        self.main_frame.setLayout(self.main_layout)


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

        # TODO make the list widget show up in the right location
        # create a list widget to hold all the menu settings
        self.menu_list = QListWidget()
        self.eq_data = QtWidgets.QListWidgetItem("Equipment Data")
        self.led_indicator = QtWidgets.QListWidgetItem("LED Indicators")
        self.output_contacts = QtWidgets.QListWidgetItem("Output Contacts")
        self.current_diff = QtWidgets.QListWidgetItem("Current Differential")
        self.w_winding_over = QtWidgets.QListWidgetItem("W-Winding Overcurrent")
        self.x_winding_over = QtWidgets.QListWidgetItem("X-Winding Overcurrent")
        self.volts_hz = QtWidgets.QListWidgetItem("Volts/Hz Element")

        # add the menu lists to the list widget
        self.menu_list.addItem(self.eq_data)
        self.menu_list.addItem(self.led_indicator)
        self.menu_list.addItem(self.output_contacts)
        self.menu_list.addItem(self.current_diff)
        self.menu_list.addItem(self.w_winding_over)
        self.menu_list.addItem(self.x_winding_over)
        self.menu_list.addItem(self.volts_hz)
        # self.menu_list.setMinimumSize(500, 500)

        # set up the GUI for the desktop application
        self.relay_name = QtWidgets.QLabel("Relay Name (40 Characters)")
        self.relay_name_entry = QtWidgets.QTextEdit()
        self.relay_name_entry.setMaximumHeight(50)

        self.trans_nameplate = QtWidgets.QLabel("Transformer Nameplate Max MVA Rating (float 0.2 - 5000)")
        self.trans_nameplate_entry = QtWidgets.QTextEdit()
        self.trans_nameplate_entry.setMaximumHeight(50)

        self.sys_nom_freq = QtWidgets.QLabel("System Nominal Frequency (float 45 - 65)")
        self.sys_nom_freq_entry = QtWidgets.QTextEdit()
        self.sys_nom_freq_entry.setMaximumHeight(50)

        self.source_side_winding = QtWidgets.QLabel("Source Side Winding")
        self.source_side_winding_cb = QComboBox()
        self.source_side_winding_cb.setMinimumHeight(50)
        self.source_side_winding_cb.addItem("W-Winding")
        self.source_side_winding_cb.addItem("X-Winding")

        self.trans_connect_type = QtWidgets.QLabel("Transformer Connection Type")
        self.trans_connect_type_cb = QComboBox()
        self.trans_connect_type_cb.setMinimumHeight(50)
        self.trans_connect_type_cb.addItem("test1")
        self.trans_connect_type_cb.addItem("test2")

        self.w_winding_group = QtWidgets.QGroupBox()
        self.w_winding_group.setTitle("W-Winding")
        self.w_winding_layout = QtWidgets.QVBoxLayout()

        self.w_winding_volt_rate = QtWidgets.QLabel("Line-to-Line Voltage Rating(in kV) of W-Winding (float 1-1000)")
        self.w_winding_volt_rate_entry = QtWidgets.QTextEdit()
        self.w_winding_volt_rate_entry.setMaximumHeight(50)
        self.w_winding_phase_ct = QtWidgets.QLabel("W-Winding Phase CT Ratio Wye-Connection (float 1-50000)")
        self.w_winding_phase_ct_entry = QtWidgets.QTextEdit()
        self.w_winding_phase_ct_entry.setMaximumHeight(50)
        self.w_winding_neutral = QtWidgets.QLabel("W-Winding Neutral CT Ratio (float 1-50000)")
        self.w_winding_neutral_entry = QtWidgets.QTextEdit()
        self.w_winding_neutral_entry.setMaximumHeight(50)
        self.w_winding_phase_pt = QtWidgets.QLabel("W-Winding Phase PT Ratio Wye-Connection (float 1-50000)")
        self.w_winding_phase_pt_entry = QtWidgets.QTextEdit()
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
        self.x_winding_volt_rate_entry = QtWidgets.QTextEdit()
        self.x_winding_volt_rate_entry.setMaximumHeight(50)
        self.x_winding_phase_ct = QtWidgets.QLabel("X-Winding Phase CT Ratio Wye-Connection (float 1-50000)")
        self.x_winding_phase_ct_entry = QtWidgets.QTextEdit()
        self.x_winding_phase_ct_entry.setMaximumHeight(50)
        self.x_winding_neutral = QtWidgets.QLabel("X-Winding Neutral CT Ratio (float 1-50000)")
        self.x_winding_neutral_entry = QtWidgets.QTextEdit()
        self.x_winding_neutral_entry.setMaximumHeight(50)
        self.x_winding_phase_pt = QtWidgets.QLabel("X-Winding Phase PT Ratio Wye-Connection (float 1-50000)")
        self.x_winding_phase_pt_entry = QtWidgets.QTextEdit()
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
        self.nom_phase_volt_entry = QtWidgets.QTextEdit()
        self.nom_phase_volt_entry.setMaximumHeight(50)

        # create a scroll area to put everything in
        # TODO make it so the scroll area has the scroll bar
        self.scrollable = QtWidgets.QScrollArea()
        self.scrollable.setWidgetResizable(True)
        # self.scrollable.setVerticalScrollBarPolicy()
        # self.scrollable.setMinimumSize(2000, 2000)
        self.scrollable.setGeometry(10, 10, 200, 200)
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

        self.scrollable.setLayout(self.scroll_layout)

        # create buttons to save and load settings
        self.button_layout = QtWidgets.QGridLayout()
        self.save_button = QtWidgets.QPushButton("Save File")
        self.load_button = QtWidgets.QPushButton("Load File")
        self.button_layout.addWidget(self.save_button)

        # set the layout and add all the widgets to it
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.menu_list, 0, 0)
        self.layout.addWidget(self.scrollable, 1, 1)
        # self.layout.addWidget(self.button_layout)
        self.layout.addWidget(self.save_button, 2, 2)
        self.layout.addWidget(self.load_button, 2, 3)

        self.setLayout(self.layout)

        # self.main_layout.addWidget(self.menu_list)

    # TODO make method to get the information housed in the various text boxes
    def get_relay_name(self):
        relay_name = self.relay_name_entry.toPlainText()
        return relay_name

    # TODO make a method to save the settings into a file
    def save_settings(self):
        relay_name = self.get_relay_name()
        settings_file = open("settings.txt", "a")
        settings_file.write(relay_name)
    # TODO make a method to load the settings from a file


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(QDesktopWidget().availableGeometry().size() * 0.9)
    widget.show()

    sys.exit(app.exec_())