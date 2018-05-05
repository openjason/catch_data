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
#include <string.h>
#include <fstream>
#include <iostream>
#include <time.h>

char *read_file = "E:\\automail\\automail.log";
char FILE_RD[99];
size_t VIEW_BLOCK_SIZE = 1024*20;//每次读写的大小,此处为20k
FILE * pFile;
long lSize;
char * buffer;
char mystring [200];
char *str_t = new char[64];

    time_t t = time(0);
    char tmp[64];
    char *ts = new char[64];// = (char *)malloc(32);

//wxRichTextCtrl rtc;


//定义全局变量

//(*InternalHeaders(LogFileViewerFrame)
#include <wx/artprov.h>
#include <wx/bitmap.h>
#include <wx/icon.h>
#include <wx/image.h>
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
const long LogFileViewerFrame::ID_open_logf = wxNewId();
const long LogFileViewerFrame::ID_man_refr = wxNewId();
const long LogFileViewerFrame::idMenuQuit = wxNewId();
const long LogFileViewerFrame::idMenuAbout = wxNewId();
const long LogFileViewerFrame::ID_STATUSBAR1 = wxNewId();
const long LogFileViewerFrame::ID_TIMER1 = wxNewId();
//*)

BEGIN_EVENT_TABLE(LogFileViewerFrame,wxFrame)
    //(*EventTable(LogFileViewerFrame)
        EVT_TIMER(ID_TIMER1, LogFileViewerFrame::OnTimer1Trigger)
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

    Create(parent, wxID_ANY, _("AutoMail Log File Viewer.          Designed by 东信和平安全部.   版本号:v0.1803"), wxDefaultPosition, wxDefaultSize, wxDEFAULT_FRAME_STYLE, _T("wxID_ANY"));
    SetClientSize(wxSize(1258,621));
    {
    	wxIcon FrameIcon;
    	FrameIcon.CopyFromBitmap(wxArtProvider::GetBitmap(wxART_MAKE_ART_ID_FROM_STR(_T("wxART_FLOPPY")),wxART_OTHER));
    	SetIcon(FrameIcon);
    }
    Panel1 = new wxPanel(this, ID_PANEL1, wxPoint(176,192), wxDefaultSize, wxTAB_TRAVERSAL|wxFULL_REPAINT_ON_RESIZE, _T("ID_PANEL1"));
    FlexGridSizer1 = new wxFlexGridSizer(2, 1, 0, 1);
    Panel2 = new wxPanel(Panel1, ID_PANEL2, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL, _T("ID_PANEL2"));
    BoxSizer1 = new wxBoxSizer(wxHORIZONTAL);
    Button1 = new wxButton(Panel2, ID_BUTTON1, _("打开日志文件"), wxDefaultPosition, wxDefaultSize, 0, wxDefaultValidator, _T("ID_BUTTON1"));
    BoxSizer1->Add(Button1, 2, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText1 = new wxStaticText(Panel2, ID_STATICTEXT1, _("e:\\automail\\automail.log"), wxDefaultPosition, wxDefaultSize, 0, _T("ID_STATICTEXT1"));
    BoxSizer1->Add(StaticText1, 3, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Button2 = new wxButton(Panel2, ID_BUTTON2, _("手动刷新"), wxDefaultPosition, wxSize(129,24), 0, wxDefaultValidator, _T("ID_BUTTON2"));
    BoxSizer1->Add(Button2, 2, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText2 = new wxStaticText(Panel2, ID_STATICTEXT2, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0, _T("ID_STATICTEXT2"));
    BoxSizer1->Add(StaticText2, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Button_quit = new wxButton(Panel2, ID_BUTTON3, _("退出"), wxDefaultPosition, wxDefaultSize, 0, wxDefaultValidator, _T("ID_BUTTON3"));
    BoxSizer1->Add(Button_quit, 2, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    StaticText3 = new wxStaticText(Panel2, ID_STATICTEXT3, _("Label"), wxDefaultPosition, wxSize(150,14), 0, _T("ID_STATICTEXT3"));
    BoxSizer1->Add(StaticText3, 3, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 5);
    Panel2->SetSizer(BoxSizer1);
    BoxSizer1->Fit(Panel2);
    BoxSizer1->SetSizeHints(Panel2);
    FlexGridSizer1->Add(Panel2, 1, wxALL|wxALIGN_CENTER_HORIZONTAL|wxALIGN_CENTER_VERTICAL, 0);
    RichTextCtrl1 = new wxRichTextCtrl(Panel1, ID_RICHTEXTCTRL1, _("等待刷新日志文件..."), wxPoint(-1,-1), wxSize(495,405), wxRE_MULTILINE, wxDefaultValidator, _T("ID_RICHTEXTCTRL1"));
    wxRichTextAttr rchtxtAttr_1;
    rchtxtAttr_1.SetBulletStyle(wxTEXT_ATTR_BULLET_STYLE_ALIGN_LEFT);
    FlexGridSizer1->Add(RichTextCtrl1, 1, wxALL|wxEXPAND, 1);
    Panel1->SetSizer(FlexGridSizer1);
    FlexGridSizer1->Fit(Panel1);
    FlexGridSizer1->SetSizeHints(Panel1);
    MenuBar1 = new wxMenuBar();
    Menu1 = new wxMenu();
    MenuItem3 = new wxMenuItem(Menu1, ID_open_logf, _("打开日志文件"), wxEmptyString, wxITEM_NORMAL);
    Menu1->Append(MenuItem3);
    MenuItem4 = new wxMenuItem(Menu1, ID_man_refr, _("手动刷新"), wxEmptyString, wxITEM_NORMAL);
    Menu1->Append(MenuItem4);
    Menu1->AppendSeparator();
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
    Timer1.Start(1000, false);
    FileDialog1 = new wxFileDialog(this, _("Select file"), wxEmptyString, wxEmptyString, wxFileSelectorDefaultWildcardStr, wxFD_DEFAULT_STYLE, wxDefaultPosition, wxDefaultSize, _T("wxFileDialog"));

    Connect(ID_BUTTON1,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton1Click1);
    Connect(ID_BUTTON2,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton2Click1);
    Connect(ID_BUTTON3,wxEVT_COMMAND_BUTTON_CLICKED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton_quitClick);
    Connect(ID_RICHTEXTCTRL1,wxEVT_COMMAND_TEXT_UPDATED,(wxObjectEventFunction)&LogFileViewerFrame::OnRichTextCtrl1Text);
    Panel1->Connect(wxEVT_SIZE,(wxObjectEventFunction)&LogFileViewerFrame::OnPanel1Resize,0,this);
    Connect(ID_open_logf,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton1Click1);
    Connect(ID_man_refr,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnButton2Click1);
    Connect(idMenuQuit,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnQuit);
    Connect(idMenuAbout,wxEVT_COMMAND_MENU_SELECTED,(wxObjectEventFunction)&LogFileViewerFrame::OnAbout);
    Connect(ID_TIMER1,wxEVT_TIMER,(wxObjectEventFunction)&LogFileViewerFrame::OnTimer1Trigger);
    Connect(wxEVT_SIZE,(wxObjectEventFunction)&LogFileViewerFrame::OnResize);
    //*)
    strncpy(FILE_RD,read_file,strlen(read_file));
//    wxRichTextCtrl &rtc =*RichTextCtrl1;
    LogFileViewerFrame::refresh_log();
}

LogFileViewerFrame::~LogFileViewerFrame()
{
    //(*Destroy(LogFileViewerFrame)
    //*)
}

void LogFileViewerFrame::OnQuit(wxCommandEvent& event)
{
    int answer = wxMessageBox("确认退出程序？", "Confirm",wxYES_NO, this);
    if (answer == wxYES)
        Close();

}

void LogFileViewerFrame::OnAbout(wxCommandEvent& event)
{
    wxString msg = wxbuildinfo(long_f);

    wxMessageBox("LogFileViewer, software Designed by Jason Chan in EP.\nCode::Blocks 17.12 with wxWidgets.\nEmail:2058807@qq.com", _("Welcome to..."));
}


int LogFileViewerFrame::refresh_log(void)
{

    wxRichTextCtrl &rtc = *RichTextCtrl1;
    pFile = fopen ( FILE_RD , "r" );
  if (pFile==NULL) {
    wxMessageBox(FILE_RD,"无法打开文件...",wxOK);
    return 1;
  }

  // obtain file size:
    fseek (pFile , 0 , SEEK_END);
    lSize = ftell (pFile);
    rewind (pFile);

  // allocate memory to contain the whole file:
    buffer = (char*) malloc (VIEW_BLOCK_SIZE);
    if (buffer == NULL)
        {
            wxMessageBox("Memory error","error",wxOK);
            return 1;
        }
    fseek (pFile,lSize-VIEW_BLOCK_SIZE,SEEK_SET);
    if (pFile == NULL)
        {    wxMessageBox("Memory error","error",wxOK);
        return 1;
       }
    else
        {
        rtc.Clear();
//        mystring[0] = '\0';
        strcpy(mystring,"#此程序只显示20K字节大小的内容，更多内容请直接查看日志文件.");
        while(!feof(pFile))
        {
            if (strlen(mystring)>1)
                {
                rtc.MoveHome();
                rtc.WriteText(mystring);
                }
            fgets (mystring , 200 , pFile);
        }
     }
  fclose (pFile);
  free (buffer);
  return 0;
}

char *timestring(void)
{
    t = time(0);
    strftime(tmp, sizeof(tmp), "%Y/%m/%d %X %A",localtime(&t) );
    strcpy(ts,tmp);
    return tmp;
}


void LogFileViewerFrame::OnButton1Click1(wxCommandEvent& event)
{
    wxString bwfilename = wxFileSelector("Choose a file to open");

    if ( !bwfilename.empty() )
        {
            strncpy(FILE_RD,bwfilename.char_str(),bwfilename.Len());
            FILE_RD[bwfilename.Len()]='\0';
            wxStaticText &wx_statict1 = *StaticText1;
            wx_statict1.SetLabel(bwfilename);
        }
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
    int answer = wxMessageBox("确认退出程序？", "Confirm",wxYES_NO, this);
    if (answer == wxYES)
        Close();

}

void LogFileViewerFrame::OnTimer1Trigger(wxTimerEvent& event)
{

    str_t = timestring();
    wxStaticText &wx_statict3 = *StaticText3;
    wx_statict3.SetLabel(str_t);
//    if (str_t[18] == '0' or str_t[18] == '5')
    if (str_t[18] == '0')
    {
        LogFileViewerFrame::refresh_log();
    }
}

void LogFileViewerFrame::OnButton2Click1(wxCommandEvent& event)
{
    LogFileViewerFrame::refresh_log();
}

void LogFileViewerFrame::OnRichTextCtrl1Text(wxCommandEvent& event)
{
}
