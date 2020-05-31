from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import F, Q


def get_audit_qs(model_name, object_id):
    FieldDiff = apps.get_model('audit_trail', 'FieldDiff')
    return FieldDiff.objects.filter(
        (Q(xaction__entity__entity_name=model_name, xaction__pfield_val=object_id)
         | Q(
                    xaction__xaction_parent_entity_child_fields__parent_entity_child_fields__parent_entity__entity_name=model_name,
                    xaction__xaction_parent_entity_child_fields__field_val=object_id))). \
        order_by('-xaction__ts'). \
        annotate(transacted_on=F('xaction__ts'),
                 transacted_by=F('xaction__user__' + get_user_model().USERNAME_FIELD),
                 transaction_type=F('xaction__xaction_type'),
                 field_name=F('field_id__name'),
                 current_val=F('curr_val__data'),
                 current_val_type=F('curr_val__content_type__type'),
                 previous_val=F('prev_val__data'),
                 previous_val_type=F('prev_val__content_type__type')
                 )


def get_audit_trail(model_name, object_id):
    return get_audit_qs(
        model_name, object_id
    ).values(
        'transacted_on', 'transacted_by',
        'transaction_type', 'field_name',
        'current_val', 'current_val_type',
        'previous_val', 'previous_val_type',
        'xaction__display_text'
    )
