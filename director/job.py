from copy import copy
from datetime import datetime
from multiprocessing import Process, Queue
from StringIO import StringIO
import sys

from django.core.management import call_command
from django.db import transaction
from django.dispatch import receiver
from django.http import HttpRequest

from .models import Job, Artefact
from .signals import new_artefact


def command_name(f, *args, **kwargs):
    """
    make a descriptive name for the job command
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


def serialize(obj):
    if isinstance(obj, HttpRequest):
        return 'HttpRequest {method} {path}{querystring}'.format(
            method=obj.method,
            path=obj.path_info,
            querystring=obj.META['QUERY_STRING'],
        )
    else:
        return unicode(obj)


def worker(f, q, f_args, f_kwargs):
    """
    this function is run in the sub process
    """
    cmd, cmd_args, cmd_kwargs = command_name(f, *f_args, **f_kwargs)
    with transaction.commit_on_success():
        job = Job.objects.create(
            command=cmd,
            command_args=[
                serialize(arg) for arg in cmd_args
            ],
            command_kwargs={
                key: serialize(val) for key, val in cmd_kwargs.items()
            },
        )
    q.put(job)

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
        result = f(*f_args, **f_kwargs)
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

    # TODO:
    # save `result` as Artefact file
    Artefact.objects.create(
        job=job,
        **kwargs
    )


def run_job(f=call_command, *args, **kwargs):
    """
    This is the main public function to call
    """
    q = Queue()
    kwargs = {
        'f': f,
        'q': q,
        'f_args': args,
        'f_kwargs': kwargs,
    }
    p = Process(target=worker, kwargs=kwargs)
    p.start()
    return q.get(block=True)
