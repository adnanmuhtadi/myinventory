from django import forms
from .models import *


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'household',
            'room',
            'location',
            'category',
            'item_name',
            'quantity',
            'reorder_level',
            'has_warranty',
            'item_notes'
        ]
        widgets = {
            # Use CheckboxInput widget for has_warranty field
            'has_warranty': forms.CheckboxInput()
        }


class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = Stock
        fields = [
            'household',
            'room',
            'category',
            'item_name',
            'start_date',
            'end_date'
        ]


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'household',
            'room',
            'location',
            'category',
            'item_name',
            'quantity',
            'reorder_level',
            'has_warranty',
            'item_notes'
        ]
        widgets = {
            # Use CheckboxInput widget for has_warranty field
            'has_warranty': forms.CheckboxInput()
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'issue_quantity',
            'item_usage'
        ]


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity']


class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['reorder_level']


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name'
        ]


class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name'
        ]


class LocationCreateForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'name'
        ]


class LocationUpdateForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'name'
        ]


class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'name'
        ]


class RoomUpdateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'name'
        ]
