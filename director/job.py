from copy import copy
from datetime import datetime
from multiprocessing import Process
from StringIO import StringIO
import sys

from django.core.management import call_command
from django.dispatch import receiver

from .models import Job, Artefact
from .signals import new_artefact


def command_name(f, *args, **kwargs):
    """

    """
    command_args = copy(args)
    command_kwargs = copy(kwargs)
    if f is call_command:
        name = './manage.py {}'.format(
            command_kwargs.pop('name', command_args.pop(0))
        )
    else:
        try:
            f.__self__
        except AttributeError:
            # bare function (or staticmethod)
            name = '{}.{}'.format(
                f.__module__,
                f.__name__
            )
        else:
            # method or classmethod
            name = '{}.{}.{}'.format(
                f.__self.__.__module__,
                f.__self.__.__name__,
                f.__name__,
            )
    return name, command_args, command_kwargs


def worker(f, *args, **kwargs):
    """
    this function is run in the sub process
    """
    command, command_args, command_kwargs = command_name(f, *args, **kwargs)
    job = Job.objects.create(
        command=command,
        command_args=command_args,
        command_kwargs=command_kwargs,
    )

    @receiver(new_artefact)
    def register_artefact(sender, **kwargs):
        Artefact.objects.create(
            job=job,
            **kwargs
        )

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr
    sys.stdout = stdout = StringIO()
    sys.stderr = stderr = StringIO()
    try:
        call_command(command, *args, **kwargs)
    except SystemExit as e:
        exit_code = e.message
    except BaseException as e:
        exit_code = 1
    else:
        exit_code = 0
    finally:
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr
        stdout.seek(0)
        stderr.seek(0)

        job.stdout = stdout.read()
        job.stderr = stderr.read()
        job.exit_code = exit_code
        job.ended_at = datetime.now()
        job.save()


def run_job(f=call_command, *args, **kwargs):
    p = Process(target=f, args=args, kwargs=kwargs)
    p.start()
