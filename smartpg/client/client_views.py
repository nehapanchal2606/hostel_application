import random
import sys
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from Admin.form import feedbackForm, wishlistForm, pgownerForm, userFrom
from Admin.models import user, area, pgdetails, feedback, gallery, pgowner, pgfacility, facility, bookingdetails,\
    wishlist, inquiry
from datetime import date
import hashlib


def home_page(request):
    a = area.objects.all()
    p = pgdetails.objects.all()
    f = feedback.objects.all()
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)

    return render(request, "home_page.html",{"p": p, "f": f, "a": a, "rate": q})


def client_header(request, id):
    p = pgdetails.objects.get(pg_id=id)
    return render(request, "client_header.html", {"p": p})


def client_login(request):
    if request.method == "POST":

        e = request.POST["email"]
        p = request.POST["password"]
        print("+++++++++++++++++++++",e)

        np = hashlib.md5(p.encode('utf')).hexdigest()
        print("++++++++++++++++++++",np)

        val = user.objects.filter(email=e, password=np,is_admin=0).count()

        if val == 1:
            val = user.objects.filter(email=e, password=np,is_admin=0)
            print("+++++++++++++++++", val)
            for items in val:
                request.session['client_name'] = items.user_name
                request.session['client_id'] = items.user_id
                request.session['client_email'] = items.email
                print("----------",items.user_name)
                return redirect("/client/home_page/")
        else:
            messages.error(request, "Invalid username and password")
            return render(request, "client_login.html")
    else:
            return render(request, "client_login.html")


def client_forgot_password(request):
        return render(request, "client_forgot_password.html")


def registration_show(request):
    u = user.objects.all()
    return render(request, "client_registration.html", {"user": u})


def client_registration(request):
    a = area.objects.all()
    if request.method == "POST":
        form = userFrom(request.POST)
        print("--------", form.errors)
        if form.is_valid():
            try:
                form.save()
                return redirect("/client/client_login/")
            except:
                print("--------", sys.exc_info())
        else:
            pass
    else:
        form = userFrom()
        return render(request, "client_registration.html", {"form": form, "area": a})

    return render(request, "client_registration.html", {"form": form, "area": a})


def Send_OTP(request):
    otp1 = random.randint(10000, 99999)

    e = request.POST.get('email')
    print("---------------", e)
    request.session['client_email'] = e
    obj = user.objects.filter(email=e,is_admin=0).count()

    if obj == 1:
        data = user.objects.filter(email=e,is_admin=0)

        request.session['client_email'] = e

        val = user.objects.filter(email=e).update(otp=otp1, otp_used=0)
        subject = 'OTP Verification'
        message = str(otp1)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [e, ]
        send_mail(subject, message, email_from, recipient_list)
        return render(request, "reset_password.html")

    else:
        messages.error(request, "Invalid User Name or Password")
        return render(request, "client_forgot_password.html")


def set_password(request):
    totp = request.POST['otp']
    print("+++++++++++otp_++++++++++++++++++++", totp)
    tpassword = request.POST.get('npass')
    cpassword = request.POST.get('cpass')

    if tpassword == cpassword:
        e = request.session['client_email']
        val = user.objects.filter(email=e, is_admin=0, otp=totp, otp_used=0).count()

        if val == 1:
            tp = hashlib.md5(tpassword.encode('utf')).hexdigest()
            val = user.objects.filter(email=e, is_admin=0).update(otp_used=1, password=tp)
            return redirect('/client/client_login/')
        else:
            messages.error(request, 'OTP does not match')
            return render(request, "reset_password.html")
    else:
        messages.error(request, 'New Password & Confirm Password does not match')
        return render(request, "reset_password.html")

    return render(request, "reset_password.html")


def hostel_view(request):
    a = area.objects.all()
    p = pgdetails.objects.all()
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)
    # rows='''SELECT pg_id_id as ID , AVG(rate) as AVG FROM feedback GROUP by pg_id_id'''
    # print(rows)
    # qs=feedback.objects.raw(rows)

    print("++++++++++++++++++++++",q)

    page = request.GET.get('page', 1)
    print("page ----------------", page)
    paginator = Paginator(p, 6)

    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    return render(request, "hostel-grid-view.html", {"a": a, "pd": qs,"rate":q})


