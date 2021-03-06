# -*- coding: utf-8 -*-
from pathlib import Path
import scrapy
from scrapy.http import Request

from pudl_scrapers import items
from pudl_scrapers.helpers import new_output_dir


class Ferc1Spider(scrapy.Spider):
    name = 'ferc1'
    allowed_domains = ['www.ferc.gov']
    start_urls = ['https://www.ferc.gov/docs-filing/forms/form-1/data.asp']

    def __init__(self, year=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if year is not None:
            year = int(year)

            if year < 1994:
                raise ValueError("Years before 1994 are not supported")

        self.year = year

    def start_requests(self):
        """
        Start requesting Ferc 1 forms

        Yields:
            List of Requests for Ferc 1 forms
        """
        # Spider settings are not available during __init__, so finalizing here
        settings_output_dir = Path(self.settings.get("OUTPUT_DIR"))
        output_root = settings_output_dir / "ferc1"
        self.output_dir = new_output_dir(output_root)

        if self.year is not None:
            yield self.form_for_year(self.year)
            return

        yield from self.all_form_requests()

    def parse(self, response):
        """
        Produce the Ferc1 item

        Args:
            response: scrapy.http.Response containing ferc1 data

        Yields:
            Ferc1 item
        """
        path = self.output_dir / ("ferc1-%s.zip" % response.meta["year"])

        yield items.Ferc1(data=response.body, year=response.meta["year"],
                          save_path=path)

    def form_for_year(self, year):
        """
        Produce a form request for the given year

        Args:
            year: int

        Returns:
            Request for the Ferc 1 form
        """
        url = "ftp://eforms1.ferc.gov/f1allyears/f1_%d.zip" % year
        return Request(url, meta={"year": year}, callback=self.parse)

    def all_form_requests(self):
        """
        Produces form requests for all supported years

        Yields:
            Requests for all available Ferc form 1 zip files
        """
        for year in range(1994, 2021):
            yield self.form_for_year(year)
