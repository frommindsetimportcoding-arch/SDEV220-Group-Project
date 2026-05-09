"""
Defining our database. Each class represents a database entity (table). This is where we create our objects
which requires persistence. 
"""
from django.db import models
from django.core.validators import MinValueValidator

from .services import AmazonApi
import logging
logger = logging.getLogger(__name__)

amazon_api = AmazonApi()

# Create your models here.
class Item(models.Model):
    """
    Creates an item object and uses the amazon_product_url to reach out to the API and retrieve the 
    name, amazon_image_url, and estimated_price. Use def calculate_urgency to assign a priority_level
    from one to five. 
    """
    # URLs
    amazon_product_url = models.URLField(null=True, blank=False)
    amazon_image_url = models.URLField(null=True, blank=True)
    amazon_wishlist_url = models.URLField(null=True, blank=False)

    # Info
    name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200, blank=False)
    #description = models.TextField(blank=True)

    # Inventory
    quantity = models.IntegerField(default=0)
    max_quantity = models.IntegerField(blank=False, validators=[MinValueValidator(1)])  # Maximum qty and forces input with MinValue

    # Priority
    priority_level = models.IntegerField()  # 1 being the lowest and 5 being the highest

    # API-based price
    estimated_price = models.FloatField(null=True, blank=True)

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

    
    def calculate_urgency(self):
        """Calculates priority_level by iterating through each of the threshold percentages in lvl_list.
           Then checks the ratio of quantity/max_quantity and compares this to the percentage value of the 
           lvl_? using lvl_percent(lvl)."""
        
        # Leaving these comments to help me write a better doc string. 
        # Needs Description. Also, need to flip flop (maybe map) values that I get from my comprehension.
        # Currently 1-5 and i need 5-1 as five makes sense to be most urgent. 
        lvl_list = [self.lvl_1, self.lvl_2, self.lvl_3, self.lvl_4, self.lvl_5]
        ratio = self.quantity / self.max_quantity if self.max_quantity else 0

        self.priority_level = next((len(lvl_list) - lvl for lvl in range(len(lvl_list)) 
                              if ratio <= self.lvl_percent(lvl_list[lvl])), 1)
        return self.priority_level 
    
    def save(self, *args, **kwargs):
        self.calculate_urgency()

        if not self.amazon_image_url or not self.estimated_price:
            if self.amazon_product_url:
                asin = amazon_api.extract_asin(self.amazon_product_url)

                if asin:
                    data = amazon_api.get_product_info(asin)

                    if data:
                        if not data.get('price'):
                            logger.warning(f'API WARNING: No price found for ASIN {asin} ({self.name}).')

                        if not self.name:
                            self.name = data['name']

                        if not self.amazon_image_url:
                            self.amazon_image_url = data['image']

                        if not self.estimated_price:
                            self.estimated_price = data['price']
                    else:
                        # Log if the entire API call fails.
                        logger.error(f'API ERROR: Failed to fetch any data for ASIN {asin}.')
            else:
                # If we make it to this condition, it means were missing an image or price,
                # but there is not URL to go find them.
                logger.info(f"Item '{self.name}' saved without providing URL for API | URL: '{self.amazon_product_url}'.")  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name   