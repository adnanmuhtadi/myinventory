from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, reverse, get_object_or_404
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
    # Initialize the title and form
    title = 'List of Items'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()

    if request.method == 'POST':
        # Get filter values from the form
        household = form['household'].value()
        room = form['room'].value()
        category = form['category'].value()
        item_name = form['item_name'].value()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Apply filters if values are provided (not None or empty)
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)

        if category:
            queryset = queryset.filter(category_id=category)

        if room:
            queryset = queryset.filter(room_id=room)

        if household:
            queryset = queryset.filter(household_id=household)

            # Apply date range filter if both start and end dates are provided
            if start_date and end_date:
                try:
                    if start_date >= end_date:
                        messages.error(
                            request, "Start date cannot be after end date")
                    else:
                        queryset = queryset.filter(
                            last_updated__range=[start_date, end_date])
                except ValidationError:
                    messages.error(
                        request, "Invalid date format. Please use YYYY-MM-DD")

        if form['export_to_CSV'].value() == True:
            # Export data to CSV if the export checkbox is selected
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="List Of Stock.csv"'
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
            for stock in queryset:
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

    # Paginate the queryset and get the current page number
    paginator = Paginator(queryset, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)

    context = {
        "form": form,
        "title": title,
        "items": items,  # Pass the paginated items to the template
    }

    return render(request, "./includes/list_items.html", context)


@login_required
def list_history(request):
    title = 'Items Audit Log'
    form = StockSearchForm(request.POST or None)
    queryset = StockHistory.objects.all().order_by('-last_updated')

    if request.method == 'POST':
        category = form['category'].value()
        item_name = form['item_name'].value()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if category:
            queryset = queryset.filter(category_id=category)

        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)

            # Apply date range filter if both start and end dates are provided
            if start_date and end_date:
                try:
                    if start_date >= end_date:
                        messages.error(
                            request, "Start date cannot be after end date")
                    else:
                        queryset = queryset.filter(
                            last_updated__range=[start_date, end_date])
                except ValidationError:
                    messages.error(
                        request, "Invalid date format. Please use YYYY-MM-DD")

        if form['export_to_CSV'].value() == True:
            # Export data to CSV if the export checkbox is selected
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            writer = csv.writer(response)
            writer.writerow([
                'CATEGORY',
                'ITEM NAME',
                'QUANTITY',
                'ISSUE QUANTITY',
                'RECEIVE QUANTITY',
                'LAST UPDATED'
            ])
            for stock in queryset:
                writer.writerow([
                    stock.category,
                    stock.item_name,
                    stock.quantity,
                    stock.issue_quantity,
                    stock.receive_quantity,
                    stock.last_updated
                ])
            return response

    # Create a Paginator instance with the queryset and specify the number of items per page
    # Change '10' to the desired number of items per page
    paginator = Paginator(queryset, 10)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')

    # Get the Page object for the current page
    page = paginator.get_page(page_number)

    context = {
        "form": form,
        "title": title,
        "queryset": queryset,
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
            item_usage=instance.item_usage,
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
            item_usage=instance.item_usage,
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
    # Create a StockCreateForm instance from the POST data, if available
    form = StockCreateForm(request.POST or None)
    success_message = f"A new item has been added successfully"

    # Check if the "Save" button was clicked
    if "save" in request.POST:
        # Check if the form data is valid
        if form.is_valid():
            # Save the form data to the database
            form.save()

            # Display a success message
            messages.success(request, success_message)

            # Redirect to the 'list_items' page
            return redirect('list_items')

    # Check if the "Add Another" button was clicked (moved outside of the first if block)
    elif "add_another" in request.POST:
        # Check if the form data is valid
        if form.is_valid():
            # Save the form data to the database
            form.save()

            # Display a success message
            messages.success(request, success_message)

            # Redirect to the 'add_items' page to add another item
            return redirect('add_items')

    # Prepare the context for rendering the template
    context = {
        "form": form,
        "title": "Add Item",
    }

    # Render the 'add_items' template with the context
    return render(request, "./includes/add_items.html", context)


@login_required
def update_items(request, pk):
    # Retrieve the Stock object with the specified primary key (pk)
    stock_instance = get_object_or_404(Stock, id=pk)

    if request.method == 'POST':
        # Check if the request method is POST (form submission)
        form = StockUpdateForm(request.POST, instance=stock_instance)
        if form.is_valid():
            # Check if the form data is valid
            updated_stock = form.save()
            item_name = updated_stock.item_name
            # Construct a success message
            success_message = f"The item '{item_name}' has been updated successfully"
            # Show a success message
            messages.success(request, success_message)
            # Redirect to the item list page upon success
            return redirect('/list_items')
    else:
        # Create a form instance with the data from the Stock object
        form = StockUpdateForm(instance=stock_instance)

    # Prepare the context for rendering the update item page
    context = {
        "title": f"Updating Item: {stock_instance.item_name}",
        'form': form
    }

    # Render the update item page
    return render(request, './includes/add_items.html', context)


@login_required
def delete_items(request, pk):
    try:
        # Get the Stock object with the given primary key (pk)
        queryset = Stock.objects.get(id=pk)
        item_name = queryset.item_name.title()  # Store the item name

        if request.method == 'POST':
            # Check if the request method is POST (delete confirmation)
            queryset.delete()  # Delete the Stock object

            success_message = f"The item '{item_name}' has been deleted successfully"
            # Show a success message
            messages.success(request, success_message)

            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'message': success_message})

        # Render the confirmation page
        return render(request, './includes/delete.html')

    except Stock.DoesNotExist:
        # Handle the case where the Stock object does not exist
        # You can customize this part to handle the error as needed
        # Render a 404.html template for a "Not Found" error
        return render(request, './includes/404.html')


