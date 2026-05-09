from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import IceCream, CustomerProfile, Category

# ---------------- HOME PAGE ----------------
def home_page(request):
    return render(request, 'shop/home.html')

# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_home')
            elif user.is_staff:
                return redirect('staff_home')
            else:
                return redirect('customer_home')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid username or password'})

    return render(request, 'shop/login.html')

# ---------------- CUSTOMER SIGNUP ----------------
def customer_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        dob = request.POST.get('dob')

        if User.objects.filter(username=username).exists():
            return render(request, 'shop/signup.html', {'error': 'Username already exists.<br>Please choose a different one.'})

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=False,
            is_superuser=False
        )
        user.first_name = request.POST.get('full_name', '')
        user.save()
        CustomerProfile.objects.create(user=user, dob=dob if dob else None)
        return render(request, 'shop/login.html', {'message': 'Signup successful! You can now log in.'})

    return render(request, 'shop/signup.html')

def forgot_password(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        username = request.POST.get('username')
        
        if action == 'verify':
            dob = request.POST.get('dob')
            try:
                user = User.objects.get(username=username, is_staff=False, is_superuser=False)
                # Ensure profile exists
                profile, created = CustomerProfile.objects.get_or_create(user=user)
                
                if str(profile.dob) == dob:
                    return render(request, 'shop/forgot_password.html', {'verified_username': username})
                else:
                    return render(request, 'shop/forgot_password.html', {'error': 'Incorrect Date of Birth.'})
            except User.DoesNotExist:
                return render(request, 'shop/forgot_password.html', {'error': 'User not found.'})
                
        elif action == 'reset':
            new_password = request.POST.get('new_password')
            try:
                user = User.objects.get(username=username, is_staff=False, is_superuser=False)
                user.set_password(new_password)
                user.save()
                return render(request, 'shop/login.html', {'message': 'Password reset successful! You can now log in.'})
            except User.DoesNotExist:
                return render(request, 'shop/forgot_password.html', {'error': 'User not found.'})

    return render(request, 'shop/forgot_password.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------- ADMIN HOME ----------------
@login_required
@never_cache
def admin_home(request):
    return render(request, 'shop/admin_home.html')


# ---------------- STAFF MANAGEMENT ----------------
@login_required
@never_cache
def manage_staff(request):
    staff_users = User.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'shop/manage_staff.html', {'staff_users': staff_users})


@login_required
@never_cache
def add_staff(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        password = request.POST['password']
        
        # Generate username from name (lowercase, no spaces)
        username = full_name.lower().replace(" ", "")

        if User.objects.filter(username=username).exists():
            return render(request, 'shop/add_staff.html', {'error': 'A staff member with this name/username already exists.'})

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True
        )
        user.first_name = request.POST.get('full_name', '')
        user.save()
        return redirect('manage_staff')

    return render(request, 'shop/add_staff.html')


@login_required
@never_cache
def edit_staff(request, user_id):
    staff = get_object_or_404(User, id=user_id, is_staff=True)

    if request.method == 'POST':
        staff.first_name = request.POST.get('full_name', '')

        if request.POST['password']:
            staff.set_password(request.POST['password'])

        staff.save()
        return redirect('manage_staff')

    return render(request, 'shop/edit_staff.html', {'staff': staff})


@login_required
def delete_staff(request, user_id):
    if request.method == 'POST':
        staff = get_object_or_404(User, id=user_id, is_staff=True)
        staff.delete()

    return redirect('manage_staff')


# ---------------- CUSTOMER MANAGEMENT ----------------
@login_required
@never_cache
def manage_customers(request):
    customers = User.objects.filter(is_staff=False, is_superuser=False)
    return render(request, 'shop/manage_customers.html', {'customers': customers})


@login_required
@never_cache
def add_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.first_name = request.POST.get('full_name', '')
        user.save()
        return redirect('manage_customers')

    return render(request, 'shop/add_customer.html')


@login_required
def delete_customer(request, user_id):
    if request.method == 'POST':
        customer = get_object_or_404(User, id=user_id, is_staff=False)
        customer.delete()

    return redirect('manage_customers')


# ---------------- STAFF DASHBOARD & INVENTORY ----------------
@login_required
@never_cache
def staff_home(request):
    items = IceCream.objects.all()
    categories_qs = Category.objects.all()
    
    def sort_key(cat):
        name = cat.name.lower()
        if 'scoop' in name: return 1
        if 'cone' in name: return 2
        if 'bar' in name: return 3
        return 4
        
    categories = sorted(categories_qs, key=sort_key)
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', 'all')

    if search:
        items = items.filter(name__icontains=search)
    if category_id and category_id != 'all':
        items = items.filter(category_id=category_id)

    return render(request, 'shop/staff_home.html', {
        'items': items,
        'categories': categories,
        'search': search,
        'current_category': category_id,
    })

@login_required
@never_cache
def add_item(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        stock = request.POST.get('stock', 0)
        image = request.FILES.get('image')
        
        category_name = request.POST.get('category_name')
        
        category = None
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)

        IceCream.objects.create(
            name=name,
            price=price,
            stock=stock,
            image=image,
            category=category
        )
        return redirect('staff_home')

    return render(request, 'shop/add_item.html', {'categories': categories})

@login_required
@never_cache
def edit_item(request, item_id):
    item = get_object_or_404(IceCream, id=item_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        item.name = request.POST['name']
        item.price = request.POST['price']
        item.stock = request.POST.get('stock', 0)
        
        category_name = request.POST.get('category_name')
        
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            item.category = category
        else:
            item.category = None
            
        if 'image' in request.FILES:
            item.image = request.FILES['image']
            
        item.save()
        return redirect('staff_home')

    return render(request, 'shop/edit_item.html', {'item': item, 'categories': categories})

@login_required
def delete_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(IceCream, id=item_id)
        item.delete()
    return redirect('staff_home')

# ---------------- CUSTOMER DASHBOARD ----------------
@login_required
@never_cache
def customer_home(request):
    items = IceCream.objects.all()
    categories_qs = Category.objects.all()
    
    def sort_key(cat):
        name = cat.name.lower()
        if 'scoop' in name: return 1
        if 'cone' in name: return 2
        if 'bar' in name: return 3
        return 4
        
    categories = sorted(categories_qs, key=sort_key)
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', 'all')

    if search:
        items = items.filter(name__icontains=search)
    if category_id and category_id != 'all':
        items = items.filter(category_id=category_id)

    return render(request, 'shop/customer_home.html', {
        'items': items,
        'categories': categories,
        'search': search,
        'current_category': category_id,
    })

@login_required
@never_cache
def cart_view(request):
    return render(request, 'shop/cart.html')