# -*- coding: utf-8 -*-
# user defined imports
# PyQt4 imports
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

from databaseModels import Dbase, treeList  # databaseListModel
import Utilities.preprocessing as pp
#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.builder import make

# general imports
import numpy as np
import datetime as dt

class PlotWidget(qg.QWidget):
    """

    """
    def __init__(self, parent):
        qg.QWidget.__init__(self, parent)
        
        self.data = Dbase(DBaseName = None)
        self.y1Data = np.arange(0,100) #self.data.Query()
        self.y2Data = np.arange(0,100)
        self.xData = np.arange(0,100) #np.arange(0, len(self.yData))
        self.setMinimumSize(700, 600)
        #---guiqwt related attributes:
        self.plot = None
        self.curve_item = None
        #---
        
    def setup_widget(self, title):
        """Create the plot widget:
        """
        self.plot = CurvePlot(self)
        self.curve_item = (make.curve([], [], color='b'))
        self.second_curve_item = (make.curve([], [], color='g'))

        self.plot.add_item(self.curve_item)
        self.plot.add_item(self.second_curve_item)
        self.plot.set_antialiasing(True)

        self.databaseScroll = treeList(DBaseName = None)
        self.databaseScroll.setSortingEnabled(True)

        spacer = qg.QSpacerItem(30,40)
        
        preprocessData = qg.QGroupBox(u"preprocess data")
        
        # create buttons
        listButton = qg.QPushButton(u"Refresh list")
        processButton = qg.QPushButton(u"       run preprocessing       ")
        addwaveletButton = qg.QPushButton(u"  add wavelet spikes to DB  ")
        
        self.checkAddData = qg.QMessageBox()
        
        self.wavelet = qg.QCheckBox(u"wavelet filter      ")
        label1 = qg.QLabel("enter threshold value: ")
        self.waveletThreshold = qg.QLineEdit(u"10")

        

        # connect user actions with methods:
        self.connect(listButton, qc.SIGNAL('clicked()'), self.but_clicked)
        self.connect(processButton, qc.SIGNAL('clicked()'), 
                     self.run_preprocess)
        self.connect(self.databaseScroll, 
                     qc.SIGNAL("doubleClicked(QModelIndex)"), 
                     self.double_clicked)
        self.connect(addwaveletButton, qc.SIGNAL('clicked()'), 
                     self.add_data_to_DBase)
        
        vlayout = qg.QVBoxLayout()
        hlayout = qg.QHBoxLayout()

        
        vlayout.addWidget(self.databaseScroll)
        vlayout.addWidget(listButton)

        vlayout.addWidget(self.plot)
        vlayout.addSpacerItem(spacer)
        
        
        hlayout.addWidget(self.wavelet)
        hlayout.addWidget(label1)
        hlayout.addWidget(self.waveletThreshold)

        hlayout.addWidget(processButton)        
        hlayout.addWidget(addwaveletButton)
        preprocessData.setLayout(hlayout)
        vlayout.addWidget(preprocessData)
        
        self.setLayout(vlayout)
        
        self.update_curve()

                                             
    def run_preprocess(self):
        """
        """
        if self.wavelet.isChecked():
            try:
                yData = self.y1Data
                waveletFilt = pp.wavefilter(yData)
                self.y1Data = waveletFilt
                
                thresh = float(self.waveletThreshold.displayText())
                foo = self.y1Data > thresh
                self.y2Data = self.spikes = pp.spikeThreshold(foo)
                self.y2Data = self.y2Data * max(self.y1Data)
                
                index = self.databaseScroll
                root = index.parent().parent().row()
                neuron = index.parent().row()
                epoch = index.row()  
                
                r = self.databaseScroll
                self.data = Dbase(r, PRINT = 1)               
                n = self.databaseScroll
                epochs = self.data.GetTree(n)
                e = epochs[epoch]
                
                self.spikeOverwriteLoc = [r, n + '.' + e + '.spikes', n + '.' + e, 
                                          n, n + '_' + e + '_spikes']
                self.data.Data.CloseDatabase(PRINT=1)
                print 'spike handle: ', self.spikeOverwriteLoc[0:2]
                self.update_curve()
                
            except ValueError:
                print 'ValueError. Could not compute wave filter'
                pass


    def add_data_to_DBase(self):
        """
        """
        self.checkAddData.setText("Are you sure you want to add filtered \
                                spikes (green trace) to the DB?")
        self.checkAddData.setInformativeText("This will overwrite the existing\
                                                spike data.")
        self.checkAddData.setStandardButtons(qg.QMessageBox.Yes | qg.QMessageBox.No )
        self.checkAddData.setDefaultButton(qg.QMessageBox.Yes)
        choice = self.checkAddData.exec_() == qg.QMessageBox.Yes
        if choice:
            tim = dt.datetime.utcnow().ctime()
            
            self.data = Dbase(self.spikeOverwriteLoc[0], PRINT = 1)
            self.data.Data.RemoveChild(self.spikeOverwriteLoc[1], option=1)
            self.data.Data.AddData2Database('spikes', self.spikes,
                                            self.spikeOverwriteLoc[2])
            self.data.Data.AddGitVersion(self.spikeOverwriteLoc[3],
                                         Action = 'updated_{0}'.format(
                                         self.spikeOverwriteLoc[4] + 
                                         str(tim.day) + '_' +
                                         str(tim.month) + '_' +
                                         str(tim.year) ))
                                         
            self.data.Data.CloseDatabase(PRINT=1)
            
            """ add git version here """
            print 'spike data successfully overwritten.'

    
    def update_curve(self):
        """Update curve
        """
        self.curve_item.set_data(self.xData, self.y1Data)
        self.second_curve_item.set_data(self.xData, self.y2Data)
        self.plot.replot()
        self.plot.do_autoscale()
        
    def but_clicked(self):
        """
        when refresh button is clicked, the tree is refreshed
        """
        self.databaseScroll.refreshTree()
    
    def double_clicked(self):
        """
        when a name button is clicked, iterate over the model, 
        find the neuron with this name, and set the treeviews current item
        """
        index = self.databaseScroll.currentIndex()
        item = self.databaseScroll.currentItem()
        clickedCol = index.column()

        hasChild = True
        ind = index.parent()
        colCount = 1
        parents = []
        while hasChild:
            #find root index and parents
            root = ind.row()
            if root != -1:
                parent = str(self.databaseScroll.itemFromIndex(
                                        ind).text(clickedCol - colCount))
                parents.insert(0, parent)
            if root == -1:
                hasChild = False
                if parents == []:
                    parent = str(self.databaseScroll.itemFromIndex(
                                        index).text(0))
                    parents.insert(0, parent)
                    
            ind = ind.parent()
            colCount += 1

        name = str(item.text(clickedCol))
        print 'name: ', name
        print 'parents: ', parents
        
        if len(parents) == 1:
            parents.append('')
        if name[:-3] == '.h5':
            name = '/'
        
        kind = self.databaseScroll.GetDtype(parents[0], name, parents[1:])
        print kind
        #if dtype_ == 'np.array':
        #    clickedData = self.databaseScroll.GetData(parents[0], name, 
        #                                          parents[1:])
        #    print clickedData
        '''    
        if index.column() == 2:
            root = index.parent().parent().row()
            neuron = index.parent().row()
            epoch = index.row()
            print root, neuron, epoch
            r = self.databaseScroll
            self.data = Dbase(r, PRINT = 1)
            
            neurons = self.data.GetTree()         
            n = neurons[neuron]
                
            epochs = self.data.GetTree(n)
            e = epochs[epoch]
            
            if e != 'git':
            
                rawDataquery = self.data.Query(NeuronName = n, Epoch = e, DataName = 'rawData')
                try:
                    self.spikesDataquery = self.data.Query(NeuronName = n, Epoch = e, DataName = 'spikes')   
                    self.y1Data = rawDataquery
                    if max(self.y1Data) < 0:
                        self.y2Data = min(self.y1Data) * self.spikesDataquery
                    else:
                        self.y2Data = max(self.y1Data) * self.spikesDataquery
                except (TypeError, ValueError):
                    
                    print 'spike data not available.'
                    self.y2Data = self.y1Data
    
                self.xData = np.arange(0, len(self.y1Data))
                self.update_curve()
                self.data.Data.CloseDatabase(PRINT=1)
            
        if index.column() == 3:
            
            root = index.parent().parent().parent().row()
            neuron = index.parent().parent().row()
            epoch = index.parent().row()
            data = index.row()

            try:
                r = self.databaseScroll
                self.data = Dbase(r, PRINT = 1)
                
                neurons = self.data.GetTree()
                n = neurons[neuron]
                
                epochs = self.data.GetTree(n)
                e = epochs[epoch]
                
                if e != 'git':
                    d = self.databaseScroll.dataName[data] # account for git dataName
                    
                    if d != 'params':
    
                        query = self.data.Query( NeuronName = n, Epoch = e, DataName = d)
                    
                        if query.shape[0] > 1:
                            
                            self.y1Data = query
                            
                            try:
                                if max(self.y1Data) < 0:
                                    self.y2Data = min(self.y1Data) * self.spikesDataquery
                                else:
                                    self.y2Data = max(self.y1Data) * self.spikesDataquery
                            except TypeError:
                                    self.y2Data = self.y1Data
                             
                                
                            self.xData = np.arange(0, len(self.y1Data))
                            self.update_curve()
                        
                        if query.shape[0] == 1:
                            print ' '
                            print d, ': ', query[0]
                            
                    self.data.Data.CloseDatabase(PRINT=1)
                    
            except ValueError:
                pass
        
        if index.column() == 4:
            
            root = index.parent().parent().parent().parent().row()
            neuron = index.parent().parent().parent().row()
            epoch = index.parent().parent().row()
            data = index.parent().row()
            param = index.row()

            r = self.databaseScroll.DataBasesOpen[root]
            self.data = Dbase(r, PRINT = 1)           
            neurons = self.data.GetTree()
            n = neurons[neuron]
            
            epochs = self.data.GetTree(n)
            e = epochs[epoch]
            
            d = self.databaseScroll.dataName[data] # account for git dataName
            p = self.databaseScroll.paramName[param]
            query =  self.data.Query(NeuronName = n, Epoch = e, 
                                     DataName = d + '.' + p)[0]
            print ' '
            print p, ': ', query
            self.data.Data.CloseDatabase(PRINT=1)
        '''