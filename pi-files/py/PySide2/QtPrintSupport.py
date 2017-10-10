from PySide2.QtGui import QPagedPaintDevice as _QPagedPaintDevice
from PySide2.QtWidgets import QDialog as _QDialog

class _Object(object):
    __dict__ = None


from . import QtWidgets as _QtWidgets

class QPrintPreviewWidget(_QtWidgets.QWidget):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def currentPage(*args, **kwargs):
        pass
    
    
    def fitInView(*args, **kwargs):
        pass
    
    
    def fitToWidth(*args, **kwargs):
        pass
    
    
    def orientation(*args, **kwargs):
        pass
    
    
    def pageCount(*args, **kwargs):
        pass
    
    
    def print_(*args, **kwargs):
        pass
    
    
    def setAllPagesViewMode(*args, **kwargs):
        pass
    
    
    def setCurrentPage(*args, **kwargs):
        pass
    
    
    def setFacingPagesViewMode(*args, **kwargs):
        pass
    
    
    def setLandscapeOrientation(*args, **kwargs):
        pass
    
    
    def setOrientation(*args, **kwargs):
        pass
    
    
    def setPortraitOrientation(*args, **kwargs):
        pass
    
    
    def setSinglePageViewMode(*args, **kwargs):
        pass
    
    
    def setViewMode(*args, **kwargs):
        pass
    
    
    def setVisible(*args, **kwargs):
        pass
    
    
    def setZoomFactor(*args, **kwargs):
        pass
    
    
    def setZoomMode(*args, **kwargs):
        pass
    
    
    def updatePreview(*args, **kwargs):
        pass
    
    
    def viewMode(*args, **kwargs):
        pass
    
    
    def zoomFactor(*args, **kwargs):
        pass
    
    
    def zoomIn(*args, **kwargs):
        pass
    
    
    def zoomMode(*args, **kwargs):
        pass
    
    
    def zoomOut(*args, **kwargs):
        pass
    
    
    AllPagesView = None
    
    
    CustomZoom = None
    
    
    FacingPagesView = None
    
    
    FitInView = None
    
    
    FitToWidth = None
    
    
    SinglePageView = None
    
    
    ViewMode = None
    
    
    ZoomMode = None
    
    
    __new__ = None
    
    
    paintRequested = None
    
    
    previewChanged = None
    
    
    staticMetaObject = None


class QAbstractPrintDialog(_QDialog):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addEnabledOption(*args, **kwargs):
        pass
    
    
    def enabledOptions(*args, **kwargs):
        pass
    
    
    def exec_(*args, **kwargs):
        pass
    
    
    def fromPage(*args, **kwargs):
        pass
    
    
    def isOptionEnabled(*args, **kwargs):
        pass
    
    
    def maxPage(*args, **kwargs):
        pass
    
    
    def minPage(*args, **kwargs):
        pass
    
    
    def printRange(*args, **kwargs):
        pass
    
    
    def printer(*args, **kwargs):
        pass
    
    
    def setEnabledOptions(*args, **kwargs):
        pass
    
    
    def setFromTo(*args, **kwargs):
        pass
    
    
    def setMinMax(*args, **kwargs):
        pass
    
    
    def setOptionTabs(*args, **kwargs):
        pass
    
    
    def setPrintRange(*args, **kwargs):
        pass
    
    
    def toPage(*args, **kwargs):
        pass
    
    
    AllPages = None
    
    
    CurrentPage = None
    
    
    DontUseSheet = None
    
    
    locals()['None'] = None
    
    
    PageRange = None
    
    
    PrintCollateCopies = None
    
    
    PrintCurrentPage = None
    
    
    PrintDialogOption = None
    
    
    PrintDialogOptions = None
    
    
    PrintPageRange = None
    
    
    PrintRange = None
    
    
    PrintSelection = None
    
    
    PrintShowPageSize = None
    
    
    PrintToFile = None
    
    
    Selection = None
    
    
    __new__ = None
    
    
    staticMetaObject = None


