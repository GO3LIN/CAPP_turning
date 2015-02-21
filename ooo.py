import sys
import os
import subprocess
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from PyQt4 import QtCore, QtGui
import OCC.Display.pyqt4Display
from OCC.STEPControl import STEPControl_Reader
from OCC.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
import parseStep
from OCC.Graphic3d import *
from OCC.Quantity import Quantity_Color

from first import Ui_Form
import config_control_design as stepCode
import recognition

class Main(QtGui.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        #super(Ui_Form, self).__init__()
        #self.setupUi(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.aResShape = None
        self.aResStock = None
        self.closed_s = None
        self.stock = stepCode.closed_shell
        self.stock.points = []
        self.stock.sd = 0.0
        self.ui.importButton.clicked.connect(self.importClicked)
        self.ui.separateButton.clicked.connect(self.separateClicked)
        self.ui.stockButton.clicked.connect(self.stockClicked)
        self.ui.checkMButton.clicked.connect(self.checkMClicked)
        self.ui.recognitionButton.clicked.connect(self.recognitionClicked)
        self.ui.clearButton.clicked.connect(self.clearClicked)
        #w = self.ui.tabWidget_2.widget(0)
        self.ui.viewer = OCC.Display.pyqt4Display.qtViewer3d(self.ui.view3d)
        self.ui.stockViewer = OCC.Display.pyqt4Display.qtViewer3d(self.ui.stockView)
        self.ui.deltaViewer = OCC.Display.pyqt4Display.qtViewer3d(self.ui.deltaView)

        la = QtGui.QVBoxLayout(self.ui.view3d)
        la.addWidget(self.ui.viewer)
        la2 = QtGui.QVBoxLayout(self.ui.stockView)
        la2.addWidget(self.ui.stockViewer)
        la3 = QtGui.QVBoxLayout(self.ui.deltaView)
        la3.addWidget(self.ui.deltaViewer)

        #Tree Widget
        

        # Place the widget in the center of the screen
        screen = QtGui.QDesktopWidget().screenGeometry()
        mysize = self.geometry()
        hpos = ( screen.width() - mysize.width() ) / 2
        vpos = ( screen.height() - mysize.height() - mysize.height() ) / 2
        self.move(hpos, vpos)

    def recognitionClicked(self):
        if(self.closed_s == None):
            self.closed_s = parseStep.readStep(self.currentStep)
        reco = recognition.recognition(self.closed_s, self.stock)
        cylinder_res = reco.process('cylinder')
        face_res = reco.process('face')

        #self.ui.recoCylinder.setText(str(reco_res.max_diameter))
        self.ui.treeWidget.clear()
        self.fillTreeCylinderFeature(cylinder_res)
        self.fillTreeFaceFeature(face_res)
    def fillTreeFaceFeature(self, results):
        face_feature = QtGui.QTreeWidgetItem(self.ui.treeWidget)
        face_feature.setText(0, 'Face Feature')
        items = []

        if(results.leftFound):
            item = QtGui.QTreeWidgetItem(face_feature)
            item.setText(0, 'Left y coordinate: '+str(results.vp_min_y))
            items.append(item)
            for af in results.min_af_list:
                item = QtGui.QTreeWidgetItem(face_feature)
                item.setText(0, af.stepLine)
                items.append(item)
        if(results.rightFound):
            item = QtGui.QTreeWidgetItem(face_feature)
            item.setText(0, 'Right y coordinate: '+str(results.vp_max_y))
            items.append(item)
            for af in results.max_af_list:
                item = QtGui.QTreeWidgetItem(face_feature)
                item.setText(0, af.stepLine)
                items.append(item)
        self.ui.treeWidget.addTopLevelItems(items)

    def fillTreeCylinderFeature(self, results):
        cylinder_feature = QtGui.QTreeWidgetItem(self.ui.treeWidget)
        cylinder_feature.setText(0, 'Cylinder Feature')
        items = []

        if(results.max_diameter==0):
            item = QtGui.QTreeWidgetItem(cylinder_feature)
            item.setText(0, 'No cylinder feature found.')
            items.append(item)
        else:
            item = QtGui.QTreeWidgetItem(cylinder_feature)
            item.setText(0, 'Max diameter: '+str(results.max_diameter)+'mm')
            items.append(item)
            for af in results.advanced_faces:
                item = QtGui.QTreeWidgetItem(cylinder_feature)
                item.setText(0, af.stepLine)
                items.append(item)
        self.ui.treeWidget.addTopLevelItems(items)
        
    
    def checkMClicked(self):
       # print self.aResShape[0].Location().IsEqual(self.aResShape[1].Location())
        cutted = BRepAlgoAPI_Cut(self.aResStock, self.aResShape).Shape()
        #print self.aResShape[0].IsEqual(self.are)
        self.ui.deltaViewer._display.EraseAll()
        self.ui.deltaViewer._display.DisplayShape(cutted, transparency=0.5, update=True)
        print cutted.IsNull()
        #print self.aResShape[0].IsEqual(self.aResShape[1])


    def stockClicked(self):
        fili = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        self.stock = parseStep.readStep(fili)
        for face in self.stock.cfs_faces:
            if isinstance(face.face_geometry, stepCode.cylindrical_surface):
                for oe in iter(face.bounds).next().bound.edge_list:
                    eg =oe.edge_element.edge_geometry
                    if isinstance(eg, stepCode.circle):
                        self.stock.points.append(eg.position.location.coordinates)
                self.stock.sd = face.face_geometry.radius *2
                self.ui.stockSD.setText(self.ui.stockSD.text()+' '+str(self.stock.sd)+' mm')
                break

        self.ui.stockSL.setText(self.ui.stockSL.text()+' '+str(abs(self.stock.points[0][1]-self.stock.points[1][1]))+' mm')
        self.ui.stockViewer._display.EraseAll()
        self.drawStock(fili)

    def clearClicked(self):
        subprocess.Popen(['python',os.getcwd()+os.path.sep+'ooo.py'])
        sys.exit(0)

    def separateClicked(self):
        self.closed_s = parseStep.readStep(self.currentStep)
        self.ui.gtdText.setText(str(parseStep.printStep(self.closed_s)))

    def drawStock(self, stepFile):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(str(stepFile))
         
        if status == IFSelect_RetDone:  # check status
            failsonly = False
            step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
            step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)

            ok = step_reader.TransferRoot(1)
            _nbs = step_reader.NbShapes()
            self.aResStock = step_reader.Shape(1)
            couleur = Quantity_Color()
            Quantity_Color.Argb2color(00000,couleur)
            
            self.ui.stockViewer._display.DisplayShape(self.aResStock, update=True, transparency=0.5, material=Graphic3d_NOM_STEEL)
            #self.modelTab._display.DisplayColoredShape(self.aResShape, update=True, color=couleur)
        else:
            print("Error: can't read file.")
            sys.exit(0)

    def drawShape(self, stepFile, different=False):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(str(stepFile))
         
        if status == IFSelect_RetDone:  # check status
            failsonly = False
            step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
            step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)

            ok = step_reader.TransferRoot(1)
            _nbs = step_reader.NbShapes()
            shape = step_reader.Shape(1)
            self.aResShape = shape
            couleur = Quantity_Color()
            Quantity_Color.Argb2color(00000,couleur)

            if different:
                mat = Graphic3d_NOM_STEEL
            else:
                mat = None
            
            self.ui.viewer._display.DisplayShape(shape, update=True, transparency=0.5, material=mat)
            #self.modelTab._display.DisplayColoredShape(self.aResShape, update=True, color=couleur)
        else:
            print("Error: can't read file.")
            sys.exit(0)

    def setShape(self, stepFile):
        self.drawShape(stepFile)
        #self.drawShape('cy1.stp')

        #self.pushButton.setText("Import STEP file of a part")

    def importClicked(self):
        fili = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        self.ui.viewer._display.EraseAll()
        self.setShape(fili)
        self.currentStep = str(fili)
        fname = open(fili)
        data = fname.read()
        self.ui.stepText.setText(data)
        fname.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    window.ui.viewer.InitDriver()
    window.ui.stockViewer.InitDriver()
    window.ui.deltaViewer.InitDriver()

    sys.exit(app.exec_())