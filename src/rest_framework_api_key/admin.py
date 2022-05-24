import typing

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.db.models import QuerySet
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render

from .models import AbstractAPIKey, APIKey


class APIKeyModelAdmin(admin.ModelAdmin):
    model: typing.Type[AbstractAPIKey]

    list_display = (
        "prefix",
        "name",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
    )
    list_filter = ("created", "expiry_date", "revoked")
    search_fields = ("name", "prefix")
    search_help_text = "Search with: Name, Prefix"  # New in Django 4.0
    readonly_fields = ("prefix", "revoked", "_has_expired", "created")
    fieldsets = [
        ("API-Key", {"fields": [("name", "prefix")]}),
        ("Status", {"fields": [("revoked", "_has_expired")]}),
        ("Settings", {"fields": ["expiry_date"]}),
        ("Record Time Stamps", {"fields": ["created"]}),
    ]
    actions = ("revoke", "verify")

    def get_readonly_fields(
        self, request: HttpRequest, obj: models.Model = None
    ) -> typing.Tuple[str, ...]:
        obj = typing.cast(AbstractAPIKey, obj)
        fields: typing.Tuple[str, ...]
        fields = super(APIKeyModelAdmin, self).get_readonly_fields(request, obj) or ()
        if obj is not None and obj.revoked:
            fields += ("name", "expiry_date")
        return fields

    def save_model(
        self,
        request: HttpRequest,
        obj: AbstractAPIKey,
        form: typing.Any = None,
        change: bool = False,
    ) -> None:
        created = not obj.pk

        if created:
            key = self.model.objects.assign_key(obj)
            obj.save()
            message = (
                "The API key for {} is: {}. ".format(obj.name, key)
                + "Please store it somewhere safe: "
                + "you will not be able to see it again."
            )
            messages.add_message(request, messages.WARNING, message)
        else:
            obj.save()

    @admin.action(description="Revoke selected API-Key", permissions=["change"])
    def revoke(
        self,
        request: HttpRequest,
        queryset: typing.Union[QuerySet, typing.List[AbstractAPIKey]],
    ) -> None:
        """
        Implementation of custom action to revoke given API-Key.
        Requires selecting only one API-Key.
        """
        if len(queryset) != 1:
            return self.message_user(
                request, "Please select (only) one API-Key to revoke.", messages.ERROR
            )

        api_key = queryset[0]
        api_key.revoked = True
        api_key.save(update_fields=["revoked"])
        self.log_change(request, api_key, "Revoked the API-Key.")

        return self.message_user(request, queryset, messages.SUCCESS)

    @admin.action(description="Verify Key of selected API-Key")
    def verify(
        self,
        request: HttpRequest,
        queryset: typing.Union[QuerySet, typing.List[AbstractAPIKey]],
    ) -> typing.Optional[HttpResponse]:
        """
        Implementation of custom action to verify given API-Key.
        Requires selecting only one API-Key.
        """

        class VerificationForm(forms.Form):
            """
            Instance of forms.Form to customize its behavior
            for the :model:"rest_framework_api_key.APIKey" Verify action.
            """

            key = forms.CharField(required=True, max_length=200, label="API-Key")

        if len(queryset) != 1:
            return self.message_user(
                request, "Please select (only) one API-Key to verify.", messages.ERROR
            )

        api_key = queryset[0]

        if "apply" in request.POST:
            form = VerificationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                key = data.get("key")
                if api_key.is_valid(key):
                    self.message_user(
                        request, "Verification Succeed.", messages.SUCCESS
                    )
                    self.log_change(
                        request, api_key, "Verified the API-Key. Verification Succeed"
                    )
                else:
                    self.message_user(request, "Verification Failed.", messages.ERROR)
                    self.log_change(
                        request, api_key, "Verified the API-Key. Verification Failed"
                    )
        else:
            form = VerificationForm()
        return render(
            request,
            "admin/rest_framework_api_key/apikey/verify.html",
            context={
                **self.admin_site.each_context(request),
                "opts": self.opts,
                "instance": api_key,
                "form": form,
                "subtitle": "Verify",
                "title": api_key.name,
                "action": "verify",
            },
        )


admin.site.register(APIKey, APIKeyModelAdmin)

APIKeyAdmin = APIKeyModelAdmin  # Compatibility with <1.3
