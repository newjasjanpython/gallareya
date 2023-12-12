from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid

# Create your models here.


class MeUser(AbstractUser, models.Model):
    slug = models.SlugField()
    privacy = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name


@receiver(pre_save, sender=MeUser)
def generate_secure_user_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = str(uuid.uuid4())[:14]


SOCIALS_AVAIBLE = (
    ("facebook", "Facebook"),
    ("twitter", "Twitter"),
    ("instagram", "Instagram"),
    ("linkedIn", "LinkedIn"),
    ("pinterest", "Pinterest"),
    ("snapchat", "Snapchat"),
    ("tiktok", "TikTok"),
    ("youtube", "YouTube"),
    ("reddit", "Reddit"),
    ("whatsapp", "WhatsApp"),
    ("wechat", "WeChat"),
    ("tumblr", "Tumblr"),
    ("flickr", "Flickr"),
    ("twitch", "Twitch"),
    ("telegram", "Telegram"),
)

SOCIALS_ICONS = {
    "facebook": '<i class="fab fa-facebook"></i>',
    "twitter": '<i class="fab fa-twitter"></i>',
    "instagram": '<i class="fab fa-instagram"></i>',
    "linkedIn": '<i class="fab fa-linkedin"></i>',
    "pinterest": '<i class="fab fa-pinterest"></i>',
    "snapchat": '<i class="fab fa-snapchat"></i>',
    "tiktok": '<i class="fab fa-tiktok"></i>',
    "youtube": '<i class="fab fa-youtube"></i>',
    "reddit": '<i class="fab fa-reddit"></i>',
    "whatsapp": '<i class="fab fa-whatsapp"></i>',
    "wechat": '<i class="fab fa-weixin"></i>',
    "tumblr": '<i class="fab fa-tumblr"></i>',
    "flickr": '<i class="fab fa-flickr"></i>',
    "twitch": '<i class="fab fa-twitch"></i>',
    "telegram": '<i class="fab fa-telegram"></i>',
}


class Social(models.Model):
    user = models.ForeignKey(MeUser, on_delete=models.CASCADE, related_name='socials')
    name = models.CharField(choices=SOCIALS_AVAIBLE, max_length=256)
    link = models.CharField(max_length=256)

    def icon_name(self):
        try:
            return mark_safe(SOCIALS_ICONS[self.name])
        except KeyError:
            return mark_safe('<i class="fa-sharp fa-solid fa-circle-exclamation"></i>')
