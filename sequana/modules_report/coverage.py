# coding: utf-8
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>,
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Module to write coverage report"""
import os

import pandas as pd

from sequana import bedtools
from sequana.modules_report.base_module import SequanaBaseModule
from sequana.utils import config


class SequanaModule(SequanaBaseModule):
    """ Write HTML report of coverage analysis. This class takes either a
    :class:`GenomeCov` instances or a csv file where analysis are stored.
    """
    def __init__(self, data):
        """
        :param input: 
        """
        super().__init__()
        try:
            self.bed = bedtools.GenomeCov(data)
        except FileNotFoundError:
            msg = ("The csv file is not present. Please, check if your"
                   " file is present.")
            raise FileNotFoundError(msg)
        except TypeError:
            self.bed = data
        try:
            self.create_reports()
        except:
            msg = ("Data must be either a csv file or a :class:`GenomeCov` "
                   "instance.")
            raise TypeError(msg)
        self.title = "Coverage Report of {0}".format(config.sample_name)
        self.intro = ("<p>Report the coverage of your sample {0} to check the "
                      "quality of your mapping and to highlight regions of "
                      "interest (under and over covered).</p>".format(
                      config.sample_name))
        self.create_report_content()
        self.create_html(config.sample_name + ".coverage.html")

    def create_report_content(self):
        self.sections = list()
        self.chromosome_table()

    def chromosome_table(self):
        """ Create table with links to chromosome reports
        """
        formatter = '<a target="_blank" alt={0} href="{1}">{0}</a>'
        link = "coverage_reports" + os.sep + "{0}.cov.html"
        df = pd.DataFrame([[formatter.format(chrom.chrom_name,
                          link.format(chrom.chrom_name)),
                          chrom.get_size(), chrom.get_mean_cov(),
                          chrom.get_var_coef()] for chrom in
                          self.bed.chr_list],
                          columns=["chromosome", "size", "mean_coverage",
                          "coef_variation"])
        html_table = self.dataframe_to_html_table(df)
        self.sections.append({
            "name": "Chromosomes",
            "anchor": "chromosomes",
            "content": (
                "<p>Link to coverage analysis report for each chromosome. "
                "Size, mean coverage and coefficient of variation are reported"
                " in the table below.</p>\n{0}".format(html_table))
            })

    def create_reports(self):
        """ Create HTML report for each chromosome present in data.
        """ 
        chrom_output_dir = config.output_dir + os.sep + "coverage_reports"
        if not os.path.exists(chrom_output_dir):
            os.makedirs(chrom_output_dir)
        for chrom in self.bed:
            ChromosomeCoverageModule(chrom)


class ChromosomeCoverageModule(SequanaBaseModule):
    """ Write HTML report of coverage analysis for each chromosome. It is
    created by CoverageModule.
    """
    def __init__(self, chromosome):
        """
        """
        super().__init__()
        # to define where are css and js
        self.path = "../"
        self.chromosome = chromosome
        self.title = "Coverage analysis of chromosome {0}".format(
            self.chromosome.chrom_name)
        self.intro = ("<p>The genome coverage analysis of the chromosome "
                      "<b>{0}</b>.</p>".format(self.chromosome.chrom_name))
        self.create_report_content()
        self.create_html("coverage_reports/{0}.cov.html".format(
            self.chromosome.chrom_name))


    def create_report_content(self):
        """ Generate the sections list to fill the HTML report.
        """
        self.sections = list()
        
        self.coverage_plot()
        self.coverage_barplot()
        # self.submappings()
        self.basic_stats()
        self.regions_of_interest()
        self.normalized_coverage()
        self.zscore_distribution()

    def coverage_plot(self):
        """ Coverage section.
        """
        image = self.create_embedded_png(self.chromosome.plot_coverage,
                                      input_arg="filename")
        self.sections.append({
            "name": "Coverage",
            "anchor": "coverage",
            "content": (
                "<p>The following figure shows the per-base coverage along the"
                " reference genome (black line). The blue line indicates the "
                "running median. From the normalised coverage, we estimate "
                "z-scores on a per-base level. The red lines indicates the "
                "z-scores at plus or minus N standard deviations, where N is "
                "chosen by the user. (default:4)</p>\n{0}".format(image))
        })

    def coverage_barplot(self):
        """ Coverage barplots section.
        """
        image1 = self.create_embedded_png(self.chromosome.plot_hist_coverage,
                                       input_arg="filename",
                                       style="width:45%")
        image2 = self.create_embedded_png(self.chromosome.plot_hist_coverage,
                                       input_arg="filename",
                                       kwargs={"logx": False},
                                       style="width:45%")
        self.sections.append({
            "name": "Coverage histogram",
            "anchor": "cov_barplot",
            "content": (
                "<p>The following figure contains the histogram of the genome "
                "coverage. The X and Y axis being in log scale.</p>\n"
                "{0}\n{1}".format(image1, image2))
        })

    def basic_stats(self):
        """ Basics statistics section.
        """
        html_table = self.dataframe_to_html_table(
            self.chromosome.get_stats(output="dataframe"), {"index": False})
        self.sections.append({
            "name": "Basic stats",
            "anchor": "basic_stats",
            "content": (
                "<p>The following table gives some basic statistics about the "
                "genome coverage.</p>\n{0}".format(html_table))
        })

    def regions_of_interest(self):
        """ Region of interest section.
        """
        rois = self.chromosome.get_roi()
        low_roi = rois.get_low_roi()
        high_roi = rois.get_high_roi()
        html_low_roi = self.dataframe_to_html_table(low_roi)
        html_high_roi = self.dataframe_to_html_table(high_roi)
        roi_paragraph = (
            "Regions with a z-score {0}er than {1:.2f} and at "
            "least one base with a z-score {0}er than {2:.2f} are detected as "
            "{0} coverage region. Thus, there are {3} {0} coverage regions.")
        low_paragraph = roi_paragraph.format("low",
                                             self.chromosome.thresholds.low2,
                                             self.chromosome.thresholds.low,
                                             len(low_roi))
        high_paragraph = roi_paragraph.format("high",
                                              self.chromosome.thresholds.high2,
                                              self.chromosome.thresholds.high,
                                              len(high_roi))
        self.sections.append({
            "name": "Regions Of Interest (ROI)",
            "anchor": "roi",
            "content": (
                "<p>Running median is the median computed along the genome "
                "using a sliding window. The following tables give regions of "
                "interest detected by sequana. Here is some captions:</p>\n"
                "<ul><li>mean_cov: the average of coverage</li>\n"
                "<li>mean_rm: the average of running median</li>\n"
                "<li>mean_zscore: the average of zscore</li>\n"
                "<li>max_zscore: the higher zscore contains in the region</li>"
                "</ul>\n"
                "<h3>Low coverage region</h3>\n{0}\n{1}\n"
                "<h3>High coverage region</h3>\n{2}\n{3}\n").format(
                low_paragraph, html_low_roi, high_paragraph, html_high_roi)
        })

    def normalized_coverage(self):
        """ Barplot of normalized coverage section.
        """
        image = self.create_embedded_png(
            self.chromosome.plot_hist_normalized_coverage,
            input_arg="filename")
        self.sections.append({
            "name": "Normalized coverage",
            "anchor": "normalized_coverage",
            "content": (
                "<p>Distribution of the normalized coverage with predicted "
                "Gaussian. The red line should be followed the trend of the "
                "barplot.</p>\n{0}".format(image))
        })

    def zscore_distribution(self):
        """ Barplot of zscore distribution section.
        """
        image = self.create_embedded_png(self.chromosome.plot_hist_zscore,
                                      input_arg="filename")
        self.sections.append({
            "name": "Z-Score distribution",
            "anchor": "zscore_distribution",
            "content": (
                "<p>Distribution of the z-score (normalised coverage); You "
                "should see a Gaussian distribution centered around 0. The "
                "estimated parameters are mu={0:.2f} and sigma={1:.2f}.</p>\n"
                "{2}".format(self.chromosome.best_gaussian["mu"],
                             self.chromosome.best_gaussian["sigma"],
                             image))
        })
