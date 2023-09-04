from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
import csv
from django.contrib import messages
from .models import *
from .forms import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce


############################################################
# Home View
############################################################
def home(request):
    title = 'Welcome: This is the Home Page'
    form = 'Welcome: This is the Home Page'
    context = {
        "title": title,
        "test": form,
    }

    return render(request, "./includes/home.html", context)


############################################################
# List all Items view
############################################################
@login_required
def list_items(request):
    title = 'List of Items'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()

    if request.method == 'POST':
        household = form['household'].value()
        room = form['room'].value()
        category = form['category'].value()
        item_name = form['item_name'].value()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if item_name is not None:  # Check if item_name is not None
            queryset = queryset.filter(item_name__icontains=item_name)

        if category is not None and category != '':
            queryset = queryset.filter(category_id=category)

        if room is not None and room != '':
            queryset = queryset.filter(room_id=room)

        if household is not None and household != '':
            queryset = queryset.filter(household_id=household)

            if start_date and end_date:
                try:
                    if start_date >= end_date:
                        context["error_message"] = "Start date cannot be after end date."
                    else:
                        queryset = queryset.filter(
                            last_updated__range=[start_date, end_date])
                except ValidationError:
                    messages.error(
                        request, "Invalid date format. Please use YYYY-MM-DD.")

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
            writer = csv.writer(response)
            writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
            instance = queryset
            for stock in instance:
                writer.writerow(
                    [stock.category, stock.item_name, stock.quantity])
                return response

    context = {
        "form": form,
        "title": title,
        "queryset": queryset,
    }

    return render(request, "./includes/list_items.html", context)


############################################################
# Add Items, Update Item, Delete Item, Item Details
############################################################
@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "A new item has been added")
        return redirect('list_items')
    context = {
        "form": form,
        "title": "Add Item",
    }

    return render(request, "./includes/add_items.html", context)


@login_required
def update_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = StockUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            instance = form.save(commit=False)
            form.save()
            messages.success(request, "The item '" +
                             str(instance.item_name) + "' has been updated.")
            return redirect('/list_items')

    context = {
        "title": f"Updating Item: {queryset.item_name}",
        'form': form
    }

    return render(request, './includes/add_items.html', context)


@login_required
def delete_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, "The item '" +
                         str(queryset.item_name) + "' has been deleted.")
        return redirect('/list_items')

    context = {
        "confirm": f"Are you sure you want to delete the following Item? {queryset.item_name}",
    }

    return render(request, './includes/delete.html', context)


@login_required
def item_detail(request, pk):
    queryset = Stock.objects.get(id=pk)
    context = {
        "title": queryset.item_name,
        "queryset": queryset,
    }
    return render(request, "./includes/item_detail.html", context)


@login_required
def issue_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)

    if "save" in request.POST:
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.issue_quantity > 0 and instance.issue_quantity <= instance.quantity:
                instance.quantity -= instance.issue_quantity
                instance.issue_by = str(request.user)
                messages.success(request, str(instance.item_name) + " has been issued to " + str(instance.issue_to) +
                                 ". There are now " + str(instance.quantity) + " left in Store")
                instance.save()
                return redirect("/list_items")
            else:
                if instance.issue_quantity <= 0:
                    messages.error(
                        request, "Issue quantity must be greater than 0.")
                else:
                    messages.error(
                        request, "Issue quantity exceeds available quantity.")
    elif "add_another" in request.POST:
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.issue_quantity > 0 and instance.issue_quantity <= instance.quantity:
                instance.quantity -= instance.issue_quantity
                instance.issue_by = str(request.user)
                messages.success(request, str(instance.item_name) + " has been issued to " + str(instance.issue_to) +
                                 ". There are now " + str(instance.quantity) + " left in Store")
                instance.save()
                return redirect('/item_detail/'+str(instance.id))
            else:
                if instance.issue_quantity <= 0:
                    messages.error(
                        request, "Issue quantity must be greater than 0.")
                else:
                    messages.error(
                        request, "Issue quantity exceeds available quantity.")

    context = {
        "title": 'Item Out - ' + str(queryset.item_name),
        "queryset": queryset,
        "form": form,
        "username": 'Issue By: ' + str(request.user),
    }
    return render(request, "./includes/give_take.html", context)


@login_required
def receive_items(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)

    if request.method == "POST":
        if 'save' in request.POST:  # Check if the "Save & Back to Item Detail" button was clicked
            if form.is_valid():
                instance = form.save(commit=False)
                instance.quantity += instance.receive_quantity
                instance.save()
                messages.success(request, "Received SUCCESSFULLY. " + str(
                    instance.quantity) + " " + str(instance.item_name)+"s now in Store")
                # Redirect to item detail page
                return redirect('/item_detail/'+str(instance.id))

        elif 'add_another' in request.POST:  # Check if the "Save & Back to Item List" button was clicked
            if form.is_valid():
                instance = form.save(commit=False)
                instance.quantity += instance.receive_quantity
                instance.save()
                messages.success(request, "Received SUCCESSFULLY. " + str(
                    instance.quantity) + " " + str(instance.item_name)+"s now in Store")
                return redirect('/list_items')  # Redirect to item list

    context = {
        "title": 'Item In - ' + str(queryset.item_name),
        "instance": queryset,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }
    return render(request, "./includes/give_take.html", context)


