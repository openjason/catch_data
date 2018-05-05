/***************************************************************
 * Name:      LogFileViewerApp.cpp
 * Purpose:   Code for Application Class
 * Author:    JasonChan (openjc@outlook.com)
 * Created:   2018-03-05
 * Copyright: JasonChan ()
 * License:
 **************************************************************/

#include "LogFileViewerApp.h"

//(*AppHeaders
#include "LogFileViewerMain.h"
#include <wx/image.h>
//*)

IMPLEMENT_APP(LogFileViewerApp);

bool LogFileViewerApp::OnInit()
{
    //(*AppInitialize
    bool wxsOK = true;
    wxInitAllImageHandlers();
    if ( wxsOK )
    {
    	LogFileViewerFrame* Frame = new LogFileViewerFrame(0);
    	Frame->Show();
    	SetTopWindow(Frame);
    }
    //*)
    return wxsOK;

}
