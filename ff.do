cd "F:\project\stata_project\0215"
import delimited ffact.csv,clear

local ffcts "mkt_rf smb hml rmw cma esg"
//描述性统计 T检验 表2结果
foreach v in `ffcts' {
asdoc ttest `v'==0,dec(8) //小数点保留8位
}

local mkt_test "rmw cma esg"
//市场风格检验 截距项为表3结果
foreach m in `mkt_test' {
reg `m' mkt_rf smb hml
outreg2 using "mkt_test2.doc", append
}

local ffcts "mkt_rf smb hml rmw cma esg"
//冗余检验
foreach m in `ffcts' {
// di "`m'"
local xfact: list ffcts - m
reg `m' `xfact'
outreg2 using "resu2.doc", append
}