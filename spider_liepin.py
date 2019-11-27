import re
import time
import logging
import json
import datetime
import requests
import urllib
import urllib3
import pandas as pd
from bs4 import BeautifulSoup

class init:
	request_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

#获取职位清单
def getJobsList(url:str):
	job_list = []
	try:
		headers = init.request_headers
		response = requests.get(url,headers=headers)
		soup = BeautifulSoup(response.text,'html.parser')
		job_ul = soup.find_all('ul',class_='sojob-list')[0]
		for li in job_ul.find_all('li'):
			job_list.append(li.find_all('a')[0]['href'])
	except:
		pass
	return job_list

#获取单个职位详情
def getJobDetail(url):
	job_deatil = {}
	try:
		headers = init.request_headers
		response = requests.get(url,headers=headers)
		soup = BeautifulSoup(response.text,'html.parser')
		titleInfo = soup.find_all('div',class_='title-info')[0]
		job_deatil['职位'] = titleInfo.find_all('h1')[0].get_text().strip()
		basicInfor = soup.find_all('p',class_='basic-infor')[0]
		job_deatil['薪资'] = soup.find_all('p',class_='job-item-title')[0].get_text().strip()
		job_deatil['地区'] = basicInfor.find_all('span')[0].get_text().strip()
		job_deatil['更新时间'] = basicInfor.find_all('time')[0]['title']
		jobQualifications = soup.find_all('div',class_='job-qualifications')[0]
		jobQualifications_list = []
		for item in jobQualifications.find_all('span'):
			jobQualifications_list.append(item.get_text().strip())
		job_deatil['职位要求'] = '；'.join(jobQualifications_list)
		welfare = soup.find_all('ul',class_='comp-tag-list clearfix')[0]
		welfare_list = []
		for item in welfare.find_all('span'):
			welfare_list.append(item.get_text().strip())
		job_deatil['福利'] = '；'.join(welfare_list)
		jobContent = soup.find_all('div',class_='content content-word')[0]
		job_deatil['职位描述'] = jobContent.get_text().strip()
		jobOtherInformation = soup.find_all('div',class_='job-item main-message')[0]
		jobOtherInformation_list = []		
		for item in jobOtherInformation.find_all('li'):
			jobOtherInformation_list.append(item.get_text().strip())
		job_deatil['其他信息'] = '；'.join(jobOtherInformation_list)
	except Exception as e:
		logging.exception(e)
	return job_deatil

#输入未格式化的客户信息dict，输出格式化后的客户信息dict
def createXlsxSheet(jobDict:dict):
	data_dict = {}
	data_dict['职位'] = []
	data_dict['薪资'] = []
	data_dict['地区'] = []
	data_dict['更新时间'] = []
	data_dict['职位要求'] = []
	data_dict['福利'] = []
	data_dict['职位描述'] = []
	data_dict['其他信息'] = []
	for item in jobDict.values():
		data_dict['职位'].append(item.get('职位'))
		data_dict['薪资'].append(item.get('薪资'))
		data_dict['地区'].append(item.get('地区'))
		data_dict['更新时间'].append(item.get('更新时间'))
		data_dict['职位要求'].append(item.get('职位要求'))
		data_dict['福利'].append(item.get('福利'))
		data_dict['职位描述'].append(item.get('职位描述'))
		data_dict['其他信息'].append(item.get('其他信息'))
	return data_dict

#输入职位信息dict，生成xlsx文件
def write_xls(data_dict:dict,outputName='output.xlsx'):
	writer = pd.ExcelWriter(outputName)
	df = pd.DataFrame(data_dict)
	df.to_excel(writer,index=False)
	writer.save()
	writer.close()

#输入搜索详情页url
def doCrawling(start_url:str):
	jl = getJobsList(start_url)
	jdd = {}
	for url in jl:
		jd = getJobDetail(url)
		print('搜索得到职位：' + jd['职位'])
		i = len(jdd)
		jdd[str(i)] = jd
		time.sleep(5)	#给运维和反爬工程师喘口气，好吗？
	data = createXlsxSheet(jdd)
	write_xls(data)

doCrawling('https://www.liepin.com/company/8637876/')