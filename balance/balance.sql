CREATE TABLE [days](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [kehu] CHAR(10), 
  [wuliao] CHAR(30), 
  [date] DATE, 
  [fachu] INTEGER, 
  [chengpin] INTEGER, 
  [jianka] INTEGER, 
  [feika] INTEGER);

CREATE TABLE [maillist](
  [id] INTEGER PRIMARY KEY, 
  [kehu] CHAR(10), 
  [picihao] CHAR(20), 
  [shenqinbianhao] CHAR(20), 
  [youjifangshi] INT, 
  [youjidanghao] CHAR(20), 
  [jichudi] CHAR(10), 
  [zhikafangshi] CHAR(16), 
  [chikarenxingmin] CHAR(10), 
  [kazhuxingmin] CHAR(10), 
  [kamiandaima] CHAR(10), 
  [fakayuanyin] CHAR(10), 
  [kahao] CHAR(20), 
  [youjidizhi] CHAR(40), 
  [youbian] CHAR(10), 
  [chikarenshouji] CHAR(12), 
  [youjiriqi] DATETEXT, 
  [shengchengriqi] DATETEXT, 
  [zhufukabiaoji] CHAR(2), 
  [emsliushuihao] CHAR(10), 
  [pid] CHAR(9), 
  [quyu] CHAR(10));

CREATE TABLE [price](
  [id] INTEGER, 
  [kamiandaima] CHAR(10), 
  [kapianbanbenhao] CHAR(20), 
  [wuliao] CHAR(20), 
  [mingcheng] CHAR(30), 
  [gerenhuafuwu] VARCHAR(50), 
  [fuwumingcheng] VARCHAR(50), 
  [fuwuleixinbiaoshi] CHAR(20), 
  [gerenhuajiage] FLOAT, 
  [xinpianka] CHAR(30), 
  [gongyiqueren] VARCHAR(50), 
  [kongbaikajiage] FLOAT);

CREATE TABLE "price_old"(
  [id] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [kehu] CHAR(10), 
  [chanpingongyi] VARCHAR(60), 
  [baojiawushui] FLOAT, 
  [shui] FLOAT, 
  [baojiahanshui] FLOAT);

CREATE TABLE [wuliao](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT, 
  [kehu] CHAR(10), 
  [wuliao] CHAR(30), 
  [style] CHAR(20), 
  [name] CHAR(50), 
  [suoshuyuefen] DATETEXT, 
  [shangyuejiecun] INT64, 
  [benyuerucang] INT64, 
  [benyuejiecun] INT64, 
  [benyuefachushu] INT64, 
  [benyuechengpinshu] INT64, 
  [benyuejiankashu] INT64, 
  [benyuefeikashu] INT64, 
  [benyuefeikaleijishu] INT64, 
  [shangyuejiankaleijishu] INT64, 
  [shangyuefeikaleijishu] INT64, 
  [benyuexiaohuikongbaikashu] INT64, 
  [benyuexiaohuifeikashu] INT64);

CREATE INDEX [] ON [days]([date]);

