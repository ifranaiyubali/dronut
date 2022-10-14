# coding: utf-8
# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""XML reporting for coverage.py"""

import os
import os.path
import sys
import time
import defusedxml.minidom

from coverage.misc import isolate_module
from django.utils.module_loading import import_string

DTD_URL = 'https://raw.githubusercontent.com/cobertura/web/master/htdocs/xml/coverage-04.dtd'

def abs_file(path):
    """Return the absolute normalized form of `path`."""
    try:
        path = os.path.realpath(path)
    except UnicodeError:
        pass
    path = os.path.abspath(path)
    return path


def canonical_filename(filename):
    """Return a canonical file name for `filename`.
    An absolute path with no redundant components and normalized case.
    """
    cf = filename
    if not os.path.isabs(filename):
        for path in [os.curdir] + sys.path:
            if path is None:
                continue
            f = os.path.join(path, filename)
            try:
                exists = os.path.exists(f)
            except UnicodeError:
                exists = False
            if exists:
                cf = f
                break
    cf = abs_file(cf)
    return cf


MAX_FLAT = 200

def get_analysis_to_report(coverage, morfs):
    """Get the files to report on.
    For each morf in `morfs`, if it should be reported on (based on the omit
    and include configuration options), yield a pair, the `FileReporter` and
    `Analysis` for the morf.
    """
    file_reporters = coverage._get_file_reporters(morfs)
    config = coverage.config

    for fr in sorted(file_reporters):
        try:
            analysis = coverage._analyze(fr)
        except Exception:
            # Only report errors for .py files, and only if we didn't
            # explicitly suppress those errors.
            # NotPython is only raised by PythonFileReporter, which has a
            # should_be_python() method.
            if fr.should_be_python():
                if config.ignore_errors:
                    msg = "Couldn't parse Python file '{}'".format(fr.filename)
                    coverage._warn(msg, slug="couldnt-parse")
                else:
                    raise
        else:
            yield (fr, analysis)


def rate(hit, num):
    """Return the fraction of `hit`/`num`, as a string."""
    if num == 0:
        return "1"
    else:
        return "%.4g" % (float(hit) / num)


