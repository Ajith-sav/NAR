# /////////////////////\\\\\\\\\\\\\\\\\\\\\\
# importing required libraries
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from printer import PrintHandler
import pyperclip as pc
import errors
import about
import datetime
import os
import sys

# /////////////////////\\\\\\\\\\\\\\\\\\\\\\\\

class BookMarkToolBar(QToolBar):
    bookmarkClicked = pyqtSignal(QUrl, str)

    def __init__(self, parent=None):
        super(BookMarkToolBar, self).__init__(parent)
        self.actionTriggered.connect(self.onActionTriggered)
        self.bookmark_list = []

    def setBoorkMarks(self, bookmarks):
        for bookmark in bookmarks:
            self.addBookMarkAction(bookmark["title"], bookmark["url"])

    def addBookMarkAction(self, title, url):
        bookmark = {"title": title, "url": url}
        fm = QFontMetrics(self.font())
        if bookmark not in self.bookmark_list:
            text = fm.elidedText(title, Qt.ElideRight, 150)
            action = self.addAction(text)
            action.setData(bookmark)
            self.bookmark_list.append(bookmark)

    @pyqtSlot(QAction)
    def onActionTriggered(self, action):
        bookmark = action.data()
        self.bookmarkClicked.emit(bookmark["url"], bookmark["title"])


# --------------------------------------------------------------------------------

