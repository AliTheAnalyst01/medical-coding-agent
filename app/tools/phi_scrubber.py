from functools import lru_cache
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


@lru_cache(maxsize=1)
def _get_engines():
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    return analyzer, anonymizer


def scrub_phi(text: str) -> str:
    analyzer, anonymizer = _get_engines()
    results = analyzer.analyze(text=text, language="en")
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
