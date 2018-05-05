#include <io.h>
#include <fstream>
#include <string.h>
#include <vector>
#include <stdio.h>
#include <iostream>
using namespace std;

//��ȡ���е��ļ���
void GetAllFiles( string path, vector<string>& files)
{

	long   hFile   =   0;
	//�ļ���Ϣ
	struct _finddata_t fileinfo;//�����洢�ļ���Ϣ�Ľṹ��
	string p;
	if((hFile = _findfirst(p.assign(path).append("\\*").c_str(),&fileinfo)) !=  -1)  //��һ�β���
	{
		do
		{
			if((fileinfo.attrib &  _A_SUBDIR))  //������ҵ������ļ���
			{
				if(strcmp(fileinfo.name,".") != 0  &&  strcmp(fileinfo.name,"..") != 0)  //�����ļ��в���
				{
					files.push_back(p.assign(path).append("\\").append(fileinfo.name) );
					GetAllFiles( p.assign(path).append("\\").append(fileinfo.name), files );
				}
			}
			else //������ҵ��Ĳ������ļ���
			{
				files.push_back(p.assign(fileinfo.name) );  //���ļ�·�����棬Ҳ����ֻ�����ļ���:    p.assign(path).append("\\").append(fileinfo.name)
			}

		}while(_findnext(hFile, &fileinfo)  == 0);

		_findclose(hFile); //��������
	}

}

//��ȡ�ض���ʽ���ļ���
void GetAllFormatFiles( string path, vector<string>& files,string format)
{
	//�ļ����
	long   hFile   =   0;
	//�ļ���Ϣ
	struct _finddata_t fileinfo;
	string p;
	if((hFile = _findfirst(p.assign(path).append("\\*" + format).c_str(),&fileinfo)) !=  -1)
	{
		do
		{
			if((fileinfo.attrib &  _A_SUBDIR))
			{
				if(strcmp(fileinfo.name,".") != 0  &&  strcmp(fileinfo.name,"..") != 0)
				{
					//files.push_back(p.assign(path).append("\\").append(fileinfo.name) );
					GetAllFormatFiles( p.assign(path).append("\\").append(fileinfo.name), files,format);
				}
			}
			else
			{
//				files.push_back( p.assign(fileinfo.name));  //���ļ�·�����棬Ҳ����ֻ�����ļ���:    p.assign(path).append("\\").append(fileinfo.name)
				files.push_back( p.assign(path).append("\\").append(fileinfo.name));  //���ļ�·�����棬Ҳ����ֻ�����ļ���:    p.assign(path).append("\\").append(fileinfo.name)
			}
		}while(_findnext(hFile, &fileinfo)  == 0);

		_findclose(hFile);
	}
}

// �ú�����������������һ��Ϊ·���ַ���(string���ͣ����Ϊ����·��)��
// �ڶ�������Ϊ�ļ������ļ����ƴ洢����(vector����,���ô���)��
// ���������е��ø�ʽ(��������������ļ�"AllFiles.txt"�У���һ��Ϊ����)��

int main()
{
	string filePath = "E:\\test";
	vector<string> files;
	char * distAll = "e:\\test\\file_ls.txt";

	//��ȡ���е��ļ����������ļ����ļ�
	//GetAllFiles(filePath, files);

	//��ȡ���и�ʽΪ"format"���ļ�
	string format = ".exe";
	GetAllFormatFiles(filePath, files,format);
	ofstream ofn(distAll);
	int size = files.size();
	ofn<<size<<endl;
	for (int i = 0;i<size;i++)
	{
		ofn<<files[i]<<endl; // д���ļ�
		cout<< files[i] << endl;//�������Ļ
	}
	ofn.close();
	return 0;
}