# main window
class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.defaultUrl = QUrl() 

        # this will hide the title bar
        #self.setWindowFlag(Qt.FramelessWindowHint)

        # creating a tab widget
        self.tabs = QTabWidget()

         # font for tabs
        self.tabs.setFont(QFont('Arial', 9))

        # making document mode true
        self.tabs.setDocumentMode(True)

        # adding action when double clicked
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

        # adding action when tab is changed
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # making tabs closeable
        self.tabs.setTabsClosable(True)

        # adding action when tab close is requested
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        # open new tab when Ctrl+T pressed
        #AddNewTabKeyShortcut = QShortcut("Ctrl+T", self)
        #AddNewTabKeyShortcut.activated.connect(lambda: self.add_new_tab(QUrl('https://duckduckgo.com'), "New tab"))

        # Close current tab on Ctrl+W
        #CloseCurrentTabKeyShortcut = QShortcut("Ctrl+W", self)
        #CloseCurrentTabKeyShortcut.activated.connect(lambda: self.close_current_tab(self.tabs.currentIndex()))

        # Exit browser on shortcut Ctrl+Shift+W
        #ExitBrowserShortcutKey = QShortcut("Ctrl+Shift+W", self)
        #ExitBrowserShortcutKey.activated.connect(sys.exit)
        
        # making tabs as central widget
        self.setCentralWidget(self.tabs)

        # creating a status bar
        # bottom of the window
        self.status = QStatusBar()
 
        # setting status bar to the main window
        self.setStatusBar(self.status)

        # creating a tool bar for navigation
        navtb = QToolBar("Navigation")
 
        # set tool bar icon size
        navtb.setIconSize(QSize(30, 30))
        # adding tool bar to the main window
        self.addToolBar(navtb)

        # creating back action
        back_btn = QAction(QIcon("Icon/left.png"), "Back", self)
        # setting status tip
        back_btn.setStatusTip("Back to previous page")
        # create the shortcut for back button
        back_btn.setShortcut("Alt+Left")
        # adding action to back button
        # making current tab to go back
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        # adding this to the navigation tool bar
        navtb.addAction(back_btn)

        # similarly adding next button
        next_btn = QAction(QIcon("Icon/right-arrow.png"), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.setShortcut("Alt+Right")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        # similarly adding reload button
        reload_btn = QAction(QIcon("Icon/reloading.png"), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.setShortcut("Ctrl+R")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        # creating home action
        home_btn = QAction(QIcon("Icon/home.png"), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.setShortcut("Ctrl+H")

        # adding action to home button
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # similarly adding stop action
        stop_btn = QAction(QIcon("Icon/stop-sign.png"), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.setShortcut("Escape")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        # =================================================================
        # set url
        self.urlbar = QLineEdit(self)
        # lineedit current font
        font = self.urlbar.font()
        # change it's size
        font.setPointSize(10)
        # set font
        self.urlbar.setFont(font)
        self.urlbar.setFrame(False)
        self.urlbar.returnPressed.connect(self.onReturnPressed)
        self.urlbar.setShortcutEnabled(True)
        self.urlbar.setToolTip(self.urlbar.text())
        
        # set the focus on url bar shortcut Ctrl+E
        FocusOnAddressBar = QShortcut("Ctrl+E", self)
        FocusOnAddressBar.activated.connect(self.urlbar.setFocus)


        # ==================================================================

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # set the favoriteButton
        self.favoriteButton = QToolButton()
        self.favoriteButton.setIcon(QIcon("Icon/book.png"))
        self.favoriteButton.clicked.connect(self.addFavoriteClicked)

        # set the button end of the url
        toolbar = self.addToolBar("Address bar")
        toolbar.setIconSize(QSize(30, 30))
        toolbar.addWidget(self.urlbar)
        toolbar.addWidget(self.favoriteButton)

        # Action to Bookmark
        self.addToolBarBreak()
        self.bookmarkToolbar = BookMarkToolBar("Bookmark")
        self.bookmarkToolbar.bookmarkClicked.connect(self.add_new_tab)
        self.addToolBar(self.bookmarkToolbar)
        self.readSettings()
  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # The context menu
        context_menu = QMenu(self)

        # Set the object's name
        context_menu.setObjectName("ContextMenu")

        # Button for the three dot context menu button
        ContextMenuButton = QPushButton(self)
        ContextMenuButton.setObjectName("ContextMenuButton")

        # Enable three dot menu by pressing Alt+F
        ContextMenuButton.setShortcut("Alt+F")

        # Give the three dot image to the Qpushbutton
        ContextMenuButton.setIcon(QIcon("Icon/more.png"))

        # Add icon
        ContextMenuButton.setObjectName("ContextMenuTriggerButn")
        ContextMenuButton.setToolTip("More")

        # Add the context menu to the three dot context menu button
        ContextMenuButton.setMenu(context_menu)

        # """Actions of the three dot context menu"""
        # """Add icon to more button"""

        # Add new tab
        newTabAction = QAction("New tab", self)
        newTabAction.setIcon(QIcon("Icon/plus_+_48px.png"))
        newTabAction.triggered.connect(lambda: self.add_new_tab(QUrl('https://duckduckgo.com'), "New tab"))
        newTabAction.setToolTip("Add a new tab")
        newTabAction.setShortcut("Ctrl+T")
        context_menu.addAction(newTabAction)

        # Close tab action
        CloseTabAction = QAction("Close tab", self)
        CloseTabAction.setIcon(QIcon("Icon/close_window_52px.png"))
        CloseTabAction.triggered.connect(lambda: self.close_current_tab(self.tabs.currentIndex()))
        CloseTabAction.setToolTip("Close current tab")
        CloseTabAction.setShortcut("Ctrl+W")
        context_menu.addAction(CloseTabAction)

        context_menu.addSeparator()


        # Feature to copy site url
        CopySiteAddress = QAction(
            QIcon(( "Icon/link.png")),
            "Copy site url",
            self,
           )
        CopySiteAddress.triggered.connect(self.CopySiteLink)
        CopySiteAddress.setToolTip("Copy current site address")
        context_menu.addAction(CopySiteAddress)

        # Fetaure to go to copied site url
        PasteAndGo = QAction(
            QIcon("Icon/paste.png"),
            "Paste and go",
            self,
        )
        PasteAndGo.triggered.connect(self.PasteUrlAndGo)
        PasteAndGo.setToolTip("Go to the an url copied to your clipboard")
        context_menu.addAction(PasteAndGo)
        
        #add separtor
        context_menu.addSeparator()

         # Save page as
        SavePageAs = QAction("Save page as", self)
        SavePageAs.setIcon(QIcon("Icon/floppy-disk.png"))
        SavePageAs.setToolTip("Save current page to this device")
        SavePageAs.setShortcut("Ctrl+S")
        SavePageAs.triggered.connect(self.save_page)
        context_menu.addAction(SavePageAs)

       
        # Print this page action
        PrintThisPageAction = QAction("Print this page", self)
        PrintThisPageAction.setIcon(QIcon("Icon/printing.png"))
        PrintThisPageAction.triggered.connect(self.print_this_page)
        PrintThisPageAction.setShortcut("Ctrl+P")
        PrintThisPageAction.setToolTip("Print current page")
        context_menu.addAction(PrintThisPageAction)

        # Print with preview
        PrintPageWithPreview = QAction(
            QIcon("Icon/print.png"),
            "Print page with preview",
            self,
        )
        PrintPageWithPreview.triggered.connect(self.PrintWithPreview)
        PrintPageWithPreview.setShortcut("Ctrl+Shift+P")
        context_menu.addAction(PrintPageWithPreview)

        # Save page as PDF
        SavePageAsPDF = QAction(
            QIcon("Icon/download.png"),
            "Save as PDF",
            self,
        )
        SavePageAsPDF.triggered.connect(self.save_as_pdf)
        context_menu.addAction(SavePageAsPDF)
        

        context_menu.addSeparator()
        
        # About action
        AboutAction = QAction("About", self)
        AboutAction.setIcon(QIcon("Icon/about icon.png"))
        AboutAction.triggered.connect(self.about)
        AboutAction.setToolTip("About")
        AboutAction.setShortcut("Ctrl+A")
        context_menu.addAction(AboutAction)

        #exit button in QMenu
        ExitAction = QAction("Exit", self)
        ExitAction.setIcon(QIcon("Icon/log-out.png"))
        ExitAction.triggered.connect(sys.exit)
        ExitAction.setToolTip("Exit")
        ExitAction.setShortcut("Ctrl+Shift+W")
        context_menu.addAction(ExitAction)

        # set more button to end of address bar(ContextMenuButton)
        toolbar.addWidget(ContextMenuButton)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1!!!!!!!!!!!!!

        # creating first tab
        self.add_new_tab(QUrl('https://duckduckgo.com'), 'Homepage')

        # showing all the components
        self.show()

        # opening window in maximized size (full screen)
        self.showMaximized()

        # setting window title

        self.setWindowTitle("NAR Browser")

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    

    def onReturnPressed(self):
        # set user input in urlbar -(self.urlbar.text())-
        self.tabs.currentWidget().setUrl(QUrl.fromUserInput(self.urlbar.text()))

    def readSettings(self):
        setting = QSettings()
        self.defaultUrl = setting.value("defaultUrl", QUrl('https://duckduckgo.com'))
        self.bookmarkToolbar.setBoorkMarks(setting.value("bookmarks", []))
  

    def saveSettins(self):
        settings = QSettings()
        settings.setValue("defaultUrl", self.defaultUrl)
        settings.setValue("bookmarks", self.bookmarkToolbar.bookmark_list)

    def closeEvent(self, event):
        self.saveSettins()
        super(MainWindow, self).closeEvent(event)

    def addFavoriteClicked(self):
        loop = QEventLoop()

        def callback(resp):
            setattr(self, "title", resp)
            loop.quit()

        browser = self.tabs.currentWidget()
        browser.page().runJavaScript("(function() { return document.title;})();", callback)
        url= browser.url()
        loop.exec_()
        self.bookmarkToolbar.addBookMarkAction(getattr(self, "title"), url)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # method for adding new tab
    def add_new_tab(self, qurl=None, label="New tab"):

        # if url is blank
        if qurl is None:
            # creating a search engine url
            qurl = QUrl('https://duckduckgo.com')

        # creating a QWebEngineView object
        browser = QWebEngineView()

        # setting url to browser
        browser.setUrl(qurl)

        # setting tab index
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # adding action to the browser when url is changed
        # update the url
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        # adding action to the browser when loading is finished
        # set the tab title
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))


    # when double clicked is pressed on tabs
    def tab_open_doubleclick(self, i):

        # checking index i.e
        # No tab under the click
        if i == -1:
            # creating a new tab
            self.add_new_tab()
 
    # when tab is changed
    def current_tab_changed(self, i):

        # get the curl
        qurl = self.tabs.currentWidget().url()

        # update the url
        self.update_urlbar(qurl, self.tabs.currentWidget())

        # update the title
        self.update_title(self.tabs.currentWidget())

    # when tab is closed
    def close_current_tab(self, i):

        # if there is only one tab
        if self.tabs.count() < 2:
            # do nothing
            return

        # else remove the tab
        self.tabs.removeTab(i)

    # method for updating the title
    def update_title(self, browser):

        # if signal is not from the current tab
        if browser != self.tabs.currentWidget():
            # do nothing
            return

        # get the page title
        title = self.tabs.currentWidget().page().title()

        # set the window title
        self.setWindowTitle("% s - NAR Browser" % title)

    # action to go to home
    def navigate_home(self):

        # go to google
        self.tabs.currentWidget().setUrl(QUrl("https://duckduckgo.com"))

    # method for navigate to url
    def navigate_to_url(self):

        # get the line edit text
        # convert it to QUrl object
        q = QUrl(self.urlbar.text())

        # if scheme is blank
        if q.scheme() == "":
            # set scheme
            q.setScheme("http")

        # set the url
        self.tabs.currentWidget().setUrl(q)

    # method to update the url
    def update_urlbar(self, q, browser=None):

        # If this signal is not from the current tab, ignore
        if browser != self.tabs.currentWidget():
            return

        # set text to the url bar
        self.urlbar.setText(q.toString())

        # set cursor position
        self.urlbar.setCursorPosition(0)

    # paste the url go to search 
    def PasteUrlAndGo(self):
        self.add_new_tab(QUrl(pc.paste()), self.tabs.currentWidget().title())         

    # Copy url of currently viewed page to clipboard
    def CopySiteLink(self):
        pc.copy(self.tabs.currentWidget().url().toString())
  
    # save the page in html page
    def save_page(self):
        filepath, filter = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save Page As",
            directory="",
            filter="Webpage, complete (*.htm *.html);;Hypertext Markup Language (*.htm *.html);;All files (*.*)",
        )
        try:
            if filter == "Hypertext Markup Language (*.htm *.html)":
                self.tabs.currentWidget().page().save(
                    filepath, format=QWebEngineDownloadItem.MimeHtmlSaveFormat
                )

            elif filter == "Webpage, complete (*.htm *.html)":
                self.tabs.currentWidget().page().save(
                    filepath, format=QWebEngineDownloadItem.CompleteHtmlSaveFormat
                )

        except:
            self.showErrorDlg()  

    # Print handler
    def print_this_page(self):
        try:
            handler_print = PrintHandler()
            handler_print.setPage(self.tabs.currentWidget().page())
            handler_print.print()

        except:
            self.showErrorDlg()  

    # Print page with preview
    def PrintWithPreview(self):
        handler = PrintHandler()
        handler.setPage(self.tabs.currentWidget().page())
        handler.printPreview()
               
    # Save as pdf
    def save_as_pdf(self):
        filename, filter = QFileDialog.getSaveFileName(
            parent=self, caption="Save as", filter="PDF File (*.pdf);;All files (*.*)"
        )

        self.tabs.currentWidget().page().printToPdf(filename)

    def showErrorDlg(self):
         dlg = errors.errorMsg()
         dlg.exec_()
                   
    # connect the button to about code
    def about(self):
        self.AboutDialogue = about.AboutDialog()
        self.AboutDialogue.show()


# creating a PyQt5 application
app = QApplication(sys.argv)

# setting name to the application
app.setApplicationName("NAR Browser")

# Setting title window icon
app.setWindowIcon(QIcon("Icon/NAR.jpg"))

# creating MainWindow object
window = MainWindow()

# loop
app.exec_()
