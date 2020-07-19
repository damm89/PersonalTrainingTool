from allauth.account.views import SignupView
from allauth.account.forms import SignupForm


class ProfileSignupView(SignupView):

  template_name = 'account/signup.html'
  success_url = ''
  form_class = SignupForm
  profile_class = None  
  is_user = None
  is_customer = None

  def form_valid(self, form):
    response = super(ProfileSignupView, self).form_valid(form)
    profile = self.profile_class
    profile.is_user = self.is_user
    profile.save()

    return response