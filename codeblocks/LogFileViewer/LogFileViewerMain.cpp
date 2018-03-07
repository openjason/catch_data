/***************************************************************
 * Name:      LogFileViewerMain.cpp
 * Purpose:   Code for Application Frame
 * Author:    JasonChan (openjc@outlook.com)
 * Created:   2018-03-05
 * Copyright: JasonChan ()
 * License:
 **************************************************************/

#include "LogFileViewerMain.h"
#include <wx/msgdlg.h>
#include "string"
#include <fstream>
#include <iostream>
#include <time.h>
#include <stdio.h>

//(*InternalHeaders(LogFileViewerFrame)
#include <wx/intl.h>
#include <wx/string.h>
//*)

//helper functions
enum wxbuildinfoformat {
    short_f, long_f };

wxString wxbuildinfo(wxbuildinfoformat format)
{
    wxString wxbuild(wxVERSION_STRING);

    if (format == long_f )
    {
#if defined(__WXMSW__)
        wxbuild << _T("-Windows");
#elif defined(__UNIX__)
        wxbuild << _T("-Linux");
#endif

#if wxUSE_UNICODE
        wxbuild << _T("-Unicode build");
#else
        wxbuild << _T("-ANSI build");
#endif // wxUSE_UNICODE
    }

    return wxbuild;
}

//(*IdInit(LogFileViewerFrame)
const long LogFileViewerFrame::ID_BUTTON1 = wxNewId();
const long LogFileViewerFrame::ID_STATICTEXT1 = wxNewId();
const long LogFileViewerFrame::ID_BUTTON2 = wxNewId();
const long LogFileViewerFrame::ID_STATICTEXT2 = wxNewId();
const long LogFileViewerFrame::ID_BUTTON3 = wxNewId();
const long LogFileViewerFrame::ID_STATICTEXT3 = wxNewId();
const long LogFileViewerFrame::ID_PANEL2 = wxNewId();
const long LogFileViewerFrame::ID_RICHTEXTCTRL1 = wxNewId();
const long LogFileViewerFrame::ID_PANEL1 = wxNewId();
const long LogFileViewerFrame::idMenuQuit = wxNewId();
const long LogFileViewerFrame::idMenuAbout = wxNewId();
const long LogFileViewerFrame::ID_STATUSBAR1 = wxNewId();
const long LogFileViewerFrame::ID_TIMER1 = wxNewId();
//*)

BEGIN_EVENT_TABLE(LogFileViewerFrame,wxFrame)
    //(*EventTable(LogFileViewerFrame)
        EVT_TIMER(TIMER_ID, MyFrame::OnTimer)
    //*)
END_EVENT_TABLE()

