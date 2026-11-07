"""Network-free INSPIRE API pagination/completeness regression tests."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspire_quirkonium_citations import (citations,small_record,references,
    validate_citation_cross_checks,canonical_recid)

class TestInspireGraph(unittest.TestCase):
    @staticmethod
    def hit(n):
        return {"id":n,"metadata":{"titles":[{"title":f"Quirk number {n}"}],
                "arxiv_eprints":[{"value":f"2504.{n:05d}"}],
                "citation_count":2}}
    def test_full_page_pagination_then_complete(self):
        pages=[
            {"hits":{"total":101,"hits":[self.hit(i) for i in range(100)]}},
            {"hits":{"total":101,"hits":[self.hit(100)]}}
        ]
        with (patch("inspire_quirkonium_citations.fetch_json",
                    side_effect=pages) as get,
              patch("inspire_quirkonium_citations.time.sleep")):
            x=citations("123",max_pages=2)
        self.assertTrue(x["complete"])
        self.assertEqual(x["page_count"],2)
        self.assertEqual(len(x["items"]),101)
        self.assertEqual(get.call_count,2)

    def test_truncated_page_not_called_complete(self):
        pages=[{"hits":{"total":101,
                        "hits":[self.hit(i) for i in range(100)]}}]
        with patch("inspire_quirkonium_citations.fetch_json",
                   side_effect=pages):
            x=citations("123",max_pages=1)
        self.assertFalse(x["complete"])

    def test_api_failure_marks_incomplete(self):
        with patch("inspire_quirkonium_citations.fetch_json",
                   side_effect=RuntimeError("API unavailable")):
            x=citations("123",max_pages=2)
        self.assertFalse(x["complete"])
        self.assertTrue(x["errors"])

    def test_arxiv_lookup_alias_uses_numeric_control_number(self):
        result={"id":"2504.02940","metadata":{
            "control_number":2912345,
            "arxiv_eprints":[{"value":"2504.02940"}],
            "titles":[{"title":"Seed"}]}}
        self.assertEqual(canonical_recid(result),"2912345")
        self.assertEqual(small_record(result)["recid"],"2912345")

    def test_external_arxiv_alias_without_control_number_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"no canonical numeric"):
            canonical_recid({"id":"0805.4667","metadata":{}})

    def test_numeric_hit_id_accepted(self):
        self.assertEqual(canonical_recid(self.hit(808)), "808")

    def test_missing_known_2025_to_2008_citation_is_inconsistent(self):
        data={
          "scalar_2008":{
            "arxiv":"0805.4667","metadata":{
              "recid":"108","arxiv":["0805.4667"],"citation_count":0},
            "forward":{"total":0,"items":[]}},
          "scalar_2025":{
            "arxiv":"2504.02940","metadata":{
              "recid":"125","arxiv":["2504.02940"],"citation_count":2},
            "forward":{"total":2,"items":[]}},
        }
        issues=validate_citation_cross_checks(data)
        self.assertTrue(any(x["type"]=="MISSING_DOCUMENTED_CITATION"
                            and x["expected_citing_recid"]=="125"
                            for x in issues))

    def test_cited_relation_present_and_ids_match(self):
        data={
          "scalar_2008":{
            "arxiv":"0805.4667","metadata":{
              "recid":"108","arxiv":["0805.4667"],"citation_count":1},
            "forward":{"total":1,"items":[{"recid":"125"}]}},
          "scalar_2025":{
            "arxiv":"2504.02940","metadata":{
              "recid":"125","arxiv":["2504.02940v2"],"citation_count":0},
            "forward":{"total":0,"items":[]}},
        }
        self.assertEqual(validate_citation_cross_checks(data),[])

    def test_citation_metadata_count_disagreement_detected(self):
        data={
          "scalar_2008":{
            "arxiv":"0805.4667","metadata":{
              "recid":"108","arxiv":["0805.4667"],"citation_count":35},
            "forward":{"total":0,"items":[]}},
          "scalar_2025":{
            "arxiv":"2504.02940","metadata":{
              "recid":"125","arxiv":["2504.02940"],"citation_count":2},
            "forward":{"total":2,"items":[]}},
        }
        issues=validate_citation_cross_checks(data)
        self.assertTrue(any(x["type"]=="COUNT_DISAGREEMENT"
                            for x in issues))

    def test_references_preserve_existing_external_ids(self):
        paper={"metadata":{"references":[{"record":{"$ref":"https://inspirehep.net/api/literature/5"},
              "reference":{"title":{"title":"Old quirk paper"},
                           "arxiv_eprint":"0805.4667"}}]}}
        out=references(paper)
        self.assertEqual(out[0]["arxiv"],"0805.4667")
        self.assertEqual(len(out),1)

if __name__=="__main__":
    unittest.main()
