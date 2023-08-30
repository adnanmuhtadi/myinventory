from django.db import models


# Create your models here.
class Household(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name.title() if self.name else ""


class Room(models.Model):
    name = models.CharField(max_length=50, blank=True,
                            null=True, help_text="Which room is the item at?")

    def __str__(self):
        return self.name.title() if self.name else ""


class Location(models.Model):
    name = models.CharField(max_length=50, blank=True,
                            null=True, help_text="Where is the item located?")

    def __str__(self):
        return self.name.title() if self.name else ""


class Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True,
                            help_text="What category is the item related to? (such Cables/Computer Parts/Tools?)")

    def __str__(self):
        return self.name.title() if self.name else ""


class Stock(models.Model):
    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)
    issue_by = models.CharField(max_length=50, blank=True, null=True)
    issue_to = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    reorder_level = models.IntegerField(default='3', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    has_warranty = models.BooleanField(default=False, blank=False, null=True)
    item_notes = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.item_name


class StockHistory(models.Model):
    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, blank=True, null=True)
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_by = models.CharField(max_length=50, blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)
    issue_by = models.CharField(max_length=50, blank=True, null=True)
    issue_to = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    reorder_level = models.IntegerField(default='0', blank=True, null=True)
    last_updated = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True)
    timestamp = models.DateTimeField(
        auto_now_add=False, auto_now=False, null=True)

    def __str__(self):
        return self.item_name
