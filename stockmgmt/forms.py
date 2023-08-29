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
            'item_notes'
        ]


class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)

    class Meta:
        model = Stock
        fields = ['household', 'room', 'category',
                  'item_name', 'start_date', 'end_date']


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
            'item_notes'
        ]


class IssueForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['issue_quantity', 'issue_to']


class ReceiveForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['receive_quantity', 'receive_by']


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
