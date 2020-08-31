
from django.utils.translation import ugettext as _
from rest_framework.exceptions import ValidationError


class FrozenPostError(ValidationError):
    default_detail = _('삭제 가능 기한을 지나 삭제할 수 없습니다.')
    default_code = 'denied-deletion'
