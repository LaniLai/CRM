from django.test import TestCase

# Create your tests here.

from django.forms import ModelForm

import re
url = '/bossadmin/repository/customerinfo/?&pager=2&pager=2'

ret = re.search('&pager=\d+', url)
print(url.strip(ret.group()))
