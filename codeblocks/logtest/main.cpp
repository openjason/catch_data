#include "RcLogInfo.h"



RcLogInfo::RcLogInfo(void)
{
    m_pfLogFile = NULL;
    memset(m_cInfo,NULL,sizeof(m_cInfo));
}

RcLogInfo::~RcLogInfo(void)
{
    if (NULL != m_pfLogFile)
    {
        fclose(m_pfLogFile);
        m_pfLogFile = NULL;
    }
}

int RcLogInfo::SetLogFile(FILE *pfLogFile)
{
    m_pfLogFile=pfLogFile;
    return 0;
}

int RcLogInfo::WriteLogInfo(const char *pInfo)
{
    if(NULL != m_pfLogFile)
    {
        fprintf(m_pfLogFile,"%s",pInfo);
        fflush(m_pfLogFile);
        return 0;
    }
    return 1;


}


int main(void)
{
    //////////////////////////////////////////////////////////////////////////
    char cPath[MAX_PATH];
    memset(cPath,0,MAX_PATH);
    if (!GetModuleFileName(NULL,cPath,MAX_PATH))
    {
        return false;
    }
    char *FileName = cPath + strlen(cPath)-1;
    while(*FileName !='\\')
    {
        --FileName;
    }
    *FileName = '\0';
    char cFileName[MAX_PATH]={'\0'};
    sprintf(cFileName,"%s\\%s",cPath,"TestLog.log");


    //////////////////////////////////////////////////////////////////////////
    FILE *m_pfLogFile=NULL;
    if(NULL != m_pfLogFile)
    {
        fclose(m_pfLogFile);
    }
    m_pfLogFile = fopen(cFileName,"at+");
    if(NULL == m_pfLogFile)
    {
        return 1;
    }


    //////////////////////////////////////////////////////////////////////////
    RcLogInfo rl;
    rl.SetLogFile(m_pfLogFile);


    //////////////////////////////////////////////////////////////////////////
    timeb aTime;
    ftime(&aTime);
    sprintf(rl.m_cInfo,"–¥»’÷æ≤‚ ‘******************************+++++++++++++++++++++++_________________%s .%ld ms\n",ctime(&(aTime.time)),aTime.millitm);
    rl.WriteLogInfo(rl.m_cInfo);


    return 0;


}
