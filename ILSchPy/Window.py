import sys
import math
import operator as op
import numpy as np
from Interpreter import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# 高亮编辑器
def format(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)

    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

## 语法字体颜色
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('darkGray'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}

## Python语法高亮
class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

## Scheme语法高亮
class SchemeHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Scheme language.
    """
    # Scheme keywords
    keywords = [
        'cons', 'car', 'cdr',
        'caar', 'cadr', 'cdar', 'cddr',
        'caaar', 'caadr', 'cadar', 'caddr',
        'cdaar', 'cdadr', 'cddar', 'cdddr',
        'length', 'list', 'append', 'void',
        'newline', 'display', 'displayln',
        'define', 'let', 'cond', 'if', 'begin',
        'lambda', 'and', 'or']
    '''['set!', 'let*',
        'null?', 'eq?', 'equal?',
        'number?', 'symbol?', 'pair?', 'list?',
    ]'''

    # Scheme operators
    operators = [
        '\+', '-', '\*', '/', 'remainder',
        '=', '<', '>', '<=', '>=',
        # Future operators
        '!=', '\%', '\*\*',
    ]

    # Scheme braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in SchemeHighlighter.keywords]
        # rules += [(r'\b(%s)\?\b' % w, 0, STYLES['Keyword'])
        #           for w in SchemeHighlighter.keywords_ask]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in SchemeHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in SchemeHighlighter.braces]

        # All other rules
        rules += [
            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdefine\b\s*(\w+)', 1, STYLES['defclass']),
            # (r'\bdefine\b\s*(\(\w+)', 1, STYLES['defclass']),

            # From ';' until a newline
            (r';[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

## 左侧数字部分
class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

## 编辑器主体
class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        
        # 高亮显示
        self.highlight = SchemeHighlighter(self.document())

        # 行号、当前行相关
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 12 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        # print('CodeEditor.updateLineNumberArea: rect.contains(self.viewport().rect()) = {}'.format(
        #     rect.contains(self.viewport().rect())))
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(228, 228, 228))  # 6: Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QColor(6))  # Qt.black)
                painter.setFont(QFont('Courier New', 12))
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                 Qt.AlignCenter, number)  # Right, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect();
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor(Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

        
# 窗体
class Form(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window Layout
        self.setWindowTitle('[*Untitled] - ILSchPy')
        self.settingWindowTitle = 'Settings - ILSchPy'
        self.setGeometry(150, 200, 800, 600)

        self.editor = CodeEditor()
        self.editor.setFont(QFont('Consolas', 15))
        # self.editor.setFont(QFont('Bookshelf Symbol 7', 15))

        self.text_res = QTextBrowser()
        self.text_res.setFont(QFont('Courier New', 13))

        self.layout = QGridLayout()
        self.layout.addWidget(self.editor, 0, 0, 5, 1)
        self.layout.addWidget(self.text_res, 5, 0, 3, 1)

        self.c_widget = QWidget()
        self.c_widget.setLayout(self.layout)
        self.setCentralWidget(self.c_widget)

        # Parameters
        self.filename = '*Untitled'        # file name & path
        self.settings = ''
        self.fileSaved = True            # current document saved
        self.fileSavedSucceed = 0        # a tmp var to solve when choosing 'Cancel'
        self.txtClearRun = False            # clear the text_res when running the code
        self.DebugFileOpen = True        # to debug things about files
        self.DebugRunSource = True        # to debug things about codes
        self.DebugSettings = True
        # self.settingFilePath = ''
        self.settingFileName = './data/settings.scp'

        self.editor.textChanged.connect(self.fileSetSaved)
        self.settingInitialize()

        # MENU FROM HERE
        self.statusBar()
        mainMenu = self.menuBar()

        # fileMenu: New, Save, Open
        fileMenu = mainMenu.addMenu('&File')

        newAction = QAction('&New', self)
        newAction.setShortcut(QKeySequence.New)
        newAction.triggered.connect(self.fileNew)

        saveAction = QAction('&Save', self)
        saveAction.setShortcut(QKeySequence.Save)
        saveAction.triggered.connect(self.fileSave)

        openAction = QAction('&Open', self)
        openAction.setShortcut(QKeySequence.Open)
        openAction.triggered.connect(self.fileOpen)

        fileMenu.addAction(newAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(openAction)

        # editMenu:
        editMenu = mainMenu.addMenu('&Edit')

        undoAction = QAction('&Undo', self)
        undoAction.setShortcut(QKeySequence.Undo)
        undoAction.triggered.connect(self.editor.undo)

        redoAction = QAction('&Redo', self)
        redoAction.setShortcut(QKeySequence.Redo)
        redoAction.triggered.connect(self.editor.redo)

        cutAction = QAction('Cu&t', self)
        cutAction.setShortcut(QKeySequence.Cut)
        cutAction.triggered.connect(self.editor.cut)

        copyAction = QAction('&Copy', self)
        copyAction.setShortcut(QKeySequence.Copy)
        copyAction.triggered.connect(self.editor.copy)

        pasteAction = QAction('&Paste', self)
        pasteAction.setShortcut(QKeySequence.Paste)
        pasteAction.triggered.connect(self.editor.paste)

        selectAllAction = QAction('Se&lect All', self)
        selectAllAction.setShortcut(QKeySequence.SelectAll)
        selectAllAction.triggered.connect(self.editor.selectAll)
        
        settingAction = QAction('&Settings', self)
        settingAction.setShortcut('Ctrl+Alt+S')
        settingAction.triggered.connect(self.settingsEdit)
        
        settingDefaultAction = QAction('&Default Settings', self)
        settingDefaultAction.setShortcut('Ctrl+Alt+D')
        settingDefaultAction.triggered.connect(self.settingsDefault)

        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)
        editMenu.addSeparator()
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(selectAllAction)
        editMenu.addSeparator()
        editMenu.addAction(settingAction)
        editMenu.addAction(settingDefaultAction)
        
        # runMenu:
        runMenu = mainMenu.addMenu('&Run')
        
        runAction = QAction('&Run', self)
        runAction.setShortcut('F5')
        runAction.triggered.connect(self.runCode)
        
        runMenu.addAction(runAction)
        

    def setTitle(self):
        self.setWindowTitle('[' + self.filename + '] - ILSchPy')

    def print_debug_info(self, c, str):
        if c == 'F' and self.DebugFileOpen:
            self.text_res.append('<font color="#6600cc"><b>[F] </b></font>' + str)
        elif c == 'R' and self.DebugRunSource:
            self.text_res.append('<font color="#6600cc"><b>[R] </b></font>' + str)
        elif c == 'S' and self.DebugSettings:
            self.text_res.append('<font color="#6600cc"><b>[S] </b></font>' + str)
    
    # File Menu
    def fileSetSaved(self, stat=False):
        if stat!= self.fileSaved:
            self.print_debug_info('F', '<i>saved: ' + str(self.fileSaved) + ' -> '+ str(stat) + '</i>')
            self.fileSaved = stat

    def fileAskSave(self):
        self.print_debug_info('F', '&nbsp;&nbsp;<font color="blue">fileAskSave:</font> fileSaved = ' + str(self.fileSaved))
        if not self.fileSaved:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Save changes to "' + self.filename + '"?')
            msg.setWindowTitle('Confirm')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            i = msg.exec_()
            # print(i)
            if i == QMessageBox.Cancel:
                self.fileSavedSucceed = -1
            elif i == QMessageBox.No:
                self.fileSavedSucceed = 0
            elif i == QMessageBox.Yes:
                tmp = self.fileSave()
                self.fileSavedSucceed = tmp
            self.print_debug_info('F', '&nbsp;&nbsp;MsgBoxRes = ' + str(self.fileSavedSucceed))
        else:
            self.fileSavedSucceed = 0

    def fileNew(self):   # New File
        self.print_debug_info('F', '<font color="red"><b>FileNew</b></font>')
        self.print_debug_info('F', '&nbsp;&nbsp;FileSavedSucceed = ' + str(self.fileSavedSucceed))
        self.fileAskSave()
        self.print_debug_info('F', '&nbsp;&nbsp;FileSavedSucceed = ' + str(self.fileSavedSucceed))
        if self.fileSavedSucceed == -1:
            return
        elif self.fileSavedSucceed == 0:
            self.filename = '*Untitled'
            self.editor.setPlainText('')
            self.fileSetSaved(True)
            self.setTitle()

    def fileSave(self):  # Save File
        self.print_debug_info('F', '<font color="red"><b>FileSave</b></font>')
        from os.path import isfile
        
        if self.windowTitle() == self.settingWindowTitle:
            # print('here!')
            file = open(self.filename, 'w')
            file.write(self.editor.toPlainText())
            file.close()
            self.fileSetSaved(True)
            return 0
        
        if self.filename == '*Untitled':
            fd = QFileDialog(self)
            self.filename = fd.getSaveFileName(self, 'Save File', '/Untitled', 'SchPy sourse (*.scp);;Racket source (*.rkt);;text (*.txt)')
            self.print_debug_info('F', '&nbsp;&nbsp;filename = ' + str(self.filename))
            self.filename = self.filename[0]
            if self.filename == '':
                self.filename = '*Untitled'
                return -1
        
        file = open(self.filename, 'w')
        file.write(self.editor.toPlainText())
        file.close()
        self.fileSetSaved(True)
        if self.windowTitle() != self.settingWindowTitle:
            self.setTitle()
        return 0

    def fileOpen(self):  # Open File
        self.print_debug_info('F', '<font color="red"><b>FileOpen</b></font>')
        self.fileAskSave()
        if self.fileSavedSucceed == -1:
            return
        elif self.fileSavedSucceed == 0:
            fd = QFileDialog(self)
            self.filename = fd.getOpenFileName(self, 'Open File', '', 'Scheme source (*.scp *.rkt *.txt)')
            self.print_debug_info('F', '&nbsp;&nbsp;filename = ' + str(self.filename))
            self.filename = self.filename[0]
            # print(self.filename)
            from os.path import isfile
            if isfile(self.filename):
                text = open(self.filename).read()
                self.print_debug_info('F', '  text = ' + str(text))
                self.editor.setPlainText(text)
                self.fileSetSaved(True)
                self.setTitle()
            else:
                self.filename = '*Untitled'
                self.editor.setPlainText('; Something Wrong in the Document')
                self.setTitle()

    # Edit Menu
    def settingInitialize(self):
        import os
        from os.path import isfile
        self.print_debug_info('S', '<b> Initialize the settings </b>')
        filepath = r'\Program Files\ILSchPy\data\ '
        filename = self.settingFileName # r'\Program Files\ILSchPy\data\settings.scp'
        # if not os.path.exists(filepath): 
        #     os.makedirs(filepath)
        # print(isfile(filename))
        if isfile(filename):
            text = open(filename).read()
            self.settings = text
            self.setSettings()
        else:
            # print('fuck it')
            return
            
    def settingsEdit(self):
        if self.windowTitle() == self.settingWindowTitle:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('You are in settingd editor now!')
            msg.setWindowTitle('Error')
            i = msg.exec_()
            return
        self.fileAskSave()
        if self.fileSavedSucceed == -1:
            return
        elif self.fileSavedSucceed == 0:
            import os
            from os.path import isfile
            filepath = r'\Program Files\ILSchPy\data\ '
            # self.filename = r'\Program Files\ILSchPy\data\settings.scp'
            self.filename = self.settingFileName
            if not os.path.exists(filepath): 
                os.makedirs(filepath)
            self.setWindowTitle(self.settingWindowTitle)
            # print(isfile(self.filename))
            if isfile(self.filename):
                # print(self.filename)
                text = open(self.filename).read()
                self.editor.setPlainText(text)
                # self.settings = text
                self.fileSetSaved(True)
            else:
                self.print_debug_info('S', 'cannot open the settings file')
                self.settingsDefault(1)
                
    def settingsDefault(self, index=0):
        if self.windowTitle() != self.settingWindowTitle and index == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('You can only use this in Settings Editor.')
            msg.setWindowTitle('Error')
            i = msg.exec_()
            return
        self.settings = '''; settings
(list dc ds df (fs 15) (ff "Consolas"))
            
; 本文档用于配置编辑器的基本信息，仅需将所需参数加入到list中即可

#| 相关变量说明：
(define df (open debug_file))   ;开启文件相关Debug工具
(define dc (open debug_code))   ;开启代码相关Debug工具
(define ds (open debug_set))    ;开启设置相关Debug工具
(define rc (open run_clear))    ;在运行代码前，清空输出框
(define fs (lambda (x) (set_font_size x)))  ;将字号设为x
(define ff (lambda (str) (set_font str)))   ;将字体设为str
祝你成功 |#
        '''
        self.editor.setPlainText(self.settings)
        self.fileSetSaved(False)
        
    def setSettings(self):
        setting_name = ['df', 'dc', 'ds', 'rc']
        setting_func = ['fs', 'ff']
        res = {'df': False, 'dc': False, 'ds': False, 'rc': False,
               'fs': 15, 'ff': 'Consolas'}
        settinglst = parse(pretrans('(' + self.settings + ' *RETURN* )'))[0]
        # print(settinglst)
        
        try:
            # settinglst = parse(pretrans('(' + self.settings + ' *RETURN* )'))[0]
            # print(settinglst)
            if settinglst[0] != 'list':
                self.print_debug_info('S', '<b>Error: </b> excepted: list')
                return False
            # print(res)
            for s in settinglst[1:]:
                # print(s)
                if isinstance(s, list):
                    op = s[0]
                    if op not in setting_func:
                        self.print_debug_info('S', '<b>Error: </b> something wrong in functions.')
                        return False
                    if op == 'fs':
                        res['fs'] = int(s[1])
                    elif op == 'ff':
                        # print(s[1][1])
                        res['ff'] = s[1][1]
                else:
                    if s not in setting_name:
                        self.print_debug_info('S', '<b>Error: </b> something wrong in settings - ' + str(s))
                        return False
                    res[s] = True
                
            self.DebugFileOpen = True if res['df'] else False
            self.DebugRunSource = True if res['dc'] else False
            self.DebugSettings = True if res['ds'] else False
            self.txtClearRun = True if res['rc']  else False
            self.print_debug_info('S', '<b>Settings Result:&nbsp;</b>' + str(res))
            # print(res)
            self.editor.setFont(QFont(res['ff'], res['fs']))
            
        except Exception as e:
            print(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Something Wrong in Settings Text')
            msg.setWindowTitle('Error')
            i = msg.exec_()
           
    
    # Run Menu
    def runCode(self):
        if self.windowTitle() == self.settingWindowTitle:
            # print('run settings')
            self.settings = self.editor.toPlainText()
            self.setSettings()
            return
        if self.txtClearRun:
            self.text_res.setText('')
        else:
            self.text_res.append('')
        
        print('Run Code >>> ')
        interpreter = Interpreter()
        run_code = self.editor.toPlainText()
        # print(run_code)
        # self.print_debug_info('R', '<font color = "red"><b> RunCode </b></font> <br> <b>Code:</b> ' + run_code)
        run_code = '( ' + run_code + ' *RETURN* )'
        run_code = parse(pretrans(run_code))
        for code in run_code:
            self.print_debug_info('R', '<font color = "red"><b> RunCode </b></font> <br> <b>Code:</b> ' + str(code))
            run_res = interpreter.getResult(code)
            self.text_res.append(str(run_res))
        del interpreter
        print()

# 对代码的预处理
def pretrans(code):
    code = code.replace('(', ' ( ').replace(')', ' ) ')
    code = code.replace('[', ' [ ').replace(']', ' ] ')
    code = code.replace('"', ' " ').replace(';', ' ; ')
    code = code.replace('#|', ' #| ').replace('|#', ' |# ')
    code = code.replace("'", " ' ").replace('\n', ' *RETURN* ')
    code = code.split()
    # print('- After pretrans: ', end='')
    # print(code)
    return code

def parse(exps):
    code = exps.pop(0)
    if code == '*RETURN*':
        return None
    elif code == ';':
        while exps[0] != '*RETURN*':
            exps.pop(0)
        exps.pop(0)
        return None
    elif code == '#|':
        while exps[0] != '|#':
            exps.pop(0)
        exps.pop(0)
        return None
    elif code == '(':
        res=[]
        while exps[0] != ')':
            res.append(parse(exps))
        exps.pop(0)
        while None in res:
            res.remove(None)
        return res
    elif code == '[':
        res=[]
        while exps[0] != ']':
            res.append(parse(exps))
        exps.pop(0)
        while None in res:
            res.remove(None)
        return res
    elif code == "'":
        val = exps.pop(0)
        return ['quoted', val]
    elif code == '"':
        res = []
        while exps[0] != '"':
            res.append(exps.pop(0))
        exps.pop(0)
        res_str = '"'
        res_str += " ".join(res)
        res_str += '"'
        return ['quoted', res_str]
    else:
        return atom(code)

def atom(code):
    try:
        return int(code)
    except ValueError:
        try:
            return float(code)
        except ValueError:
            return Symbol(code)

def to_Scheme_code(exps):
    return exps


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Form()
    form.show()
    sys.exit(app.exec_())