@login_required
def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)

    if request.method == 'POST':
        if 'save' in request.POST:  # Check if the "Save & Back to Item List" button was clicked
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "Reorder level for " + str(instance.item_name) +
                                 " is updated to " + str(instance.reorder_level))
                return redirect("/list_items")  # Redirect to the item list

        elif 'add_another' in request.POST:  # Check if the "Save & Back to Item Detail" button was clicked
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, "Reorder level for " + str(instance.item_name) +
                                 " is updated to " + str(instance.reorder_level))
                # Redirect to item detail page
                return redirect("/item_detail/" + str(instance.id))

    context = {
        "title": f"Reordering Item for: {queryset.item_name}",
        "instance": queryset,
        "form": form,
    }

    return render(request, "./includes/give_take.html", context)


############################################################
# Add Category & View table, Update Category Delete Category
############################################################
@login_required
def add_category(request):
    form = CategoryCreateForm(request.POST or None)
    if request.method == "POST":
        if "save" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new category has been added.")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new category has been added.")
                return redirect('add_category')

    # Annotate the categories with total quantity per category
    categories = Category.objects.annotate(
        total_quantity=Coalesce(Subquery(
            Stock.objects.filter(category=OuterRef('pk'))
            .values('category')
            .annotate(total=Sum('quantity'))
            .values('total')
        ), 0)
    )

    context = {
        "form": form,
        "title": "Add Category",
        "categories": categories,
    }

    return render(request, "./includes/add_category.html", context)


@login_required
def update_category(request, pk):
    queryset = Category.objects.get(id=pk)
    form = CategoryUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = CategoryUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, "The category '" +
                             str(queryset.name) + "' has been updated.")
            return redirect('/add_category')

    context = {
        "title": f"Updating Item: {queryset.name.title()}",
        'form': form
    }

    return render(request, './includes/add_category.html', context)


@login_required
def delete_category(request, pk):
    queryset = Category.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, "The category '" +
                         str(queryset.name) + "' has been deleted.")
        return redirect('/add_category')

    return render(request, './includes/delete.html')


############################################################
# Add Location & view table, Update Location, Delete Location
############################################################
@login_required
def add_location(request):
    form = LocationCreateForm(request.POST or None)
    if request.method == "POST":
        if "save" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new location has been added.")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new location has been added.")
                return redirect('add_location')

    locations = Location.objects.annotate(
        total_quantity=Coalesce(Subquery(
            Stock.objects.filter(location=OuterRef('pk'))
            .values('location')
            .annotate(total=Sum('quantity'))
            .values('total')
        ), 0)
    )
    context = {
        "form": form,
        "title": "Add Location",
        "locations": locations,
    }

    return render(request, "./includes/add_location.html", context)


@login_required
def update_location(request, pk):
    queryset = Location.objects.get(id=pk)
    form = LocationUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = LocationUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            messages.success(request, "The location '" +
                             str(queryset.name) + "' has been updated.")
            form.save()
            return redirect('/add_location')

    context = {
        "title": f"Updating Location: {queryset.name.title()}",
        'form': form
    }

    return render(request, './includes/add_location.html', context)


@login_required
def delete_location(request, pk):
    queryset = Location.objects.get(id=pk)
    if request.method == 'POST':
        queryset.delete()
        messages.success(request, "The location '" +
                         str(queryset.name) + "' has been deleted.")
        return redirect('/add_location')

    return render(request, './includes/delete.html')


############################################################
# Add Room & view table, Update Room, Delete Room
############################################################
def add_room(request):
    form = RoomCreateForm(request.POST or None)
    if request.method == "POST":
        if "save" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new room has been added.")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "The new room has been added.")
                return redirect('add_room')

    rooms = Room.objects.annotate(
        total_quantity=Coalesce(Subquery(
            Stock.objects.filter(room=OuterRef('pk'))
            .values('room')
            .annotate(total=Sum('quantity'))
            .values('total')
        ), 0)
    )
    context = {
        "form": form,
        "title": "Add Room",
        "rooms": rooms,
    }

    return render(request, "./includes/add_room.html", context)


@login_required
def update_room(request, pk):
    queryset = Room.objects.get(id=pk)
    form = RoomUpdateForm(instance=queryset)
    if request.method == 'POST':
        form = RoomUpdateForm(request.POST, instance=queryset)
        if form.is_valid():
            form.save()
            messages.success(request, "The room '" +
                             str(queryset.name) + "' has been updated.")
            return redirect('/add_room')

    context = {
        "title": f"Updating Room: {queryset.name.title()}",
        'form': form,
    }

    return render(request, './includes/add_room.html', context)


@login_required
def delete_room(request, pk):
    queryset = Room.objects.get(id=pk)
    if request.method == 'POST':
        queryset_name = queryset.name.title()
        queryset.delete()
        messages.success(request, f"Successfully deleted '{queryset_name}'")
        return JsonResponse({'success': True, 'message': f'Room "{queryset_name}" deleted successfully'})

    return render(request, './includes/delete.html')
