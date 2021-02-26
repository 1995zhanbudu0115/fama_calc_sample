cd "D:\stata_project\fama_calc_sample"
global style "wq"
import delimited ffact_$style.csv,clear


local ffcts "mkt_rf smb hml rmw cma esg"
pwcorr_a `ffcts',sig

//
local ffcts "mkt_rf smb hml rmw cma esg"
//描述性统计 T检验 表2结果
foreach v in `ffcts' {
ttest `v'==0 //小数点保留8位
}

sum mkt_rf smb hml rmw cma esg
local mkt_test "rmw cma esg"
//市场风格检验 截距项为表3结果
foreach m in `mkt_test' {
reg `m' mkt_rf smb hml
outreg2 using "mkt_test_$style.doc", append
}

local ffcts "mkt_rf smb hml rmw cma esg"
//冗余检验
foreach m in `ffcts' {
// di "`m'"
local xfact: list ffcts - m
reg `m' `xfact'
outreg2 using "ry_test_$style.doc", append
}

// 因子正交化
local offcts "smb hml rmw cma esg" // 需要正交的因子
foreach of in `offcts' {
local xfact: list ffcts - of
reg `of' `xfact'
predict `of'o,resid
}
save ffact_$style,replace



// -----------------------25组回归 HMLO----------------------------
import delimited 25分组收益size-bm.csv,clear
merge m:1 date using ffact_$style,nogen

//分组回归计算各组的回归系数，使用Newey-West t统计量
bys me_group5 bm_group5: asreg dret mkt_rf smb hmlo rmw cma esg, se rmse newey(4)
keep me_group5 bm_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hmlo _b_rmw _b_cma _b_esg _b_cons _se_mkt_rf _se_smb _se_hmlo _se_rmw _se_cma _se_esg _se_cons
duplicates drop me_group5 bm_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hmlo _b_rmw _b_cma _b_esg _b_cons _se_mkt_rf _se_smb _se_hmlo _se_rmw _se_cma _se_esg _se_cons, force
drop if _adjR2 == .
* 计算t值和p值  标注星号
foreach i in cons mkt_rf smb hmlo rmw cma esg {
	gen t_`i'=_b_`i'/_se_`i'
	gen p_`i'=ttail(_Nobs, abs(t_`i'))*2
	gen star_`i'="*" if p_`i'<0.1
	replace star_`i'="**" if p_`i'<0.05
	replace star_`i'="***" if p_`i'<0.01
}

export excel using 25分组回归结果hmlo.xlsx, firstrow(var) replace

// -----------------------25组回归 RMWO----------------------------
import delimited 25分组收益size-op.csv,clear
merge m:1 date using ffact_$style,nogen

//分组回归计算各组的回归系数，使用Newey-West t统计量
bys me_group5 op_group5: asreg dret mkt_rf smb hml rmwo cma esg, se rmse newey(4)
keep me_group5 op_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmwo _b_cma _b_esg _b_cons _se_mkt_rf _se_smb _se_hml _se_rmwo _se_cma _se_esg _se_cons
duplicates drop me_group5 op_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmwo _b_cma _b_esg _b_cons _se_mkt_rf _se_smb _se_hml _se_rmwo _se_cma _se_esg _se_cons, force
drop if _adjR2 == .
* 计算t值和p值  标注星号
foreach i in cons mkt_rf smb hml rmwo cma esg {
	gen t_`i'=_b_`i'/_se_`i'
	gen p_`i'=ttail(_Nobs, abs(t_`i'))*2
	gen star_`i'="*" if p_`i'<0.1
	replace star_`i'="**" if p_`i'<0.05
	replace star_`i'="***" if p_`i'<0.01
}

export excel using 25分组回归结果rmwo.xlsx, firstrow(var) replace

// -----------------------25组回归 CMAO----------------------------
import delimited 25分组收益size-inv.csv,clear
merge m:1 date using ffact_$style,nogen

//分组回归计算各组的回归系数，使用Newey-West t统计量
bys me_group5 inv_group5: asreg dret mkt_rf smb hml rmw cmao esg, se rmse newey(4)
keep me_group5 inv_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmw _b_cmao _b_esg _b_cons _se_mkt_rf _se_smb _se_hml _se_rmw _se_cmao _se_esg _se_cons
duplicates drop me_group5 inv_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmw _b_cmao _b_esg _b_cons _se_mkt_rf _se_smb _se_hml _se_rmw _se_cmao _se_esg _se_cons, force
drop if _adjR2 == .
* 计算t值和p值  标注星号
foreach i in cons mkt_rf smb hml rmw cmao esg {
	gen t_`i'=_b_`i'/_se_`i'
	gen p_`i'=ttail(_Nobs, abs(t_`i'))*2
	gen star_`i'="*" if p_`i'<0.1
	replace star_`i'="**" if p_`i'<0.05
	replace star_`i'="***" if p_`i'<0.01
}

export excel using 25分组回归结果cmao.xlsx, firstrow(var) replace

// -----------------------25组回归 ESGO----------------------------
import delimited 25分组收益size-esg.csv,clear
merge m:1 date using ffact_$style,nogen

//分组回归计算各组的回归系数，使用Newey-West t统计量
bys me_group5 esg_group5: asreg dret mkt_rf smb hml rmw cma esgo, se rmse newey(4)
keep me_group5 esg_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmw _b_cma _b_esgo _b_cons _se_mkt_rf _se_smb _se_hml _se_rmw _se_cma _se_esgo _se_cons
duplicates drop me_group5 esg_group5 _rmse _Nobs _R2 _adjR2 _b_mkt_rf _b_smb _b_hml _b_rmw _b_cma _b_esgo _b_cons _se_mkt_rf _se_smb _se_hml _se_rmw _se_cma _se_esgo _se_cons, force
drop if _adjR2 == .
* 计算t值和p值  标注星号
foreach i in cons mkt_rf smb hml rmw cma esgo {
	gen t_`i'=_b_`i'/_se_`i'
	gen p_`i'=ttail(_Nobs, abs(t_`i'))*2
	gen star_`i'="*" if p_`i'<0.1
	replace star_`i'="**" if p_`i'<0.05
	replace star_`i'="***" if p_`i'<0.01
}

export excel using 25分组回归结果esgo.xlsx, firstrow(var) replace






 
 