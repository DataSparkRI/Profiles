from django.test import TestCase

class UserTest(TestCase):
    def test_profile_created(self):
        """
        Tests that a new user gets a default profile
        """
        from django.contrib.auth.models import User
        u = User.objects.create(
            username='test',
            password='test'
        )
        self.failUnless(u.get_profile())

    def test_profile_filled(self):
        """ Test that registration profile values are populated in the Profile. """
        from django.contrib.auth.models import User
        r=self.client.post('/account/register/', {
            'first_name': 'Test',
            'last_name': 'Example',
            'username': 'test',
            'email': 'test.user@example.com',
            'password1': 'test',
            'password2': 'test',
            'organization': 'ProvPlan',
            'tos': True,
        })
        self.failUnlessEqual(User.objects.count(), 1)
        user = User.objects.all()[0]
        self.failUnlessEqual(user.get_profile().organization,'ProvPlan')
  
    def test_first_last_name(self):
        """ Test first and last name for newly registered accounts """
        from django.contrib.auth.models import User
        self.client.post('/account/register/', {
            'first_name': 'Test',
            'last_name': 'Example',
            'username': 'test',
            'email': 'test.user@example.com',
            'password1': 'test',
            'password2': 'test',
            'organization': 'ProvPlan',
            'tos': True,
        })
        self.failUnlessEqual(User.objects.count(), 1)
        user = User.objects.all()[0]
        self.failUnlessEqual(user.first_name,'Test')
        self.failUnlessEqual(user.last_name,'Example')

    def test_username_uniqueness(self):
        """ Test that email address that would result in the same slugged username
        can still be used (up to 100 times).
        """
        from django.contrib.auth.models import User
        def get_post_data(num):
            return {
            'first_name': 'Test',
            'last_name': 'Example',
            #'username': 'test',
            'email': 'emailaddresslongerthanthirtycharacters@%s.com' % num,
            'password1': 'test',
            'password2': 'test',
            'organization': 'ProvPlan',
            'tos': True,
            }
  
        for i in range(100):
            response = self.client.post('/account/register/', get_post_data(i))
        self.failUnlessEqual(User.objects.count(), 100)


