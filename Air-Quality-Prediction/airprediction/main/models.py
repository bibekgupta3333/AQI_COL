from django.db import models

# Create your model

class Dataset(models.Model):
	date=models.CharField(max_length=120)
	Ozone=models.DecimalField(max_digits=10, decimal_places=6,blank=False)
	Pm25=models.DecimalField(max_digits=10, decimal_places=6,blank=False,null=True)

	
class Dataset1(models.Model):
	date=models.CharField(max_length=120)
	Ozone=models.DecimalField(max_digits=10, decimal_places=6,blank=False)
	Pm25=models.DecimalField(max_digits=10, decimal_places=6,blank=False,null=True)

class Dataset2(models.Model):
	date=models.CharField(max_length=120)
	Ozone=models.DecimalField(max_digits=10, decimal_places=6,blank=False)
	Pm25=models.DecimalField(max_digits=10, decimal_places=6,blank=False,null=True)

class Dataset3(models.Model):
	date=models.CharField(max_length=120)
	Ozone=models.DecimalField(max_digits=10, decimal_places=6,blank=False)
	Pm25=models.DecimalField(max_digits=10, decimal_places=6,blank=False,null=True)




class whole_dataset(models.Model):
	date=models.CharField(max_length=120)
	location=models.TextField(max_length=120)
	year=models.IntegerField(blank=False)
	month=models.IntegerField(blank=False)
	day=models.IntegerField(blank=False)
	rainfall=models.DecimalField(max_digits=10,decimal_places=6,blank=False,null=True)
	tmax=models.DecimalField(max_digits=10,decimal_places=6,blank=False,null=True)
	tmin=models.DecimalField(max_digits=10,decimal_places=6,blank=False,null=True)
	relative_humidity=models.DecimalField(max_digits=10,decimal_places=6,blank=False,null=True)
	ozone=models.DecimalField(max_digits=10, decimal_places=6,blank=False)
	Pm25=models.DecimalField(max_digits=10, decimal_places=6,blank=False,null=True)

