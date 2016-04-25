#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import Qt
import PyQt4.Qwt5 as Qwt
import numpy as np
from datetime import datetime as date
import sys
from Relay_QCheckBox import *

class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(785, 275)
        self.setFixedWidth(785)
        self.setFixedHeight(275)
        self.setWindowTitle('Remote Relay Control v1.0')
        self.setContentsMargins(0,0,0,0)
        self.spdt_cb        = []   #list to hold spdt relay check boxes
        self.dpdt_cb        = []   #list to hold dpdt relay check boxes
        self.spdt_a_value   = 0   #SPDT BANK A Value, 0-255
        self.spdt_b_value   = 0   #SPDT BANK B Value, 0-255
        self.dpdt_a_value   = 0   #DPDT BANK A Value, 0-255
        self.dpdt_b_value   = 0   #DPDT BANK B Value, 0-255
        self.relays_cmd     = [0,0,0,0] # Relay Register Value Commanded, 0-225, [SPDTA, SPDTB, DPDTA, DPDTB]
        self.relay_callback = None #Callback accessor for remote relay control
        self.set_relay_msg  = '' # '$,R,AAA,BBB,CCC,DDD'
        self.connected      = False  #Connection Status to remote relay control box
        self.adc_interval   = 1000 #ADC Auto Update Interval in milliseconds
        self.initUI()
        self.darken()
        self.setFocus()
        
    def initUI(self):
        self.initFrames()
        self.initSPDTCheckBoxes()
        self.initDPDTCheckBoxes()
        self.initADC()
        self.initNet()
        self.initControls()
        self.connectSignals()

    def connectSignals(self):
        self.resetButton.clicked.connect(self.resetButtonEvent) 
        self.connectButton.clicked.connect(self.connectButtonEvent)
        self.adc_auto_cb.stateChanged.connect(self.catchADCAutoEvent)
        self.readStatusButton.clicked.connect(self.readStatusButtonEvent)
        self.readRelayButton.clicked.connect(self.readRelayButtonEvent)
        self.readVoltButton.clicked.connect(self.readVoltButtonEvent)
        self.updateButton.clicked.connect(self.updateButtonEvent)
        QtCore.QObject.connect(self.ADCtimer, QtCore.SIGNAL('timeout()'), self.readVoltButtonEvent)
        QtCore.QObject.connect(self.adc_interval_le, QtCore.SIGNAL('editingFinished()'), self.updateADCInterval)
        QtCore.QObject.connect(self.ipAddrTextBox, QtCore.SIGNAL('editingFinished()'), self.updateIPAddress)
        QtCore.QObject.connect(self.portTextBox, QtCore.SIGNAL('editingFinished()'), self.updatePort)
    

    def updateButtonEvent(self):
        a = self.relay_callback.set_relays(self.relays_cmd)
        if (a != -1): self.updateRelayStatus(a)
    
    def catchCheckBoxEvent(self, reltype, relay_id, value):
        #Catches Relay_QCheckBox Event
        #print str(reltype) + str(relay_id) + " " + str(value)
        if   (reltype == 'SPDT'):
            if (relay_id <= 8): self.relays_cmd[0] += value #SPDTA
            else:  self.relays_cmd[1] += value #SPDTB
        elif (reltype == 'DPDT'):
            if (relay_id <= 8): self.relays_cmd[2] += value #DPDTA
            else:  self.relays_cmd[3] += value #DPDTB
        #self.formatSetRelayMsg()

    def formatSetRelayMsg(self):
        self.set_relay_msg = '$,R,'
        #SPDT A
        if   (len(str(self.relays_cmd[0])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[0])
        elif (len(str(self.relays_cmd[0])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[0])
        elif (len(str(self.relays_cmd[0])) == 3): self.set_relay_msg +=        str(self.relays_cmd[0])
        self.set_relay_msg += ','
        #SPDT B
        if   (len(str(self.relays_cmd[1])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[1])
        elif (len(str(self.relays_cmd[1])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[1])
        elif (len(str(self.relays_cmd[1])) == 3): self.set_relay_msg +=        str(self.relays_cmd[1])
        self.set_relay_msg += ','
        #DPDT A
        if   (len(str(self.relays_cmd[2])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[2])
        elif (len(str(self.relays_cmd[2])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[2])
        elif (len(str(self.relays_cmd[2])) == 3): self.set_relay_msg +=        str(self.relays_cmd[2])
        self.set_relay_msg += ','
        #DPDT B
        if   (len(str(self.relays_cmd[3])) == 1): self.set_relay_msg += '00' + str(self.relays_cmd[3])
        elif (len(str(self.relays_cmd[3])) == 2): self.set_relay_msg += '0'  + str(self.relays_cmd[3])
        elif (len(str(self.relays_cmd[3])) == 3): self.set_relay_msg +=        str(self.relays_cmd[3])

        print self.set_relay_msg

    def readVoltButtonEvent(self):
        a = self.relay_callback.get_adcs()
        if (a != -1): self.updateADC(a)

    def readRelayButtonEvent(self):
        a = self.relay_callback.get_relays()
        if (a != -1): self.updateRelayStatus(a)

    def readStatusButtonEvent(self):
        #print 'GUI|  Read Status Button Clicked'
        a,b = self.relay_callback.get_status()
        #print a,b
        if (a != -1): self.updateRelayStatus(a)
        if (b != -1): self.updateADC(b)
        #else: 
        #    print 'GUI|  Not Connected to Relay Controller'
        #    print 'GUI|  Must Connect to Relay Controller before reading Status'

    def updateRelayStatus(self, rel):
        mask = 0b00000001
        for i in range(8):
            #SPDT A
            if ((rel[0]>>i) & mask): self.spdt_cb[i].setCheckState(QtCore.Qt.Checked)
            else: self.spdt_cb[i].setCheckState(QtCore.Qt.Unchecked)
            #SPDT B
            if ((rel[1]>>i) & mask): self.spdt_cb[i+8].setCheckState(QtCore.Qt.Checked)
            else: self.spdt_cb[i+8].setCheckState(QtCore.Qt.Unchecked)
            #DPDT A
            if ((rel[2]>>i) & mask): self.dpdt_cb[i].setCheckState(QtCore.Qt.Checked)
            else: self.dpdt_cb[i].setCheckState(QtCore.Qt.Unchecked)
            #DPDT B
            if ((rel[3]>>i) & mask): self.dpdt_cb[i+8].setCheckState(QtCore.Qt.Checked)
            else: self.dpdt_cb[i+8].setCheckState(QtCore.Qt.Unchecked)

    def updateADC(self,adcs):
        for i in range(len(adcs)):
            self.field_value[i] = str(adcs[i]) + 'V'
            self.adc_field_values_qlabels[i].setText(self.field_value[i])

    def catchADCAutoEvent(self, state):
        CheckState = (state == QtCore.Qt.Checked)
        if CheckState == True:  
            self.ADCtimer.start()
            print self.getTimeStampGMT() + "GUI|  Started ADC Auto Update, Interval: " + str(self.adc_interval) + " [ms]"
        else:
            self.ADCtimer.stop()
            print self.getTimeStampGMT() + "GUI|  Stopped ADC Auto Update"

    def updateADCInterval(self):
        self.adc_interval = float(self.adc_interval_le.text()) * 1000.0
        self.ADCtimer.setInterval(self.adc_interval)
        print self.getTimeStampGMT() + "GUI|  Updated ADC Auto Interval to " + str(self.adc_interval) + " [ms]"

    def connectButtonEvent(self):
        if (not self.connected):  #Not connected, attempt to connect
            self.connected = self.relay_callback.connect()
            if (self.connected): 
                self.connectButton.setText('Disconnect')
                self.net_label.setText("Connected")
                self.net_label.setStyleSheet("QLabel {  font-weight:bold; color:rgb(0,255,0) ; }")
                self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
                self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(225,225,225); color:rgb(0,0,0);}")
                self.ipAddrTextBox.setEnabled(False)
                self.portTextBox.setEnabled(False)
        else:
            self.connected = self.relay_callback.disconnect()
            if (not self.connected): 
                self.connectButton.setText('Connect')
                self.net_label.setText("Disconnected")
                self.net_label.setStyleSheet("QLabel {  font-weight:bold; color:rgb(255,0,0) ; }")
                self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
                self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
                self.ipAddrTextBox.setEnabled(True)
                self.portTextBox.setEnabled(True)

    def resetButtonEvent(self):
        for i in range(16):
            if self.spdt_cb[i].CheckState==True: self.spdt_cb[i].setCheckState(QtCore.Qt.Unchecked)
            if self.dpdt_cb[i].CheckState==True: self.dpdt_cb[i].setCheckState(QtCore.Qt.Unchecked)
        print self.getTimeStampGMT() + "GUI|  Cleared Relay Banks, Change Not Applied to RR Controller"

    def setCallback(self, callback):
        self.relay_callback = callback

    def initADC(self):
        field_name  = [ 'ADC1:', 'ADC2:', 'ADC3:', 'ADC4:', 'ADC5:', 'ADC6:', 'ADC7:', 'ADC8:']
        self.field_value = [ '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V', '0.00V' ]

        self.adc_auto_cb = QtGui.QCheckBox("Auto", self)  #Automatically update ADC voltages checkbox option
        self.adc_auto_cb.setStyleSheet("QCheckBox { font-size: 12px; \
                                                    background-color:rgb(0,0,0); \
                                                    color:rgb(255,255,255); }")

        self.adc_interval_le = QtGui.QLineEdit()
        self.adc_interval_le.setText("1")
        self.adc_validator = QtGui.QDoubleValidator()
        self.adc_interval_le.setValidator(self.adc_validator)
        self.adc_interval_le.setEchoMode(QtGui.QLineEdit.Normal)
        self.adc_interval_le.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.adc_interval_le.setMaxLength(4)
        self.adc_interval_le.setFixedWidth(30)
        
        label = QtGui.QLabel('Interval[s]')
        label.setAlignment(QtCore.Qt.AlignRight)
        label.setAlignment(QtCore.Qt.AlignVCenter)
        label.setStyleSheet("QLabel { font-size: 12px; background-color: rgb(0,0,0); color:rgb(255,255,255) ; }")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.adc_interval_le)
        hbox1.addWidget(label)

        self.adc_field_labels_qlabels = []        #List containing Static field Qlabels, do not change
        self.adc_field_values_qlabels = []       #List containing the value of the field, updated per packet

        self.ADCtimer = QtCore.QTimer(self)
        self.ADCtimer.setInterval(self.adc_interval)

        vbox = QtGui.QVBoxLayout()

        for i in range(len(field_name)):
            hbox = QtGui.QHBoxLayout()
            self.adc_field_labels_qlabels.append(QtGui.QLabel(field_name[i]))
            self.adc_field_labels_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            self.adc_field_values_qlabels.append(QtGui.QLabel(self.field_value[i]))
            self.adc_field_values_qlabels[i].setAlignment(QtCore.Qt.AlignLeft)
            hbox.addWidget(self.adc_field_labels_qlabels[i])
            hbox.addWidget(self.adc_field_values_qlabels[i])
            vbox.addLayout(hbox)
        vbox.addWidget(self.adc_auto_cb)
        vbox.addLayout(hbox1)
        self.adc_fr.setLayout(vbox)

    def initNet(self):
        self.ipAddrTextBox = QtGui.QLineEdit()
        self.ipAddrTextBox.setText("192.168.42.11")
        self.ipAddrTextBox.setInputMask("000.000.000.000;")
        self.ipAddrTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.ipAddrTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.ipAddrTextBox.setMaxLength(15)

        self.portTextBox = QtGui.QLineEdit()
        self.portTextBox.setText("2000")
        self.port_validator = QtGui.QIntValidator()
        self.port_validator.setRange(0,65535)
        self.portTextBox.setValidator(self.port_validator)
        self.portTextBox.setEchoMode(QtGui.QLineEdit.Normal)
        self.portTextBox.setStyleSheet("QLineEdit {background-color:rgb(255,255,255); color:rgb(0,0,0);}")
        self.portTextBox.setMaxLength(5)
        self.portTextBox.setFixedWidth(50)

        label = QtGui.QLabel('Status:')
        label.setAlignment(QtCore.Qt.AlignRight)
        self.net_label = QtGui.QLabel('Disconnected')
        self.net_label.setAlignment(QtCore.Qt.AlignLeft)
        self.net_label.setFixedWidth(150)

        self.connectButton = QtGui.QPushButton("Connect")
        self.net_label.setStyleSheet("QLabel {  font-weight:bold; color:rgb(255,0,0) ; }")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.ipAddrTextBox)
        hbox1.addWidget(self.portTextBox)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(label)
        hbox2.addWidget(self.net_label)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.connectButton)
        vbox.addLayout(hbox2)

        self.net_fr.setLayout(vbox)
    
    def updateIPAddress(self):
        ip_addr = self.ipAddrTextBox.text()
        self.relay_callback.set_ipaddr(ip_addr)

    def updatePort(self):
        port = self.portTextBox.text()
        self.relay_callback.set_port(port)

    def initControls(self):
        self.updateButton = QtGui.QPushButton("Update")
        self.resetButton = QtGui.QPushButton("Reset")
        self.readRelayButton = QtGui.QPushButton("Read Relay")
        self.readVoltButton = QtGui.QPushButton("Read ADCs")
        self.readStatusButton = QtGui.QPushButton("Read Status")

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.readRelayButton)
        hbox1.addWidget(self.readStatusButton)
        hbox1.addWidget(self.readVoltButton)

        hbox2 = QtGui.QHBoxLayout()
        #hbox.addStretch(1)
        hbox2.addWidget(self.updateButton)
        hbox2.addWidget(self.resetButton)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.button_fr.setLayout(vbox)

    def initSPDTCheckBoxes(self):
        hbox1 = QtGui.QHBoxLayout()

        for i in range(8):
            self.spdt_cb.append(Relay_QCheckBox(self, i+1  , 'SPDT'+str(i+1)  , 0, pow(2,i)))
            hbox1.addWidget(self.spdt_cb[i])
        hbox2 = QtGui.QHBoxLayout()
        for i in range(8):
            self.spdt_cb.append(Relay_QCheckBox(self, i+1+8, 'SPDT'+str(i+1+8), 0, pow(2,i)))
            hbox2.addWidget(self.spdt_cb[i+8])

        #for i in range(16): print str(self.spdt_cb[i].name)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.spdt_fr.setLayout(vbox)
    
    def initDPDTCheckBoxes(self):
        hbox1 = QtGui.QHBoxLayout()
        for i in range(8):
            self.dpdt_cb.append(Relay_QCheckBox(self, i+1, 'DPDT'+str(i+1), 1, pow(2,i)))
            hbox1.addWidget(self.dpdt_cb[i])
        hbox2 = QtGui.QHBoxLayout()
        for i in range(8):
            self.dpdt_cb.append(Relay_QCheckBox(self, i+1+8, 'DPDT'+str(i+1+8), 1, pow(2,i)))
            hbox2.addWidget(self.dpdt_cb[i+8])

        #for i in range(16): print str(self.dpdt_cb[i].name)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.dpdt_fr.setLayout(vbox)

    def initFrames(self):
        self.spdt_fr = QtGui.QFrame(self)
        self.spdt_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.spdt_fr.setFixedWidth(650)

        self.dpdt_fr = QtGui.QFrame(self)
        self.dpdt_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.dpdt_fr.setFixedWidth(650)

        self.adc_fr = QtGui.QFrame(self)
        self.adc_fr.setFrameShape(QtGui.QFrame.StyledPanel)

        self.button_fr = QtGui.QFrame(self)
        self.button_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_fr.setFixedWidth(445)

        self.net_fr = QtGui.QFrame(self)
        self.net_fr.setFrameShape(QtGui.QFrame.StyledPanel)
        self.net_fr.setFixedWidth(200)

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()

        hbox2.addWidget(self.net_fr)
        hbox2.addWidget(self.button_fr)        

        vbox.addWidget(self.spdt_fr)
        vbox.addWidget(self.dpdt_fr)
        vbox.addLayout(hbox2)
        
        hbox1.addLayout(vbox)
        hbox1.addWidget(self.adc_fr)

        self.setLayout(hbox1)

    def darken(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.black)
        palette.setColor(QtGui.QPalette.WindowText,QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text,QtCore.Qt.white)
        self.setPalette(palette)

    def getTimeStampGMT(self):
        return str(date.utcnow()) + " GMT | "

