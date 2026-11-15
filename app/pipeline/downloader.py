from pathlib import Path
import time

from app.utils.logger import log


class PDFDownloader:

    def __init__(self, session):

        self.session = session

        self.output_dir = Path("pdfs")

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def download(self, tender):

        pdf_url = tender.get("pdf_url")

        if not pdf_url:

            log.warning("No PDF URL")

            return False

        filename = (
            tender["bid_number"]
            .replace("/", "_")
            .replace("\\", "_")
            + ".pdf"
        )

        filepath = self.output_dir / filename

        # Already downloaded

        if filepath.exists():

            tender["pdf_path"] = str(filepath)

            tender["downloaded"] = True

            log.info(f"Already exists : {filename}")

            return True

        # Retry 3 times

        for attempt in range(3):

            try:

                response = self.session.get(
                    pdf_url,
                    timeout=60,
                    stream=True
                )

                response.raise_for_status()

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                )

                if "pdf" not in content_type.lower():

                    raise Exception(
                        f"Invalid content type : {content_type}"
                    )

                with open(filepath, "wb") as f:

                    for chunk in response.iter_content(8192):

                        if chunk:

                            f.write(chunk)

                # Verify PDF

                with open(filepath, "rb") as f:

                    if f.read(4) != b"%PDF":

                        filepath.unlink(
                            missing_ok=True
                        )

                        raise Exception(
                            "Invalid PDF"
                        )

                tender["pdf_path"] = str(filepath)

                tender["downloaded"] = True

                log.success(
                    f"Downloaded : {filename}"
                )

                return True

            except Exception as e:

                log.warning(
                    f"{filename} Retry {attempt+1}/3 : {e}"
                )

                time.sleep(2)

        tender["downloaded"] = False

        tender["pdf_path"] = None

        log.error(f"Failed : {filename}")

        return False

    def download_all(self, tenders):

        downloaded = 0

        skipped = 0

        failed = 0

        for tender in tenders:

            if not tender.get("is_software"):

                skipped += 1

                continue

            if self.download(tender):

                downloaded += 1

            else:

                failed += 1

        log.info(f"Downloaded : {downloaded}")

        log.info(f"Skipped : {skipped}")

        log.info(f"Failed : {failed}")

        return downloaded