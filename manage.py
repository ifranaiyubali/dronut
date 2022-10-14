#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dronut.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    is_testing = 'test' in sys.argv

    if is_testing:
        import coverage

        cov = coverage.coverage(source=['dronut_app', ],
                                omit=['*/tests*', '*/migrations/*', '*/urls*', '*/setting*',
                                      '*/__init__*', '*/wsgi*', '*/apps*', '*/management/commands/*', 'common/*'])
        cov.set_option('report:show_missing', True)
        cov.erase()
        cov.start()
    execute_from_command_line(sys.argv)

    if is_testing:
        cov.stop()
        cov.save()

        rel_dir = os.path.normcase(os.path.abspath(os.curdir) + os.sep)
        files = cov.get_data().measured_files()
        files_to_scan = []
        for filename in files:
            fnorm = os.path.normcase(filename)
            if fnorm.startswith(rel_dir):
                files_to_scan.append(filename[len(rel_dir):].replace('\\', '/'))

        output_path = 'coverage-rep.xml'
        open_kwargs = {}
        open_kwargs['encoding'] = 'utf8'
        outfile = open(output_path, "w", **open_kwargs)
        file_to_close = outfile
        delete_file = False
        from xmlreporter import XmlReporter
        try:
            xmlreporter = XmlReporter(cov)
            xmlreporter.report(files_to_scan, outfile=outfile)
        except Exception:
            delete_file = True
            raise
        finally:
            if file_to_close:
                file_to_close.close()
                if delete_file:
                    os.remove(output_path)

        cov.report()


if __name__ == '__main__':
    main()
