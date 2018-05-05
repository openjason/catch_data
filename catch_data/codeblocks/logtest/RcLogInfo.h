/*
*   写日志类
*
*/
#pragma once

#include <windows.h>
#include <time.h>
#include<stdio.h>
#include <sys/timeb.h>
#include <iostream>
using namespace std;

class RcLogInfo
{
public:
    RcLogInfo(void);
    ~RcLogInfo(void);

public:
    //日志文件
    FILE* m_pfLogFile;
    char m_cInfo[255];

    int  SetLogFile(FILE *pfLogFile);
    int  WriteLogInfo(const char *pInfo);
};