class QPageSetupDialog(_QDialog):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def done(*args, **kwargs):
        pass
    
    
    def exec_(*args, **kwargs):
        pass
    
    
    def open(*args, **kwargs):
        pass
    
    
    def printer(*args, **kwargs):
        pass
    
    
    def setVisible(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    staticMetaObject = None


class QPrintEngine(_Object):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def abort(*args, **kwargs):
        pass
    
    
    def metric(*args, **kwargs):
        pass
    
    
    def newPage(*args, **kwargs):
        pass
    
    
    def printerState(*args, **kwargs):
        pass
    
    
    def property(*args, **kwargs):
        pass
    
    
    def setProperty(*args, **kwargs):
        pass
    
    
    PPK_CollateCopies = None
    
    
    PPK_ColorMode = None
    
    
    PPK_CopyCount = None
    
    
    PPK_Creator = None
    
    
    PPK_CustomBase = None
    
    
    PPK_CustomPaperSize = None
    
    
    PPK_DocumentName = None
    
    
    PPK_Duplex = None
    
    
    PPK_FontEmbedding = None
    
    
    PPK_FullPage = None
    
    
    PPK_NumberOfCopies = None
    
    
    PPK_Orientation = None
    
    
    PPK_OutputFileName = None
    
    
    PPK_PageMargins = None
    
    
    PPK_PageOrder = None
    
    
    PPK_PageRect = None
    
    
    PPK_PageSize = None
    
    
    PPK_PaperName = None
    
    
    PPK_PaperRect = None
    
    
    PPK_PaperSize = None
    
    
    PPK_PaperSource = None
    
    
    PPK_PaperSources = None
    
    
    PPK_PrinterName = None
    
    
    PPK_PrinterProgram = None
    
    
    PPK_QPageLayout = None
    
    
    PPK_QPageMargins = None
    
    
    PPK_QPageSize = None
    
    
    PPK_Resolution = None
    
    
    PPK_SelectionOption = None
    
    
    PPK_SupportedResolutions = None
    
    
    PPK_SupportsMultipleCopies = None
    
    
    PPK_WindowsPageSize = None
    
    
    PrintEnginePropertyKey = None
    
    
    __new__ = None


class QPrinter(_QPagedPaintDevice):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def abort(*args, **kwargs):
        pass
    
    
    def actualNumCopies(*args, **kwargs):
        pass
    
    
    def collateCopies(*args, **kwargs):
        pass
    
    
    def colorMode(*args, **kwargs):
        pass
    
    
    def copyCount(*args, **kwargs):
        pass
    
    
    def creator(*args, **kwargs):
        pass
    
    
    def devType(*args, **kwargs):
        pass
    
    
    def docName(*args, **kwargs):
        pass
    
    
    def doubleSidedPrinting(*args, **kwargs):
        pass
    
    
    def duplex(*args, **kwargs):
        pass
    
    
    def fontEmbeddingEnabled(*args, **kwargs):
        pass
    
    
    def fromPage(*args, **kwargs):
        pass
    
    
    def fullPage(*args, **kwargs):
        pass
    
    
    def getPageMargins(*args, **kwargs):
        pass
    
    
    def isValid(*args, **kwargs):
        pass
    
    
    def metric(*args, **kwargs):
        pass
    
    
    def newPage(*args, **kwargs):
        pass
    
    
    def numCopies(*args, **kwargs):
        pass
    
    
    def orientation(*args, **kwargs):
        pass
    
    
    def outputFileName(*args, **kwargs):
        pass
    
    
    def outputFormat(*args, **kwargs):
        pass
    
    
    def pageOrder(*args, **kwargs):
        pass
    
    
    def pageRect(*args, **kwargs):
        pass
    
    
    def pageSize(*args, **kwargs):
        pass
    
    
    def paintEngine(*args, **kwargs):
        pass
    
    
    def paperName(*args, **kwargs):
        pass
    
    
    def paperRect(*args, **kwargs):
        pass
    
    
    def paperSize(*args, **kwargs):
        pass
    
    
    def paperSource(*args, **kwargs):
        pass
    
    
    def printEngine(*args, **kwargs):
        pass
    
    
    def printProgram(*args, **kwargs):
        pass
    
    
    def printRange(*args, **kwargs):
        pass
    
    
    def printerName(*args, **kwargs):
        pass
    
    
    def printerState(*args, **kwargs):
        pass
    
    
    def resolution(*args, **kwargs):
        pass
    
    
    def setCollateCopies(*args, **kwargs):
        pass
    
    
    def setColorMode(*args, **kwargs):
        pass
    
    
    def setCopyCount(*args, **kwargs):
        pass
    
    
    def setCreator(*args, **kwargs):
        pass
    
    
    def setDocName(*args, **kwargs):
        pass
    
    
    def setDoubleSidedPrinting(*args, **kwargs):
        pass
    
    
    def setDuplex(*args, **kwargs):
        pass
    
    
    def setEngines(*args, **kwargs):
        pass
    
    
    def setFontEmbeddingEnabled(*args, **kwargs):
        pass
    
    
    def setFromTo(*args, **kwargs):
        pass
    
    
    def setFullPage(*args, **kwargs):
        pass
    
    
    def setMargins(*args, **kwargs):
        pass
    
    
    def setNumCopies(*args, **kwargs):
        pass
    
    
    def setOrientation(*args, **kwargs):
        pass
    
    
    def setOutputFileName(*args, **kwargs):
        pass
    
    
    def setOutputFormat(*args, **kwargs):
        pass
    
    
    def setPageMargins(*args, **kwargs):
        pass
    
    
    def setPageOrder(*args, **kwargs):
        pass
    
    
    def setPageSize(*args, **kwargs):
        pass
    
    
    def setPageSizeMM(*args, **kwargs):
        pass
    
    
    def setPaperName(*args, **kwargs):
        pass
    
    
    def setPaperSize(*args, **kwargs):
        pass
    
    
    def setPaperSource(*args, **kwargs):
        pass
    
    
    def setPrintProgram(*args, **kwargs):
        pass
    
    
    def setPrintRange(*args, **kwargs):
        pass
    
    
    def setPrinterName(*args, **kwargs):
        pass
    
    
    def setResolution(*args, **kwargs):
        pass
    
    
    def setWinPageSize(*args, **kwargs):
        pass
    
    
    def supportedResolutions(*args, **kwargs):
        pass
    
    
    def supportsMultipleCopies(*args, **kwargs):
        pass
    
    
    def toPage(*args, **kwargs):
        pass
    
    
    def winPageSize(*args, **kwargs):
        pass
    
    
    Aborted = None
    
    
    Active = None
    
    
    AllPages = None
    
    
    Auto = None
    
    
    Cassette = None
    
    
    Cicero = None
    
    
    Color = None
    
    
    ColorMode = None
    
    
    CurrentPage = None
    
    
    CustomSource = None
    
    
    DevicePixel = None
    
    
    Didot = None
    
    
    DuplexAuto = None
    
    
    DuplexLongSide = None
    
    
    DuplexMode = None
    
    
    DuplexNone = None
    
    
    DuplexShortSide = None
    
    
    Envelope = None
    
    
    EnvelopeManual = None
    
    
    Error = None
    
    
    FirstPageFirst = None
    
    
    FormSource = None
    
    
    GrayScale = None
    
    
    HighResolution = None
    
    
    Idle = None
    
    
    Inch = None
    
    
    Landscape = None
    
    
    LargeCapacity = None
    
    
    LargeFormat = None
    
    
    LastPageFirst = None
    
    
    LastPaperSource = None
    
    
    Lower = None
    
    
    Manual = None
    
    
    MaxPageSource = None
    
    
    Middle = None
    
    
    Millimeter = None
    
    
    NativeFormat = None
    
    
    OnlyOne = None
    
    
    Orientation = None
    
    
    OutputFormat = None
    
    
    PageOrder = None
    
    
    PageRange = None
    
    
    PaperSource = None
    
    
    PdfFormat = None
    
    
    Pica = None
    
    
    Point = None
    
    
    Portrait = None
    
    
    PrintRange = None
    
    
    PrinterMode = None
    
    
    PrinterResolution = None
    
    
    PrinterState = None
    
    
    ScreenResolution = None
    
    
    Selection = None
    
    
    SmallFormat = None
    
    
    Tractor = None
    
    
    Unit = None
    
    
    Upper = None
    
    
    __new__ = None


class QPrinterInfo(_Object):
    def __copy__(*args, **kwargs):
        pass
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def __nonzero__(*args, **kwargs):
        """
        x.__nonzero__() <==> x != 0
        """
    
        pass
    
    
    def defaultDuplexMode(*args, **kwargs):
        pass
    
    
    def description(*args, **kwargs):
        pass
    
    
    def isDefault(*args, **kwargs):
        pass
    
    
    def isNull(*args, **kwargs):
        pass
    
    
    def isRemote(*args, **kwargs):
        pass
    
    
    def location(*args, **kwargs):
        pass
    
    
    def makeAndModel(*args, **kwargs):
        pass
    
    
    def printerName(*args, **kwargs):
        pass
    
    
    def state(*args, **kwargs):
        pass
    
    
    def supportedDuplexModes(*args, **kwargs):
        pass
    
    
    def supportedPaperSizes(*args, **kwargs):
        pass
    
    
    def supportedResolutions(*args, **kwargs):
        pass
    
    
    def supportedSizesWithNames(*args, **kwargs):
        pass
    
    
    def supportsCustomPageSizes(*args, **kwargs):
        pass
    
    
    def availablePrinterNames(*args, **kwargs):
        pass
    
    
    def availablePrinters(*args, **kwargs):
        pass
    
    
    def defaultPrinter(*args, **kwargs):
        pass
    
    
    def defaultPrinterName(*args, **kwargs):
        pass
    
    
    def printerInfo(*args, **kwargs):
        pass
    
    
    __new__ = None


class QPrintPreviewDialog(_QDialog):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def done(*args, **kwargs):
        pass
    
    
    def open(*args, **kwargs):
        pass
    
    
    def printer(*args, **kwargs):
        pass
    
    
    def setVisible(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    paintRequested = None
    
    
    staticMetaObject = None


class QPrintDialog(QAbstractPrintDialog):
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def done(*args, **kwargs):
        pass
    
    
    def exec_(*args, **kwargs):
        pass
    
    
    def open(*args, **kwargs):
        pass
    
    
    def options(*args, **kwargs):
        pass
    
    
    def setOption(*args, **kwargs):
        pass
    
    
    def setOptions(*args, **kwargs):
        pass
    
    
    def setVisible(*args, **kwargs):
        pass
    
    
    def testOption(*args, **kwargs):
        pass
    
    
    __new__ = None
    
    
    accepted = None
    
    
    staticMetaObject = None



