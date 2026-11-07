"""Network-free INSPIRE API pagination/completeness regression tests."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspire_quirkonium_citations import citations,small_record,references

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

    def test_references_preserve_existing_external_ids(self):
        paper={"metadata":{"references":[{"record":{"$ref":"https://inspirehep.net/api/literature/5"},
              "reference":{"title":{"title":"Old quirk paper"},
                           "arxiv_eprint":"0805.4667"}}]}}
        out=references(paper)
        self.assertEqual(out[0]["arxiv"],"0805.4667")
        self.assertEqual(len(out),1)

if __name__=="__main__":
    unittest.main()
