from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.conf import settings
# Create your models here.


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    name = models.CharField(max_length=200,blank=True)
    profile_pic = models.ImageField(upload_to="userProfile/")
    mobile_no = models.CharField(max_length=10,blank=True)
    dob = models.DateField(null=True,blank=True)
    qualification = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.username
    

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6,decimal_places=2)
    discount_price = models.DecimalField(max_digits=6,decimal_places=2)
    image = models.ImageField(upload_to="course_cover/")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="teacher")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mode = models.CharField(max_length=10,choices=[("online","online"),("offline","offline")],default="online")
    duration = models.DurationField(null=True,blank=True)
    


    def __str__(self):
        return self.title
    

class Topic(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="course")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
class Content(models.Model):
    TEXT = "text"
    VIDEO = "video"
    BLOG = "blog"
    FILE = "file"

    CONTENT_TYPE = [
        (TEXT, "text"),
        (VIDEO, "video"),
        (BLOG, "blog"),
        (FILE,"file")

    ]
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE,related_name="topic")
    content_type = models.CharField(max_length=10,choices=CONTENT_TYPE)

    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    video = models.URLField(blank=True)
    file = models.FileField(upload_to="topic/content/",blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
class Batch(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="batch")
    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="batch_teacher")
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    batch_time = models.TimeField(null=True,blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return self.name
    

class BatchEnroll(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    join_batch = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=[("active","active"),("complete","complete"),("left","left")],default="active")

    def __str__(self):
        return f"{self.batch.name}-{self.student.email}"

class EnrollCourse(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="enrollment")
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="enroll_students")
    enroll_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress = models.PositiveSmallIntegerField(default=0)
    duration = models.DurationField(null=True,blank=True)
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.student.email}-{self.course.title}"
    

class RewartPoints(models.Model):
    EARN = "earn"
    SPEND = "spend"

    TRANSACTION_TYPE = [
        (EARN,"earn"),
        (SPEND,"spend")
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reward")
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPE,default=SPEND)
    points = models.PositiveIntegerField()
    reason = models.CharField(max_length=200,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.points}"
    

class Payment(models.Model):

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

    STATUS_CHOICES = [
        (PENDING, "pending"),
        (SUCCESS, "success"),
        (FAILED, "failed"),
        (REFUNDED, "refunded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="payments")

    course = models.ForeignKey(Course,on_delete=models.CASCADE,null=True,blank=True)
    subscription = models.ForeignKey("Subscription",on_delete=models.CASCADE,null=True,blank=True)

    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100,null=True,blank=True)
    signature = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=15,choices=STATUS_CHOICES,default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id}-{self.status}"
    

class Subscription(models.Model):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

    PLAN_CHOICE = [
        (BASIC,"basic"),
        (STANDARD,"standard"),
        (PREMIUM,"premium")
    ]

    plan = models.CharField(max_length=15,choices=PLAN_CHOICE)
    price = models.DecimalField(max_digits=6,decimal_places=2,editable=False)
    duration = models.DurationField()

    def __str__(self):
        return f"{self.plan} - ₹{self.price}"
    
    def save(self,*args,**kwargs):
        if self.plan == self.BASIC:
            self.price = 900.00
            self.duration = timedelta(days=30)
        elif self.plan == self.STANDARD:
            self.price = 2499.00
            self.duration = timedelta(days=90)
        elif self.plan == self.PREMIUM:
            self.price = 5199.00
            self.duration = timedelta(days=180)

        super.save(*args,**kwargs)


class Assignment(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name="assignment")

    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to="assignment/file/",null=True,blank=True)
    duration = models.DurationField(default=timedelta(days=7))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
