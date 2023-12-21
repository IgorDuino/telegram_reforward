from django import forms


class BroadcastMessageForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    broadcast_text = forms.CharField(widget=forms.Textarea)


class BroadcastPhotoForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    photo_file_id = forms.CharField(widget=forms.Textarea)
    broadcast_text = forms.CharField(widget=forms.Textarea)
    button_text = forms.CharField(widget=forms.TextInput, required=False)
    button_url = forms.CharField(widget=forms.TextInput, required=False)
