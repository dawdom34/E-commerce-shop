from django.db import models


class Coupon(models.Model):
    # Coupon name
    coupon = models.CharField(unique=True, max_length=150)
    # Discount in percent
    discount = models.SmallIntegerField(default=15)
    # Information whether the coupon is valid
    is_active = models.BooleanField(default=True)
    # Counting how many times coupon was applied
    counter = models.IntegerField(default=0)

    def counter_increment(self):
        """
        Increment counter if someone applied coupon
        """
        self.counter += 1
        self.save()

    def __str__(self):
        return self.coupon

    def activate_coupon(self):
        """
        Set is_active status to True
        """
        if self.is_active is False:
            self.is_active = True
            self.save()

    def deactivate_coupon(self):
        """
        Set is_active status to False
        """
        if self.is_active is True:
            self.is_active = False
            self.save()
