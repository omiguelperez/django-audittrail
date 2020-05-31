'''
Created on 02-Feb-2017

@author: dharmikp
'''

from django.db import models

class ParentEntityChildFieldMap(models.Model):
    """
    
    """

    parent_entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE
    )

    child_field = models.ForeignKey(
        'Field',
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'parent_entity_child_field_map'
