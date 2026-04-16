from django.db import models

class Expense(models.Model):
    title       = models.CharField(max_length=100, blank=True, null=True)
    amount      = models.FloatField()
    category    = models.CharField(max_length=50)
    date        = models.DateField()
    description = models.TextField(blank=True, null=True)
    reference   = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title or self.category


class Budget(models.Model):
    """Monthly spending limit per category."""
    category = models.CharField(max_length=50, unique=True)
    limit    = models.FloatField()

    def __str__(self):
        return f"{self.category}: ₹{self.limit}"