# -*- coding: utf-8 -*-
"""Integration tests: datasets managers define in the browser."""

from Missing import Value as MissingValue
from senaite.dashboard import storage
from senaite.dashboard.dashboards import usage
from senaite.dashboard.exceptions import Forbidden
from senaite.dashboard.exceptions import NotFound
from senaite.dashboard.exceptions import ValidationError
from senaite.dashboard.query import catalogs
from senaite.dashboard.query import custom
from senaite.dashboard.query import inspection
from senaite.dashboard.query.compute import compute
from senaite.dashboard.query.compute import get_data_version
from senaite.dashboard.query.registry import get_dataset
from senaite.dashboard.query.registry import get_datasets
from senaite.dashboard.tests.base import DashboardTestCase

CLIENTS = {
    "title": {"en": u"Clients", "de": u"Kunden"},
    "portal_type": "Client",
    "fields": [
        {"index": "review_state", "kind": "state", "title": u"Status"},
        {"index": "created", "kind": "date", "title": u"Created",
         "lab_only": False},
    ],
    "columns": [{"name": "Title", "kind": "text", "title": u"Name"}],
}


class CustomDatasetsTestCase(DashboardTestCase):

    def names(self, env):
        return [dataset.name for dataset in get_datasets(env)]

    def test_only_types_of_senaite_are_offered(self):
        types = [c["portal_type"] for c in catalogs.get_candidates()]
        self.assertIn("AnalysisRequest", types)
        self.assertIn("Client", types)
        self.assertNotIn("Document", types)
        self.assertNotIn("Folder", types)
        self.assertNotIn("Patient", types)
        self.assertNotIn("Plone Site", types)

    def test_personal_data_and_results_are_blocked(self):
        for name in ("getResult", "getPatientFullName",
                     "getMedicalRecordNumberValue", "getEmailAddress",
                     "patient_birthdate"):
            self.assertTrue(catalogs.is_blocked(name), name)
        self.assertFalse(catalogs.is_blocked("getClientUID"))

    def test_internal_indexes_are_not_offered(self):
        for name in ("allowedRolesAndUsers", "object_provides", "path",
                     "portal_type", "UID"):
            self.assertFalse(catalogs.is_offered(name), name)
        self.assertTrue(catalogs.is_offered("review_state"))

    def test_dates_of_an_index_read_as_dates(self):
        # 31 December 2026, 23:59 as the DateIndex keeps it
        minutes = (((2026 * 12 + 12) * 31 + 31) * 24 + 23) * 60 + 59
        self.assertEqual(catalogs.index_date_text(minutes), u"2026-12-31")

    def test_examples_leave_out_empty_values(self):
        values = [MissingValue, u"", u" ", None, u"WineScan", u"WineScan"]
        self.assertEqual(inspection.sample_column_values(values),
                         [u"WineScan", u"WineScan"])

    def test_inspection_proposes_kinds(self):
        manager = self.as_user("manager")
        answer = inspection.inspect("AnalysisRequest", manager)
        fields = {f["index"]: f for f in answer["fields"]}
        self.assertEqual(fields["review_state"]["kind"], "state")
        self.assertEqual(fields["getClientUID"]["kind"], "reference")
        self.assertEqual(fields["getClientUID"]["portal_type"], "Client")
        self.assertEqual(fields["created"]["kind"], "date")
        blocked = [name for name in fields if catalogs.is_blocked(name)]
        self.assertEqual(blocked, [])

    def test_a_saved_dataset_is_offered_to_the_laboratory(self):
        record = custom.save(CLIENTS, self.as_user("manager"))
        self.assertTrue(record["name"].startswith(custom.PREFIX))
        self.assertIn(record["name"], self.names(self.as_user("analyst")))
        self.assertNotIn(record["name"],
                         self.names(self.as_user("contact")))

    def test_columns_are_for_the_laboratory_unless_opened(self):
        opened = dict(CLIENTS, lab_only=False, columns=[
            {"name": "Title", "kind": "text"}])
        name = custom.save(opened, self.as_user("manager"))["name"]
        contact = self.as_user("contact")
        dataset = get_dataset(name, contact)
        self.assertEqual(dataset.get_columns(contact), [])

    def test_fields_are_for_the_laboratory_unless_opened(self):
        record = custom.save(dict(CLIENTS, lab_only=False),
                             self.as_user("manager"))
        contact = self.as_user("contact")
        dataset = get_dataset(record["name"], contact)
        names = [field.name for field in dataset.get_fields(contact)]
        self.assertEqual(names, ["created"])

    def test_columns_of_lab_only_fields_are_for_the_laboratory(self):
        opened = dict(CLIENTS, lab_only=False, columns=[
            {"name": "Title", "kind": "text", "lab_only": False},
            {"name": "review_state", "kind": "state", "lab_only": False}])
        name = custom.save(opened, self.as_user("manager"))["name"]
        contact = self.as_user("contact")
        dataset = get_dataset(name, contact)
        self.assertEqual([c.name for c in dataset.get_columns(contact)],
                         ["Title"])
        self.assertRaises(ValidationError, compute, "list", {
            "dataset": name, "columns": ["review_state"]}, contact)
        analyst = self.as_user("analyst")
        self.assertEqual(len(dataset.get_columns(analyst)), 2)

    def test_names_blocked_later_are_not_offered(self):
        record = custom.save(CLIENTS, self.as_user("manager"))
        record["columns"].append(
            {"name": "getEmailAddress", "title": u"Email", "kind": "text"})
        record["fields"].append({"index": "path", "title": u"Path",
                                 "kind": "text", "lab_only": True})
        storage.set_dataset(record)
        dataset = get_dataset(record["name"], self.as_user("analyst"))
        self.assertNotIn("getEmailAddress", dataset.columns)
        self.assertNotIn("path", dataset.fields)

    def test_a_dataset_saved_again_has_a_new_version(self):
        manager = self.as_user("manager")
        record = custom.save(CLIENTS, manager)
        version = get_data_version(record["name"])
        custom.remove(record["name"], manager)
        again = custom.save(CLIENTS, manager)
        self.assertEqual(again["name"], record["name"])
        self.assertEqual(again["revision"], record["revision"])
        self.assertNotEqual(get_data_version(again["name"]), version)

    def test_a_span_titled_with_a_number_can_be_measured(self):
        span = {"title": u"24h check", "start": "created", "end": "created"}
        manager = self.as_user("manager")
        record = custom.save(dict(CLIENTS, spans=[span]), manager)
        name = record["spans"][0]["name"]
        self.assertEqual(name, "span-24h-check")
        answer = compute("span", {"dataset": record["name"], "span": name},
                         manager)
        self.assertEqual(answer["count"], 0)

    def test_tiles_count_on_a_saved_dataset(self):
        manager = self.as_user("manager")
        record = custom.save(CLIENTS, manager)
        answer = compute("count", {"dataset": record["name"]}, manager)
        self.assertEqual(answer, {"value": 0})

    def test_definitions_are_checked(self):
        manager = self.as_user("manager")
        wrong_index = dict(CLIENTS, fields=[{"index": "nope",
                                             "kind": "text"}])
        wrong_kind = dict(CLIENTS, fields=[{"index": "created",
                                            "kind": "state"}])
        wrong_type = dict(CLIENTS, portal_type="Document")
        for body in (wrong_index, wrong_kind, wrong_type,
                     dict(CLIENTS, title=u" ")):
            self.assertRaises(ValidationError, custom.save, body, manager)

    def test_saving_again_keeps_the_name(self):
        manager = self.as_user("manager")
        record = custom.save(CLIENTS, manager)
        again = custom.save(dict(CLIENTS, name=record["name"]), manager)
        self.assertEqual(again["name"], record["name"])
        self.assertEqual(again["revision"], 2)

    def test_only_managers_define_datasets(self):
        analyst = self.as_user("analyst")
        self.assertRaises(Forbidden, custom.save, CLIENTS, analyst)
        self.assertRaises(Forbidden, inspection.inspect, "Client", analyst)

    def test_remove(self):
        manager = self.as_user("manager")
        record = custom.save(CLIENTS, manager)
        custom.remove(record["name"], manager)
        self.assertRaises(ValidationError, get_dataset, record["name"],
                          manager)
        self.assertRaises(NotFound, custom.remove, record["name"], manager)

    def test_usage_counts_global_dashboards(self):
        manager = self.as_user("manager")
        record = custom.save(CLIENTS, manager)
        counts = usage.count_usage(record["name"], manager)
        self.assertEqual(counts, {"dashboards": 0, "library": 0})
