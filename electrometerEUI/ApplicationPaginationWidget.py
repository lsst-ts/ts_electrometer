
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QStackedLayout, QListWidget)

class ApplicationPaginationWidget(QWidget):
    def __init__(self, Electrometer):
        QWidget.__init__(self)
        self.Electrometer = Electrometer
        self.mainLayout = QHBoxLayout()
        self.pageLayout = QStackedLayout()
        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self.changePage)
        self.mainLayout.addWidget(self.list)
        self.mainLayout.addLayout(self.pageLayout)
        self.setLayout(self.mainLayout)
        self.pages = []

    def addPage(self, text, widget):
        self.pages.append([text, widget])
        self.list.addItem(text)
        self.pageLayout.addWidget(widget)

    def changePage(self):
        items = self.list.selectedItems()
        if len(items) > 0:
            text = items[0].text()
            for pages in self.pages:
                if pages[0] == text:
                    self.pageLayout.setCurrentWidget(pages[1])