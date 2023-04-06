from django.db import models

# Create your models here.


class area(models.Model):
    area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)

    class Meta:
        db_table = "area"


class user(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=30)
    contact = models.CharField(max_length=15)
    area_id= models.ForeignKey(area, on_delete=models.CASCADE)
    is_admin = models.IntegerField()
    otp = models.CharField(max_length=10, null=True)
    otp_used = models.IntegerField(null=True)

    class Meta:
        db_table = "user"

class pgowner(models.Model):
    owner_id = models.AutoField(primary_key=True)
    owner_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=30)
    contact = models.CharField(max_length=15)
    area_id = models.ForeignKey(area, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, null=True)
    otp_used = models.IntegerField(null=True)

    class Meta:
        db_table = "pgowner"


class pgdetails(models.Model):
    pg_id = models.AutoField(primary_key=True)
    pg_name = models.CharField(max_length=50)
    pg_type = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    img = models.CharField(max_length=200)
    address = models.CharField(max_length=50)
    owner_id = models.ForeignKey(pgowner, on_delete=models.CASCADE)
    area_id = models.ForeignKey(area, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        db_table = "pgdetails"


class bookingdetails(models.Model):
    booking_id = models.AutoField(primary_key=True)
    booking_date = models.DateField(max_length=20)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    pg_id = models.ForeignKey(pgdetails, on_delete=models.CASCADE)
    booking_status = models.CharField(max_length=20)

    class Meta:
        db_table = "bookingdetails"


class facility(models.Model):
    facility_id = models.AutoField(primary_key=True)
    facility_name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)

    class Meta:
        db_table = "facility"


class gallery(models.Model):
    gallery_id = models.AutoField(primary_key=True)
    gallery_name = models.CharField(max_length=50)
    pg_id = models.ForeignKey(pgdetails, on_delete=models.CASCADE)

    class Meta:
        db_table = "gallery"


class inquiry(models.Model):
    inquiry_id = models.AutoField(primary_key=True)
    inquiry_title = models.CharField(max_length=20)
    inquiry_type = models.CharField(max_length=50)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    email = models.EmailField(max_length=30)
    contact = models.CharField(max_length=15)

    class Meta:
        db_table = "inquiry"


class pgfacility(models.Model):
    pg_facility_id = models.AutoField(primary_key=True)
    facility_id = models.ForeignKey(facility, on_delete=models.CASCADE)
    pg_id = models.ForeignKey(pgdetails, on_delete=models.CASCADE)

    class Meta:
        db_table = "pgfacility"


class feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    date=models.DateField()
    rate=models.IntegerField(5)
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    pg_id = models.ForeignKey(pgdetails, on_delete=models.CASCADE)
    des=models.CharField(max_length=50)

    class Meta:
        db_table = "feedback"


class wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    date = models.DateField()
    user_id = models.ForeignKey(user, on_delete=models.CASCADE)
    pg_id = models.ForeignKey(pgdetails, on_delete=models.CASCADE)

    class Meta:
        db_table = "wishlist"

