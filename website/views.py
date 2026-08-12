
from .models import Course, Gallery, Blog
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .models import Staff
from src.models import AdmissionToken, AdmissionApplication, SchoolClass, Session




def is_staff(user):
    if user.staff:
        return True

    


# def loginPage(request):
    
#     page = 'login'
#     if request.user.is_authenticated:
#         if hasattr(request.user, 'staff'):
#             return redirect(reverse('staff-dashboard'))
#         elif hasattr(request.user, 'student'):
#             return redirect(reverse('student-dashboard'))
#         # return redirect('home')
#         else:
#             return redirect(reverse('admin:index'))


#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')


#         try:
#             user = User.objects.get(username=username)
            
#         except:
#             messages.error(request, 'User does not exist')

#         user = authenticate(request, username=username, password=password)


#         if user is not None:
#             login(request, user)
#             if hasattr(user, 'student'):
#                 return redirect(reverse('student-dashboard'))
#             elif hasattr(user, 'staff'):
#                 return redirect(reverse('staff-dashboard'))
                  
#         messages.error(request, 'Username OR password does not exit')
#         return redirect(reverse('login'))

#     context = {'page': page}
#     return render(request, 'website/login.html')



# def logoutUser(request):
#     logout(request)
#     return redirect('login')




def home(request):
   
    return render(request, 'website/index.html')


def about(request):
    return render(request, 'website/about.html')



def gallery(request):

    gallery_object = Gallery.objects.all()
    paginator = Paginator(gallery_object, 9)

    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)
    context = {
        'images': images,
    }

    return render(request, 'website/gallery.html', context)



def single_gallery(request, pk):
    c = Gallery.objects.get(id=pk)
    context = {
        'single_gallery': c,
    }
    return render(request, 'website/single-gallery.html', context)



def news(request):
    news_list = Blog.objects.all()
    paginator = Paginator(news_list, 3)  # Show 10 news items per page

    page = request.GET.get('page')
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        news = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        news = paginator.page(paginator.num_pages)

    context = {
        'news': news
    }
    return render(request, 'website/news.html', context)


def news_single(request, pk):
    c = Blog.objects.get(id=pk)
    b = Blog.objects.all()
    context = {
        'news_single': c,
        'news': b
    }
    return render(request, 'website/news-single.html', context)

def staff_single(request, pk):
    c = Staff.objects.get(id=pk)
    context = {
        'staff_single': c,
    }
    return render(request, 'website/staff-single.html', context)


def contact(request):
    return render(request, 'website/contact.html')


def journals(request):
    return render(request, 'website/journals.html')


# ---------------------------------------------------------------------------
# Online Admission Application (Public side)
# ---------------------------------------------------------------------------

def admission_token_entry(request):
    if request.method == 'POST':
        code = request.POST.get('token_code', '').strip()

        try:
            token = AdmissionToken.objects.get(token_code=code)
        except AdmissionToken.DoesNotExist:
            messages.error(request, 'Invalid admission token. Please check the code and try again.')
            return redirect('admission_token_entry')

        if not token.is_active:
            messages.error(request, 'This token has been deactivated. Please contact the school.')
            return redirect('admission_token_entry')

        if token.is_used:
            messages.error(request, 'This token has already been used to submit an application.')
            return redirect('admission_token_entry')

        request.session['admission_token_id'] = token.id
        return redirect('admission_apply')

    return render(request, 'website/admission_token_entry.html')


def admission_apply(request):
    token_id = request.session.get('admission_token_id')
    if not token_id:
        messages.error(request, 'Please enter your admission token to begin your application.')
        return redirect('admission_token_entry')

    token = get_object_or_404(AdmissionToken, id=token_id)
    if token.is_used or not token.is_active:
        del request.session['admission_token_id']
        messages.error(request, 'This token is no longer valid. Please contact the school.')
        return redirect('admission_token_entry')

    school_classes = SchoolClass.objects.all()
    sessions = Session.objects.all()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        date_of_birth = request.POST.get('date_of_birth')
        sex = request.POST.get('sex')
        contact_address = request.POST.get('contact_address', '').strip()
        religion = request.POST.get('religion', '').strip()
        nationality = request.POST.get('nationality', '').strip()
        state_of_origin = request.POST.get('state_of_origin', '').strip()
        lga = request.POST.get('lga', '').strip()
        guardian_phone_number = request.POST.get('guardian_phone_number', '').strip()
        guardian_occupation = request.POST.get('guardian_occupation', '').strip()
        health_status = request.POST.get('health_status', '').strip()
        qualifications_obtained = request.POST.get('qualifications_obtained', '').strip()
        class_applying_for_id = request.POST.get('class_applying_for')
        session_id = request.POST.get('session')
        passport_photograph = request.FILES.get('passport_photograph')
        declaration_agreed = request.POST.get('declaration_agreed') == 'on'
        declaration_full_name = request.POST.get('declaration_full_name', '').strip()
        declaration_date = request.POST.get('declaration_date')

        required_fields = {
            'Full Name': full_name,
            'Phone Number': phone_number,
            'Date of Birth': date_of_birth,
            'Sex': sex,
            'Contact Address': contact_address,
            'Religion': religion,
            'Nationality': nationality,
            'State of Origin': state_of_origin,
            'L.G.A.': lga,
            "Parent's/Guardian's Phone Number": guardian_phone_number,
            "Parent's/Guardian's Occupation": guardian_occupation,
            'Class Applying For': class_applying_for_id,
            'Academic Session': session_id,
            'Declaration Full Name': declaration_full_name,
            'Declaration Date': declaration_date,
        }
        errors = [f'{label} is required.' for label, value in required_fields.items() if not value]
        if not passport_photograph:
            errors.append('Passport photograph is required.')
        if not declaration_agreed:
            errors.append('You must agree to the declaration before submitting.')

        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'token': token,
                'school_classes': school_classes,
                'sessions': sessions,
                'form_data': request.POST,
                'today': timezone.now().date(),
            }
            return render(request, 'website/admission_apply.html', context)

        application = AdmissionApplication.objects.create(
            token=token,
            full_name=full_name,
            phone_number=phone_number,
            date_of_birth=date_of_birth,
            sex=sex,
            contact_address=contact_address,
            religion=religion,
            nationality=nationality,
            state_of_origin=state_of_origin,
            lga=lga,
            guardian_phone_number=guardian_phone_number,
            guardian_occupation=guardian_occupation,
            health_status=health_status,
            qualifications_obtained=qualifications_obtained,
            class_applying_for_id=class_applying_for_id or None,
            session_id=session_id or None,
            passport_photograph=passport_photograph,
            declaration_agreed=declaration_agreed,
            declaration_full_name=declaration_full_name,
            declaration_date=declaration_date,
        )

        if not application.application_number:
            application.application_number = f"APP-{application.submitted_at.year}-{application.id:05d}"
            application.save()

        token.is_used = True
        token.used_at = timezone.now()
        token.save()

        del request.session['admission_token_id']
        request.session['submitted_application_id'] = application.id

        return redirect('admission_success', pk=application.id)

    context = {
        'token': token,
        'school_classes': school_classes,
        'sessions': sessions,
        'today': timezone.now().date(),
    }
    return render(request, 'website/admission_apply.html', context)


def admission_success(request, pk):
    application = get_object_or_404(AdmissionApplication, id=pk)
    if request.session.get('submitted_application_id') != application.id:
        return redirect('admission_token_entry')
    return render(request, 'website/admission_success.html', {'application': application})