@login_required
def item_detail(request, pk):
    try:
        # Try to retrieve the Stock object with the given primary key (pk)
        queryset = Stock.objects.get(id=pk)

        # Prepare the context data for rendering the item_detail.html template
        context = {
            "title": queryset.item_name,  # Set the page title to the item's name
            "queryset": queryset,  # Include the Stock object in the context
        }

        # Render the item_detail.html template with the provided context
        return render(request, "./includes/item_detail.html", context)

    except Stock.DoesNotExist:
        # If the Stock object with the given primary key does not exist, handle the exception
        # You can customize this part to display an appropriate error message or template
        # Render a 404.html template
        return render(request, './includes/404.html')


@login_required
def issue_items(request, pk):
    # Get the Stock object based on the primary key (pk)
    queryset = Stock.objects.get(id=pk)

    # Create an instance of the IssueForm, pre-populated with the Stock object data
    form = IssueForm(request.POST or None, instance=queryset)

    if form.is_valid():
        # If the submitted form is valid, update the Stock object
        instance = form.save(commit=False)

        if instance.issue_quantity > 0 and instance.issue_quantity <= instance.quantity:
            # If the issue quantity is greater than 0 and does not exceed the available quantity, proceed
            instance.quantity -= instance.issue_quantity
            instance.receive_quantity = 0
            instance.issue_by = str(request.user)

            # Display a success message indicating the item has been issued and the updated quantity
            messages.success(
                request, f"{instance.issue_quantity} '{instance.item_name}' has been issued. There are now {instance.quantity} left in the {instance.location}")

            instance.save()

            if "add_another" in request.POST:
                # If "Add Another" button is clicked, redirect to the item detail page for further actions
                return redirect('/item_detail/' + str(instance.id))
            else:
                # Otherwise, redirect to the item list
                return redirect("/list_items")
        else:
            if instance.issue_quantity <= 0:
                # Display an error message if the issue quantity is not greater than 0
                messages.error(
                    request, "Issue quantity must be greater than 0.")
            else:
                # Display an error message if the issue quantity exceeds the available quantity
                messages.error(
                    request, "Issue quantity exceeds available quantity.")
    else:
        # Create a new empty IssueForm for GET requests (initial page load)
        form = IssueForm()

    # Prepare the context data for rendering the template
    context = {
        "title": f'Item Out - {queryset.item_name}',
        "queryset": queryset,
        "form": form,
        "username": f'Issue By: {request.user}',
    }

    # Render the template with the prepared context data
    return render(request, "./includes/give_take.html", context)


