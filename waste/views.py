from typing import Any, Dict
from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.contrib.auth.models import auth,User 
from django.contrib.auth import login
from django.http import JsonResponse
from waste.models import user_Registration,userType,products,locations
from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

class indexview(TemplateView):
    template_name="home.html"
    def get_context_data(self, **kwargs):
        context=super(indexview,self).get_context_data(**kwargs)
        context['product']=products.objects.all()
        return context
    
class login_view(TemplateView):
    template_name="login.html"
    def post(self,request,*args,**kwargs):
        username=request.POST['username']
        print(username)
        password =request.POST['password']
        user=auth.authenticate(username=username,password=password)
        if user is not  None:
            login(request,user)
            if user.last_name=='1' :
                request.session['id']=user.id
                request.session.save()
                if user.is_superuser:
                    return redirect('/admin')
                elif userType.objects.get(user_id=user.id).type=="collector":
                    request.session['cid']=user.id
                    request.session.save()
                    return redirect('/collector')
                elif userType.objects.get(user_id=user.id).type == "user":
                   return redirect('/user')
                else:
                    request.session['id']=user.id
                    request.session.save()
                    return redirect('/user')

            else:
                request.session['id']=user.id
                request.session.save()
                return redirect('/user')
        else:
            return render(request,'login.html',{'message':"Invalid Username or Password"})
        
class userRegistration(TemplateView):
    template_name = 'register.html'
    
    def post(self, request, *args, **kwargs):
        # Use .get() to avoid MultiValueDictKeyError
        fullname = request.POST.get('name', '').strip()
        address  = request.POST.get('address', '').strip()
        email    = request.POST.get('email', '').strip()
        phone    = request.POST.get('phone', '').strip()
        pincode  = request.POST.get('pincode', '').strip()
        password = request.POST.get('password', '')

        # Basic validation
        if not fullname or not email or not password:
            message = "Name, email and password are required."
            return render(request, 'register.html', {'message': message, 'post': request.POST})

        # Optional: more validation (email format, phone digits, password length) here

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    password=password,
                    first_name=fullname,
                    email=email,
                )
                # Save your profile model (user_Registration) and userType
                reg = user_Registration(
                    user=user,
                    name=fullname,
                    email=email,
                    password=password,
                    address=address,
                    mobile=phone,
                    pincode=pincode
                )
                reg.save()

                usertype = userType(user=user, type='user')
                usertype.save()

            message = "Registered successfully."
            return render(request, 'login.html', {'message': message})

        except IntegrityError:
            # likely username/email already exists
            message = "Username/email already used."
            return render(request, 'register.html', {'message': message, 'post': request.POST})

        except Exception as e:
            # log error e for debugging
            message = f"An error occurred: {e}"
            return render(request, 'register.html', {'message': message})  


class shop(TemplateView):
    template_name='shop-guest.html'
    def get_context_data(self, **kwargs):
        context=super(shop,self).get_context_data(**kwargs)
        prod=products.objects.filter(status='1')
        context['prod']=prod
        return context
    
class view_product(TemplateView):
    template_name='product-guest.html'
    def get_context_data(self,**kwargs):
        context=super(view_product,self).get_context_data(**kwargs)
        pid=self.request.GET['id']
        pd=products.objects.get(id=pid)
        uid=self.request.session.get('id')
        #print("UserId :",uid)
        user=user_Registration.objects.get(user_id=uid)                                                                        
        context['user']=user
        context['pd']=pd
        return context
    
def check_pincode_view(request):
    if request.method == 'GET':
        pincode = request.GET.get('pincode', '')
        exists = locations.objects.filter(pincode=pincode).exists()
        return JsonResponse({'exists': exists})
    
class view_product(TemplateView):
    template_name='product.html'
    def get_context_data(self,**kwargs):
        context=super(view_product,self).get_context_data(**kwargs)
        pid=self.request.GET['id']
        pd=products.objects.get(id=pid)
        context['pd']=pd
        return context
        
from django.views import View
class CheckPincodeView(View):
    def get(self, request):
        pincode = request.GET.get('pincode')
        
        # Replace this with your actual pincode validation logic
        valid_pincodes = locations.objects.all()
        for i in valid_pincodes:
            if pincode == i.pincode:
                message = 'Valid pincode'
                print( i.pincode)
                return JsonResponse({'message': message})
            else:
                print( i.pincode)
                message = 'Invalid pincode'
        
        return JsonResponse({'message': message})
class Check(TemplateView):
    template_name="chech.html"