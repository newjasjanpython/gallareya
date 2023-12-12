from django.db.models.signals import pre_save
from django.dispatch import receiver
from PIL.Image import open as imopen
from django.db import models
import random
import uuid
import os

# Create your models here.


class Artist(models.Model):
    secure_key = models.CharField(max_length=14, editable=False)
    user = models.OneToOneField('artist.MeUser', on_delete=models.CASCADE, related_name='artist_obj')
    fullname = models.CharField(max_length=256, verbose_name="To'liq ismi")
    about = models.TextField(verbose_name='Malumot')
    image = models.ImageField(upload_to='images/artist/', verbose_name='Surati')
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    class Meta:
        ordering = ('-pk',)

    def get_rate(self):
        values = list(map(lambda t: float(t.get_rate()), self.arts.all()))
        try:
            res = sum(values) / len(values)
            return str(res)
        except:
            return '0.0'

    def get_likes(self):
        return sum([i.likes for i in self.arts.all()])

    def get_image(self):
        if self.image:
            return self.image.url
        return "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    def get_name(self):
        return self.fullname
    
    def get_text(self):
        return self.about or "Rassom"
    
    def get_link(self):
        return f"/profile/{self.user.username}"

    def __str__(self):
        return self.get_name()


@receiver(pre_save, sender=Artist)
def generate_secure_key(sender, instance, **kwargs):
    if not instance.secure_key:
        instance.secure_key = str(uuid.uuid4())[:14]


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Nomi")
    ordering = models.PositiveBigIntegerField(default=0)
    has_image = models.BooleanField(default=False)
    dark_image = models.ImageField(upload_to='images/categories/', null=True, blank=True)
    light_image = models.ImageField(upload_to='images/categories/', null=True, blank=True)

    wall_image = models.ImageField(upload_to='images/three/wall/room/', null=True, blank=True)
    floor_image = models.ImageField(upload_to='images/three/floor/room/', null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_image(self):
        try:
            c = random.choice(list(self.carts.all()))
            if c.image:
                return c.image.url
            return c.image_url
        except:
            return 'https://source.unsplash.com/random/1366x786?not-found'

    def get_name(self):
        return self.name
    
    def get_text(self):
        return f"{self.name} nomli bo'lim"
    
    def get_link(self):
        return f"/view:{self.pk}/category"

    def __str__(self):
        return self.get_name()


class OnVerifyArt(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name='verify_arts', verbose_name="Sanatkor", null=True, blank=True)
    about = models.TextField(default="No data about image", verbose_name='Malumot', null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='verify_carts', verbose_name='Turi', blank=True)
    image = models.CharField(max_length=99999, null=True, blank=True)
    name = models.CharField(max_length=256, verbose_name='Nomi', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    viewed = models.BooleanField(default=False)
    rates = models.PositiveBigIntegerField(default=0)

    verified = models.BooleanField(default=False)


class Art(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.PROTECT, related_name='arts', verbose_name="Sanatkor")
    about = models.TextField(default="No data about image", verbose_name='Malumot')
    categories = models.ManyToManyField(Category, related_name='carts', verbose_name='Turi')
    image = models.FileField(upload_to='images/arts/', verbose_name='Surat', null=True, blank=False)
    image_url = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, verbose_name='Nomi')
    search_time = models.PositiveBigIntegerField(default=0, editable=False)
    views = models.PositiveBigIntegerField(default=0)
    likes = models.PositiveBigIntegerField(default=0, editable=False)
    on_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ('-likes',)

    def get_rate(self):
        values = list(map(lambda t: t.rate, self.rates.all()))
        try:
            res = sum(values) / len(values)
            return str(res)
        except:
            return '0.0'

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def get_name(self):
        return self.name
    
    def get_text(self):
        return self.about
    
    def get_link(self):
        return f"/view:{self.pk}/art"

    def get_extension(self):
        name, extension = os.path.splitext(self.image.path)
        return extension

    def __str__(self):
        return self.get_name()

    def framed(self):
        try:
            return f"/frame-image-properly?path=." + self.image.url
        except:
            return "https://img.freepik.com/free-vector/page-found-concept-illustration_114360-1869.jpg"

    def image_width(self):
        try:
            image = imopen(self.image.path)
            width = image.width
            height = image.height
            percentage = height // 30
            new_width = width // percentage

            return new_width
        except FileNotFoundError:
            return 60


class Rate(models.Model):
    object_elem = models.ForeignKey(Art, on_delete=models.CASCADE, related_name='rates')
    rate = models.DecimalField(decimal_places=2, max_digits=3)


class WebUser(models.Model):
    user = models.OneToOneField('artist.MeUser', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_images')
    data = models.TextField()

    def __str__(self):
        return self.user.username


class Feedback(models.Model):
    web_user = models.ForeignKey(WebUser, on_delete=models.CASCADE)
    art = models.ForeignKey(Art, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.web_user.user.username}'s feedback on {self.date}"
    
    class Meta:
        ordering = ('-id',)


class AnonimousDevices(models.Model):
    ip = models.GenericIPAddressField()
    meta_cookies = models.CharField(max_length=256)
    data = models.TextField()