def list_view(request):
    a = area.objects.all()
    p = pgdetails.objects.all()
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)
    print("----", q)
    page = request.GET.get('page', 1)
    print("page ----------------", page)
    paginator = Paginator(p, 3)

    try:
        qs1 = paginator.page(page)
    except PageNotAnInteger:
        qs1 = paginator.page(1)
    except EmptyPage:
        qs1 = paginator.page(paginator.num_pages)

    return render(request, "hostel-list-view.html", {"a":a,"qs1":qs1, "rate":q, "p":p})


def hostel_page(request,id=0):
    pf = pgfacility.objects.filter(pg_facility_id=id)
    f1 = pgfacility.objects.filter(pg_id_id=id)
    a = area.objects.filter(area_id=id)
    po = pgowner.objects.filter(owner_id=id)
    u = user.objects.filter(user_id=id)
    u = user.objects.filter(user_id=id)
    p = pgdetails.objects.filter(pg_id=id)
    f = feedback.objects.filter(pg_id_id=id)
    g = gallery.objects.filter(pg_id_id=id)
    return render(request, "hostel-single-page.html", {"f": f, "g":g, "p":p, "u":u, "id":id ,"po":po, "a":a, "pf":pf, "f1": f1})


def client_edit(request):
    u = request.session['client_id']
    c = user.objects.get(user_id=u,is_admin=0)
    a = area.objects.all()
    print("++++++++++++++++++++++++++++++++++++++++++++", c)
    return render(request,"user_edit_profile.html", {"u": c, "area": a})


def client_update(request):
    u = request.session['client_id']
    c = user.objects.get(user_id=u)
    a = area.objects.all()
    print("++++++++++++++++++++++++++++++++",c)
    if request.method == "POST":
        form = userForm(request.POST, instance=c)
        print("--------", form.errors)
        if form.is_valid():
            try:
                form.save()
                return redirect("/client/home_page/")
            except:
                print("--------", sys.exc_info())
        else:
            return render(request, "user_edit_profile.html", {"form":form,"u": c, "area": a})

        return render(request, "user_edit_profile.html", {"u": c})


def client_logout(request):
    try:
        del request.session['client_id']
        del request.session['client_name']
        del request.session['client_email']

    except:
        pass

    return redirect("/client/client_login/")


def owner_logout(request):
    try:
        del request.session['owner_id']
        del request.session['owner_name']
        del request.session['email']

    except:
        pass

    return redirect("/client/owner_login/")


def load_menu(request):
    a = area.objects.all()
    return render(request, "test.html", {"a":a})


def user_dashboard(request, id = 0):
    p = pgdetails.objects.filter(pg_id=id)
    i = request.session['client_email']
    print("-------------",i)
    u = user.objects.filter(email=i)
    return render(request, "user-dashboard.html", {"u": u, "p": p})


def user_booking(request, id = 0):
    id = request.session['client_id']
    b = bookingdetails.objects.filter(user_id_id =id)
    return render(request, "user-dashboard-booking.html", {"b": b})


def feedback_insert(request):

    if request.method == "POST":
        try:
            d = date.today()
            # d = date.strftime("%Y-%m-%d")
            uid = request.session['client_id']
            desc=request.POST.get('feedback')
            rate=request.POST["rate"]
            id=request.POST.get('pg_id')
            form=feedback(des=desc,user_id_id=uid,pg_id_id=id,date=d,rate=rate)
            form.save()
            return redirect("/client/hostel_page/%s" % id)

        except:
            print("++++++++++++++",sys.exc_info())
    return redirect("/client/hostel_page/%s" % id)
    # return render(request,"hostel-single-page.html",{"p":id})


