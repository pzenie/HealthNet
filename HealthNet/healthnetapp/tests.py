import datetime
from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import UserProfile,DoctorProfile,Entry,Hospital

# Most testing is currently done manually (e.g. linking, registration, login),
# as site functionality is basic enough that doing so is manageable.
# However, some calculations and formulas (e.g. age) are tested here.

def create_user_birthday(birthday):
    '''
    Creates a user with the given birthdate.
    '''
    return UserProfile(birth = birthday)

class AgeMethodTests(TestCase):
    def test_age_calculation(self):
        '''
        UserProfile.age() should return the age of the user correctly.
        366 is used to account for leap years.
        '''
        now = timezone.now()
        user = create_user_birthday(now - datetime.timedelta(days = 366*15))
        self.assertEqual(user.age(), 15)
        user = create_user_birthday(now - datetime.timedelta(days = 366*20))
        self.assertEqual(user.age(), 20)
        user = create_user_birthday(now - datetime.timedelta(days = 366*40))
        self.assertEqual(user.age(), 40)
        user = create_user_birthday(now - datetime.timedelta(days = 366*90))
        self.assertEqual(user.age(), 90)