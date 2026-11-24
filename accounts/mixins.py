from django.contrib import messages


class DeleteMessageMixin:
    """Adds a success message + a cancel link to any DeleteView."""

    success_message = "Deleted successfully."

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, self.success_message)
        return response

    def get_cancel_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.get_cancel_url()
        return context