def booking_insert(request):
    if request.method == "POST":
        try:
            bd = date.today().strftime("%Y-%m-%d")
            uid = request.session['client_id']
            pid = request.POST.get('pg_id')
            status=request.POST["booking_status"]
            form = bookingdetails(user_id_id=uid,pg_id_id=pid,booking_date=bd,booking_status=status)
            form.save()
            return redirect("/client/hostel_view/")
        except:
            print("----------",sys.exc_info())
    return redirect("/client/hostel_view/%s" % pid)


def display_pg(request):
    pg=request.POST.get("selectpg")
    a=request.POST.get("selectbasic")
    print("------",pg,"----------",a)
    p = pgdetails.objects.filter(pg_type=pg,area_id_id=a)
    print(p)

    return render(request,"hostel-grid-view.html",{"pd":p})


def wishlist_show(request):
    wish = wishlist.objects.all()
    p = pgdetails.objects.all()
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)

    return render(request, "user-dashboard-wishlist.html",{"wish":wish,"p":p, "rate":q})


def insert_wishlist(request):

    if request.method == "POST":
        try:
            d = date.today().strftime("%Y-%m-%d")
            p_id = request.POST["pg_id"]
            uid = request.session['client_id']

            obj = wishlist(date=d, pg_id_id=p_id, user_id_id=uid)
            obj.save()
            return redirect("/client/wishlist/")
        except:
            print("----------", sys.exc_info())
    else:
        return render(request, "user-dashboard-wishlist.html")
    return render(request, "user-dashboard-wishlist.html")


def wish_delete(request,id):
    wish = wishlist.objects.get(wishlist_id=id)
    wish.delete()
    return redirect("/client/wishlist/")


def area_pg(request,id):
    p=pgdetails.objects.filter(area_id=id)
    return render(request, "hostel-grid-view.html", {"pd": p})


def client_inquiry(request):
    u = user.objects.all()
    return render(request, "contact-us-page.html", {"u":u})


def insert_inquiry(request):
    if request.method == "POST":
        try:
            uid = request.session['client_id']
            email = request.session['client_email']
            type = request.POST.get("inquiry_type")
            title = request.POST.get("inquiry_title")
            contact = request.POST['contact']
            form = inquiry(user_id_id=uid,inquiry_type=type,inquiry_title=title, email=email,contact=contact)
            form.save()
            return redirect("/client/client_inquiry/")
        except:
            print("----------",sys.exc_info())

    return redirect("/client/client_inquiry/")


def partner_dashboard(request):
    return render(request, "partner-dashboard.html")


def order_dashboard(request):
    return render(request, "partner-my-order-dashboard.html")


def manage_dashboard(request):
    return render(request, "partner-manage-service-dashboard.html")


def inbox_dashboard(request):
    return render(request, "partner-inbox-dashboard.html")


def withdraw(request):
    return render(request, "partner-withdraw-dashboard.html")


def sort_data(request):
    id = request.GET.get('sort')
    print("---- SORT 000000000000",id)
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)
    if id == '1':
        p = pgdetails.objects.all().order_by("amount","pg_name")
    else:
        p = pgdetails.objects.all().order_by("-amount")

    return render(request,"sort.html",{"product":p, "rate":q})


def data_sort(request):
    id = request.GET.get('sort')
    print("---- SORT 000000000000",id)
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)
    if id == '1':
        p = pgdetails.objects.all().order_by("pg_name")
    else:
        p = pgdetails.objects.all().order_by("-pg_name")

    return render(request, "short.html", {"product":p, "rate":q})


def price_filter(request):
    s = request.GET.get('start')
    e = request.GET.get('end')
    print("--- Price Filter---")
    id = request.GET.get('sort')
    print("---- SORT 000000000000",id)
    sql1 = "SELECT pg_id_id as feedback_id , FLOOR(AVG(rate)) as AVG FROM feedback GROUP by pg_id_id"
    q = feedback.objects.raw(sql1)

    p = pgdetails.objects.filter(amount__range=[int(s), int(e)])

    for data in p:
        print("+++", data.amount)
    return render(request, "list_short.html", {"product":p, "rate":q})

