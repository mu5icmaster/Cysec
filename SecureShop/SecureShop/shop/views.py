from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.middleware.csrf import rotate_token
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Product, Order, OrderItem
from .forms import ProductForm
from .authz import admin_required

audit = logging.getLogger("audit")

# ----------------------------------------------------------------------
# Utility helpers for email-code login
# ----------------------------------------------------------------------
def _set_preauth(request, user_id, code):
    request.session["preauth"] = {
        "user_id": user_id,
        "code": code,
        "expires_at": (timezone.now() + timedelta(minutes=10)).isoformat(),
        "attempts": 0,
    }

def _get_preauth(request):
    return request.session.get("preauth")

def _clear_preauth(request):
    request.session.pop("preauth", None)

# ----------------------------------------------------------------------
# Views
# ----------------------------------------------------------------------
def home(request):
    products = Product.objects.all().order_by("id")[:20]
    return render(request, "home.html", {"products": products})

def register(request):
    if request.method == "POST":
        # honeypot bot trap
        if request.POST.get("website"):
            messages.error(request, "Registration failed.")
            return redirect("register")

        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            audit.info("user_registered", extra={"user": user.id})
            messages.success(request, "Account created.")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    """Step 1: username/password check, then send email code."""
    next_url = request.GET.get("next") or request.POST.get("next")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # generate 6-digit code
            code = get_random_string(6, allowed_chars="0123456789")
            _set_preauth(request, user.id, code)

            # email the code (prints to console in dev)
            if user.email:
                send_mail(
                    subject="Your SecureShop login code",
                    message=f"Your code is: {code} (valid for 10 minutes)",
                    from_email=None,
                    recipient_list=[user.email],
                )
            else:
                messages.info(request, f"Dev note: code is {code} (user has no email).")

            # preserve ?next across steps
            if next_url:
                request.session["next_url"] = next_url
            return redirect("login_verify")

        messages.error(request, "Invalid credentials")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form, "next": next_url})

@csrf_protect
def login_verify(request):
    """Step 2: user enters emailed 6-digit code."""
    pre = _get_preauth(request)
    if not pre:
        messages.error(request, "Session expired. Please login again.")
        return redirect("login")

    # expiry check
    if timezone.now() > timezone.datetime.fromisoformat(pre["expires_at"]).replace(tzinfo=timezone.utc):
        _clear_preauth(request)
        messages.error(request, "Code expired. Please login again.")
        return redirect("login")

    if request.method == "POST":
        code = (request.POST.get("code") or "").strip()
        pre["attempts"] += 1
        request.session["preauth"] = pre

        if pre["attempts"] > 5:
            _clear_preauth(request)
            messages.error(request, "Too many attempts. Please login again.")
            return redirect("login")

        if code == pre["code"]:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.get(id=pre["user_id"])
            rotate_token(request)
            login(request, user)
            _clear_preauth(request)
            next_url = request.session.pop("next_url", None)
            audit.info("user_2fa_ok", extra={"user": user.id})
            if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                return redirect(next_url)
            return redirect("home")

        messages.error(request, "Invalid code.")
    return render(request, "login_verify.html", {})

@login_required
def logout_view(request):
    audit.info("user_logout", extra={"user": request.user.id})
    logout(request)
    return redirect("home")

# ----------------------------------------------------------------------
# Product management (staff only)
# ----------------------------------------------------------------------
@login_required
@admin_required
def product_new(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created")
            return redirect("home")
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form})

@login_required
@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated")
            return redirect("home")
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form})

# ----------------------------------------------------------------------
# Cart + checkout
# ----------------------------------------------------------------------
@login_required
@require_POST
def cart_add(request, pk):
    cart = request.session.get("cart", {})
    qty = int(cart.get(str(pk), 0)) + 1
    if qty > 20:
        qty = 20
        messages.info(request, "Cart limit reached (20 items).")
    cart[str(pk)] = qty
    request.session["cart"] = cart
    return redirect("home")

@login_required
def cart_view(request):
    cart = request.session.get("cart", {})
    items, total = [], 0
    ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.objects.filter(id__in=ids)}
    for pid, qty in cart.items():
        p = products.get(int(pid))
        if not p:
            continue
        sub = p.price_cents * int(qty)
        items.append({"product": p, "qty": qty, "sub": sub})
        total += sub
    return render(request, "cart.html", {"items": items, "total": total})

@login_required
@require_POST
@transaction.atomic
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")
    order = Order.objects.create(user=request.user)
    ids = [int(pid) for pid in cart.keys()]
    products = {p.id: p for p in Product.objects.filter(id__in=ids)}
    for pid, qty in cart.items():
        p = products.get(int(pid))
        if not p:
            continue
        OrderItem.objects.create(order=order, product=p, qty=int(qty), price_cents=p.price_cents)
    request.session["cart"] = {}
    audit.info("order_created", extra={"user": request.user.id, "order": order.id})
    messages.success(request, f"Order {order.id} created.")
    return redirect("home")

# ----------------------------------------------------------------------
# My Orders (privacy-safe list)
# ----------------------------------------------------------------------
@login_required
def orders_mine(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "orders_mine.html", {"orders": orders})