@login_required
def receive_items(request, pk):
    # Get the Stock object based on the primary key (pk)
    queryset = Stock.objects.get(id=pk)

    # Create an instance of the ReceiveForm, pre-populated with the Stock object data
    form = ReceiveForm(request.POST or None, instance=queryset)

    if request.method == "POST":
        if form.is_valid():
            # If the submitted form is valid, update the Stock object
            instance = form.save(commit=False)
            instance.quantity += instance.receive_quantity
            instance.issue_quantity = 0  # Set issue_quantity to 0

            # Display a success message indicating the item has been received and the updated quantity
            messages.success(
                request, f"{instance.receive_quantity} '{instance.item_name}' has been put back. There are now {instance.quantity} in the {instance.location}")

            instance.save()

            if "add_another" in request.POST:
                # If "Add Another" button is clicked, redirect to the item detail page for further actions
                return redirect('/item_detail/' + str(instance.id))
            else:
                # Otherwise, redirect to the item list
                return redirect("/list_items")
        else:
            if instance.issue_quantity <= 0:
                # Display an error message if received quantity is not greater than 0
                messages.error(
                    request, "Received quantity must be greater than 0")
            else:
                # Display an error message if received quantity exceeds available quantity
                messages.error(
                    request, "Received quantity exceeds available quantity")

    else:
        # Create a new empty ReceiveForm for GET requests (initial page load)
        form = ReceiveForm()

    # Prepare the context data for rendering the template
    context = {
        "title": 'Item In - ' + str(queryset.item_name),
        "instance": queryset,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }

    # Render the template with the prepared context data
    return render(request, "./includes/give_take.html", context)


@login_required
def reorder_level(request, pk):
    # Retrieve the Stock object based on the provided 'pk'
    stock_instance = Stock.objects.get(id=pk)

    # Create a ReorderLevelForm instance with the Stock object as the instance
    form = ReorderLevelForm(request.POST or None, instance=stock_instance)

    if request.method == 'POST':
        # Check if the "Save & Back to Item List" button was clicked
        if 'save' in request.POST or 'add_another' in request.POST:
            # If the form is valid, save it
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                item_name = instance.item_name
                reorder_level = instance.reorder_level

                # Display a success message with the updated reorder level
                messages.success(
                    request, f"Reorder level for '{item_name}' is updated to {reorder_level}")

                if 'save' in request.POST:
                    # If "Save & Back to Item List" was clicked, redirect to the item list
                    return redirect("/list_items")
                elif 'add_another' in request.POST:
                    # If "Save & Back to Item Detail" was clicked, redirect to the item detail page
                    return redirect(f"/item_detail/{instance.id}")

    context = {
        "title": f"Reordering Item for: {stock_instance.item_name}",
        "instance": stock_instance,
        "form": form,
    }

    return render(request, "./includes/give_take.html", context)


############################################################
# Add Category & View table, Update Category Delete Category
############################################################
@login_required
def add_category(request):
    # Create a CategoryCreateForm instance
    form = CategoryCreateForm(request.POST or None)

    if request.method == "POST":
        # If it's a POST request, check which button was clicked
        if "save" in request.POST or "add_another" in request.POST:
            # If the form is valid, save it
            if form.is_valid():
                form.save()
                messages.success(
                    request, "The new category has been added successfully")

                if "save" in request.POST:
                    # If "Save" button was clicked, redirect to 'add_items'
                    return redirect('add_items')
                elif "add_another" in request.POST:
                    # If "Add Another" button was clicked, redirect to 'add_category'
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

    # Render the 'add_category' template with the context
    return render(request, "./includes/add_category.html", context)


@login_required
def update_category(request, pk):
    # Retrieve the Category object based on the provided 'pk'
    category = Category.objects.get(id=pk)

    if request.method == 'POST':
        # If it's a POST request, update the CategoryUpdateForm with the POST data and the category instance
        form = CategoryUpdateForm(request.POST, instance=category)
        if form.is_valid():
            # If the form is valid, save it
            form.save()
            messages.success(
                request, f"The category '{category.name}' has been updated successfully")
            # Redirect to 'add_category' after a successful update

            return redirect('add_category')

    else:
        # If it's not a POST request, initialize the form with the category instance
        form = CategoryUpdateForm(instance=category)

    context = {
        "title": f"Updating Item: {category.name.title()}",
        'form': form,
    }

    # Render the 'add_category' template with the context
    return render(request, './includes/add_category.html', context)


@login_required
def delete_category(request, pk):
    try:
        # Attempt to retrieve the Category object based on the provided 'pk'
        category = Category.objects.get(id=pk)
        category_name = category.name.title()

        if request.method == 'POST':
            # If it's a POST request, delete the category
            category.delete()
            success_message = f"The category '{category_name}' has been deleted successfully"
            messages.success(
                request, success_message)
            # Return a JSON response indicating success

            return JsonResponse({'success': True, 'message': success_message})

    except Category.DoesNotExist:
        # Handle the case where the category does not exist
        pass

    # Render the default 'delete' template
    return render(request, './includes/delete.html')


