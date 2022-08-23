# importing required libraries
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWebEngineWidgets import * 
from PyQt5.QtPrintSupport import *
from printer import PrintHandler
import pyperclip as pc
import errors
import about
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

#.............................................................................

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

        self.tabs.setStyleSheet("""QTabWidget::pane { /* The tab widget frame */
                                  border-top: 2px solid #C2C7CB;
                                  position: absolute;
                                  top: -0.5em;
                                  }
                                  QTabBar::tab { /* set size of the tab*/
                                    width: 200px;
                                    height: 13px;
                                    padding: 0px;
                                  }
                                  QTabWidget::tab-bar {
                                  alignment: center;
                                  }

                                   /* Style the tab using the tab sub-control. Note that
                                   it reads QTabBar _not_ QTabWidget */
                                  QTabBar::tab {
                                  background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                  stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                                  border: 2px solid #C4C4C3;
                                  border-bottom-color: #C2C7CB; /* same as the pane color */
                                  border-top-left-radius: 4px;
                                  border-top-right-radius: 4px;
                                  min-width: 6ex;
                                  padding: 2px;
                                  }

                                  QTabBar::tab:selected, QTabBar::tab:hover {
                                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                    stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                                  }

                                  QTabBar::tab:selected {
                                   border-color: #9B9B9B;
                                   border-bottom-color: #C2C7CB; /* same as pane color */
                                   }""")

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
         
        # making tabs as central widget
        self.setCentralWidget(self.tabs)

        # creating a status bar
        # bottom of the window
        self.status = QStatusBar()

        self.status.setStyleSheet("""QStatusBar {
                                     background: white;
                                     }

                                     QStatusBar::item {
                                     border: 1px solid red;
                                     border-radius: 3px;
                                     }""")

        # setting status bar to the main window
        self.setStatusBar(self.status)

        # creating a tool bar for navigation
        self.navtb = QToolBar("Navigation")

        self.navtb.setStyleSheet("""QToolBar {
                               background: #f2f2f2;
                               spacing: 2px; /* spacing between items in the tool bar */
                               }""")
        # set tool bar icon size
        self.navtb.setIconSize(QSize(30, 25))
        # adding tool bar to the main window
        self.addToolBar(self.navtb)

        # creating back action
        back_btn = QAction(QIcon("Icon/left.png"), "Back", self)
        # setting status tip
        back_btn.setStatusTip("Back")
        # create the shortcut for back button
        back_btn.setShortcut("Alt+Left")
        # adding action to back button
        # making current tab to go back
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        # adding this to the navigation tool bar
        self.navtb.addAction(back_btn)

        #add separtor
        self.navtb.addSeparator()

        # similarly adding next button
        next_btn = QAction(QIcon("Icon/right-arrow.png"), "Forward", self)
        next_btn.setStatusTip("Forward")
        next_btn.setShortcut("Alt+Right")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navtb.addAction(next_btn)

        #add separtor
        self.navtb.addSeparator()

        # similarly adding reload button
        self.reload_btn = QAction(QIcon("Icon/reloading.png"), "Reload", self)
        self.reload_btn.setStatusTip("Reload page")
        self.reload_btn.setShortcut("Ctrl+R")
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navtb.addAction(self.reload_btn)

        #add separtor
        self.navtb.addSeparator()

        # creating home action
        home_btn = QAction(QIcon("Icon/home.png"), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.setShortcut("Ctrl+H")
        # adding action to home button
        home_btn.triggered.connect(self.navigate_home)
        self.navtb.addAction(home_btn)

        #add separtor
        self.navtb.addSeparator()
        # =======================================================
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
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
        self.urlbar.setPlaceholderText("Search...")
        self.urlbar.setToolTip(self.urlbar.text())
        self.urlbar.setClearButtonEnabled(True)
        #set https icon in urlbar
        self.action = self.urlbar.addAction(
            app.style().standardIcon(QStyle.StandardPixmap.SP_VistaShield),
            QLineEdit.ActionPosition.LeadingPosition
            )
        self.layout.addWidget(self.urlbar)
        self.setStyleSheet("""
            QLineEdit{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            padding-top:3px;
            padding-left:6px;
            padding-bottom:3px;
            border:2px solid transparent;
            border-radius: 5px;
            font-size:15px;
            background-color: #e6e6e6;
            font-weight: 500;
            color: black;
            max-width: 1000%;
            height: 25px;
            }
            QLineEdit:focus{
                border-color:#52a2f8;
                background: white;
            }
            QLineEdit:hover{
                border-color:#0000ff;
            }
            """)
        # set the focus on url bar shortcut Ctrl+E
        FocusOnAddressBar = QShortcut("Ctrl+E", self)
        FocusOnAddressBar.activated.connect(self.urlbar.setFocus)
        
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # set the favoriteButton
        self.favoriteButton = QToolButton()
        self.favoriteButton.setStyleSheet("""QToolButton { /* all types of tool button */
                                             border: 0px solid #8f8f91;
                                             border-radius: 1px;
                                             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0,
                                             stop: 0 #f6f7fa, stop: 1 #dadbde);
                                             }""")
        self.favoriteButton.setIcon(QIcon("Icon/book.png"))
        self.favoriteButton.setToolTip("Bookmark the site")
        self.favoriteButton.clicked.connect(self.addFavoriteClicked)

        # set the button end of the url
        self.toolbar = self.addToolBar("Address bar")
        self.toolbar.setIconSize(QSize(30, 30))
        self.toolbar.addWidget(self.urlbar)
        self.toolbar.addWidget(self.favoriteButton)
        
        # Action to Bookmark
        self.addToolBarBreak()
        self.bookmarkToolbar = BookMarkToolBar("Bookmark")
        self.bookmarkToolbar.bookmarkClicked.connect(self.add_new_tab)
        self.addToolBar(self.bookmarkToolbar)
        self.readSettings()

        #add separtor
        self.toolbar.addSeparator() 
 
        self.search_btn = QPushButton(self)
        self.search_btn.setObjectName("search_btn")
        self.search_btn.setToolTip("Search the site")
        self.search_btn.setShortcut("Enter")
        self.search_btn.setIcon(QIcon("Icon/transparency.png"))
        self.search_btn.clicked.connect(self.onReturnPressed)
        self.search_btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color :  #f2f2f2;"
                             "height: 27px;"
                             "width: 30%;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : #33adff;"
                             "}"
                             )
        self.search_btn = self.toolbar.addWidget(self.search_btn)

        #add separtor
        self.toolbar.addSeparator() 

        self.stop_btn = QPushButton(self)
        self.stop_btn.setObjectName("stop_butn")
        self.stop_btn.setToolTip("Stop loading current page")
        self.stop_btn.setShortcut("Escape")
        self.stop_btn.setIcon(QIcon("Icon/stop-sign.png"))
        self.stop_btn.clicked.connect(self.stop_loading_tab)
        self.stop_btn.setStyleSheet("QPushButton"
                             "{"
                             "background-color :  #f2f2f2;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : #33adff;"
                             "}"
                             )
                            
        # Added stop button
        self.stop_action = self.toolbar.addWidget(self.stop_btn)
        self.stop_btn.setIconSize(QSize(28, 28))
        # Set stop action to be invisible
       
        #add separtor
        self.toolbar.addSeparator() 
 #-------------------------------------------------------------------       

        # The context menu
        context_menu = QMenu(self)

        # Set the object's name
        context_menu.setObjectName("ContextMenu")

        context_menu.setStyleSheet("""QMenu {
                                      background-color:  #f2f2f2; /* sets background of the menu */
                                      border: 1px solid black;
                                      }
                                      QMenu::item {
                                      background-color: transparent;
                                      } 
                                      QMenu::item:selected { /* when user selects item using mouse or keyboard */
                                      background-color:  #33adff;
                                        }""")

        # Button for the three dot context menu button
        ContextMenuButton = QPushButton(self)
        ContextMenuButton.setObjectName("ContextMenuButton")

        # adding background color to button
        # and background color to pressed button
        ContextMenuButton.setStyleSheet("QPushButton"
                             "{"
                             "background-color :  #f2f2f2;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : #33adff;"
                             "}"
                             )
  
        # Enable three dot menu by pressing Alt+F
        ContextMenuButton.setShortcut("Alt+F")

        # Give the three dot image to the Qpushbutton
        ContextMenuButton.setIcon(QIcon("Icon/more.png"))

        ContextMenuButton.setIconSize(QSize(15, 29))

        # Add icon
        ContextMenuButton.setObjectName("ContextMenuTriggerButn")
        ContextMenuButton.setToolTip("More")

        # Add the context menu to the three dot context menu button
        ContextMenuButton.setMenu(context_menu)

        # """Actions of the three dot context menu"""
        """Add icon to more button"""

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
        CopySiteAddress = QAction(QIcon(( "Icon/link.png")), "Copy site url", self, )
        CopySiteAddress.triggered.connect(self.CopySiteLink)
        CopySiteAddress.setToolTip("Copy current site address")
        context_menu.addAction(CopySiteAddress)

        # Fetaure to go to copied site url
        PasteAndGo = QAction(QIcon("Icon/paste.png"), "Paste and go", self, )
        PasteAndGo.triggered.connect(self.PasteUrlAndGo)
        PasteAndGo.setToolTip("Go to the an url copied to your clipboard")
        context_menu.addAction(PasteAndGo)
       
        #add separtor
        context_menu.addSeparator()
        
         # Open page
        OpenPgAction = QAction("Open", self)
        OpenPgAction.setIcon(QIcon("Icon/open.png"))
        OpenPgAction.setToolTip("Open html file")
        OpenPgAction.setShortcut("Ctrl+O")
        OpenPgAction.triggered.connect(self.open_local_file)
        context_menu.addAction(OpenPgAction)

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
        PrintPageWithPreview = QAction(QIcon("Icon/print.png"), "Print page with preview", self, )
        PrintPageWithPreview.triggered.connect(self.PrintWithPreview)
        PrintPageWithPreview.setShortcut("Ctrl+Shift+P")
        context_menu.addAction(PrintPageWithPreview)

        # Save page as PDF
        SavePageAsPDF = QAction(QIcon("Icon/download.png"), "Save as PDF", self, )
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
        self.toolbar.addWidget(ContextMenuButton)

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
    @pyqtSlot(int)
    def loadProgressHandler(self, prog):
        if self.tabs.currentWidget() is not self.sender():
            return

        loading = prog < 100

        self.stop_btn.setVisible(loading)
        self.reload_btn.setVisible(not loading) 
    
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

        browser.loadProgress.connect(self.loadProgressHandler)

        # Full screen enable
        browser.settings().setAttribute(
           QWebEngineSettings.FullScreenSupportEnabled, True
        )
        
        browser.page().fullScreenRequested.connect(
            lambda request, browser=browser: self.handle_fullscreen_requested(
                request, browser
            )
        )

        """ adding action to the browser when url is changed """
        # update the url
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        """ adding action to the browser when loading is finished """
        # set the tab title
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))
 
        #request full screen 
        browser.page().fullScreenRequested.connect(
            lambda request, browser=browser: self.handle_fullscreen_requested(
                request, browser
            )
        )
    
    #set the video in full screen mode
    def handle_fullscreen_requested(self, request, browser):
        request.accept()

        if request.toggleOn():
            self.showFullScreen()
            self.statusBar().hide()
            self.navtb.hide()
            self.toolbar.hide()
            self.bookmarkToolbar.hide()
            self.tabs.tabBar().hide()
        else:
            self.showMaximized()
            self.statusBar().show()
            self.navtb.show()
            self.toolbar.show()
            self.bookmarkToolbar.show()
            self.tabs.tabBar().show()

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

        # go to dockdockgo
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
        self.urlbar.setCursorPosition(-1)

    def stop_loading_tab(self):
        if self.tabs.currentWidget() is None:
            return

        self.tabs.currentWidget().stop()    

    # paste the url go to search 
    def PasteUrlAndGo(self):
        self.add_new_tab(QUrl(pc.paste()), self.tabs.currentWidget().title())         

    # Copy url of currently viewed page to clipboard
    def CopySiteLink(self):
        pc.copy(self.tabs.currentWidget().url().toString())
        
 # Function to open a local file

    def open_local_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open file",
            directory="",
            filter="Hypertext Markup Language (*.htm *.html *.mhtml);;All files (*.*)",
        )
        if filename:
            try:
                with open(filename, "r", encoding="utf8") as f:
                    opened_file = f.read()
                    self.tabs.currentWidget().setHtml(opened_file)

            except:
                dlg = errors.fileErrorDialog()
                dlg.exec_()

        self.urlbar.setText(filename)       
  
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

# set dark therme to mainwindow____________________
"""#qApp.setStyle("Fusion")

#dark_palette = QPalette()
#dark_palette.setColor(QPalette.Window, QColor(53, 53, 53)) 
#dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
#dark_palette.setColor(QPalette.Button, QColor(53, 53, 53)) 
#dark_palette.setColor(QPalette.HighlightedText, Qt.red) 

#qApp.setPalette(dark_palette)
#qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }") """
#___________________________________________________

# setting name to the application
app.setApplicationName("NAR Browser")

# Setting title window icon
app.setWindowIcon(QIcon("Icon/main/internet.png"))

# creating MainWindow object
window = MainWindow()

# loop
app.exec_()
