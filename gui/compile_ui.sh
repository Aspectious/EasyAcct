#!/bin/zsh
echo Compiling Main Window
pyuic6 EasyAcct.ui -o gui_main.py
echo Compiling Connection Manager
pyuic6 EasyAcct_ConnDialogBox.ui -o gui_conn.py
echo Compiling Account Editor
pyuic6 EasyAcct_AcctEditor.ui -o gui_acctedit.py
echo Compiling Balance Editor
pyuic6 EasyAcct_BalEditor.ui -o gui_baledit.py
echo Compiling Transaction History Viewer
pyuic6 EasyAcct_Transhistory.ui -o gui_transhistory.py
echo Done!