############################################################
# Add Location & view table, Update Location, Delete Location
############################################################
@login_required
def add_location(request):
    # Create a LocationCreateForm instance
    form = LocationCreateForm(request.POST or None)

    if request.method == "POST":
        # If it's a POST request, check which button was clicked
        if "save" in request.POST or "add_another" in request.POST:
            # If the form is valid, save it
            if form.is_valid():
                form.save()
                messages.success(
                    request, "The new location has been added successfully")

                if "save" in request.POST:
                    # If "Save" button was clicked, redirect to 'add_items'
                    return redirect('add_items')
                elif "add_another" in request.POST:
                    # If "Add Another" button was clicked, redirect to 'add_location'
                    return redirect('add_location')

    # Annotate locations with total_quantity
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

    # Render the 'add_location' template with the context
    return render(request, "./includes/add_location.html", context)


@login_required
def update_location(request, pk):
    try:
        # Retrieve the location object based on the provided 'pk'
        location = Location.objects.get(id=pk)
        location_name = location.name.title()  # Get the location name for messages

        if request.method == 'POST':
            # If it's a POST request, update the form with the POST data and the location instance
            form = LocationUpdateForm(request.POST, instance=location)

            # Check if the form data is valid
            if form.is_valid():
                # Save the form data, updating the location
                form.save()
                messages.success(
                    request, f"The location '{location_name}' has been updated successfully")
                return redirect('add_location')  # Redirect to a success page

        else:
            # If it's not a POST request, initialize the form with the location instance
            form = LocationUpdateForm(instance=location)

    except Location.DoesNotExist:
        # Handle the case where the location does not exist
        return render(request, './includes/404.html')  # Render a 404 template

    # Prepare the context for rendering the update form
    context = {
        "title": f"Updating Location: {location_name}",  # Set the page title
        'form': form  # Pass the form to the template
    }

    # Render the update location form page
    return render(request, './includes/add_location.html', context)


@login_required
def delete_location(request, pk):
    try:
        # Attempt to retrieve the location object based on the provided 'pk'
        location = Location.objects.get(id=pk)
        location_name = location.name.title()  # Get the location name for messages

        if request.method == 'POST':
            # If it's a POST request, delete the location
            location.delete()

            # Notify the user of the successful deletion
            success_message = f'The location "{location_name}" has been deleted successfully'
            # Show a success message
            messages.success(request, success_message)

            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'message': success_message})

    except Location.DoesNotExist:
        # Handle the case where the location does not exist
        pass

    # Render the default delete template
    return render(request, './includes/delete.html')


############################################################
# Add Room & view table, Update Room, Delete Room
############################################################
@login_required
def add_room(request):
    # Create a RoomCreateForm instance
    form = RoomCreateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # If it's a valid POST request, save the form data
        form.save()
        messages.success(request, "The new room has been added successfully")

        if "save" in request.POST:
            # If "Save" button was clicked, redirect to 'add_items'
            return redirect('add_items')
        elif "add_another" in request.POST:
            # If "Add Another" button was clicked, redirect to 'add_room'
            return redirect('add_room')

    # Annotate rooms with total_quantity
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

    # Render the 'add_room' template with the context
    return render(request, "./includes/add_room.html", context)


@login_required
def update_room(request, pk):
    # Retrieve the room object based on the provided 'pk'
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        # If it's a POST request, update the RoomUpdateForm with the POST data and the room instance
        form = RoomUpdateForm(request.POST, instance=room)
        if form.is_valid():
            # If the form is valid, save it
            form.save()
            messages.success(
                request, f"The room '{room.name}' has been updated successfully")
            # Redirect to 'add_room' after successful update

            return redirect('add_room')

    else:
        # If it's not a POST request, initialize the form with the room instance
        form = RoomUpdateForm(instance=room)

    context = {
        "title": f"Updating Room: {room.name.title()}",
        'form': form,
    }

    # Render the 'add_room' template with the context
    return render(request, './includes/add_room.html', context)


@login_required
def delete_room(request, pk):
    try:
        # Attempt to retrieve the room object based on the provided 'pk'
        room = Room.objects.get(id=pk)
        room_name = room.name.title()

        if request.method == 'POST':
            # If it's a POST request, delete the room
            room.delete()
            success_message = f"The room '{room_name}' has been deleted successfully"
            messages.success(
                request, success_message)
            # Return a JSON response indicating success
            return JsonResponse({'success': True, 'message': success_message})

    except Room.DoesNotExist:
        # Handle the case where the room does not exist
        pass

    # Render the default 'delete' template
    return render(request, './includes/delete.html')
