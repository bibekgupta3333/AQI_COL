from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd

import joblib
model= joblib.load(r'C:\Users\DELL\Desktop\project\multilinear\regressionmodel.pkl')



# Creati your views here.
def homepage(request):
	
	import json
	import requests

	api_request= requests.get("http://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=27.700769&longitude=85.300140&distance=25&API_KEY=7AC96E40-0D38-49D2-A5FF-0240E15F336E")

	try:
		api= json.loads(api_request.content)
	except Exception as e:
		api="error...."


	if api[0]['Category']['Name'] == 'Good':
		Category_Description = "(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
		Category_color="good"
	elif api[0]['Category']['Name']  == 'Moderate':
		Category_Description= "(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
		Category_color="moderate"
	elif api[0]['Category']['Name']  == 'Unhealthy for Sensitive Groups':
	  	Category_Description= "(101-150) Members of sensitive groups may experience health effects. The general public is less likely to be affected."
	  	Category_color="Unhealthy_for_Sensitive_Groups"
	elif api[0]['Category']['Name'] == 'Unhealthy':
		Category_Description= "(151-200) Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
		Category_color="Unhealthy"
	elif api[0]['Category']['Name'] == 'Very Unhealthy':
	 	Category_Description="(201-300) Health alert: The risk of health effects is increased for everyone."
	 	Category_color="Very_Unhealthy"
	elif api[0]['Category']['Name'] == 'Hazardous':
		Category_Description="(301 and higher) Health warning of emergency conditions: everyone is more likely to be affected."
		Category_color="Hazardous"

	if api[1]['Category']['Name'] == 'Good':
		Category_Description1 = "(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
		Category_color1="good"
	elif api[1]['Category']['Name']  == 'Moderate':
		Category_Description1= "(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
		Category_color1="moderate"
	elif api[1]['Category']['Name']  == 'Unhealthy for Sensitive Groups':
	  	Category_Description1= "(101-150) Members of sensitive groups may experience health effects. The general public is less likely to be affected."
	  	Category_color1="Unhealthy_for_Sensitive_Groups"
	elif api[1]['Category']['Name'] == 'Unhealthy':
		Category_Description1= "(151-200) Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
		Category_color1="Unhealthy"
	elif api[1]['Category']['Name'] == 'Very Unhealthy':
	 	Category_Description1="(201-300) Health alert: The risk of health effects is increased for everyone."
	 	Category_color1="Very_Unhealthy"
	elif api[1]['Category']['Name'] == 'Hazardous':
		Category_Description1="(301 and higher) Health warning of emergency conditions: everyone is more likely to be affected."
		Category_color1="Hazardous"

	

                                        				
	return render (request,'main/homepage.html', {'api':api,'Category_Description': Category_Description,'Category_color':Category_color,'Category_Description1':Category_Description1,'Category_color1':Category_color1,},)


def about(request):
	return render(request, 'main/about.html')

def past_data(request):
	return render(request, 'main/past_data.html')

def predict(request):
	return render(request, 'main/predict.html')

def predictaqi(request):
	print(request)
	if request.method=='POST':
		temp={}
		temp['date']=request.POST.get('date')
		temp2= temp.copy()

	collect={ '2020-09-01':42.384532,
			            '2020-09-02': 44.12150383,
			            '2020-09-03': 44.67722625,
			            '2020-09-04': 44.86121631,
			            '2020-09-05': 46.35331658,
			            '2020-09-06': 48.71251297,
			            '2020-09-06': 51.87595561,
			            '2020-09-06': 55.42052656,
			            '2020-09-07':58.69027731,
			            '2020-09-08':61.21789739,
			            '2020-09-09': 62.78797948,
			            '2020-09-09': 63.40960047,
			            '2020-09-10': 63.21970525,
			            '2020-09-11':62.30399159,
			            '2020-09-12':60.99629274,
			            '2020-09-13':  57.53033796,
			            '2020-09-14':51.96320269,
			            '2020-09-15' : 46.14597502,
			            '2020-09-16':42.42510301,
			            '2020-09-17':40.85397905,
			            '2020-09-18' :40.07651359,
			            '2020-09-19' : 39.14226174,
			            '2020-09-20':38.20752934,
			            '2020-09-21' :37.58471079,
			            '2020-09-22' :  37.38815498,
			            '2020-09-23' :37.63716322,
			            '2020-09-24' :37.93239772,
			            '2020-09-25':61.91262299,
			            '2020-09-26':64.03342021,
			            '2020-09-27' :66.02630448,
			            '2020-09-28' :38.36439261,
			            '2020-09-29':39.71120924,
			             '2020-09-30':41.42749381, }

	result=temp2['date']
	for k in collect:
		if(k==result):
			pred=collect[k]

	actual=pred	
	if actual <= 50:
		color="good"
		descp="(0-50) Air quality is satisfactory, and air pollution poses little or no risk."
		name="Good AQI"
	
		
	elif actual >=50:
		color="moderate"
		descp="(51-100) Air quality is acceptable. However, there may be a risk for some people,particularly those who are unusually sensitive to air pollution."
		name="Moderate AQI"


	context={'actual': actual,'color':color,'descp':descp,'name':name,}

	

		


	return render(request,'main/predict.html',context)
	
		#return render(request,'main/predict.html',{'pred1':pred1},)



	#testdata=pd.DataFrame({'x':temp2}).transpose()
	#scoreval=model.predict(testdata)[0][0]`
	
	