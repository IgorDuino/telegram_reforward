import random

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import BroadcastMessageForm, BroadcastPhotoForm
from .models import User
from .tasks.broadcast import broadcast_message, broadcast_photo


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "username",
        "first_name",
        "last_name",
        "language_code",
        "deep_link",
        "created_at",
        "updated_at",
        "is_blocked_bot",
    ]
    list_per_page = 30
    list_filter = ["is_blocked_bot"]
    search_fields = ("username", "user_id")

    actions = ["broadcast", "broadcast_photo"]

    def invited_users(self, obj):
        return User.objects.filter(
            deep_link=str(obj.user_id),
            is_blocked_bot=False,
            created_at__gte=obj.created_at,
        ).count()

    def broadcast(self, request, queryset):
        if "apply" in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            user_ids = list(set(u.user_id for u in queryset))
            random.shuffle(user_ids)
            broadcast_message.delay(message=broadcast_message_text, user_ids=user_ids)
            self.message_user(request, f"Broadcasting of {len(queryset)} messages has been started")

            return HttpResponseRedirect(request.get_full_path())

        form = BroadcastMessageForm(
            initial={"_selected_action": queryset.values_list("user_id", flat=True)}
        )
        return render(
            request,
            "admin/broadcast_message.html",
            {"items": queryset, "form": form, "title": " "},
        )

    def broadcast_photo(self, request, queryset):
        if "apply" in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]
            photo_file_id = request.POST["photo_file_id"]
            button_text = request.POST.get("button_text")
            button_url = request.POST.get("button_url")

            if (button_text and not button_url) or (button_url and not button_text):
                self.message_user(
                    request,
                    "Button text and url must be filled together",
                    level="ERROR",
                )
                return HttpResponseRedirect(request.get_full_path())

            user_ids = list(set(u.user_id for u in queryset))
            random.shuffle(user_ids)
            broadcast_photo.delay(
                message=broadcast_message_text,
                user_ids=user_ids,
                file_id=photo_file_id,
                button_text=button_text,
                button_url=button_url,
            )

            self.message_user(
                request,
                "Broadcasting of photo and text to %d users just started" % len(queryset),
            )
            return HttpResponseRedirect(request.get_full_path())

        form = BroadcastPhotoForm(
            initial={"_selected_action": queryset.values_list("user_id", flat=True)}
        )
        return render(
            request,
            "admin/broadcast_photo.html",
            {"items": queryset, "form": form, "title": " "},
        )
