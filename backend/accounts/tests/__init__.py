
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from social_django.models import UserSocialAuth


user_model = get_user_model()

_token = Token()


class UserMixin:
    def _create_user(self, **kwargs):
        data = {
            'username': kwargs.pop('username', 'testuser1'),
            'password': kwargs.pop('password', 'asdfasdf'),
            'email': kwargs.pop('email', 'testuser1@lineup.com'),
            'level': kwargs.pop('level', 'associate'),
            'open_status': kwargs.pop('open_status', 'private'),
            **kwargs,
        }
        user = user_model.objects.create_user(**data)
        Token.objects.get_or_create(
            user=user,
            defaults={'key': kwargs.pop('token', _token.generate_key())}
        )
        return user

    def attach_socialauth(self, user, provider, uid=None, extra_data=None):
        if not uid:
            uid = f'${user.username}-${provider}'
        attr = getattr(self, f'_{provider}_extra_data')
        obj, _ = UserSocialAuth.objects.get_or_create(
            user=user, provider=provider, uid=uid,
            defaults={
                'extra_data': attr(extra_data) if callable(attr) else {},
            }
        )
        return obj

    @staticmethod
    def _steemconnect_extra_data(data=None):
        result = {'auth_time': 1535691936, 'id': 752089, 'expires': '604800', 'granted_scopes': ['vote', 'comment', 'delete_comment', 'comment_options', 'custom_json', 'claim_reward_balance'], 'account': {'id': 0, 'name': 'kaycha', 'owner': {'weight_threshold': 1, 'account_auths': [], 'key_auths': [['key-auth', 1]]}, 'active': {'weight_threshold': 1, 'account_auths': [], 'key_auths': [['key-auth', 1]]}, 'posting': {'weight_threshold': 1, 'account_auths': [['busy.app', 1], ['dtube.app', 1], ['lineup.app', 1], ['myproject.app', 1]], 'key_auths': [['key-auths', 1]]}, 'memo_key': 'memo-key', 'json_metadata': {'profile': {'profile_image': 'https://en.gravatar.com/userimage/3703223/9e24c36fcd262158dafbd45a956e1a9e.png?size=200', 'name': 'Kay Cha'}}, 'proxy': '', 'last_owner_update': '1970-01-01T00:00:00', 'last_account_update': '2018-05-29T08:41:12', 'created': '2018-02-11T07:30:18', 'mined': False, 'recovery_account': 'steem', 'last_account_recovery': '1970-01-01T00:00:00', 'reset_account': 'null', 'comment_count': 0, 'lifetime_vote_count': 0, 'post_count': 8, 'can_vote': True, 'voting_power': 0, 'last_vote_time': '2018-05-29T08:07:51', 'balance': '0.000 STEEM', 'savings_balance': '0.000 STEEM', 'sbd_balance': '0.000 SBD', 'sbd_seconds': '0', 'sbd_seconds_last_update': '1970-01-01T00:00:00', 'sbd_last_interest_payment': '1970-01-01T00:00:00', 'savings_sbd_balance': '0.000 SBD', 'savings_sbd_seconds': '0', 'savings_sbd_seconds_last_update': '1970-01-01T00:00:00', 'savings_sbd_last_interest_payment': '1970-01-01T00:00:00', 'savings_withdraw_requests': 0, 'reward_sbd_balance': '0.000 SBD', 'reward_steem_balance': '0.000 STEEM', 'reward_vesting_balance': '0.000000 VESTS', 'reward_vesting_steem': '0.000 STEEM', 'vesting_shares': '1022.473633 VESTS', 'delegated_vesting_shares': '0.000000 VESTS', 'received_vesting_shares': '29495.580100 VESTS', 'vesting_withdraw_rate': '0.000000 VESTS', 'next_vesting_withdrawal': '1969-12-31T23:59:59', 'withdrawn': 0, 'to_withdraw': 0, 'withdraw_routes': 0, 'curation_rewards': 0, 'posting_rewards': 0, 'proxied_vsf_votes': [0, 0, 0, 0], 'witnesses_voted_for': 0, 'last_post': '2018-06-30T08:04:21', 'last_root_post': '2018-06-30T08:04:21', 'average_bandwidth': 0, 'lifetime_bandwidth': '0', 'last_bandwidth_update': '2018-07-06T08:30:51', 'average_market_bandwidth': 0, 'lifetime_market_bandwidth': 0, 'last_market_bandwidth_update': '1970-01-01T00:00:00', 'vesting_balance': '0.000 STEEM', 'reputation': 0, 'transfer_history': [], 'market_history': [], 'post_history': [], 'vote_history': [], 'other_history': [], 'witness_votes': [], 'tags_usage': [], 'guest_bloggers': []}, 'username': 'kaycha', 'name': 'kaycha', 'access_token': 'token', 'token_type': None}
        if isinstance(data, dict) and data:
            result.update(data)
        return result

    @staticmethod
    def _switch_user_level(user, level):
        user.level = level
        user.save()
        user.update_model_permissions()
        return user

