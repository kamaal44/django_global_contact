import urllib
import urllib2
import re
from django.db import models
from django.forms.fields import EMPTY_VALUES, Field
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
from django.forms import ValidationError
import re

class CountryManager(models.Manager):
  pass
  
class Country(models.Model):
  alpha_2 = models.CharField(max_length=2) # http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
  alpha_3 = models.CharField(max_length=3) # http://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
  name = models.CharField(max_length=100)
  phone_countrycode = models.IntegerField() # http://en.wikipedia.org/wiki/List_of_country_calling_codes
  # Phone formats are in the format "+%(ccode)s%(0)d%(1)d%(2)d" etc.
  phone_formats = models.CharField(max_length=200,default='[]') # stored as a stringified list.
  phone_format_default = models.IntegerField(default=0) # 0 based index from phone_formats
  address_format = models.CharField(max_length=300, null=True) # stored as a stringified list.
  # Example address format ['%(postcode_prefix)s-%(postcode)s','%(country)s'] . Lines are added as is.

  def _get_phone_formats(self):
    try:
      phoneformats = eval(self.phone_format)
    except:
      # The phone format is not legal .. so we just return empty
      phoneformats = []
    return phoneformats
      
  def _set_phone_formats(self, phoneformats):
    if not isinstance(phoneformats, list):
      raise TypeError, _(u"Phone formats must be in list format")
    self.phone_format = str(phoneformats)
  
  phone_formats = property(_get_phone_formats, _set_phone_formats)

  def default_phone_formats(self):
    try:
      return self.phoneformats[self.phone_format_default]
    except:
      return '' # If there is no 

  def formated_phone_number(self,phonenumber, formatindex=0):
    if formatindex != self.phone_format_default: formatindex = self.phone_format_default
    if len(self.phone_formats) == 0 or formatindex > len(self.phone_formats):
      return phonenumber # We don't know any formatting so we just return the same number
    phoneformat = self.phone_formats[formatindex]
    phonenumber = re.sub('\.|\s|-|\(|\)','',phonenumber) # First we strip all old formatting
    # Check if the number is international
    ccode = str(self.phone_countrycode)
    if phonenumber[0:len(ccode)+1] == '+%s' % ccode or phonenumber[0:len(ccode)+2] == '00%s' % ccode:
      # We strip the internationalization
      phonenumber = re.sub('\+%(ccode)s|00%(ccode)s','',self.phone_countrycode) 

    context = {'ccode':ccode}
    ct = 0
    for digit in re.findall('\d',phonenumber):
      context[str(ct)] = digit
    return phoneformat % context

  def _get_address_formats(self):
    try:
      addressformat = eval(self.address_format)
    except:
      # The phone format is not legal .. so we just return empty
      addressformat = []
    return addressformat

  def _set_address_formats(self, addressformat):
    if not isinstance(addressformat, list):
      raise TypeError, _(u"Must be in list format")
    self.address_format = str(addressformat)

  address_format = property(_get_address_format, _set_address_format)

  def formated_address(self, address):
    """Returns a list of lines representing the formated lines in the address"""
    fa = []
    for line in self.address_format:
      fa.append( line % address )
    return fa

  objects = CountryManager()

