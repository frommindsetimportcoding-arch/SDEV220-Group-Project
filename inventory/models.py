from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Item(models.Model):
    """
    Docstring for Items
    """
    items = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.IntegerField(default=0)
    max_quantity = models.IntegerField(blank=False, validators=[MinValueValidator(1)])  # Maximum qty and forces input with MinValue
    priority_level = models.IntegerField()  # 1 being the lowest and 5 being the highest
    unit_price = models.FloatField()

    # Thresholds as percentages
    lvl_1 = models.IntegerField(default=20)
    lvl_2 = models.IntegerField(default=40)
    lvl_3 = models.IntegerField(default=50)
    lvl_4 = models.IntegerField(default=75)
    lvl_5 = models.IntegerField(default=95)

    # I'm thinking I could use the @staticmethod here to remove the need for self parameter. 
    # Maybe play with this if you have extra time.
    
    @staticmethod
    def lvl_percent(lvl):
        return lvl / 100

    @property
    def calculate_urgency(self):
        # Needs Description. Also, need to flip flop (maybe map) values that I get from my comprehension.
        # Currently 1-5 and i need 5-1 as five makes sense to be most urgent. 
        lvl_list = [self.lvl_1, self.lvl_2, self.lvl_3, self.lvl_4, self.lvl_5]
        ratio = self.quantity / self.max_quantity if self.max_quantity else 0

        self.priority_level = next((len(lvl_list) - lvl for lvl in range(len(lvl_list)) 
                              if ratio <= Item.lvl_percent(lvl_list[lvl])), 5)
        return self.priority_level 
    
    def save(self, *args, **kwargs):
        self.calculate_urgency
        super().save(*args, **kwargs)

    def __str__(self):
        return self.items   