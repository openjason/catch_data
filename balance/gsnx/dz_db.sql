CREATE TABLE [hztj](
  [id] INTEGER, 
  [kehu] CHAR(8), 
  [chanpinbianma] CHAR(9), 
  [chanpinmingcheng] CHAR(30), 
  [jigoudaima] CHAR(9), 
  [danweimingcheng] CHAR(40), 
  [shuliang] INT64, 
  [youjiriqi] DATETEXT);

CREATE TABLE [price](
  [id] INTEGER, 
  [kamiandaima] CHAR(10), 
  [kapianbanbenhao] CHAR(20), 
  [wuliao] CHAR(20), 
  [mingcheng] CHAR(30), 
  [grhpingrijiage1] FLOAT, 
  [grhjierijiage1] FLOAT, 
  [kongbaikajiage1] FLOAT, 
  [hetong2qiyongriqi] DATETEXT, 
  [grhpingrijiage2] FLOAT, 
  [grhjierijiage2] FLOAT, 
  [kongbaikajiage2] FLOAT, 
  [gerenhuafuwu] VARCHAR(50), 
  [fuwumingcheng] VARCHAR(50), 
  [fuwuleixinbiaoshi] CHAR(20), 
  [xinpianka] CHAR(30), 
  [gongyiqueren] VARCHAR(50));

CREATE VIEW [jiagemingxi]
AS
SELECT 
       [kehu], 
       [chanpinbianma], 
       [chanpinmingcheng], 
       [jigoudaima], 
       [danweimingcheng], 
       [shuliang], 
       [youjiriqi], 
       [grhpingrijiage1], 
       [hetong2qiyongriqi], 
       [grhpingrijiage2]
FROM   [hztj],
       [price]
WHERE  [hztj].[chanpinbianma] = [price].[kamiandaima];

