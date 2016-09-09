select a.AccountNumber as account_number, 
a.CustomerNumber as customer_number,
a.AccountName as account_name,
a.VIPNumberString as vip_number,
a.PhoneAccount as phone_account,
a.CreationDate as creation_date,
a.Active as active,         
a.ExtraInfo as extra_info,         
e.Caption1 as caption1,
e.DefaultValue1 as default_value1,
e.Length1 as length1,
e.PromptId1 as prompt_id1,
e.Required1 as required1,
e.Validation1 as validation1,
v1.Name as name1, 
e.Caption2 as caption2,
e.DefaultValue2 as default_value2,
e.Length2 as length2,
e.PromptId2 as prompt_id2,
e.Required2 as required2,
e.Validation2 as validation2,
v2.Name as name2, 
e.Caption3 as caption3,
e.DefaultValue3 as default_value3,
e.Length3  as length3,
e.PromptId3 as prompt_id3,
e.Required3 as required3,
e.Validation3 as validation3,
v3.Name as name3, 
e.Caption4 as caption4,
e.DefaultValue4 as default_value4,
e.Length4  as length4,
e.PromptId4 as prompt_id4,
e.Required4 as required4,
e.Validation4 as validation4,
v4.Name as name4, 
e.Caption5 as caption5,
e.DefaultValue5 as default_value5,
e.Length5  as length5,
e.PromptId5 as prompt_id5,
e.Required5 as required5,
e.Validation5 as validation5,
v5.Name as name5, 
e.Caption6 as caption6, 
e.DefaultValue6 as default_value6,
e.Length6  as length6,
e.PromptId6 as prompt_id6,         
e.Required6 as required6, 
e.Validation6 as validation6,
v6.Name as name6, 
e.Caption7 as caption7,
e.DefaultValue7 as default_value7,
e.Length7  as length7,
e.PromptId7 as prompt_id7,
e.Required7 as required7,
e.Validation7 as validation7,
v7.Name as name7, 
e.Caption8 as caption8,
e.DefaultValue8 as default_value8,
e.Length8  as length8,
e.PromptId8 as prompt_id8,
e.Required8 as required8,
e.Validation8 as validation8, 
v8.Name as name8 
from account a LEFT JOIN extrainfo e ON a.ExtraInfo = e.id 
left join cabmate.validation v1 on v1.id=e.Validation1 
left join cabmate.validation v2 on v2.id=e.Validation2
left join cabmate.validation v3 on v3.id=e.Validation3 
left join cabmate.validation v4 on v4.id=e.Validation4 
left join cabmate.validation v5 on v5.id=e.Validation5
left join cabmate.validation v6 on v6.id=e.Validation6
left join cabmate.validation v7 on v7.id=e.Validation7
left join cabmate.validation v8 on v8.id=e.Validation8
where a.PhoneAccount != 1 and a.AccountNumber = 'ROBF1' and a.CustomerNumber = 0 limit 1;
