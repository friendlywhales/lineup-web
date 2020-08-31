
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django_mysql.models.fields import JSONField


class DistinctArrayField(JSONField):
    def get_db_prep_value(self, value, connection, prepared=False):
        if not isinstance(value, (list, tuple)):
            raise ValidationError(_('list or tuple is allowed'))
        return super().get_db_prep_value(tuple(frozenset(value)),
                                         connection,
                                         prepared=False)

