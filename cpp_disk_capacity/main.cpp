#include <iostream>
#include <windows.h>
#include <stdio.h>
using namespace std;

char* get_disk_capacity()
{
     int DiskCount = 0;
     DWORD DiskInfo = GetLogicalDrives();
     //����GetLogicalDrives()�������Ի�ȡϵͳ���߼����������������������ص���һ��32λ�޷����������ݡ�
     while(DiskInfo)//ͨ��ѭ�������鿴ÿһλ�����Ƿ�Ϊ1�����Ϊ1�����Ϊ��,���Ϊ0����̲����ڡ�
     {
         if(DiskInfo&1)//ͨ��λ������߼���������ж��Ƿ�Ϊ1
         {
              ++DiskCount;
         }
         DiskInfo = DiskInfo >> 1;//ͨ��λ��������Ʋ�����֤ÿѭ��һ��������λ�������ƶ�һλ��
         //DiskInfo = DiskInfo/2;
     }
     cout<<"�߼���������:"<<DiskCount<<endl;
//-------------------------------------------------------------------

      int DSLength = GetLogicalDriveStrings(0,NULL);
     //ͨ��GetLogicalDriveStrings()������ȡ�����������ַ�����Ϣ���ȡ�
     char* DStr = new char[DSLength];//�û�ȡ�ĳ����ڶ�������һ��c�����ַ�������
     GetLogicalDriveStrings(DSLength,(LPTSTR)DStr);
     //ͨ��GetLogicalDriveStrings���ַ�����Ϣ���Ƶ�����������,���б�������������������Ϣ��

     int DType;
     int si=0;
     BOOL fResult;
     LONG64 i64FreeBytesToCaller;
     LONG64 i64TotalBytes;
     LONG64 i64FreeBytes;

      for(int i=0;i<DSLength/4;++i)
     //Ϊ����ʾÿ����������״̬����ͨ��ѭ�����ʵ�֣�����DStr�ڲ������������A:\NULLB:\NULLC:\NULL����������Ϣ������DSLength/4���Ի�þ����ѭ����Χ
     {
         char dir[3]={DStr[si],':','\\'};
         cout<<dir;
         DType = GetDriveType(DStr+i*4);
         //GetDriveType���������Ի�ȡ���������ͣ�����Ϊ�������ĸ�Ŀ¼
         if(DType == DRIVE_FIXED)
         {
              cout<<"Ӳ��";
         }
         else if(DType == DRIVE_CDROM)
         {
              cout<<"����";
         }
         else if(DType == DRIVE_REMOVABLE)
         {
              cout<<"���ƶ�ʽ����";
         }
         else if(DType == DRIVE_REMOTE)
         {
              cout<<"�������";
         }
         else if(DType == DRIVE_RAMDISK)
         {
              cout<<"����RAM����";
         }
         else if (DType == DRIVE_UNKNOWN)
         {
              cout<<"δ֪�豸";
         }

         fResult = GetDiskFreeSpaceEx (
              dir,
              (PULARGE_INTEGER)&i64FreeBytesToCaller,
              (PULARGE_INTEGER)&i64TotalBytes,
              (PULARGE_INTEGER)&i64FreeBytes);
         //GetDiskFreeSpaceEx���������Ի�ȡ���������̵Ŀռ�״̬,�������ص��Ǹ�BOOL��������
         if(fResult)//ͨ�����ص�BOOL�����ж��������Ƿ��ڹ���״̬
         {
              cout<<" totalspace:"<<(float)i64TotalBytes/1024/1024<<" MB";//����������
              cout<<" freespace:"<<(float)i64FreeBytesToCaller/1024/1024<<" MB";//����ʣ��ռ�
              cout<<" usage rate:"<<(float)i64FreeBytesToCaller/i64TotalBytes*100<<" %";//����ʣ��ռ�
         }
         else
         {
              cout<<" �豸δ׼����";
         }
         cout<<endl;
         si+=4;
     }

     return "pause";
}

int main()
{
//    char* disk_capatity;
//    disk_capatity =
    get_disk_capacity();
//    printf("d:%s",disk_capatity);

}
