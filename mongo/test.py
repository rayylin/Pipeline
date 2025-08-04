import pymongo
import json
import os
import asyncio
import re
from datetime import datetime
from typing import Dict, Any
from openai import OpenAI

from app.scraper.company_number_extractor import get_company_numbers
from app.core.utils.scraper_utils import scrape_using_crawl4ai, read_online_pdf, openai_call
from app.logger.app_logger import app_logger as logger
from app.core.test_prompts import GLOBAL_COMPANY_HOUSE_DETAILS_EXTRACTION_PROMPT_DS_generated_mar24820_v1
from app.embeds_store.mongodb import MongoDBClient

class CompaniesHouseScraper:
    """Scrapes and processes Companies House search results for business listings."""

    def __init__(self, company_number: str) -> None:
        self.company_number = company_number
        self.overview = f"https://find-and-update.company-information.service.gov.uk/company/{company_number}"
        self.filing_history = f"https://find-and-update.company-information.service.gov.uk/company/{company_number}/filing-history"
        self.people = f"https://find-and-update.company-information.service.gov.uk/company/{company_number}/officers"
        self.more_info = f"https://find-and-update.company-information.service.gov.uk/company/{company_number}/more"
        self.scrape_using_crawl4ai = scrape_using_crawl4ai
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.google_search = "https://www.google.com/search?q="
        self.mongo_client = MongoDBClient()

    async def scrape_filing_history(self) -> Dict[str, Any]:
        try:
            markdown = await self.scrape_using_crawl4ai(self.filing_history)
            # save_to_file(markdown, "filing_history", "ch_data", "ch", "md", self.timestamp)
            self.mongo_client.insert_one(
                db_name="ch_data",
                collection_name="scraped_filing_history",
                document={
                    "company_number": self.company_number,
                    "timestamp": self.timestamp,
                    "markdown": markdown
                }
            )
            logger.log_info(f"Successfully scraped filing history for {self.company_number}")
            return {"status": "success", "result": markdown}
        except Exception as e:
            logger.log_error(f"Failed to scrape filing history for {self.company_number}: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Scraping filing history failed: {str(e)}"}

    async def scrape_people(self) -> Dict[str, Any]:
        try:
            markdown = await self.scrape_using_crawl4ai(self.people)
            # save_to_file(markdown, "people", "ch_data", "ch", "md", self.timestamp)
            self.mongo_client.insert_one(
                db_name="test_db",
                collection_name="scraped_people",
                document={
                    "company_number": self.company_number,
                    "timestamp": self.timestamp,
                    "markdown": markdown
                }
            )
            logger.log_info(f"Successfully scraped people for {self.company_number}")
            return {"status": "success", "result": markdown}
        except Exception as e:
            logger.log_error(f"Failed to scrape people for {self.company_number}: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Scraping people failed: {str(e)}"}

    async def scrape_more_info(self) -> Dict[str, Any]:
        try:
            markdown = await self.scrape_using_crawl4ai(self.more_info)
            # save_to_file(markdown, "more_info", "ch_data", "ch", "md", self.timestamp)
            self.mongo_client.insert_one(
                db_name="test_db",
                collection_name="scraped_more_info",
                document={
                    "company_number": self.company_number,
                    "timestamp": self.timestamp,
                    "markdown": markdown
                }
            )
            logger.log_info(f"Successfully scraped more info for {self.company_number}")
            return {"status": "success", "result": markdown}
        except Exception as e:
            logger.log_error(f"Failed to scrape more info for {self.company_number}: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Scraping more info failed: {str(e)}"}

    async def scrape_overview(self) -> Dict[str, Any]:
        try:
            markdown = await self.scrape_using_crawl4ai(self.overview)
            # save_to_file(markdown, "overview", "ch_data", "ch", "md", self.timestamp)
            self.mongo_client.insert_one(
                db_name="test_db",
                collection_name="scraped_overview",
                document={
                    "company_number": self.company_number,
                    "timestamp": self.timestamp,
                    "markdown": markdown
                }
            )
            logger.log_info(f"Successfully scraped overview for {self.company_number}")
            return {"status": "success", "result": markdown}
        except Exception as e:
            logger.log_error(f"Failed to scrape overview for {self.company_number}: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Scraping overview failed: {str(e)}"}

    async def get_company_title(self):
        try:
            markdown = await self.scrape_using_crawl4ai(self.overview, id="content-container")
            title = re.search(r'^(.*?)\s+Company number', markdown)
            if title:
                return title.group(1).strip()
            else:
                return "Company Title Not Found"
        except Exception as e:
            logger.log_error(f"Failed to scrape company title for {self.company_number}: {str(e)}", exc_info=True)
            return "Company Title Not Found"

    async def extract_website_details(self, company_name: str):
        try:
            company_name = await self.get_company_title()
            search_query = f"{company_name} official website United Kingdom"
            print(company_name)
            search_query = search_query.replace(" ", "+")
            search_url = f"{self.google_search}{search_query}"
            logger.log_info(f"Searching for website {search_url}")
            search_results = await self.scrape_using_crawl4ai(search_url)

            match = re.search(r'###\s*(.*)', search_results)
            if match:
                first_text = match.group(1).strip()
                urls = re.findall(r'\((https?://[^\s]+)\)', first_text)
                if urls:
                    last_url = urls[-1]
                    logger.log_info(f"Found website {last_url}")
                    markdown = await self.scrape_using_crawl4ai(last_url)
                    # save_to_file(markdown, "website_details", "ch_data", "ch", "md", self.timestamp)
                    self.mongo_client.insert_one(
                        db_name="test_db",
                        collection_name="extracted_website_details",
                        document={
                            "company_number": self.company_number,
                            "timestamp": self.timestamp,
                            "website_url": last_url,
                            "markdown": markdown
                        }
                    )
                    logger.log_info(f"Successfully extracted website details for {self.company_number}")
                    return {"status": "success", "result": markdown}
                else:
                    logger.log_warning("No URLs found in the first text after ###")
                    return "URL Not Found"
            else:
                logger.log_warning("No text found after ### in search results")
                return "Text Not Found"
        except Exception as e:
            logger.log_error(f"Failed to extract website details for {self.company_number}: {str(e)}", exc_info=True)
            return "Website Not Found"

    def extract_proper_links(self, markdown: str) -> Dict[str, Any]:
        try:
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown)
            pattern = re.compile(r"format=pdf")
            pdf_links = [(title, link) for title, link in links if pattern.search(link)][:8]
            logger.log_info(f"Extracted {len(pdf_links)} PDF links for {self.company_number}")
            return {"status": "success", "result": pdf_links}
        except Exception as e:
            logger.log_error(f"Failed to extract proper links: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Extracting proper links failed: {str(e)}"}

    async def read_pds_information(self, pdf_links_result) -> Dict[str, Any]:
        try:
            markdown = await self.scrape_using_crawl4ai(self.filing_history)
            pdf_links_result = self.extract_proper_links(markdown)
            if pdf_links_result["status"] == "failure":
                return pdf_links_result

            pdf_links = pdf_links_result["result"]
            financial_info = {}

            for title, pdf_link in pdf_links:
                pdf_content = read_online_pdf(pdf_link, use_gpt=True)
                financial_info[title] = {
                    "Pdf Title": title,
                    "link": pdf_link,
                    "content": pdf_content["gpt_text"]
                }

            # save_to_file(financial_info, "extracted_ch_pdfs_content", "ch_data", "ch", "json", self.timestamp)
            self.mongo_client.insert_one(
                db_name="test_db",
                collection_name="extracted_ch_pdfs_content",
                document={
                    "company_number": self.company_number,
                    "timestamp": self.timestamp,
                    "financial_info": financial_info
                }
            )
            logger.log_info(f"Successfully read PDF information for {self.company_number}")
            return {"status": "success", "result": financial_info}
        except Exception as e:
            logger.log_error(f"Failed to read PDF information for {self.company_number}: {str(e)}", exc_info=True)
            return {"status": "failure", "message": f"Reading PDF information failed: {str(e)}"}

    def get_business_information(self, fh_md: str, o_md: str, m_md: str, p_md: str, jc, owd: str) -> Dict[str, Any]:
        user_prompt = f"Extract business information from overview markdown: {fh_md}, filing history markdown: {o_md}, people markdown: {p_md}, and more info markdown: {m_md}, JSON content that has pdf name, respected link, and pdf extracted content: {jc}, Official website details: {owd}"
        max_retries = 5
        for attempt in range(max_retries):
            try:
                raw_data = openai_call(
                    system_prompt=GLOBAL_COMPANY_HOUSE_DETAILS_EXTRACTION_PROMPT_DS_generated_mar24820_v1,
                    user_prompt=user_prompt)
                try:
                    parsed_data = json.loads(raw_data)
                    break
                except json.JSONDecodeError:
                    json_match = re.search(r'```json\s*({.*?})\s*```', raw_data, re.DOTALL)
                    if json_match:
                        parsed_data = json.loads(json_match.group(1))
                        break
                    else:
                        logger.log_warning(f"Invalid JSON format for {self.company_number}, attempt {attempt + 1}")
                        if attempt == max_retries - 1:
                            return {"status": "failure", "message": "Invalid JSON format after retries"}
            except Exception as e:
                logger.log_warning(f"OpenAI call failed for {self.company_number} on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return {"status": "failure", "message": f"OpenAI call failed after {max_retries} retries: {str(e)}"}

        logger.log_info(f"Successfully processed business information for {self.company_number}")

        self.mongo_client.insert_one(
            db_name="test_db",
            collection_name="business_details",
            document={
                "company_number": self.company_number,
                "timestamp": self.timestamp,
                "details": parsed_data
            }
        )

        return {"status": "success", "result": parsed_data}

if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
        company_numbers = get_company_numbers('data/example_upload_data/Companies-House-search-results.csv')[38     :50]
        for idx, company_number in enumerate(company_numbers, 1):
            print(f"[{idx}] Company number: {company_number}")
            scraper = CompaniesHouseScraper(company_number)
            a = asyncio.run(scraper.scrape_filing_history())
            b = asyncio.run(scraper.scrape_people())
            c = asyncio.run(scraper.scrape_more_info())
            d = asyncio.run(scraper.scrape_overview())
            e = asyncio.run(scraper.read_pds_information(a['result']))
            f = asyncio.run(scraper.get_company_title())
            g = asyncio.run(scraper.extract_website_details(f))
            h = scraper.get_business_information(a['result'], b['result'], c['result'], d['result'], e['result'], g['result'])
    except RuntimeError as e:
        print("An error occurred:", e)