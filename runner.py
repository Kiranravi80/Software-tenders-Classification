import asyncio

from app.api.gem_client import GeMClient
from app.pipeline.collector import TenderCollector
from app.pipeline.downloader import PDFDownloader

from app.ai.classifier import TenderClassifier
from app.ai.extractor import TenderExtractor

from app.parser.pdf_parser import PDFParser

from app.database.mongodb import mongodb
from app.database.repository import repository
from app.database.embeddings import EmbeddingGenerator


async def main():

    print("=" * 70)
    print("GeM AI Tender Scraper")
    print("=" * 70)

    # ==========================================================
    # Connect MongoDB
    # ==========================================================

    await mongodb.connect()
    await repository.initialize()

    # ==========================================================
    # GeM Client
    # ==========================================================

    print("\nConnecting to GeM...")

    client = GeMClient()

    client.initialize()

    # ==========================================================
    # Fetch Today's Tenders
    # ==========================================================

    print("\nFetching today's tenders...")

    raw_tenders = client.fetch_all()

    print(f"Fetched {len(raw_tenders)} tenders")

    # ==========================================================
    # Normalize
    # ==========================================================

    collector = TenderCollector()

    clean_tenders = collector.process(raw_tenders)

    collector.save(
        clean_tenders,
        "output/all_tenders.json"
    )

    print(f"Saved {len(clean_tenders)} normalized tenders")

    # ==========================================================
    # AI Classification
    # ==========================================================

    print("\nRunning AI Classification...")

    classifier = TenderClassifier()

    software_tenders = []

    for index, tender in enumerate(clean_tenders, start=1):

        print(
            f"[{index}/{len(clean_tenders)}] "
            f"{tender['bid_number']}"
        )

        try:

            result = classifier.classify(tender)

            tender["is_software"] = result["is_software"]
            tender["category"] = result["category"]
            tender["confidence"] = result["confidence"]
            tender["reason"] = result["reason"]

            if tender["is_software"]:
                software_tenders.append(tender)

        except Exception as e:

            print(
                f"Classification Failed : {e}"
            )

    print()

    print("=" * 60)
    print(f"Software Tenders : {len(software_tenders)}")
    print("=" * 60)

    # ==========================================================
    # Download PDFs
    # ==========================================================

    print("\nDownloading PDFs...")

    downloader = PDFDownloader(
        client.session
    )

    downloader.download_all(
        software_tenders
    )

    # ==========================================================
    # PDF Parsing + AI Understanding
    # ==========================================================

    print("\nParsing PDFs...")

    parser = PDFParser()

    extractor = TenderExtractor()

    for index, tender in enumerate(
        software_tenders,
        start=1
    ):

        if not tender.get("downloaded"):

            continue

        print(
            f"[{index}/{len(software_tenders)}] "
            f"{tender['bid_number']}"
        )

        try:

            text = parser.extract_text(
                tender["pdf_path"]
            )

            # -------------------------
            # Phase 3
            # -------------------------

            tender["pdf_fields"] = extractor.extract(
                text
            )

            # -------------------------
            # Phase 4
            # -------------------------

            tender["ai_analysis"] = extractor.understand(
                text
            )

        except Exception as e:

            print(
                f"PDF Parsing Failed : {e}"
            )

    # ==========================================================
    # Embedding Generation
    # ==========================================================

    print("\nGenerating Embeddings...")

    embedder = EmbeddingGenerator()

    for index, tender in enumerate(
        software_tenders,
        start=1
    ):

        try:

            tender["embedding"] = embedder.generate(
                tender
            )

            print(
                f"[{index}/{len(software_tenders)}] "
                "Embedding Generated"
            )

        except Exception as e:

            print(
                f"Embedding Failed : {e}"
            )

    # ==========================================================
    # Save To MongoDB
    # ==========================================================

    print("\nSaving to MongoDB...")

    result = await repository.save_many(
        software_tenders
    )

    print()

    print("=" * 60)
    print(f"Inserted : {result['inserted']}")
    print(f"Updated  : {result['updated']}")
    print("=" * 60)

    # ==========================================================
    # Save Final JSON
    # ==========================================================

    collector.save(

        software_tenders,

        "output/software_tenders.json"

    )

    print()

    print(
        f"Saved {len(software_tenders)} software tenders"
    )

    # ==========================================================
    # Disconnect MongoDB
    # ==========================================================

    await mongodb.disconnect()

    print()

    print("=" * 70)
    print("Pipeline Completed Successfully")
    print("=" * 70)


if __name__ == "__main__":

    asyncio.run(main())