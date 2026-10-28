import unittest
from datetime import datetime
from unittest import mock

import requests
from fastapi.testclient import TestClient

import main
from schedule_of_classes_scraper import soc_scraper
from term_id_functions import default_term_id

client = TestClient(main.app)


def html_response(html):
    response = requests.Response()
    response.status_code = 200
    response._content = html.encode()
    return response


COURSES_HTML = """
<div class="course">
  <div class="course-id">TEST101</div><span class="course-title">Has Credits</span>
  <span class="course-min-credits">4</span><span class="grading-method">Reg</span>
  <div class="section delivery-blended">
    <span class="section-id">0101</span>
    <span class="section-instructor">Sujeong Kim</span><span class="section-instructor">William Regli</span>
    <span class="total-seats-count">30</span><span class="open-seats-count">10</span>
    <div class="class-days-container"><div class="row">
      <span class="section-days">TuTh</span><span class="class-start-time">2:00pm</span><span class="class-end-time">3:15pm</span>
      <span class="class-building"><span class="building-code">IRB</span><span class="class-room">0324</span></span>
    </div></div>
  </div>
</div>
<div class="course">
  <div class="course-id">TEST102</div><span class="course-title">Sparse</span>
  <div class="section delivery-online"><span class="section-id">FC01</span></div>
</div>
"""


class DefaultTermTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(default_term_id(datetime(2027, 1, 25)), "202701")  # used to return 202708
        self.assertEqual(default_term_id(datetime(2027, 2, 21)), "202708")
        self.assertEqual(default_term_id(datetime(2027, 10, 1)), "202801")


class ScheduleScraperTests(unittest.TestCase):
    def scrape(self):
        with mock.patch.object(soc_scraper.http_utils, "fetch", return_value=html_response(COURSES_HTML)):
            return {section.course_number: section for section in
                    soc_scraper.scrape_course_data_from_schedule_of_classes("TEST", "202701")}

    def test_parses_a_full_section(self):
        section = self.scrape()["TEST101"]
        self.assertEqual(section.instructor, "Sujeong Kim, William Regli")
        self.assertEqual((section.minimum_credits, section.maximum_credits), (4, 4))
        self.assertEqual((section.total_seats, section.open_seats, section.waitlist_count), (30, 10, 0))
        self.assertEqual((section.is_normal, section.is_blended, section.is_online), (1, 1, 1))
        self.assertEqual(section.class_times[0].time, "TuTh 2:00pm-3:15pm")
        self.assertEqual(section.class_times[0].room, "IRB 0324")

    def test_sparse_section_does_not_crash_or_inherit_credits(self):
        section = self.scrape()["TEST102"]
        self.assertEqual((section.minimum_credits, section.maximum_credits), (None, None))
        self.assertEqual((section.instructor, section.total_seats, section.class_times), (None, None, []))
        self.assertIsNone(section.description)


class ClassSectionsEndpointTests(unittest.TestCase):
    def test_defaults_to_current_term_at_request_time(self):
        with mock.patch.object(main, "scrape_course_data_from_schedule_of_classes", return_value=[]) as scrape, \
                mock.patch.object(main, "update_term_id", return_value="202701"):
            client.get("/v1/class_sections/CMSC351")
        scrape.assert_called_once_with("CMSC351", "202701")

    def test_unpublished_term_keeps_the_pipeline_contract(self):
        with mock.patch.object(main, "scrape_course_data_from_schedule_of_classes", return_value=[]):
            response = client.get("/v1/class_sections/CMSC351?term_id=202708")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Course not found!"})

    def test_invalid_term_is_rejected(self):
        self.assertEqual(client.get("/v1/class_sections/CMSC351?term_id=202702").status_code, 400)

    def test_upstream_failure_is_503(self):
        with mock.patch.object(main, "scrape_course_data_from_schedule_of_classes",
                               side_effect=requests.ConnectionError("down")):
            response = client.get("/v1/class_sections/CMSC351?term_id=202701")
        self.assertEqual(response.status_code, 503)


class OtherEndpointTests(unittest.TestCase):
    def test_catalog_failure_is_503(self):
        with mock.patch.object(main, "scrape_course_catalog_data", side_effect=requests.Timeout()):
            self.assertEqual(client.get("/v1/classes/CMSC131").status_code, 503)

    def test_geneds_failure_is_503(self):
        with mock.patch.object(main, "all_gen_eds_scraper", side_effect=requests.HTTPError("502")):
            self.assertEqual(client.get("/v1/geneds").status_code, 503)


if __name__ == "__main__":
    unittest.main()
