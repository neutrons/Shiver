"""PyQt widget for the Reduction Parameters section"""
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog
)

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel


class ReductionParameters(QGroupBox):
    """Generate reduction parameter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Reduction Parameters")
        layout = QGridLayout()
        self.setLayout(layout)
        
        #validators
        self.double_validator = QtGui.QDoubleValidator(self)
        self.positive_double_validator = QtGui.QDoubleValidator(self)
        self.positive_double_validator.setBottom(0.0)
        
        #mask
        layout.addWidget(QLabel("Mask"),0,0)

        self.mask_path = QLineEdit()
        self.mask_path.setReadOnly(True)
        layout.addWidget(self.mask_path,0,1,1,2)
        
        self.mask_browse = QPushButton("Browse")
        self.mask_browse.clicked.connect(self._mask_browse)
        layout.addWidget(self.mask_browse,0,3)      
        
        #normalization
        layout.addWidget(QLabel("Normalization"),1,0)

        self.norm_path = QLineEdit()
        self.norm_path.setReadOnly(True)
        layout.addWidget(self.norm_path,1,1,1,2)
        
        self.norm_browse = QPushButton("Browse")
        self.norm_browse.clicked.connect(self._norm_browse)
        layout.addWidget(self.norm_browse,1,3)
        
        self.input_widget = QWidget()
        input_layout = QHBoxLayout()
        
        #Ei
        ei_label = QLabel("Ei")
        input_layout.addWidget(ei_label)

        self.ei_input = QLineEdit()
        self.ei_input.setFixedWidth(60)
        input_layout.addWidget(self.ei_input)
        
        #T0
        t0_label = QLabel("T0")
        t0_label.setStyleSheet("margin-left:20px;")                
        input_layout.addWidget(t0_label)
        
        self.t0_input = QLineEdit()
        self.t0_input.setFixedWidth(60)
        input_layout.addWidget(self.t0_input)

        input_layout.setContentsMargins(0, 10, 0, 10)
        self.input_widget.setLayout(input_layout)
        layout.addWidget(self.input_widget,2,0,1,4)  
        
        self.sample_btn = QPushButton("Sample Options")
        self.sample_btn.clicked.connect(self.set_sample_btn)

        layout.addWidget(self.sample_btn,3,0)       

        self.adv_btn = QPushButton("Advanced Options")
        self.adv_btn.clicked.connect(self.set_adv_btn)
        layout.addWidget(self.adv_btn,3,3)    
                 
        
        self.pol_btn = QPushButton("Polarization Options")
        self.pol_btn.clicked.connect(self.set_pol_btn)
        layout.addWidget(self.pol_btn,4,0)  

        self.polarization_label = QLabel("Unpolarized Data")
        layout.addWidget(self.polarization_label,4,1)

        #set validators
        self.ei_input.setValidator(self.positive_double_validator)
        self.t0_input.setValidator(self.double_validator)

    def _mask_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Processed Nexus file (*.nxs);;All Files (*)")
        )
        if not filename:
            return
        else:
            self.mask_path.setText(filename)
      
    def _norm_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Processed Nexus file (*.nxs);;All Files (*)")
        )
        if not filename:
            return
        else:
            self.norm_path.setText(filename)       

    def set_sample_btn(self):
        """Open the dialog to set sample parameters"""    
        sample = SampleView()
        sample_model = SampleModel()
        SamplePresenter(sample, sample_model)

        # open the dialog
        dialog = sample.start_dialog()
        dialog.populate_sample_parameters()
        dialog.exec_()
    

    def set_adv_btn(self):
        """Open the dialog to set advanced options"""        
        pass  

    def set_pol_btn(self):
        """Open the dialog to set polarization options"""        
        pass                        
