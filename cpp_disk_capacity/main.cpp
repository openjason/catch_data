#include <iostream>
#include <windows.h>
#include <stdio.h>
using namespace std;

char* get_disk_capacity()
{
     int DiskCount = 0;
     DWORD DiskInfo = GetLogicalDrives();
     //利用GetLogicalDrives()函数可以获取系统中逻辑驱动器的数量，函数返回的是一个32位无符号整型数据。
     while(DiskInfo)//通过循环操作查看每一位数据是否为1，如果为1则磁盘为真,如果为0则磁盘不存在。
     {
         if(DiskInfo&1)//通过位运算的逻辑与操作，判断是否为1
         {
              ++DiskCount;
         }
         DiskInfo = DiskInfo >> 1;//通过位运算的右移操作保证每循环一次所检查的位置向右移动一位。
         //DiskInfo = DiskInfo/2;
     }
     cout<<"逻辑磁盘数量:"<<DiskCount<<endl;
//-------------------------------------------------------------------

      int DSLength = GetLogicalDriveStrings(0,NULL);
     //通过GetLogicalDriveStrings()函数获取所有驱动器字符串信息长度。
     char* DStr = new char[DSLength];//用获取的长度在堆区创建一个c风格的字符串数组
     GetLogicalDriveStrings(DSLength,(LPTSTR)DStr);
     //通过GetLogicalDriveStrings将字符串信息复制到堆区数组中,其中保存了所有驱动器的信息。

     int DType;
     int si=0;
     BOOL fResult;
     LONG64 i64FreeBytesToCaller;
     LONG64 i64TotalBytes;
     LONG64 i64FreeBytes;

      for(int i=0;i<DSLength/4;++i)
     //为了显示每个驱动器的状态，则通过循环输出实现，由于DStr内部保存的数据是A:\NULLB:\NULLC:\NULL，这样的信息，所以DSLength/4可以获得具体大循环范围
     {
         char dir[3]={DStr[si],':','\\'};
         cout<<dir;
         DType = GetDriveType(DStr+i*4);
         //GetDriveType函数，可以获取驱动器类型，参数为驱动器的根目录
         if(DType == DRIVE_FIXED)
         {
              cout<<"硬盘";
         }
         else if(DType == DRIVE_CDROM)
         {
              cout<<"光驱";
         }
         else if(DType == DRIVE_REMOVABLE)
         {
              cout<<"可移动式磁盘";
         }
         else if(DType == DRIVE_REMOTE)
         {
              cout<<"网络磁盘";
         }
         else if(DType == DRIVE_RAMDISK)
         {
              cout<<"虚拟RAM磁盘";
         }
         else if (DType == DRIVE_UNKNOWN)
         {
              cout<<"未知设备";
         }

         fResult = GetDiskFreeSpaceEx (
              dir,
              (PULARGE_INTEGER)&i64FreeBytesToCaller,
              (PULARGE_INTEGER)&i64TotalBytes,
              (PULARGE_INTEGER)&i64FreeBytes);
         //GetDiskFreeSpaceEx函数，可以获取驱动器磁盘的空间状态,函数返回的是个BOOL类型数据
         if(fResult)//通过返回的BOOL数据判断驱动器是否在工作状态
         {
              cout<<" totalspace:"<<(float)i64TotalBytes/1024/1024<<" MB";//磁盘总容量
              cout<<" freespace:"<<(float)i64FreeBytesToCaller/1024/1024<<" MB";//磁盘剩余空间
              cout<<" usage rate:"<<(float)i64FreeBytesToCaller/i64TotalBytes*100<<" %";//磁盘剩余空间
         }
         else
         {
              cout<<" 设备未准备好";
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