class XmlReporter(object):
    """A reporter for writing Cobertura-style XML coverage results."""

    def __init__(self, coverage):
        self.coverage = coverage
        self.config = self.coverage.config

        self.source_paths = set()
        if self.config.source:
            for src in self.config.source:
                if os.path.exists(src):
                    self.source_paths.add(src)
        self.packages = {}
        self.xml_out = None

    def report(self, morfs, outfile=None):
        """Generate a Cobertura-compatible XML report for `morfs`.
        `morfs` is a list of modules or file names.
        `outfile` is a file object to write the XML to.
        """
        # Initial setup.
        outfile = outfile or sys.stdout
        has_arcs = self.coverage.get_data().has_arcs()

        # Create the DOM that will store the data.
        impl = import_string(defusedxml.minidom.__origin__).getDOMImplementation()
        self.xml_out = impl.createDocument(None, "coverage", None)

        # Write header stuff.
        xcoverage = self.xml_out.documentElement
        xcoverage.setAttribute("version", "1.0")
        xcoverage.setAttribute("timestamp", str(int(time.time()*1000)))
        xcoverage.appendChild(self.xml_out.createComment(" Based on %s " % DTD_URL))

        # Call xml_file for each file in the data.
        for fr, analysis in get_analysis_to_report(self.coverage, morfs):
            self.xml_file(fr, analysis, has_arcs)

        xsources = self.xml_out.createElement("sources")
        xcoverage.appendChild(xsources)

        # Populate the XML DOM with the source info.
        for path in sorted(self.source_paths):
            rel_dir = os.path.normcase(os.path.abspath(os.curdir) + os.sep)
            rel_name = path[len(rel_dir):]
            xsource = self.xml_out.createElement("source")
            xsources.appendChild(xsource)
            txt = self.xml_out.createTextNode('./' + rel_name)
            xsource.appendChild(txt)

        lnum_tot, lhits_tot = 0, 0
        bnum_tot, bhits_tot = 0, 0

        xpackages = self.xml_out.createElement("packages")
        xcoverage.appendChild(xpackages)

        # Populate the XML DOM with the package info.
        for pkg_name, pkg_data in sorted(self.packages.items()):
            class_elts, lhits, lnum, bhits, bnum = pkg_data
            xpackage = self.xml_out.createElement("package")
            xpackages.appendChild(xpackage)
            xclasses = self.xml_out.createElement("classes")
            xpackage.appendChild(xclasses)
            for _, class_elt in sorted(class_elts.items()):
                xclasses.appendChild(class_elt)
            xpackage.setAttribute("name", pkg_name.replace(os.sep, '.'))
            xpackage.setAttribute("line-rate", rate(lhits, lnum))
            if has_arcs:
                branch_rate = rate(bhits, bnum)
            else:
                branch_rate = "0"
            xpackage.setAttribute("branch-rate", branch_rate)
            xpackage.setAttribute("complexity", "0")

            lnum_tot += lnum
            lhits_tot += lhits
            bnum_tot += bnum
            bhits_tot += bhits

        xcoverage.setAttribute("lines-valid", str(lnum_tot))
        xcoverage.setAttribute("lines-covered", str(lhits_tot))
        xcoverage.setAttribute("line-rate", rate(lhits_tot, lnum_tot))
        if has_arcs:
            xcoverage.setAttribute("branches-valid", str(bnum_tot))
            xcoverage.setAttribute("branches-covered", str(bhits_tot))
            xcoverage.setAttribute("branch-rate", rate(bhits_tot, bnum_tot))
        else:
            xcoverage.setAttribute("branches-covered", "0")
            xcoverage.setAttribute("branches-valid", "0")
            xcoverage.setAttribute("branch-rate", "0")
        xcoverage.setAttribute("complexity", "0")

        # Write the output file.
        outfile.write(serialize_xml(self.xml_out))

        # Return the total percentage.
        denom = lnum_tot + bnum_tot
        if denom == 0:
            pct = 0.0
        else:
            pct = 100.0 * (lhits_tot + bhits_tot) / denom
        return pct

    def xml_file(self, fr, analysis, has_arcs):
        """Add to the XML report for a single file."""

        # Create the 'lines' and 'package' XML elements, which
        # are populated later.  Note that a package == a directory.
        filename = fr.filename.replace("\\", "/")
        rel_dir = os.path.normcase(os.path.abspath(os.curdir) + os.sep)
        rel_name = filename[len(rel_dir):]
        dirname = os.path.dirname(rel_name) or u"."
        dirname = "/".join(dirname.split("/")[:self.config.xml_package_depth])
        package_name = dirname.replace("/", ".")
        package = self.packages.setdefault(package_name, [{}, 0, 0, 0, 0])
        xclass = self.xml_out.createElement("class")

        xclass.appendChild(self.xml_out.createElement("methods"))

        xlines = self.xml_out.createElement("lines")
        xclass.appendChild(xlines)

        xclass.setAttribute("name", package_name + '.' + os.path.relpath(rel_name, dirname))
        xclass.setAttribute("filename", './' + rel_name.replace("\\", "/"))
        xclass.setAttribute("complexity", "0")

        branch_stats = analysis.branch_stats()
        missing_branch_arcs = analysis.missing_branch_arcs()

        # For each statement, create an XML 'line' element.
        for line in sorted(analysis.statements):
            xline = self.xml_out.createElement("line")
            xline.setAttribute("number", str(line))

            # Q: can we get info about the number of times a statement is
            # executed?  If so, that should be recorded here.
            xline.setAttribute("hits", str(int(line not in analysis.missing)))

            if has_arcs:
                if line in branch_stats:
                    total, taken = branch_stats[line]
                    xline.setAttribute("branch", "true")
                    xline.setAttribute(
                        "condition-coverage",
                        "%d%% (%d/%d)" % (100*taken//total, taken, total)
                        )
                if line in missing_branch_arcs:
                    annlines = ["exit" if b < 0 else str(b) for b in missing_branch_arcs[line]]
                    xline.setAttribute("missing-branches", ",".join(annlines))
            xlines.appendChild(xline)

        class_lines = len(analysis.statements)
        class_hits = class_lines - len(analysis.missing)

        if has_arcs:
            class_branches = sum(t for t, k in branch_stats.values())
            missing_branches = sum(t - k for t, k in branch_stats.values())
            class_br_hits = class_branches - missing_branches
        else:
            class_branches = 0.0
            class_br_hits = 0.0

        # Finalize the statistics that are collected in the XML DOM.
        xclass.setAttribute("line-rate", rate(class_hits, class_lines))
        if has_arcs:
            branch_rate = rate(class_br_hits, class_branches)
        else:
            branch_rate = "0"
        xclass.setAttribute("branch-rate", branch_rate)

        package[0][rel_name] = xclass
        package[1] += class_hits
        package[2] += class_lines
        package[3] += class_br_hits
        package[4] += class_branches


def serialize_xml(dom):
    """Serialize a minidom node to XML."""
    out = dom.toprettyxml()
    return out