LogFileViewerFrame::LogFileViewerFrame(wxWindow* parent,wxWindowID id)
{
    //(*Initialize(LogFileViewerFrame)
    wxBoxSizer* BoxSizer1;
    wxFlexGridSizer* FlexGridSizer1;
    wxMenu* Menu1;
    wxMenu* Menu2;
    wxMenuBar* MenuBar1;
    wxMenuItem* MenuItem1;
    wxMenuItem* MenuItem2;

    Create(parent, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE, _T("wxID_ANY"));
    SetClientSize(wxSize(1045,600));
    Panel1 = new wxPanel(this, ID_PANEL1, wxPoint(176,192), wxDefaultSize, wxTAB_TRAVERSAL|wxFULL_REPAINT_ON_RESIZE, _T("ID_PANEL1"));
    FlexGridSizer1 = new wxFlexGridSizer(2, 1, 0, 1);
    Panel2 = new wxPanel(Panel1, ID_PANEL2, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL, _T("ID_PANEL2"));
    BoxSizer1 = new wxBoxSizer(wxHORIZONTAL);
    Button1 = new wxButton(Panel2, ID_BUTTON1, _("Label"), wxDefaultPosition, wxDefaultSize, 0, wxDefaultValidator, _T("ID_BUTTON1"));
    BoxSizer1->Add(Button1, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText1 = new wxStaticText(Panel2, ID_STATICTEXT1, _("Label"), wxDefaultPosition, wxDefaultSize, 0, _T("ID_STATICTEXT1"));
    BoxSizer1->Add(StaticText1, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Button2 = new wxButton(Panel2, ID_BUTTON2, _("Ë¢ÐÂ"), wxDefaultPosition, wxDefaultSize, 0, wxDefaultValidator, _T("ID_BUTTON2"));
    BoxSizer1->Add(Button2, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText2 = new wxStaticText(Panel2, ID_STATICTEXT2, _("Label"), wxDefaultPosition, wxDefaultSize, 0, _T("ID_STATICTEXT2"));
    BoxSizer1->Add(StaticText2, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Button_quit = new wxButton(Panel2, ID_BUTTON3, _("ÍË³ö"), wxDefaultPosition, wxDefaultSize, 0, wxDefaultValidator, _T("ID_BUTTON3"));
    BoxSizer1->Add(Button_quit, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText3 = new wxStaticText(Panel2, ID_STATICTEXT3, _("Label"), wxDefaultPosition, wxSize(141,14), 0, _T("ID_STATICTEXT3"));
    BoxSizer1->Add(StaticText3, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Panel2->SetSizer(BoxSizer1);
    BoxSizer1->Fit(Panel2);
    BoxSizer1->SetSizeHints(Panel2);
    FlexGridSizer1->Add(Panel2, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 0);
    RichTextCtrl1 = new wxRichTextCtrl(Panel1, ID_RICHTEXTCTRL1, _("Text"), wxPoint(-1,-1), wxSize(495,405), wxRE_MULTILINE, wxDefaultValidator, _T("ID_RICHTEXTCTRL1"));
    wxRichTextAttr rchtxtAttr_1;
    rchtxtAttr_1.SetBulletStyle(wxTEXT_ATTR_BULLET_STYLE_ALIGN_LEFT);
    FlexGridSizer1->Add(RichTextCtrl1, 1, wxALL|wxEXPAND, 1);
    Panel1->SetSizer(FlexGridSizer1);
    FlexGridSizer1->Fit(Panel1);
    FlexGridSizer1->SetSizeHints(Panel1);
    MenuBar1 = new wxMenuBar();
    Menu1 = new wxMenu();
    MenuItem1 = new wxMenuItem(Menu1, idMenuQuit, _("Quit\tAlt-F4"), _("Quit the application"), wxITEM_NORMAL);
    Menu1->Append(MenuItem1);
    MenuBar1->Append(Menu1, _("&File"));
    Menu2 = new wxMenu();
    MenuItem2 = new wxMenuItem(Menu2, idMenuAbout, _("About\tF1"), _("Show info about this application"), wxITEM_NORMAL);
    Menu2->Append(MenuItem2);
    MenuBar1->Append(Menu2, _("Help"));
    SetMenuBar(MenuBar1);
    StatusBar1 = new wxStatusBar(this, ID_STATUSBAR1, 0, _T("ID_STATUSBAR1"));
    int __wxStatusBarWidths_1[1] = { -1 };
    int __wxStatusBarStyles_1[1] = { wxSB_NORMAL };
    StatusBar1->SetFieldsCount(1,__wxStatusBarWidths_1);
    StatusBar1->SetStatusStyles(1,__wxStatusBarStyles_1);
    SetStatusBar(StatusBar1);
    Timer1.SetOwner(this, ID_TIMER1);

    Connect(ID_BUTTON1,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton1Click1);
    Connect(ID_BUTTON2,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton2Click1);
    Connect(ID_BUTTON3,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton_quitClick);
    Panel1->Connect(wxEVT_SIZE,(wxObjectEventFunction)&LogFileViewerFrame::OnPanel1Resize,0,this);
    Connect(idMenuQuit,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnQuit);
    Connect(idMenuAbout,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnAbout);
    Connect(wxEVT_SIZE,(wxObjectEventFunction)&LogFileViewerFrame::OnResize);
    //*)
}

LogFileViewerFrame::~LogFileViewerFrame()
{
    //(*Destroy(LogFileViewerFrame)
    //*)
}

void LogFileViewerFrame::OnQuit(wxCommandEvent& event)
{
    Close();
}

void LogFileViewerFrame::OnAbout(wxCommandEvent& event)
{
    wxString msg = wxbuildinfo(long_f);
    wxMessageBox(msg, _("Welcome to..."));
}

void LogFileViewerFrame::OnButton2Click1(wxCommandEvent& event)
{
    std::string str;
    std::string filename="e:\\automail\\automail.log";
//    filename="e:\\automail\\automail.log";

//    filename = "e:\\automail\\autoservice.log";
    std::string lines;
    int i = 0;
    // ...
//    std::ifstream in("e:\\automail\\automail.log");
    std::ifstream in(filename.c_str());
    wxRichTextCtrl &rtc = *RichTextCtrl1;
    wxStaticText &st = *StaticText2;
//    rtc.Newline();

    if (in.is_open())
        {
       rtc.Clear();
       while (getline (in, lines))
        {
            i=i+1;
            // in + "\n";
//            getline (in, lines);
//          if (in.eof()) break;
        }
       }
         in.close();
        //str = st
       str = str + "*";
       st.SetLabel(str);


}

char *timestring(void)
{
    time_t t = time(0);
    char tmp[64];
    char *ts = new char[64];// = (char *)malloc(32);
    strftime( tmp, sizeof(tmp), "%Y/%m/%d %X %A",localtime(&t) );
    strcpy(ts,tmp);
    return ts;
}


void LogFileViewerFrame::OnButton1Click1(wxCommandEvent& event)
{
    char *str_t = new char[64];
    str_t = timestring();
    wxStaticText &wx_statict3 = *StaticText3;
    wx_statict3.SetLabel(str_t);
}



void LogFileViewerFrame::OnResize(wxSizeEvent& event)
{
    int w;
    int h;
    GetSize(&w,&h);


    wxPanel &wx_panel = * Panel1;
   wx_panel.SetSize(w-5,h-55);


}

void LogFileViewerFrame::OnPanel1Resize(wxSizeEvent& event)
{
        int w;
    int h;
    GetSize(&w,&h);

    wxRichTextCtrl &rtc = *RichTextCtrl1;
    rtc.SetSize(w-10,h-100);

}

void LogFileViewerFrame::OnButton_quitClick(wxCommandEvent& event)
{
    Close();
}

void LogFileViewerFrame::OnTimer1Trigger(wxTimerEvent& event)
{

}

void LogFileViewerFrame::OnTimer1Trigger1(wxTimerEvent& event)
{

}
