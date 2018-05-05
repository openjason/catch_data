/***************************************************************
 * Name:      LogFileViewerMain.h
 * Purpose:   Defines Application Frame
 * Author:    JasonChan (openjc@outlook.com)
 * Created:   2018-03-05
 * Copyright: JasonChan ()
 * License:
 **************************************************************/

#ifndef LOGFILEVIEWERMAIN_H
#define LOGFILEVIEWERMAIN_H

//(*Headers(LogFileViewerFrame)
#include <wx/button.h>
#include <wx/filedlg.h>
#include <wx/frame.h>
#include <wx/menu.h>
#include <wx/panel.h>
#include <wx/richtext/richtextctrl.h>
#include <wx/sizer.h>
#include <wx/stattext.h>
#include <wx/statusbr.h>
#include <wx/timer.h>
//*)

class LogFileViewerFrame: public wxFrame
{
    public:

        LogFileViewerFrame(wxWindow* parent,wxWindowID id = -1);
        virtual ~LogFileViewerFrame();
        int refresh_log(void);

    private:

        //(*Handlers(LogFileViewerFrame)
        void OnQuit(wxCommandEvent& event);
        void OnAbout(wxCommandEvent& event);
        void OnButton2Click(wxCommandEvent& event);
        void OnButton2Click1(wxCommandEvent& event);
        void OnButton1Click(wxCommandEvent& event);
        void OnButton1Click1(wxCommandEvent& event);
        void OnResize(wxSizeEvent& event);
        void OnPanel1Resize(wxSizeEvent& event);
        void OnButton_quitClick(wxCommandEvent& event);
        void OnTimer1Trigger(wxTimerEvent& event);
        void OnTimer1Trigger1(wxTimerEvent& event);
        void OnTimer1Trigger2(wxTimerEvent& event);
        void OnRichTextCtrl1Text(wxCommandEvent& event);
        //*)

        //(*Identifiers(LogFileViewerFrame)
        static const long ID_BUTTON1;
        static const long ID_STATICTEXT1;
        static const long ID_BUTTON2;
        static const long ID_STATICTEXT2;
        static const long ID_BUTTON3;
        static const long ID_STATICTEXT3;
        static const long ID_PANEL2;
        static const long ID_RICHTEXTCTRL1;
        static const long ID_PANEL1;
        static const long ID_open_logf;
        static const long ID_man_refr;
        static const long idMenuQuit;
        static const long idMenuAbout;
        static const long ID_STATUSBAR1;
        static const long ID_TIMER1;
        //*)

        //(*Declarations(LogFileViewerFrame)
        wxButton* Button1;
        wxButton* Button2;
        wxButton* Button_quit;
        wxFileDialog* FileDialog1;
        wxMenuItem* MenuItem3;
        wxMenuItem* MenuItem4;
        wxPanel* Panel1;
        wxPanel* Panel2;
        wxRichTextCtrl* RichTextCtrl1;
        wxStaticText* StaticText1;
        wxStaticText* StaticText2;
        wxStaticText* StaticText3;
        wxStatusBar* StatusBar1;
        wxTimer Timer1;
        //*)

        DECLARE_EVENT_TABLE()
};

#endif // LOGFILEVIEWERMAIN_H
