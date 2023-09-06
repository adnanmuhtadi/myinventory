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
from django.core.paginator import Paginator


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
            writer.writerow([
                'ITEM NAME',
                'CATEGORY',
                'ROOM',
                'LOCATION',
                'HOUSEHOLD',
                'QUANTITY',
                'HAS WARRANTY'
            ])
            instance = queryset
            for stock in instance:
                writer.writerow([
                    stock.item_name,
                    stock.category,
                    stock.room,
                    stock.location,
                    stock.household,
                    stock.quantity,
                    stock.has_warranty
                ])
            return response

    context = {
        "form": form,
        "title": title,
        "queryset": queryset,
    }

    return render(request, "./includes/list_items.html", context)


@login_required
def list_history(request):
    header = 'LIST OF ITEMS'
    queryset = StockHistory.objects.all().order_by('-last_updated')

    # Create a Paginator instance with the queryset and specify the number of items per page
    # Change '10' to the desired number of items per page
    paginator = Paginator(queryset, 10)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the current page
    page = paginator.get_page(page_number)

    context = {
        "header": header,
        "page": page,  # Pass the Page object to the template
    }
    return render(request, "./includes/list_history.html", context)


@receiver(post_save, sender=Stock)
def copy_to_stock_history(sender, instance, created, **kwargs):
    if created:  # Check if a new Stock object is created
        # Copy data to StockHistory
        StockHistory.objects.create(
            category=instance.category,
            item_name=instance.item_name,
            quantity=instance.quantity,
            receive_quantity=instance.receive_quantity,
            receive_by=instance.receive_by,
            issue_quantity=instance.issue_quantity,
            issue_by=instance.issue_by,
            issue_to=instance.issue_to,
            phone_number=instance.phone_number,
            created_by=instance.created_by,
            reorder_level=instance.reorder_level,
            last_updated=instance.last_updated,
            timestamp=instance.timestamp
        )
    else:  # Handle updates to existing Stock objects
        # You can choose how to handle updates here, e.g., creating a new StockHistory entry or updating an existing one
        # For simplicity, let's create a new entry on each update
        StockHistory.objects.create(
            category=instance.category,
            item_name=instance.item_name,
            quantity=instance.quantity,
            receive_quantity=instance.receive_quantity,
            receive_by=instance.receive_by,
            issue_quantity=instance.issue_quantity,
            issue_by=instance.issue_by,
            issue_to=instance.issue_to,
            phone_number=instance.phone_number,
            created_by=instance.created_by,
            reorder_level=instance.reorder_level,
            last_updated=instance.last_updated,
            timestamp=instance.timestamp
        )


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
    # Get the Stock object based on the primary key (pk)
    queryset = Stock.objects.get(id=pk)
    form = IssueForm(request.POST or None, instance=queryset)

    if form.is_valid():
        instance = form.save(commit=False)
        if instance.issue_quantity > 0 and instance.issue_quantity <= instance.quantity:
            instance.quantity -= instance.issue_quantity
            instance.receive_quantity = 0
            instance.issue_by = str(request.user)
            messages.success(
                request, f"{instance.item_name} has been issued to {instance.issue_to}. There are now {instance.issue_quantity} left in Store")
            instance.save()

            if "add_another" in request.POST:
                return redirect('/item_detail/' + str(instance.id))
            else:
                return redirect("/list_items")
        else:
            if instance.issue_quantity <= 0:
                messages.error(
                    request, "Issue quantity must be greater than 0.")
            else:
                messages.error(
                    request, "Issue quantity exceeds available quantity.")
    else:
        form = IssueForm()  # Create a new empty form for GET requests

    context = {
        "title": f'Item Out - {queryset.item_name}',
        "queryset": queryset,
        "form": form,
        "username": f'Issue By: {request.user}',
    }
    return render(request, "./includes/give_take.html", context)


@login_required
def receive_items(request, pk):
    # Get the Stock object based on the primary key (pk)
    queryset = Stock.objects.get(id=pk)
    form = ReceiveForm(request.POST or None, instance=queryset)

    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.quantity += instance.receive_quantity
            instance.issue_quantity = 0  # Set issue_quantity to 0
            messages.success(
                request, f"{instance.item_name} has been issued to {instance.issue_to}. There are now {instance.receive_quantity} left in Store")
            instance.save()

            if "add_another" in request.POST:
                return redirect('/item_detail/' + str(instance.id))
            else:
                return redirect("/list_items")
        else:
            if instance.issue_quantity <= 0:
                messages.error(
                    request, "Received quantity must be greater than 0.")
            else:
                messages.error(
                    request, "Received quantity exceeds available quantity.")

    else:
        form = ReceiveForm()  # Create a new empty form for GET requests

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
                messages.success(
                    request, "The new category has been added successfully")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(
                    request, "The new category has been added successfully")
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
                             str(queryset.name) + "' has been updated successfully")
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
        queryset_name = queryset.name.title()
        queryset.delete()
        messages.success(
            request, f"The category '{queryset_name}' has been deleted successfully")
        return JsonResponse({'success': True, 'message': f'Category "{queryset_name}" has been deleted successfully'})

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
                messages.success(
                    request, "The new location has been added successfully")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(
                    request, "The new location has been added successfully")
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
                             str(queryset.name) + "' has been updated successfully")
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
        queryset_name = queryset.name.title()
        queryset.delete()
        messages.success(
            request, f"The location '{queryset_name}' has been deleted successfully")
        return JsonResponse({'success': True, 'message': f'Location "{queryset_name}" has been deleted successfully'})

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
                messages.success(
                    request, "The new room has been added successfully")
                return redirect('add_items')
        elif "add_another" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(
                    request, "The new room has been added successfully")
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
                             str(queryset.name) + "' has been updated successfully")
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
        messages.success(
            request, f"The room '{queryset_name}' has been deleted successfully")
        return JsonResponse({'success': True, 'message': f'Room "{queryset_name}" has been deleted successfully'})

    return render(request, './includes/delete.html')
