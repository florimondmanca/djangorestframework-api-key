from django.core.management import call_command


def test_system_checks_pass():
    call_command("check")
