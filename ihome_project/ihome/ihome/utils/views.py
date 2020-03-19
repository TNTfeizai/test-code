from django import http
from django.contrib.auth.mixins import LoginRequiredMixin

from ihome.utils.response_code import RETCODE


class LoginRequiredJSONMixin(LoginRequiredMixin):
    '''Verify that the current user is authenticated.'''
    def handle_no_permission(self):
        return http.JsonResponse({'errno': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})